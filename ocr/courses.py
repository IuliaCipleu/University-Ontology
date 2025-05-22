import os
import fitz  # PyMuPDF
import re
from rdflib import Graph, Namespace, Literal, RDF, URIRef
from rdflib.namespace import XSD, OWL, RDFS


# RDF Graph
g = Graph()
BASE = Namespace("http://example.org/ontology#")
g.bind("base", BASE)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# === Declare the Course class ===
g.add((BASE.Course, RDF.type, OWL.Class))

# === Declare Data Properties ===
property_definitions = {
    "hasCode": XSD.string,
    "hasTitle": XSD.string,
    "hasCredits": XSD.float,
    "hasDomain": XSD.string,
    "hasPrefix": XSD.string,
    "forYear": XSD.integer
}

g.add((BASE.StudyProgram, RDF.type, OWL.Class))

is_taught_at = BASE.isTaughtAt
g.add((is_taught_at, RDF.type, OWL.ObjectProperty))
g.add((is_taught_at, RDFS.domain, BASE.Course))
g.add((is_taught_at, RDFS.range, BASE.StudyProgram))

# === Map folder keys to StudyProgram instances ===
folder_to_program = {
    "calc_engl": "Computer_Science_BSc",
    "aut_engl": "Automation_and_Applied_Informatics_BSc",
    "is": "Applied_Informatics_MSc",
    "rcsd": "Communication_Networks_and_Distributed_Systems_MSc",
    "cps": "Cyber_Physical_Systems_MSc"
}

# === Declare each study program as an individual of StudyProgram ===
for prog_name in folder_to_program.values():
    program_uri = BASE[prog_name]
    g.add((program_uri, RDF.type, BASE.StudyProgram))


def extract_courses(text, year):
    # Clean up the text for easier regex matching
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single one

    # Pattern to match lines with course info
    course_pattern = re.compile(
        r"(?P<code>\d{2,3}\.\d{2})\s+(?P<some_int>\d+)?\s+(?P<grade_type>Nota|A/R)\s+"
        r"(?P<max_score>\d+)?\s+(?P<score1>\d+)?\s+(?P<score2>\d+)?\s+(?P<score3>\d+)?\s+"
        r"(?P<credits>[\d\.]+)?\s+(?P<prefix>DI|DF|DD|DO|DS|DC|Dfac)?\s+"
        r"(?P<title>[^\n]+)",
        re.IGNORECASE
    )

    courses = []
    for match in course_pattern.finditer(text):
        code = match.group("code").strip()
        credits = match.group("credits").strip() if match.group("credits") else "0"
        prefix = match.group("prefix").strip() if match.group("prefix") else "Unknown"
        title = match.group("title").strip()

        courses.append({
            "hasCode": code,
            "hasTitle": title,
            "hasCredits": float(credits),
            "hasPrefix": prefix,
            "forYear": int(year)
        })

    return courses


def declare_data_properties():
    for prop, dtype in property_definitions.items():
        prop_uri = BASE[prop]
        g.add((prop_uri, RDF.type, OWL.DatatypeProperty))
        g.add((prop_uri, RDFS.domain, BASE.Course))
        g.add((prop_uri, RDFS.range, dtype))


declare_data_properties()


def add_course_to_ontology(course, id):
    # Create a unique URI for the course (e.g., code_year)
    course_id = f"{id}_{course['hasCode'].replace('.', '_')}_{course['forYear']}"
    course_uri = BASE[course_id]
    g.add((course_uri, RDF.type, BASE.Course))

    # Add each data property
    for prop, dtype in property_definitions.items():
        value = course.get(prop)
        if value is not None:
            g.add((course_uri, BASE[prop], Literal(value, datatype=dtype)))
    g.add((course_uri, BASE.isTaughtAt, program_uri))


# Path to folder with PDFs
pdf_folders = [
    os.path.abspath(os.path.join("..", "pdf", "lic", "calc_engl")),
    os.path.abspath(os.path.join("..", "pdf", "lic", "aut_engl")),
    os.path.abspath(os.path.join("..", "pdf", "master", "is")),
    os.path.abspath(os.path.join("..", "pdf", "master", "cps")),
    os.path.abspath(os.path.join("..", "pdf", "master", "rcsd"))
]

# Loop through all PDF files
id_counter = 0
for pdf_folder in pdf_folders:
    folder_key = os.path.basename(pdf_folder)
    program_name = folder_to_program.get(folder_key)
    if program_name is None:
        print(f"Unknown folder: {folder_key}, skipping...")
        continue
    program_uri = BASE[program_name]
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_folder, filename)
            print(f"\n===== Reading {filename} =====\n")
            doc = fitz.open(pdf_path)
            year = os.path.splitext(filename)[0].strip()
            # Process pages
            full_text = ""
            for page_num in range(len(doc)):
                page: fitz.Page = doc[page_num]
                full_text += page.get_text()
            doc.close()

            # Extract course data
            print(full_text)
            courses = extract_courses(full_text, year)
            for course in courses:
                print(f"Adding course: {course}")
                add_course_to_ontology(course, id_counter)
                id_counter+= 1

# Save ontology to file
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\courses.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOntology saved to {output_path}")
