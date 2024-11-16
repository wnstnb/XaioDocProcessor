import json
import fitz  # PyMuPDF
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import pytesseract
import os

def load_field_config(config_path):
    """Load field configuration from JSON."""
    with open(config_path, "r") as file:
        return json.load(file)

def scale_bbox(bbox, scale):
    """Scale bounding box coordinates from PDF points to image pixels."""
    return [coord * scale for coord in bbox]

def debug_text_in_search_area(page, bbox):
    """Extract and print all text in the specified bounding box."""
    x1, y1, x2, y2 = bbox
    text = page.get_textbox((x1, y1, x2, y2))
    print(f"Text found in the search area ({bbox}): {text}")
    return text

def convert_to_black_and_white(image_path):
    """Convert an image to black and white."""
    image = Image.open(image_path)
    bw_image = image.convert("L")  # Convert to grayscale
    bw_image = bw_image.point(lambda x: 0 if x < 128 else 255, "1")  # Threshold to black and white
    bw_path = image_path.replace(".png", "_bw.png")
    bw_image.save(bw_path)
    return bw_path

def draw_dashed_rectangle(draw, bbox, outline="orange", width=2, dash_length=5):
    """Draw a dashed rectangle."""
    x1, y1, x2, y2 = bbox
    # Top side
    for i in range(int((x2 - x1) // dash_length)):
        if i % 2 == 0:  # Draw only on alternate segments
            draw.line([(x1 + i * dash_length, y1), (x1 + (i + 1) * dash_length, y1)], fill=outline, width=width)
    # Bottom side
    for i in range(int((x2 - x1) // dash_length)):
        if i % 2 == 0:
            draw.line([(x1 + i * dash_length, y2), (x1 + (i + 1) * dash_length, y2)], fill=outline, width=width)
    # Left side
    for i in range(int((y2 - y1) // dash_length)):
        if i % 2 == 0:
            draw.line([(x1, y1 + i * dash_length), (x1, y1 + (i + 1) * dash_length)], fill=outline, width=width)
    # Right side
    for i in range(int((y2 - y1) // dash_length)):
        if i % 2 == 0:
            draw.line([(x2, y1 + i * dash_length), (x2, y1 + (i + 1) * dash_length)], fill=outline, width=width)

def extract_text_with_ocr(image_path, bbox):
    """Extract text from an image within a bounding box using Tesseract OCR."""
    image = Image.open(image_path)
    cropped_image = image.crop(bbox)  # Crop to the bounding box
    text = pytesseract.image_to_string(cropped_image)
    print(f"OCR Text in the search area ({bbox}): {text}")
    return text

def calculate_region(page_width, page_height, search_area):
    """Calculate absolute coordinates for a flexible search area."""
    x_start = (search_area.get("x_start", 0) / 100) * page_width
    x_end = (search_area.get("x_end", 100) / 100) * page_width
    y_start = (search_area.get("y_start", 0) / 100) * page_height
    y_end = (search_area.get("y_end", 100) / 100) * page_height
    return x_start, y_start, x_end, y_end

def extract_fields_from_labels(pdf_path, config, output_dir="output_images", page_number=1, dpi=300):
    """Extract fields based on labels and constraints defined in JSON config."""
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Convert the first page of the PDF to PNG
    pages = convert_from_path(pdf_path, dpi=dpi)
    png_path = os.path.join(output_dir, f"page_{page_number}.png")
    pages[page_number - 1].save(png_path, "PNG")

    # Step 2: Open the PDF and extract text information
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]
    page_width = page.rect.width
    page_height = page.rect.height

    # Scaling factor: PDF points to image pixels
    scale = dpi / 72

    results = {}

    # Iterate through the fields defined in the JSON config
    for field_key, field_info in config["fields"].items():
        label_text = field_info["label"]
        match_mode = field_info.get("match_mode", "exact")  # Default to exact matching
        search_area = field_info.get("search_area", {})  # Default to full page
        offsets = field_info.get("offsets", {})

        # Calculate the search region
        x_start, y_start, x_end, y_end = calculate_region(page_width, page_height, search_area)

        label_coords = None
        value_coords = None
        value_text = None
        value_search_area = None  # This will store the region being searched for the value

        # Step 3: Locate the label in the document
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip()
                    bbox = span["bbox"]  # (x1, y1, x2, y2)
                    x1, y1, x2, y2 = bbox

                    # Match the label text based on the mode and region
                    if (
                        ((match_mode == "exact" and text == label_text) or
                        (match_mode == "loose" and label_text.lower() in text.lower()))
                        and x_start <= x1 <= x_end
                        and y_start <= y2 <= y_end
                    ):
                        label_coords = bbox
                        break
                if label_coords:
                    break
            if label_coords:
                break

        # Step 4: Retrieve the value relative to the label
        if label_coords:
            label_x1, label_y1, label_x2, label_y2 = label_coords

            # Determine value width
            value_width = offsets.get("value_width", "label_width")
            if value_width == "label_width":
                search_x2 = label_x2 + offsets.get("horizontal_offset", 0)
            else:
                search_x2 = label_x1 + offsets.get("horizontal_offset", 0) + value_width

            # Calculate the search area for the value using offsets
            search_y1 = label_y2 + offsets.get("vertical_offset", 0)
            search_y2 = search_y1 + offsets.get("value_height", 15)
            search_x1 = label_x1 + offsets.get("horizontal_offset", 0)
            value_search_area = (search_x1, search_y1, search_x2, search_y2)

            # Try extracting text using PyMuPDF
            value_text = debug_text_in_search_area(page, value_search_area)

            # If no text is found, try OCR on the black-and-white image
            if not value_text.strip():
                bw_path = convert_to_black_and_white(png_path)
                value_text = extract_text_with_ocr(bw_path, scale_bbox(value_search_area, scale))

            # If text is found, assign value coordinates
            if value_text.strip():
                value_coords = value_search_area

        # Step 5: Store results for the current field
        results[field_key] = {
            "label_coords": scale_bbox(label_coords, scale) if label_coords else None,
            "value_coords": scale_bbox(value_coords, scale) if value_coords else None,
            "value_text": value_text.strip() if value_text else '',
            "value_search_area": scale_bbox(value_search_area, scale) if value_search_area else None,
        }

    # Step 6: Visualize results
    image = Image.open(png_path)
    draw = ImageDraw.Draw(image)

    for field_key, result in results.items():
        # Mark the label
        if result["label_coords"]:
            draw.rectangle(result["label_coords"], outline="blue", width=3)

        # Mark the value search area
        if result["value_search_area"]:
            draw_dashed_rectangle(draw, result["value_search_area"], outline="orange", width=2)

        # Mark the value
        if result["value_coords"]:
            draw.rectangle(result["value_coords"], outline="green", width=3)

    # Save the marked-up image
    marked_png_path = os.path.join(output_dir, f"marked_page_{page_number}.png")
    image.save(marked_png_path)

    # Output results
    for field_key, result in results.items():
        print(f"Field: {field_key}")
        print(f"Label Coordinates: {result['label_coords']}")
        print(f"Value Search Area: {result['value_search_area']}")
        print(f"Value Coordinates: {result['value_coords']}")
        print(f"Value Text: {result['value_text']}")
        print("-" * 50)

    print(f"Marked-up image saved to: {marked_png_path}")

    # Close the PDF document
    doc.close()

    return results, marked_png_path

# Load field configuration from JSON
config_path = "field_config.json"
config = load_field_config(config_path)

# Specify the path to your PDF
pdf_path = r"data\Sample1120S2023.pdf"

# Extract fields
results, marked_image = extract_fields_from_labels(pdf_path, config)

# Print results
for field, data in results.items():
    print(f"{field}: {data['value_text']}")