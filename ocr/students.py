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

# === Declare Classes ===
g.add((BASE.Student, RDF.type, OWL.Class))
g.add((BASE.Group, RDF.type, OWL.Class))

# === Declare Data Properties ===
g.add((BASE.hasName, RDF.type, OWL.DatatypeProperty))
g.add((BASE.inGroup, RDF.type, OWL.DatatypeProperty))
g.add((BASE.hasName, RDFS.domain, BASE.Student))
g.add((BASE.hasName, RDFS.range, XSD.string))
g.add((BASE.inGroup, RDFS.domain, BASE.Student))
g.add((BASE.inGroup, RDFS.range, XSD.integer))

# === Object Property ===
g.add((BASE.isInGroup, RDF.type, OWL.ObjectProperty))
g.add((BASE.isInGroup, RDFS.domain, BASE.Student))
g.add((BASE.isInGroup, RDFS.range, BASE.Group))


# === Extract student names ===
def extract_students(text, year):
    students = []
    # Normalize text
    text = re.sub(r'\n+', '\n', text)
    lines = text.split('\n')
    student_lines = []
    recording = False

    for line in lines:
        if re.search(r'\bLista studentilor\b', line, re.IGNORECASE):
            recording = True
            continue
        if recording:
            # Stop if we hit faculty name or metadata section
            if re.search(r'Facultatea|Specializarea|Grupa|Anul|e_\d+', line):
                break
            if line.strip().isdigit():
                continue  # skip line numbers
            name = line.strip()
            if name:
                students.append({
                    "hasName": name,
                    "inGroup": int(year)
                })
    return students


# === Add student to ontology ===
def add_student_to_ontology(student, group_uri):
    student_id = student['hasName'].replace(' ', '_').replace('-', '_')
    student_uri = BASE[f"Student_{student_id}"]
    g.add((student_uri, RDF.type, BASE.Student))
    g.add((student_uri, BASE.hasName, Literal(student['hasName'], datatype=XSD.string)))
    g.add((student_uri, BASE.inGroup, Literal(student['inGroup'], datatype=XSD.integer)))
    g.add((student_uri, BASE.isInGroup, group_uri))

# === Main processing ===


pdf_folder = os.path.abspath(os.path.join("..", "pdf", "students"))
folder_key = os.path.basename(pdf_folder)

group_name = folder_key  # Use folder name as group identifier
group_uri = BASE[f"Group_{group_name}"]
g.add((group_uri, RDF.type, BASE.Group))

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"\n===== Reading {filename} =====\n")
        doc = fitz.open(pdf_path)
        year = os.path.splitext(filename)[0].strip()

        # Read all pages
        full_text = ""
        for page_num in range(len(doc)):
            page: fitz.Page = doc[page_num]
            full_text += page.get_text()
        doc.close()

        students = extract_students(full_text, year)
        for student in students:
            print(f"Adding student: {student}")
            add_student_to_ontology(student, group_uri)

# === Save ontology ===
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\students.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOntology saved to {output_path}")
