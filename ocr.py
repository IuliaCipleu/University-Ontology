import pytesseract
from PIL import Image


# Set the path to tesseract if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path based on your system

# Open an image file
img = Image.open('fig\study_programme.jpg')  # Replace 'image.png' with the path to your image

# Use pytesseract to extract text
text = pytesseract.image_to_string(img)

# Print the extracted text
print(text)
