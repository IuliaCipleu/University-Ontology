import os
import fitz  # PyMuPDF
import re
from rdflib import Graph, Namespace, Literal, RDF, URIRef

# Define namespace
EX = Namespace("http://example.org/courses/")

# RDF Graph
g = Graph()
g.bind("ex", EX)


def extract_courses(text):
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
            "code": code,
            "title": title,
            "credits": credits,
            "domain": "Unknown",
            "prefix": prefix
        })

    return courses


def add_course_to_ontology(course):
    course_uri = EX[f"Course_{course['code'].replace('.', '_')}"]
    g.add((course_uri, RDF.type, EX.Course))
    g.add((course_uri, EX.hasCode, Literal(course["code"])))
    g.add((course_uri, EX.hasTitle, Literal(course["title"])))
    g.add((course_uri, EX.hasCredits, Literal(course["credits"])))
    g.add((course_uri, EX.hasDomain, Literal(course["domain"])))
    g.add((course_uri, EX.hasPrefix, Literal(course["prefix"])))


# Path to folder with PDFs
pdf_folder = os.path.abspath(os.path.join("..", "pdf", "lic", "calc_engl"))

# Loop through all PDF files
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"\n===== Reading {filename} =====\n")
        doc = fitz.open(pdf_path)

        # Process pages
        full_text = ""
        for page_num in range(len(doc)):
            page: fitz.Page = doc[page_num]
            full_text += page.get_text()
        doc.close()

        # Extract course data
        print(full_text)
        courses = extract_courses(full_text)
        for course in courses:
            print(f"Adding course: {course}")
            add_course_to_ontology(course)

# Save ontology to file
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\courses.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOntology saved to {output_path}")
