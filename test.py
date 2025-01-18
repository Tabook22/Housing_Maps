from PIL import Image
import pytesseract
import re

# Set the Tesseract path (update this path based on your Tesseract installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_coordinates(image_path):
    """
    Extract Northing and Easting coordinates from the image using OCR.
    """
    try:
        # Use OCR to extract text from the image
        text = pytesseract.image_to_string(Image.open(image_path))
        print("Extracted Text:\n", text)  # Debugging: Print extracted text
        
        # Use regex to find all Northing and Easting pairs
        # This pattern assumes Northing and Easting are large numbers (e.g., 2615968.84, 584283.08)
        pattern = r"(\d{7}\.\d+)\s+(\d{6}\.\d+)"
        matches = re.findall(pattern, text)
        
        # Convert matches to tuples of floats
        coordinates = [(float(northing), float(easting)) for northing, easting in matches]
        return coordinates
    except Exception as e:
        print("Error in extract_coordinates:", e)
        return []

# Test the function
image_path = 'uploaded_image.jpg'
coordinates = extract_coordinates(image_path)
print("Extracted Coordinates:", coordinates)