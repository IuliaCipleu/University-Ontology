from rdflib import Graph
import shutil
import os

# Define the path to the original merged ontology
original_merged_path = r"C:\Users\Cipleu\Documents\IULIA\SCOALA\facultate\Year 4 Semester 2\KBS\Lab\Project\University-Ontology\owl\merged_ontology.owl"
backup_merged_path = original_merged_path.replace(".owl", "_backup.owl")

# Step 1: Create a backup of the original merged_ontology.owl
if os.path.exists(original_merged_path):
    shutil.copyfile(original_merged_path, backup_merged_path)
    print(f"Backup created at: {backup_merged_path}")
else:
    print("No existing merged_ontology.owl found. Proceeding without backup.")

# Step 2: Initialize a new graph
merged_graph = Graph()

# Step 3: List of OWL files to merge
owl_files = [
    "owl/study_programs.owl",
    "owl/departments.owl",
    "owl/cs_department.owl",
    "owl/courses.owl",
    "owl/students.owl",
    "owl/timetables.owl",
    "owl/matched_courses.owl",
    "owl/inferred.owl"
]

# If backup exists, include it in the merge
if os.path.exists(backup_merged_path):
    owl_files.insert(0, backup_merged_path)  # Merge it first

# Step 4: Merge all graphs
for owl_file in owl_files:
    graph = Graph()
    try:
        graph.parse(owl_file, format="xml")
        merged_graph += graph
        print(f"Merged: {owl_file}")
    except Exception as e:
        print(f"Error parsing {owl_file}: {e}")

# Step 5: Serialize the merged graph back to the original path
merged_graph.serialize(destination=original_merged_path, format="xml")
print(f"\nMerged ontology written to: {original_merged_path}")
