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

day_translation = {
    "Luni": "Monday",
    "Marti": "Tuesday",
    "Miercuri": "Wednesday",
    "Joi": "Thursday",
    "Vineri": "Friday"
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

# Define isOccupiedAt
is_occupied_at = BASE["isOccupiedAt"]
g.add((is_occupied_at, RDF.type, OWL.ObjectProperty))
g.add((is_occupied_at, RDFS.domain, BASE["Room"]))
g.add((is_occupied_at, RDFS.range, BASE["Timeslot"]))

# Define isFreeAt as inverse of isOccupiedAt
is_free_at = BASE["isFreeAt"]
g.add((is_free_at, RDF.type, OWL.ObjectProperty))
g.add((is_free_at, RDFS.domain, BASE["Room"]))
g.add((is_free_at, RDFS.range, BASE["Timeslot"]))


def split_course_info(course_str):
    # Split by ' - ' exactly into 3 parts: course name, teacher, room
    parts = [part.strip() for part in course_str.split(' - ')]
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    else:
        # If not exactly 3 parts, return the whole string as course name and empty teacher/room
        return course_str.strip(), "", ""


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


def fix_room_name(room_name):
    if room_name.startswith("BT"):
        fixed_name = room_name.replace(' ', '')
        return fixed_name
    elif room_name.startswith("Aula I."):
        return "AulaInstalatii"
    return room_name


# Read HTML files and process
for filename in sorted(os.listdir(html_folder)):
    if filename.endswith(".html"):
        filepath = os.path.join(html_folder, filename)
        try:
            df = pd.read_html(filepath)[0]
            print(f"{filename}: {df.shape}")
        except Exception as e:
            print(f"Failed to read {filename}: {e}")
            continue

        group_name = filename.replace(".html", "")
        group_ind = get_or_create_individual("Group", group_name)
        groups[group_name] = group_ind
        group_header_row_index = 2  # adjust if needed
        group_names = df.iloc[group_header_row_index, 4:].tolist()  # from col 4 to end

        # Clean group names (remove nan, strip strings)
        group_names = [str(g).strip() if pd.notna(g) else "" for g in group_names]

        for index, row in df.iterrows():
            row_data = [str(cell) if pd.notna(cell) else "" for cell in row.tolist()]
            day = next((cell for cell in row_data if cell.strip().capitalize() in ['Luni', 'Marti', 'Miercuri', 'Joi', 'Vineri']), None)
            time = next((cell for cell in row_data if cell.strip() in VALID_TIME_RANGES), None)

            if not day or not time:
                continue
            
            day_en = day_translation.get(day.strip().capitalize(), day)

            # Courses start at 4th column
            for col_idx, cell in enumerate(row_data[4:], start=4):
                if cell.strip():
                    group_for_column = group_names[col_idx - 4]  # match group by col index
                    group_ind = get_or_create_individual("Group", group_for_column)
                    groups[group_for_column] = group_ind
                    for course_name in extract_courses(cell):
                        course, teacher, room = split_course_info(course_name)
                        course_ind = get_or_create_individual("Course", course)
                        courses[course_name] = course_ind

                        timeslot_ind = get_or_create_timeslot(day_en, time)

                        # Create ScheduleEntry individual
                        se_name = f"{group_name}_{day}_{time}_{course_name}"
                        se_uri = BASE[uri_safe(se_name)]
                        g.add((se_uri, RDF.type, BASE["ScheduleEntry"]))
                        g.add((se_uri, BASE.hasGroup, group_ind))
                        g.add((se_uri, BASE.hasCourse, course_ind))
                        g.add((se_uri, BASE.hasTimeslot, timeslot_ind))

                        if teacher:
                            teacher_ind = get_or_create_individual("Teacher", teacher)
                            teachers[teacher] = teacher_ind
                            g.add((se_uri, BASE.hasTeacher, teacher_ind))

                        # Add room if exists
                        if room:
                            fixed_room = fix_room_name(room)
                            print(room, fixed_room)
                            room_ind = get_or_create_individual("Room", fixed_room)
                            rooms[fixed_room] = room_ind
                            rooms[room] = room_ind
                            g.add((se_uri, BASE.hasRoom, room_ind))                         
        
# Save ontology
g.serialize(destination=output_path, format="xml")
print(f"Ontology saved to {output_path}")
