import os
import fitz  # PyMuPDF
import re
import pandas as pd
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
g.add((BASE.StudyProgram, RDF.type, OWL.Class))

cs_bsc = BASE.Computer_Science_BSc
ai_bsc = BASE.Automation_and_Applied_Informatics_BSc
se_msc = BASE.Software_Engineering_MSc

for program in [cs_bsc, ai_bsc, se_msc]:
    g.add((program, RDF.type, BASE.StudyProgram))

# === Declare Data Properties ===
g.add((BASE.hasFirstName, RDF.type, OWL.DatatypeProperty))
g.add((BASE.hasSurname, RDF.type, OWL.DatatypeProperty))
g.add((BASE.hasFirstName, RDFS.domain, BASE.Student))
g.add((BASE.hasFirstName, RDFS.range, XSD.string))
g.add((BASE.hasSurname, RDFS.domain, BASE.Student))
g.add((BASE.hasSurname, RDFS.range, XSD.string))
g.add((BASE.inYear, RDF.type, OWL.DatatypeProperty))
g.add((BASE.inYear, RDFS.domain, BASE.Group))
g.add((BASE.inYear, RDFS.range, XSD.integer))

# === Object Property ===
g.add((BASE.inGroup, RDF.type, OWL.ObjectProperty))
g.add((BASE.inGroup, RDFS.domain, BASE.Student))
g.add((BASE.inGroup, RDFS.range, BASE.Group))
g.add((BASE.isEnrolledIn, RDF.type, OWL.ObjectProperty))
g.add((BASE.isEnrolledIn, RDFS.domain, BASE.Group))
g.add((BASE.isEnrolledIn, RDFS.range, BASE.StudyProgram))


# === Extract student names ===
def extract_students(text, year):
    students = []
    # Normalize text
    text = re.sub(r'\n+', '\n', text)
    lines = text.split('\n')
    recording = False

    for line in lines:
        if re.search(r'\bLista studentilor\b', line, re.IGNORECASE):
            recording = True
            continue
        if recording:
            if re.search(r'Facultatea|Specializarea|Grupa|Anul|e_\d+', line):
                break
            if line.strip().isdigit():
                continue  # skip line numbers
            full_name = line.strip()
            if full_name:
                parts = full_name.split(maxsplit=1)
                surname = parts[0]
                first_name = parts[1] if len(parts) > 1 else "Unknown"
                students.append({
                    "hasFirstName": first_name,
                    "hasSurname": surname
                })
    return students


# === Add student to ontology ===
def add_student_to_ontology(student, group_uri):
    student_id = f"{student['hasSurname']}_{student['hasFirstName']}".replace(' ', '_').replace('-', '_')
    student_uri = BASE[f"Student_{student_id}"]
    g.add((student_uri, RDF.type, BASE.Student))
    group_uri = BASE[f"Group_{group_name}"]
    g.add((group_uri, RDF.type, BASE.Group))
    g.add((student_uri, BASE.hasFirstName, Literal(student['hasFirstName'], datatype=XSD.string)))
    g.add((student_uri, BASE.hasSurname, Literal(student['hasSurname'], datatype=XSD.string)))
    g.add((student_uri, BASE.isInGroup, group_uri))

# === Main processing ===


pdf_folder = os.path.abspath(os.path.join("..", "pdf", "students"))
folder_key = os.path.basename(pdf_folder)
all_students = []

for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        group_name = os.path.splitext(filename)[0].strip()
        group_uri = BASE[f"Group_{group_name}"]
        g.add((group_uri, RDF.type, BASE.Group))
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
        all_students.extend(students)
        if len(group_name) == 5 and group_name.isdigit():
            year_digit = int(group_name[3])  # 4th digit (index 3)
            second_third = group_name[1:3]  # 2nd and 3rd digit

            # Set inYear
            g.add((group_uri, BASE.inYear, Literal(year_digit, datatype=XSD.integer)))

            # Determine StudyProgram
            if second_third == "04":
                g.add((group_uri, BASE.isEnrolledIn, cs_bsc))
            elif second_third == "01":
                g.add((group_uri, BASE.isEnrolledIn, ai_bsc))
            elif second_third == "23":
                g.add((group_uri, BASE.isEnrolledIn, se_msc))

# === Save ontology ===
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\students.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOntology saved to {output_path}")

if all_students:
    df = pd.DataFrame(all_students)
    # Rename columns to what you want
    df.rename(columns={"hasSurname": "Surname", "hasFirstName": "FirstName"}, inplace=True)

    excel_output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\excel\students.xlsx"
    df.to_excel(excel_output_path, index=False)
    print(f"\nStudents saved to Excel file: {excel_output_path}")
