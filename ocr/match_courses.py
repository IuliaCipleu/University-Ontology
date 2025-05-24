from rdflib import Graph, Namespace, URIRef, Literal
import re
import Levenshtein
from unidecode import unidecode
from googletrans import Translator
from rdflib.namespace import RDF, OWL, XSD

translator = Translator()

# Namespace
BASE = Namespace("http://example.org/ontology#")

# Common abbreviations mapping to check both ways (you can expand this)
ABBREVIATIONS = {
    "operatingsystems": ["os", "so", "sistemeoperare", "sistemeoperare"],
    "electrotechnics": ["et", "electrotehnica"],
    "informationsecurity": ["is", "securitateinformatica"],
    "logicprogramming": ["pl", "lp","programarelogica"],
    "logicdesign": ["pl", "ld", "proiectarelogica"],
    "computernetwork": ["cn", "pc", "proiectarearetelelor"],
}


def translate_title(title, src='ro', dest='en'):
    try:
        translated = translator.translate(title, src=src, dest=dest)
        return translated.text.lower()
    except Exception as e:
        print(f"Translation error: {e}")
        return title.lower()


def normalize_and_translate_title(title):
    """
    Normalize and translate titles by:
    - Translating (from Romanian to English by default)
    - Removing accents
    - Lowercasing
    - Removing non-alphanumeric characters
    """
    # Translate title first
    translated = translate_title(title, src='ro', dest='en')
    print(title)
    # Normalize
    normalized = unidecode(translated)
    normalized = normalized.lower()
    normalized = re.sub(r'[^a-z0-9]', '', normalized)
    return normalized


def extract_courses(graph):
    """
    Extract Course individuals with their titles and codes.
    """
    courses = []
    for s in graph.subjects(predicate=None, object=BASE.Course):
        title = graph.value(subject=s, predicate=BASE.hasTitle)
        code = graph.value(subject=s, predicate=BASE.hasCode)
        if title:
            norm_title = normalize_and_translate_title(str(title))
            courses.append({
                "uri": s,
                "title": str(title),
                "code": str(code) if code else None,
                "norm_title": norm_title
            })
    return courses


def check_abbreviation_match(title1, title2):
    """
    Check if title1 and title2 match by abbreviation mapping.
    """
    # Direct exact match shortcut
    if title1 == title2:
        return True

    # Check abbreviation lists
    for key, abbrevs in ABBREVIATIONS.items():
        if title1 == key and title2 in abbrevs:
            return True
        if title2 == key and title1 in abbrevs:
            return True
    return False


def find_matches(courses1, courses2, threshold=0.85):
    """
    Find matching courses based on normalized title similarity + abbreviation check.
    """
    matches = []
    print("Courses 1:")
    for c1 in courses1:
        print(c1["title"], "->", c1["norm_title"])
        print("\nCourses 2:")
        for c2 in courses2:
            print(c2["title"], "->", c2["norm_title"])
            # Check abbreviation match first
            if check_abbreviation_match(c1["norm_title"], c2["norm_title"]):
                sim = 1.0
            else:
                sim = Levenshtein.ratio(c1["norm_title"], c2["norm_title"])

            if sim >= threshold:
                matches.append((c1["uri"], c2["uri"], sim))
    return matches


def create_match_graph(matches):
    match_graph = Graph()
    for c1_uri, c2_uri, sim in matches:
        match_uri = URIRef(f"http://example.org/ontology#{c1_uri.split('#')[-1]}_{c2_uri.split('#')[-1]}")

        # Declare the match node as an OWL named individual
        match_graph.add((match_uri, RDF.type, OWL.NamedIndividual))

        # Add your properties
        match_graph.add((match_uri, BASE.hasMatch, c1_uri))
        match_graph.add((match_uri, BASE.hasMatch, c2_uri))
        match_graph.add((match_uri, BASE.hasSimilarity, Literal(sim, datatype=XSD.double)))
    return match_graph

# === Main Execution ===


# Load both OWL files
g1 = Graph()
g2 = Graph()

g1.parse('file:///C:/Users/Cipleu/Documents/IULIA/SCOALA/facultate/Year%204%20Semester%202/KBS/Lab/Project/University-Ontology/owl/courses.owl', format="xml")
g2.parse('file:///C:/Users/Cipleu/Documents/IULIA/SCOALA/facultate/Year%204%20Semester%202/KBS/Lab/Project/University-Ontology/owl/timetables.owl', format="xml")

courses1 = extract_courses(g1)
courses2 = extract_courses(g2)

matches = find_matches(courses1, courses2)

match_graph = create_match_graph(matches)

# Declare hasMatch as an ObjectProperty
match_graph.add((BASE.hasMatch, RDF.type, OWL.ObjectProperty))

# Declare hasSimilarity as a DatatypeProperty
match_graph.add((BASE.hasSimilarity, RDF.type, OWL.DatatypeProperty))

output_path = r"C:/Users/Cipleu/Documents/IULIA/SCOALA/facultate/Year 4 Semester 2/KBS/Lab/Project/University-Ontology/owl/matched_courses.owl"
match_graph.serialize(output_path, format="xml")

print(f"Matching courses saved in 'matched_courses.owl'")
