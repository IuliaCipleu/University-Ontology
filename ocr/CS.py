import os
import pytesseract
from PIL import Image
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, OWL, RDFS, XSD

# Setup for Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load and OCR the image
img = Image.open(r'C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\fig\CS.jpg')
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
duration_map = {'B.Sc': 4, 'M.Sc': 2, 'PhD': 3}

accumulator = ""
for line in lines:
    line = line.strip()
    if line.startswith('+ BS'):
        current_category = 'B.Sc'
        continue
    elif line.startswith('+ MS'):
        current_category = 'M.Sc'
        continue
    elif line.startswith('* PhD'):
        current_category = 'PhD'
        continue

    if current_category and line:
        # Continue accumulating lines until we hit an empty line or a new category
        if line.startswith('+') or line.startswith('*'):
            continue  # avoid lines with just '+' or '*'

        accumulator += " " + line  # combine lines for multiline cases

# After accumulating, now split by ',' and process each program
if accumulator and current_category:
    # First, normalize and split
    programs = [p.strip(" ;.") for p in accumulator.split(",") if len(p.strip()) > 3]

    for program_name in programs:
        if program_name:  # avoid empty
            program_id = program_name.replace(" ", "").replace("(", "").replace(")", "").replace("-", "").replace("’", "").replace("‘", "").replace("`", "")
            duration = duration_map[current_category]
            program_uri = BASE[program_id]
            print(program_uri)
            g.add((program_uri, RDF.type, BASE[current_category]))
            g.add((program_uri, hasName, Literal(program_name)))
            g.add((program_uri, hasLengthOfYears, Literal(duration)))

# Save OWL
output_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\cs_department.owl"
g.serialize(destination=output_path, format="xml")
print("\nOWL file 'cs_department.owl' created dynamically based on OCR.")
