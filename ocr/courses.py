import os
import fitz  # PyMuPDF
print(dir(fitz)) 
# Define path to the folder with PDFs
pdf_folder = os.path.abspath(os.path.join("..", "pdf", "lic", "calc_engl"))

# Loop through all PDF files
for filename in os.listdir(pdf_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, filename)
        print(f"\n===== Reading {filename} =====\n")

        # Open PDF file with fitz (PyMuPDF)
        doc = fitz.open(pdf_path)

        # Iterate through each page
        for page_num in range(len(doc)):
            page: fitz.Page = doc[page_num]
            page = doc[page_num]
            text = page.get_text()
            print(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
