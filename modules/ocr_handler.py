import pytesseract
from PIL import Image
import os

def scan_receipt(image_path):
    """
    Scans an image and returns the raw text.
    Requires Tesseract-OCR to be installed on your system.
    """
    if not os.path.exists(image_path):
        return "Error: File not found."

    try:
        # Open the image
        img = Image.open(image_path)
        # Extract text
        text = pytesseract.image_to_string(img)
        print("--- Scanned Text ---")
        print(text)
        print("--------------------")
        return text
    except Exception as e:
        return f"Error during OCR: {e}"