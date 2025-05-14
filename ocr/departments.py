import os
import re
import pytesseract
from PIL import Image
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL, RDFS

os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Set the path to tesseract if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path based on your system

# Open an image file
img = Image.open('fig\departments.jpg')  # Replace 'image.png' with the path to your image

# Use pytesseract to extract text
text = pytesseract.image_to_string(img)

# Print the extracted text
print(text)

# RDFLib setup
g = Graph()
BASE = Namespace("http://example.org/ontology#")
g.bind("base", BASE)

# Define class
Department = BASE.Department
g.add((Department, RDF.type, OWL.Class))

# Define properties
hasDirector = BASE.hasDirector
hasPhone = BASE.hasPhone
hasEmail = BASE.hasEmail

g.add((hasDirector, RDF.type, OWL.DatatypeProperty))
g.add((hasPhone, RDF.type, OWL.DatatypeProperty))
g.add((hasEmail, RDF.type, OWL.DatatypeProperty))

# Extract departments using regex
dept_blocks = re.split(r"\n\s*\n", text)  # Split blocks of text

for block in dept_blocks:
    if "Departamentul de" in block:
        lines = block.strip().split('\n')
        name = director = ""
        phones = []
        email = ""

        for line in lines:
            if "Departamentul de" in line:
                name = line.strip()
            elif re.search(r"@[\w\.]+", line):
                # Director and contact line
                director_match = re.search(r"(Prof\..*?),", line)
                if director_match:
                    director = director_match.group(1).strip()
                phones = re.findall(r"\+40[-\d]+", line)
                email_match = re.search(r"[\w\.-]+@[\w\.-]+", line)
                if email_match:
                    email = email_match.group(0).strip()

        if name:
            dept_id = name.replace(" ", "_").replace(",", "")
            dept_uri = BASE[dept_id]

            g.add((dept_uri, RDF.type, Department))
            if director:
                g.add((dept_uri, hasDirector, Literal(director)))
            for phone in phones:
                g.add((dept_uri, hasPhone, Literal(phone)))
            if email:
                g.add((dept_uri, hasEmail, Literal(email)))

# Serialize OWL
output_path = ".\\owl\\departments.owl"
g.serialize(destination=output_path, format="xml")
print(f"\nOWL file '{output_path}' created successfully.")
