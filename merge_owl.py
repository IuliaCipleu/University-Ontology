from rdflib import Graph

# Initialize a new graph
merged_graph = Graph()

# List of OWL files to merge
owl_files = ["study_programs.owl", "departments.owl", "cs_department.owl"]

# Loop over each OWL file, load it into the graph, and merge
for owl_file in owl_files:
    graph = Graph()
    graph.parse(owl_file, format="xml")  # Parse the OWL file into the graph
    merged_graph += graph  # Merge the graph into the merged_graph

# Serialize the merged graph into a new OWL file
merged_graph.serialize("merged_ontology.owl", format="xml")

print("\nOWL files have been merged successfully into 'merged_ontology.owl'.")
