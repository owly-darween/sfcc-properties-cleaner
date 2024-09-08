
# Properties Cleaner - Conflict Resolution Tool

This repository contains a tool for managing and resolving conflicts in properties files for different locales. The tool works in three main steps:

1. **Download** your different app_xxx cartridges.
2. **Add the Python files at the root**
3. **Run the `properties_parser.py`** script to create the Excel file `conflict_details_report.xlsx`.
4. **Run the `properties_cleaner.py`** script to resolve the conflicts via the Flask interface.

## Features

- Select and resolve conflicts for specific locales.
- View conflicting translations side-by-side.
- Automatically update the merged properties files with the chosen translations.
- Track the number of conflicts and resolved entries.

## Prerequisites

Before you get started, make sure you have the following installed:

- Python 3.8 or higher
- Flask
- Pandas
- Watchdog (for Flask's development server)
- Openpyxl (for Excel support)

You can install the required dependencies using the following command:

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, you can manually install the packages:

```bash
pip install flask pandas openpyxl watchdog
```

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/properties_cleaner.git
    cd properties_cleaner
    ```

2. **Step 1**: Download your different app_xxx cartridges and place them in the appropriate directory.

3. **Step 2**: Run the `properties_parser.py` script to generate the conflict report:
    ```bash
    python properties_parser.py
    ```

    This will create an Excel file named `conflict_details_report.xlsx` that contains all the detected conflicts between the different properties files in your cartridges.

4. **Step 3**: Run the `properties_cleaner.py` Flask application:
    ```bash
    python properties_cleaner.py
    ```

    The Flask application will start, and you can access it at `http://127.0.0.1:5000` in your web browser.

## Usage

### Step 1: Load Conflict Report

Once the Flask application is running, the tool automatically loads the conflict details from `conflict_details_report.xlsx`. Make sure the file is correctly formatted with at least the following columns:
- `Fichier` (file name)
- `Locale` (locale code, e.g., `fr_FR`, `de_DE`)
- `Properties Name` (name of the conflicting property)
- `app_1`, `app_2`, etc. (conflicting translations from different applications)

### Step 2: Select Locale

1. Navigate to the web interface at `http://127.0.0.1:5000`.
2. You will see a dropdown menu to select the locale you want to manage.
3. After selecting a locale, the first conflict for that locale will be displayed.

### Step 3: Resolve Conflicts

1. For each conflict, the tool will display the conflicting translations from different applications.
2. You can review the translations and select the best one from the dropdown list.
3. Click "Submit" to apply the chosen translation. The application will update the corresponding `merged_properties` file.
4. The next conflict for the selected locale will be displayed automatically.

### Step 4: Update Merged Properties

After resolving a conflict, the application automatically updates the relevant merged properties file in the `merged_properties/` folder. You can find this folder under the locale code, e.g., `merged_properties/fr_FR/`.

### Step 5: Repeat or Select Another Locale

Continue resolving conflicts for the selected locale, or go back to the main menu to select another locale.

## Folder Structure

The expected folder structure is as follows:

```
properties_cleaner/
│
├── conflict_details_report.xlsx    # Excel file containing conflict details
├── merged_properties/              # Folder for storing updated properties files
│   ├── fr_FR/
│   ├── de_DE/
│   └── ...                         # One folder per locale
├── templates/                      # HTML templates for Flask
│   └── index.html                  # Main interface for resolving conflicts
├── static/                         # Optional: For storing static files like CSS
├── properties_cleaner.py            # The Flask app that runs the conflict resolver
├── properties_parser.py             # The parser that generates the conflict report
└── README.md                       # This documentation
```

## Adding or Modifying the Conflict Report

If you need to update or modify the `conflict_details_report.xlsx` file, ensure it follows the format of:
- Locale codes (e.g., `fr_FR`, `de_DE`) in the `Locale` column.
- The name of the properties in `Properties Name`.
- Different translations under the `app_` columns (e.g., `app_1`, `app_2`).

After modifying, restart the Flask app to reload the changes.

## Troubleshooting

### Common Issues

- **Missing conflict report**: Ensure the `conflict_details_report.xlsx` is present in the root directory.
- **Flask not starting**: Make sure all dependencies are installed. Try running `pip install -r requirements.txt` again.
- **File encoding errors**: If you encounter issues reading or writing properties files, check the encoding of the files. The tool supports both UTF-8 and ISO-8859-1.

### Logging

The application provides basic logging via `print` statements. You can track which files are being updated and any potential issues (e.g., file not found).

## Contributing

If you'd like to contribute to this project, feel free to open a pull request or create an issue. Contributions are welcome!
