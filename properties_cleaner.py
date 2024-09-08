from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from collections import Counter
import os

# Load the conflict Excel file
conflict_file = "conflict_details_report.xlsx"

# Check if the file exists before loading it
if not os.path.exists(conflict_file):
    raise FileNotFoundError(f"The file {conflict_file} does not exist.")

df_conflicts = pd.read_excel(conflict_file)

# Create the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required to use sessions

# Function to read a properties file
def read_properties_file(file_path):
    properties = {}
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}. A new file will be created.")
        return properties

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if not line.strip() or line.startswith('#'):
                    continue
                key_value = line.strip().split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    properties[key.strip()] = value.strip()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='ISO-8859-1') as file:
            for line in file:
                if not line.strip() or line.startswith('#'):
                    continue
                key_value = line.strip().split('=', 1)
                if len(key_value) == 2:
                    key, value = key_value
                    properties[key.strip()] = value.strip()
    return properties

# Function to write the properties file after modification
def write_properties_file(file_path, properties):
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            for key, value in properties.items():
                file.write(f"{key}={value}\n")
    except UnicodeDecodeError:
        with open(file_path, 'w', encoding='ISO-8859-1') as file:
            for key, value in properties.items():
                file.write(f"{key}={value}\n")

# Main route to manage locale selection and display conflicts
@app.route('/', methods=['GET', 'POST'])
def index():
    available_locales = sorted(set(df_conflicts['Locale']))

    # Handling form submission to select a locale
    if request.method == 'POST':
        selected_locale = request.form['locale']
        session['selected_locale'] = selected_locale
        session['conflict_index'] = 0  # Reset the conflict index
        return redirect(url_for('index'))

    selected_locale = session.get('selected_locale', None)

    if selected_locale:
        # Filter conflicts based on the selected locale
        filtered_conflicts = df_conflicts[df_conflicts['Locale'] == selected_locale]
        total_conflicts = len(filtered_conflicts)

        # Select the first conflict for display
        if total_conflicts > 0:
            conflict_index = session.get('conflict_index', 0)
            if conflict_index >= total_conflicts:
                conflict_index = 0  # Go back to the beginning if conflicts are exceeded

            row = filtered_conflicts.iloc[conflict_index]
            file_name = row['Fichier']
            locale = row['Locale']
            property_name = row['Properties Name']

            # Extract the conflict values from the applications (app_1, app_2, etc.)
            conflict_values = {key: row[key] for key in row.index if key.startswith('app_') and pd.notnull(row[key])}

            # Check if any values are present
            if conflict_values:
                most_common_value, most_common_count = Counter(conflict_values.values()).most_common(1)[0]
            else:
                most_common_value, most_common_count = None, 0

            conflict = {
                'index': conflict_index,
                'file_name': file_name,
                'locale': locale,
                'property_name': property_name,
                'conflict_values': conflict_values,
                'most_common_value': most_common_value,
                'most_common_count': most_common_count
            }

        else:
            conflict = None
            total_conflicts = 0

    else:
        conflict = None
        total_conflicts = 0

    return render_template('index.html', available_locales=available_locales, selected_locale=selected_locale, conflict=conflict, total_conflicts=total_conflicts)

# Route to validate the resolution of a conflict
@app.route('/resolve', methods=['POST'])
def resolve_conflict():
    conflict_index = int(request.form['conflict_index'])
    chosen_value = request.form['chosen_value']

    selected_locale = session.get('selected_locale')
    filtered_conflicts = df_conflicts[df_conflicts['Locale'] == selected_locale]

    # Retrieve the selected conflict
    row = filtered_conflicts.iloc[conflict_index]
    file_name = row['Fichier']
    locale = row['Locale']
    property_name = row['Properties Name']

    # Path to the file in the merged_properties folder
    merged_properties_dir = os.path.join('merged_properties', locale)
    os.makedirs(merged_properties_dir, exist_ok=True)  # Ensure the directory exists
    merged_properties_file = os.path.join(merged_properties_dir, file_name)

    # Read and update the properties file
    properties = read_properties_file(merged_properties_file)
    properties[property_name] = chosen_value
    write_properties_file(merged_properties_file, properties)

    # Move to the next conflict
    next_index = conflict_index + 1
    session['conflict_index'] = next_index
    return redirect(url_for('index'))

# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
