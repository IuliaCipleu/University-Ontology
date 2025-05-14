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
g.add((BASE.Student, RDF.type, OWL.Class))
g.add((BASE.Group, RDF.type, OWL.Class))

# === Declare Data Properties ===
property_definitions = {
    "inYear": XSD.integer
}

def parse_group(group):
    
    return folder_to_enrolment


for enrol_name in folder_to_enrolment.values():
    enrol_uri = BASE[enrol_name]
    g.add((penrol_uri, RDF.type, BASE.StudyProgram))


def extract_students(text, year):
    # Clean up the text for easier regex matching
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single one

    # Pattern to match lines with student info
    student_pattern = re.compile(
        r"(?P<code>\d{2,3}\.\d{2})\s+(?P<some_int>\d+)?\s+(?P<grade_type>Nota|A/R)\s+"
        r"(?P<max_score>\d+)?\s+(?P<score1>\d+)?\s+(?P<score2>\d+)?\s+(?P<score3>\d+)?\s+"
        r"(?P<credits>[\d\.]+)?\s+(?P<prefix>DI|DF|DD|DO|DS|DC|Dfac)?\s+"
        r"(?P<title>[^\n]+)",
        re.IGNORECASE
    )

    students = []
    for match in student_pattern.finditer(text):
        code = match.group("code").strip()
        credits = match.group("credits").strip() if match.group("credits") else "0"
        prefix = match.group("prefix").strip() if match.group("prefix") else "Unknown"
        title = match.group("title").strip()

        students.append({
            "hasCode": code,
            "hasTitle": title,
            "hasCredits": float(credits),
            "hasPrefix": prefix,
            "forYear": int(year)
        })

    return students


def add_student_to_ontology(student):
    # Create a unique URI for the student (e.g., code_year)
    student_id = f"{student['hasCode'].replace('.', '_')}_{student['forYear']}"
    student_uri = BASE[student_id]
    g.add((student_uri, RDF.type, BASE.Course))

    # Add each data property
    for prop, dtype in property_definitions.items():
        value = student.get(prop)
        if value is not None:
            g.add((student_uri, BASE[prop], Literal(value, datatype=dtype)))
    g.add((student_uri, BASE.isEnroledAt, enrolment_uri))


enroled_at = BASE.enroledAt
pdf_folder = os.path.abspath(os.path.join("..", "pdf", "students"))
folder_key = os.path.basename(pdf_folder)
enrolement = folder_to_enrolement.get(folder_key)
if enrolement is None:
    print(f"Unknown folder: {folder_key}, skipping...")
    continue
enrolement_uri = BASE[enrolement]
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

        # Extract student data
        print(full_text)
        students = extract_students(full_text, enrolment)
        for student in students:
            print(f"Adding student: {student}")
            add_student_to_ontology(student)

# Save ontology to file
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\students.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOntology saved to {output_path}")
