import pandas as pd

# Load all sheets as a dictionary of DataFrames
excel_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\excel\Computer_Science_BSc.xlsx"
all_sheets = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')

# Print names of all sheets
print("Sheet names:", list(all_sheets.keys()))

# Loop through and print the first few rows of each sheet
for sheet_name, df in all_sheets.items():
    print(f"\n--- Sheet: {sheet_name} ---")
    print(df.head())
