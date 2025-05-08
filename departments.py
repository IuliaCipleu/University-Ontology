import os
import pytesseract
from PIL import Image
from rdflib import Graph, URIRef, Literal
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

# Extract department details manually based on the extracted text
departments = [
    {
        "name": "Departamentul de Calculatoare",
        "director": "Prof.dr.ing. Potolea Rodica",
        "contact": "+40-264-202389, Rodica.Potolea@cs.utcluj.ro"
    },
    {
        "name": "Departamentul de Automatica",
        "director": "Prof.dr.ing. Vlean Honoriu Mugurel",
        "contact": "+40-264-202367, Honoriu.Valean@aut.utcluj.ro"
    },
    {
        "name": "Departamentul de Matematica",
        "director": "Prof.dr.mat. Popa Vasile-Dorian",
        "contact": "+40-264-401539, +40-264-401261, Popa.Dorian@math.utcluj.ro"
    }
]

# Create a graph for the OWL file
g = Graph()

# Define base URI for the ontology
base_uri = URIRef("http://example.org/ontology#")

# Create the class for "Department"
Department = URIRef(base_uri + "Department")

# Create individuals for each department
for dept in departments:
    # Create a URI for each department
    dept_uri = URIRef(base_uri + dept["name"].replace(" ", "_"))

    # Add the department as an individual of the Department class
    g.add((dept_uri, RDF.type, Department))

    # Add properties for the director and contact information
    g.add((dept_uri, URIRef(base_uri + "hasDirector"), Literal(dept["director"])))
    g.add((dept_uri, URIRef(base_uri + "hasContact"), Literal(dept["contact"])))

# Serialize and save the data as an OWL file
g.serialize("owl\\departments.owl", format="xml")

print("\nOWL file 'departments.owl' has been created successfully.")
