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


def add_course_to_ontology(course):
    # Create a unique URI for the course (e.g., code_year)
    course_id = f"{course['hasCode'].replace('.', '_')}_{course['forYear']}"
    course_uri = BASE[course_id]
    g.add((course_uri, RDF.type, BASE.Course))

    # Add each data property
    for prop, dtype in property_definitions.items():
        value = course.get(prop)
        if value is not None:
            g.add((course_uri, BASE[prop], Literal(value, datatype=dtype)))


# Path to folder with PDFs
pdf_folder = os.path.abspath(os.path.join("..", "pdf", "lic", "calc_engl"))

# Loop through all PDF files
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
            add_course_to_ontology(course)

# Save ontology to file
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\courses.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOntology saved to {output_path}")
