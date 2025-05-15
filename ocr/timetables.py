import os
import pandas as pd
import re
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, OWL, RDFS, XSD

# Paths
html_folder = r"C:/Users/Cipleu/Documents/IULIA/SCOALA/facultate/Year 4 Semester 2/KBS/Lab/Project/University-Ontology/html/Computer_Science_BSc"
output_path = r"C:/Users/Cipleu/Documents/IULIA/SCOALA/facultate/Year 4 Semester 2/KBS/Lab/Project/University-Ontology/owl/timetables.owl"

# Namespace for ontology
BASE = Namespace("http://example.org/ontology#")

VALID_TIME_RANGES = ['8-10', '10-12', '12-14', '14-16', '16-18', '18-20']

g = Graph()

# Bind namespaces
g.bind("timetable", BASE)
g.bind("rdf", RDF)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("xsd", XSD)

# Define OWL classes
classes = ["Course", "Group", "Room", "Teacher", "Timeslot", "ScheduleEntry"]
for c in classes:
    class_uri = BASE[c]
    g.add((class_uri, RDF.type, OWL.Class))

# Define object properties with domain ScheduleEntry and ranges
properties = {
    "hasGroup": "Group",
    "hasCourse": "Course",
    "hasRoom": "Room",
    "hasTeacher": "Teacher",
    "hasTimeslot": "Timeslot"
}

for prop, rng in properties.items():
    prop_uri = BASE[prop]
    g.add((prop_uri, RDF.type, OWL.ObjectProperty))
    g.add((prop_uri, RDFS.domain, BASE["ScheduleEntry"]))
    g.add((prop_uri, RDFS.range, BASE[rng]))

# Define datatype properties for Timeslot (day and time)
for dp, dt in [("day", XSD.string), ("time", XSD.string)]:
    dp_uri = BASE[dp]
    g.add((dp_uri, RDF.type, OWL.DatatypeProperty))
    g.add((dp_uri, RDFS.domain, BASE["Timeslot"]))
    g.add((dp_uri, RDFS.range, dt))


def uri_safe(name):
    return re.sub(r'\W+', '_', name.strip())


def extract_courses(text):
    courses = []
    if isinstance(text, str):
        parts = re.split(r'/|,|;', text)
        for part in parts:
            clean = part.strip()
            if clean:
                courses.append(clean)
    return courses


# Dictionaries to avoid duplicates
groups = {}
courses = {}
rooms = {}
teachers = {}
timeslots = {}


def get_or_create_individual(kind, name):
    safe_name = uri_safe(name)
    uri = BASE[safe_name]
    # Check if individual exists by querying graph
    if (uri, RDF.type, BASE[kind]) not in g:
        g.add((uri, RDF.type, BASE[kind]))
    return uri


def get_or_create_timeslot(day, time):
    key = f"{day}_{time}"
    if key not in timeslots:
        ts_uri = BASE[uri_safe(key)]
        g.add((ts_uri, RDF.type, BASE["Timeslot"]))
        g.add((ts_uri, BASE.day, Literal(day, datatype=XSD.string)))
        g.add((ts_uri, BASE.time, Literal(time, datatype=XSD.string)))
        timeslots[key] = ts_uri
    return timeslots[key]


# Read HTML files and process
for filename in sorted(os.listdir(html_folder)):
    if filename.endswith(".html"):
        filepath = os.path.join(html_folder, filename)
        try:
            df = pd.read_html(filepath)[0]
            print(f"✅ {filename}: {df.shape}")
        except Exception as e:
            print(f"❌ Failed to read {filename}: {e}")
            continue

        group_name = filename.replace(".html", "")
        group_ind = get_or_create_individual("Group", group_name)
        groups[group_name] = group_ind

        for index, row in df.iterrows():
            row_data = [str(cell) if pd.notna(cell) else "" for cell in row.tolist()]
            day = next((cell for cell in row_data if cell.strip().capitalize() in ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri']), None)
            time = next((cell for cell in row_data if cell.strip() in VALID_TIME_RANGES), None)

            if not day or not time:
                continue

            # Courses start at 4th column
            for cell in row_data[4:]:
                if cell.strip():
                    for course_name in extract_courses(cell):
                        course_ind = get_or_create_individual("Course", course_name)
                        courses[course_name] = course_ind

                        timeslot_ind = get_or_create_timeslot(day, time)

                        # Create ScheduleEntry individual
                        se_name = f"{group_name}_{day}_{time}_{course_name}"
                        se_uri = BASE[uri_safe(se_name)]
                        g.add((se_uri, RDF.type, BASE["ScheduleEntry"]))
                        g.add((se_uri, BASE.hasGroup, group_ind))
                        g.add((se_uri, BASE.hasCourse, course_ind))
                        g.add((se_uri, BASE.hasTimeslot, timeslot_ind))

                        # You can add room and teacher similarly if info is available

# Save ontology
g.serialize(destination=output_path, format="xml")
print(f"Ontology saved to {output_path}")
