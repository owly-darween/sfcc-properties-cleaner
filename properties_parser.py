import os
import re
from collections import defaultdict
from difflib import SequenceMatcher
import pandas as pd

# Dictionary to store properties by language and by file
properties_by_language_file = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
merge_stats = defaultdict(lambda: defaultdict(lambda: {"merged": 0, "conflicts": 0}))
conflict_sources = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

# Root directory containing the cartridges
root_dir = os.getcwd()  # Use the current directory

# Function to read a properties file
def read_properties(file_path, cartridge_name):
    properties = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if not line.strip() or line.startswith('#'):
                    continue
                key_value = line.strip().split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    properties[key.strip()] = (value.strip(), cartridge_name)
    except UnicodeDecodeError:
        # If a decoding error occurs, try with ISO-8859-1
        print(f"Error decoding {file_path} with UTF-8, trying ISO-8859-1")
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            for line in file:
                if not line.strip() or line.startswith('#'):
                    continue
                key_value = line.strip().split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    properties[key.strip()] = (value.strip(), cartridge_name)
    return properties

# Function to calculate the similarity between two strings
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Function to traverse directories and read properties files
def parse_cartridges():
    for cartridge in os.listdir(root_dir):
        cartridge_path = os.path.join(root_dir, cartridge)
        resources_path = os.path.join(cartridge_path, 'cartridge', 'templates', 'resources')
        if os.path.exists(resources_path):
            for file_name in os.listdir(resources_path):
                if file_name.endswith('.properties'):
                    lang_match = re.search(r'_([a-z]{2}_[A-Z]{2})\.properties$', file_name)
                    if lang_match:
                        lang = lang_match.group(1)
                        file_path = os.path.join(resources_path, file_name)
                        properties = read_properties(file_path, cartridge)
                        for key, value in properties.items():
                            properties_by_language_file[lang][file_name][key].append((value[0], value[1], file_path))

# Function to merge the properties files and create directories by language
def merge_properties():
    output_dir = "merged_properties"
    os.makedirs(output_dir, exist_ok=True)

    for lang, files in properties_by_language_file.items():
        # Create a directory per language
        lang_dir = os.path.join(output_dir, lang)
        os.makedirs(lang_dir, exist_ok=True)
        
        for file_name, keys in files.items():
            output_file = os.path.join(lang_dir, file_name)
            with open(output_file, 'w', encoding='utf-8') as file:
                for key, value_list in keys.items():
                    values = [v[0] for v in value_list]
                    # If all values are identical, keep only one entry
                    if len(set(values)) == 1:
                        file.write(f"{key}={values[0]}\n")
                        merge_stats[lang][file_name]["merged"] += 1
                        # Remove the property from the source file
                        remove_from_source(key, value_list[0][2])
                    else:
                        # Conflict management: check if the values are truly different
                        conflict_values = {v[0] for v in value_list}
                        if len(conflict_values) > 1:
                            merge_stats[lang][file_name]["conflicts"] += 1
                            # Add conflicting values to the export file
                            conflict_sources[lang][file_name][key].extend(value_list)
                        # Merge the best value
                        best_value = find_best_value(values)
                        file.write(f"{key}={best_value}\n")
                        # Remove the property from the source file
                        for i, (value, _, path) in enumerate(value_list):
                            if value == best_value:
                                remove_from_source(key, path)

# Function to find the best value based on similarity
def find_best_value(values):
    best_value = values[0]
    max_similarity = 0
    for value in values:
        similarity_sum = sum(similarity(value, v) for v in values if v != value)
        if similarity_sum > max_similarity:
            max_similarity = similarity_sum
            best_value = value
    return best_value

# Function to remove a property from a source file
def remove_from_source(key, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        with open(file_path, 'w', encoding='utf-8') as file:
            for line in lines:
                if not line.startswith(f"{key}="):
                    file.write(line)
    except UnicodeDecodeError:
        # Handle ISO-8859-1 if necessary
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            lines = file.readlines()
        with open(file_path, 'w', encoding='ISO-8859-1') as file:
            for line in lines:
                if not line.startswith(f"{key}="):
                    file.write(line)

# Function to generate the first Excel file with the summary of merges and conflicts
def generate_summary_excel():
    data = []
    for lang, files in merge_stats.items():
        for file_name, stats in files.items():
            row = {
                "File": file_name,
                "Locale": lang,
                "Merged": stats["merged"],
                "Conflicts": stats["conflicts"]
            }
            data.append(row)
    
    df = pd.DataFrame(data)
    summary_file = "summary_report.xlsx"
    df.to_excel(summary_file, index=False)
    print(f"Summary report generated: {summary_file}")

# Function to generate the second Excel file with conflict details
def generate_conflict_details_excel():
    data = []
    for lang, files in conflict_sources.items():
        for file_name, properties in files.items():
            for key, conflict_list in properties.items():
                row = {
                    "File": file_name,
                    "Locale": lang,
                    "Properties Name": key,
                    **{app: value for value, app, _ in conflict_list}
                }
                data.append(row)
    
    df = pd.DataFrame(data)
    conflict_file = "conflict_details_report.xlsx"
    df.to_excel(conflict_file, index=False)
    print(f"Conflict details report generated: {conflict_file}")

# Script execution
parse_cartridges()
merge_properties()
generate_summary_excel()
generate_conflict_details_excel()

print("Merging of properties files completed.")
