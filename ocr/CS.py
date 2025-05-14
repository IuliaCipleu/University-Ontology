import os
import pytesseract
from PIL import Image
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL, RDFS, XSD

# Setup for Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load and OCR the image
img = Image.open('fig\\CS.jpg')
text = pytesseract.image_to_string(img)
print("Extracted text:\n", text)

# Initialize RDF graph
g = Graph()
BASE = Namespace("http://example.org/ontology#")
g.bind("base", BASE)

# Classes
StudyProgram = BASE.StudyProgram
BSc = BASE.BSc
MSc = BASE.MSc
PhD = BASE.PhD

g.add((StudyProgram, RDF.type, OWL.Class))
g.add((BSc, RDF.type, OWL.Class))
g.add((MSc, RDF.type, OWL.Class))
g.add((PhD, RDF.type, OWL.Class))

g.add((BSc, RDFS.subClassOf, StudyProgram))
g.add((MSc, RDFS.subClassOf, StudyProgram))
g.add((PhD, RDFS.subClassOf, StudyProgram))

# Properties
hasLengthOfYears = BASE.hasLengthOfYears
hasName = BASE.hasName

g.add((hasLengthOfYears, RDF.type, OWL.DatatypeProperty))
g.add((hasLengthOfYears, RDFS.domain, StudyProgram))
g.add((hasLengthOfYears, RDFS.range, XSD.integer))

g.add((hasName, RDF.type, OWL.DatatypeProperty))
g.add((hasName, RDFS.domain, StudyProgram))
g.add((hasName, RDFS.range, XSD.string))

# --- Extract program names dynamically from OCR text ---

lines = text.splitlines()
current_category = None
duration_map = {'BS': 4, 'MS': 2, 'PhD': 3}

for line in lines:
    line = line.strip()
    if line.startswith('+ BS'):
        current_category = 'BS'
        continue
    elif line.startswith('+ MS'):
        current_category = 'MS'
        continue
    elif line.startswith('* PhD'):
        current_category = 'PhD'
        continue

    if current_category and line:
        # Split on ':' or '—' to extract names, and filter short lines
        fragments = [frag.strip() for frag in line.replace('—', ':').split(':')]
        for frag in fragments:
            if len(frag) > 5 and frag[0].isupper():
                program_name = frag
                program_id = program_name.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
                duration = duration_map[current_category]

                program_uri = BASE[program_id]
                g.add((program_uri, RDF.type, BASE[current_category]))
                g.add((program_uri, hasName, Literal(program_name)))
                g.add((program_uri, hasLengthOfYears, Literal(duration)))

# Save OWL
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\merged_ontology.owl"
g.serialize(destination=output_path, format="xml")
print("\nOWL file 'cs_department.owl' created dynamically based on OCR.")
