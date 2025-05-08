import os
import pytesseract
from PIL import Image
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF, OWL, RDFS


os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Set the path to tesseract if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path based on your system

# Open an image file
img = Image.open('fig\study_programme.jpg')  # Replace 'image.png' with the path to your image

# Use pytesseract to extract text
text = pytesseract.image_to_string(img)

# Print the extracted text
print(text)

# Split the text into lines
lines = text.split("\n")

# Initialize lists for programs
bachelor_programs = []
master_programs = []

# Variables to keep track of current program level (B.Sc. or M.Sc.)
current_degree = None

# Parse the lines
for line in lines:
    if "Study Programme B.Sc." in line:
        current_degree = "B.Sc."
    elif "Study Programme M.Sc." in line:
        current_degree = "M.Sc."
    elif line.startswith("*"):
        # Example: "* Computer Science (Cluj-Napoca) (RO, EN)"
        program = line.strip("* ").split(" (")
        program_name = program[0]
        locations = program[1].split(")")[0].strip()
        languages = program[1].split(")")[1].strip("()").split(", ")

        program_data = {
            "name": program_name,
            "location": locations,
            "languages": languages
        }

        # Append to the correct list based on the degree
        if current_degree == "B.Sc.":
            bachelor_programs.append(program_data)
        elif current_degree == "M.Sc.":
            master_programs.append(program_data)

# Print parsed programs
print("B.Sc. Programs:")
for program in bachelor_programs:
    print(program)

print("\nM.Sc. Programs:")
for program in master_programs:
    print(program)

# Create a graph for the OWL file
g = Graph()

# Define the base URI for your ontology
base_uri = URIRef("http://example.org/ontology#")

# Create the class for "StudyProgram"
StudyProgram = URIRef(base_uri + "StudyProgram")

# Create subclasses for B.Sc. and M.Sc.
BSc = URIRef(base_uri + "BSc")
MSc = URIRef(base_uri + "MSc")

# Create individuals for each B.Sc. and M.Sc. program
for program in bachelor_programs:
    # Create a URI for each program
    program_uri = URIRef(base_uri + program['name'].replace(" ", "_") + "_BSc")

    # Add the program as an individual of the BSc subclass
    g.add((program_uri, RDF.type, BSc))
    g.add((program_uri, RDF.type, StudyProgram))  # Also add to StudyProgram as a general type
    
    # Add properties (name, location, language)
    g.add((program_uri, URIRef(base_uri + "hasName"), Literal(program['name'])))
    g.add((program_uri, URIRef(base_uri + "hasLocation"), Literal(program['location'])))
    for lang in program['languages']:
        g.add((program_uri, URIRef(base_uri + "hasLanguage"), Literal(lang)))

for program in master_programs:
    # Create a URI for each program
    program_uri = URIRef(base_uri + program['name'].replace(" ", "_") + "_MSc")

    # Add the program as an individual of the MSc subclass
    g.add((program_uri, RDF.type, MSc))
    g.add((program_uri, RDF.type, StudyProgram))  # Also add to StudyProgram as a general type
    
    # Add properties (name, location, language)
    g.add((program_uri, URIRef(base_uri + "hasName"), Literal(program['name'])))
    g.add((program_uri, URIRef(base_uri + "hasLocation"), Literal(program['location'])))
    for lang in program['languages']:
        g.add((program_uri, URIRef(base_uri + "hasLanguage"), Literal(lang)))

# Serialize and save the data as an OWL file
g.serialize("study_programs.owl", format="xml")

print("\nOWL file 'study_programs.owl' has been created successfully.")
