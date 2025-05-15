import os
import pandas as pd
import re

# ✅ Replace with the actual full path to your HTML folder
html_folder = r"C:/Users/Cipleu/Documents/IULIA/SCOALA/facultate/Year 4 Semester 2/KBS/Lab/Project/University-Ontology/html/Computer_Science_BSc"

# Define valid time slots
VALID_TIME_RANGES = ['8-10', '10-12', '12-14', '14-16', '16-18', '18-20']


# Function to extract clean course info
def extract_courses(text):
    courses = []
    if isinstance(text, str):
        parts = re.split(r'/|,|;', text)
        for part in parts:
            clean = part.strip()
            if clean:
                courses.append(clean)
    return courses


# Process each HTML file
for filename in sorted(os.listdir(html_folder)):
    if filename.endswith(".html"):
        filepath = os.path.join(html_folder, filename)
        try:
            df = pd.read_html(filepath)[0]
            print(f"✅ {filename}: {df.shape}")
        except Exception as e:
            print(f"❌ Failed to read {filename}: {e}")
            continue

        group = filename.replace(".html", "")

        for index, row in df.iterrows():
            row_data = [str(cell) if pd.notna(cell) else "nan" for cell in row.tolist()]
            day = next((cell for cell in row_data if cell.strip().capitalize() in ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri']), None)
            time = next((cell for cell in row_data if cell.strip() in VALID_TIME_RANGES), None)

            if not day or not time:
                continue

            for cell in row_data[4:]:
                if isinstance(cell, str) and cell != "nan":
                    for course in extract_courses(cell):
                        entry = {
                            "day": day,
                            "time": time,
                            "group": group,
                            "course": course,
                            "raw_data": row_data
                        }
                        print(entry)
