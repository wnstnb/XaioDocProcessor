import os
from nltk.corpus import stopwords
import pickle
from tqdm import tqdm
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
import torch
from transformers import CLIPProcessor, CLIPModel, pipeline
import json
import cv2
from pdf2image import convert_from_path
import time
from google import genai
from google.cloud import vision
from gemini_models import get_model
from io import BytesIO  # NEW: for in-memory file operations
from s3_utils import upload_fileobj_to_s3, download_fileobj_from_s3
import mimetypes

# Load models for fallback classification
text_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
image_model = CLIPModel.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")
image_processor = CLIPProcessor.from_pretrained("zer0int/CLIP-GmP-ViT-L-14")

# For classification using template matching
template_db_path = "template_keywords.pkl"

fallback_labels = {
    "This is a government-issued driver's license.": "drivers_license",
    "This is a government-issued passport.": "passport",
    "This a legal lease agreement between a landlord and tenant, with lease agreement verbiage.": "lease_document",
    "This a certificate verifying good standing of a business, issued or provided by a state agency.": "certificate_of_good_standing",
    "This a document issued or provided by a state or locality that explicitly authorizes a business to legally operate, and explicitly states it needs to be displayed.": "business_license",
    "This is a tax document used for financial reporting, tax filing, or recording business financials.": "unknown_tax_form_type"
}

stop_words = set(stopwords.words("english"))

with open(template_db_path, "rb") as f:
    template_db = pickle.load(f)

# Define stop words (using the NLTK corpus)
stop_words = set(stopwords.words("english"))

class PDFHandler:
    def __init__(self, pdf_path=None):
        self.pdf_path = pdf_path
        # Removed PaddleOCR initialization since we now use Cloud Vision
        self.df_pages = self.convert_pages_to_img()

    def convert_pages_to_img(self, output_dir="debug_images"):
        """
        Process each page of a PDF (or a single image file) using the Cloud Vision API for OCR.
        Instead of saving images locally, the preprocessed image is uploaded to S3.
        Returns a DataFrame with the following columns:
          - filename, preprocessed, page_number, image_width, image_height, lines, words,
            bboxes, normalized_bboxes, tokens, words_for_clf, processing_time
        """
        start_time = time.time()
        classification_results = []

        # If the file is an image rather than a PDF:
        if self.pdf_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(self.pdf_path)
            image_width, image_height = image.size

            # Convert image to bytes for Cloud Vision
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            image_bytes = buffer.getvalue()

            # Perform document text detection using Cloud Vision API
            client = vision.ImageAnnotatorClient()
            vision_image = vision.Image(content=image_bytes)
            response = client.document_text_detection(image=vision_image)
            if response.error.message:
                raise Exception(response.error.message)
            annotation = response.full_text_annotation
            text_annotations = response.text_annotations
            words = [s.description for s in text_annotations[1:]] if len(text_annotations) > 1 else []

            # Extract bounding boxes from text annotations (skip the first element)
            bboxes = []
            for s in text_annotations[1:]:
                vertices = s.bounding_poly.vertices
                x1 = min(vertex.x for vertex in vertices)
                y1 = min(vertex.y for vertex in vertices)
                x2 = max(vertex.x for vertex in vertices)
                y2 = max(vertex.y for vertex in vertices)
                bboxes.append([x1, y1, x2, y2])
            normalized_bboxes = [
                [bbox[0] / image_width, bbox[1] / image_height, bbox[2] / image_width, bbox[3] / image_height]
                for bbox in bboxes
            ]

            # Get lines by splitting the full text annotation (if available)
            lines = annotation.text.splitlines() if annotation.text else []

            tokens = [word.lower() for word in words]
            words_for_clf = set([word for word in tokens if word not in stop_words])

            # Preprocess the image (denoising) and upload to S3
            image_np = np.array(image)
            denoised, _ = self.preprocess_image(image_np)
            pp = Image.fromarray(denoised)
            fn = os.path.basename(self.pdf_path)
            buffer_pp = BytesIO()
            pp.save(buffer_pp, format="PNG")
            buffer_pp.seek(0)
            s3_object_key = f"debug_images/{os.path.splitext(fn)[0]}/page_1/preprocessed.png"
            upload_fileobj_to_s3(buffer_pp, s3_object_key)

            classification_results.append({
                "filename": fn,
                "preprocessed": s3_object_key,  # S3 reference
                "page_number": 1,
                "image_width": image_width,
                "image_height": image_height,
                "lines": lines,
                "words": words,
                "bboxes": bboxes,
                "normalized_bboxes": normalized_bboxes,
                "tokens": tokens,
                "words_for_clf": words_for_clf
            })

        else:
            print(os.getenv('POPPLER_PATH'))
            # Directly convert PDF pages to images
            pages = convert_from_path(self.pdf_path, dpi=300, poppler_path=os.getenv('POPPLER_PATH'))
            for page_num, image in enumerate(tqdm(pages, desc='converting pages...'), start=1):
                image_width, image_height = image.size

                # Convert image to bytes for Cloud Vision
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)
                image_bytes = buffer.getvalue()

                # Perform OCR using Cloud Vision API
                client = vision.ImageAnnotatorClient()
                vision_image = vision.Image(content=image_bytes)
                response = client.document_text_detection(image=vision_image)
                if response.error.message:
                    raise Exception(response.error.message)
                annotation = response.full_text_annotation
                text_annotations = response.text_annotations
                words = [s.description for s in text_annotations[1:]] if len(text_annotations) > 1 else []

                # Get bounding boxes from text annotations (skipping the first element)
                bboxes = []
                for s in text_annotations[1:]:
                    vertices = s.bounding_poly.vertices
                    x1 = min(vertex.x for vertex in vertices)
                    y1 = min(vertex.y for vertex in vertices)
                    x2 = max(vertex.x for vertex in vertices)
                    y2 = max(vertex.y for vertex in vertices)
                    bboxes.append([x1, y1, x2, y2])
                normalized_bboxes = [
                    [bbox[0] / image_width, bbox[1] / image_height, bbox[2] / image_width, bbox[3] / image_height]
                    for bbox in bboxes
                ]

                lines = annotation.text.splitlines() if annotation.text else []
                tokens = [word.lower() for word in words]
                words_for_clf = set([word for word in tokens if word not in stop_words])

                # Preprocess the image and upload to S3
                image_np = np.array(image)
                denoised, _ = self.preprocess_image(image_np)
                pp = Image.fromarray(denoised)
                fn = os.path.basename(self.pdf_path)
                buffer_pp = BytesIO()
                pp.save(buffer_pp, format="PNG")
                buffer_pp.seek(0)
                s3_object_key = f"debug_images/{os.path.splitext(fn)[0]}/page_{page_num}/preprocessed.png"
                upload_fileobj_to_s3(buffer_pp, s3_object_key)

                classification_results.append({
                    "filename": fn,
                    "preprocessed": s3_object_key,  # S3 reference for the preprocessed image
                    "page_number": page_num,
                    "image_width": image_width,
                    "image_height": image_height,
                    "lines": lines,
                    "words": words,
                    "bboxes": bboxes,
                    "normalized_bboxes": normalized_bboxes,
                    "tokens": tokens,
                    "words_for_clf": words_for_clf
                })

        df_pages = pd.DataFrame(classification_results)
        end_time = time.time()
        processing_time = end_time - start_time
        df_pages['processing_time'] = processing_time
        return df_pages

    def preprocess_image(self, image, output_dir="debug_images"):
        """
        Preprocess the image:
        1. Convert to Grayscale
        2. Denoising via fastNlMeansDenoising
        Intermediate images are saved locally for debugging.
        """
        os.makedirs(output_dir, exist_ok=True)
        if not isinstance(image, np.ndarray):
            image = np.array(image)

        # Step 1: Convert to Grayscale
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayscale_fp = os.path.join(output_dir, "1_grayscale.png")
        cv2.imwrite(grayscale_fp, grayscale)

        # Step 2: Denoising
        denoised = cv2.fastNlMeansDenoising(grayscale, h=10)
        denoised_fp = os.path.join(output_dir, "2_denoised.png")
        cv2.imwrite(denoised_fp, denoised)

        return denoised, denoised_fp


class ClassifyExtract:
    def __init__(self, row):
        self.fallback_labels = fallback_labels
        self.filename = row['filename']
        self.image_path = row['preprocessed']
        self.image_width, self.image_height = row['image_width'], row['image_height']
        self.lines = row['lines']
        self.words = row['words']
        self.bboxes = row['bboxes'] 
        self.normalized_bboxes = row['normalized_bboxes']
        self.tokens = row['tokens'] 
        self.words_for_clf = row['words_for_clf']
        self.page_label, self.page_score, self.page_confidence_scores, self.page_all_scores, self.clf_type = self.classify_document_with_confidence()
        self.k = self.load_label_info()
        self.keys = [t['key'] for t in self.k[self.page_label]]
        self.queries = [t['question'] for t in self.k[self.page_label]]
        self.coords = [t['target_coords'] for t in self.k[self.page_label]]
        self.bbox_draw_list = []
        # self.model_for_extractor = self.get_model

    def get_device(self):
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def load_template_database(self, db_path):
        with open(db_path, "rb") as f:
            return pickle.load(f)
        
    def load_label_info(self):
        with open('labels.json', 'r') as f:
            return json.load(f)
        
    def show_image(self):
        im = Image.open(self.image_path)
        return im.show()
    
    def draw_bboxes(self, image, bboxes, color="red", width=3):
        """
        Draws bounding boxes on an image.

        Args:
            image (PIL.Image.Image): The input image.
            bboxes (list of lists): List of bounding boxes [[x1, y1, x2, y2], ...].
            color (str): Color of the bounding boxes. Default is "red".
            width (int): Line width for the bounding boxes. Default is 3.

        Returns:
            PIL.Image.Image: Image with bounding boxes drawn.
        """
        # Make a copy of the image to draw on
        draw_image = image.copy()
        draw = ImageDraw.Draw(draw_image)
        
        for bbox in bboxes:
            x1, y1, x2, y2 = bbox
            # Draw the rectangle
            draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
        
        return draw_image

    def show_bboxes(self):
        img = Image.open(self.image_path).convert('RGB')
        annotated_image = self.draw_bboxes(image=img, bboxes=self.bbox_draw_list, color="red", width=2)

        # Save the image to the same directory as the preprocessed image
        annotated_image_path = self.image_path.replace("preprocessed.png", "annotated_bboxes.png")
        annotated_image.save(annotated_image_path)

        return annotated_image_path

    # Text-Based Classification
    def classify_using_text(self, text, labels, threshold=0.6):
        """
        Classify document using text-based zero-shot classification.
        """
        result = text_classifier(text, candidate_labels=labels)
        all_scores = result["scores"]
        best_label, best_score = result["labels"][0], result["scores"][0]
        best_label = self.fallback_labels[best_label]
        if best_score >= threshold:
            return best_label, best_score, None, all_scores, 'text_clf'
        return None

    # Image-Based Classification
    def classify_using_image(self, image_path, labels, threshold=0.6):
        """
        Classify document using image-based zero-shot classification.
        """
        import os
        from s3_utils import download_fileobj_from_s3

        # Check if the file exists locally; if not, download it from S3.
        if not os.path.exists(image_path):
            file_obj = download_fileobj_from_s3(image_path)
            image = Image.open(file_obj)
        else:
            image = Image.open(image_path)
        
        inputs = image_processor(text=labels, images=image, return_tensors="pt", padding=True)
        outputs = image_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)  # Image-text similarity scores
        all_scores = {l: p.item() for l, p in zip(labels, probs[0])}
        best_label = labels[probs.argmax()]
        best_label = self.fallback_labels[best_label]
        best_score = probs.max().item()
        if best_score >= threshold:
            return best_label, best_score, None, all_scores, 'image_clf'
        return None

    def classify_using_keywords(self, match_threshold=0.5):
        """
        Classify an incoming document based on keyword matching with templates,
        and return detailed scores along with normalized confidence probabilities.

        Args:
            image_path (str): Path to the incoming document image.
            template_db (dict): Template database with labels and keywords.
            match_threshold (float): Minimum match percentage required for classification.

        Returns:
            best_label (str): The label with the highest match percentage.
            best_score (float): The highest match percentage.
            confidence_scores (dict): Normalized probabilities for all document types.
            all_scores (dict): A dictionary of raw match percentages for all document types.
        """
        # Extract words from the incoming document
        # incoming_words = set(self.extract_words_from_image(image_path))
        incoming_words = self.words_for_clf
        all_scores = {}
        raw_scores = []

        # Compare against each document type in the template database
        for label, template_keywords_list in template_db.items():
            label_scores = []
            for template_keywords in template_keywords_list:
                # Calculate match percentage for this template
                intersection = incoming_words & template_keywords
                match_percentage = len(intersection) / len(template_keywords) if template_keywords else 0.0
                label_scores.append(match_percentage)

            # Average score for this document type
            avg_score = sum(label_scores) / len(label_scores) if label_scores else 0.0
            all_scores[label] = avg_score
            raw_scores.append(avg_score)

        # Normalize scores into probabilities using softmax
        raw_scores = np.array(raw_scores)
        scaled_scores = raw_scores * 100
        softmax_scores = np.exp(scaled_scores) / np.sum(np.exp(scaled_scores))

        # Create confidence scores dictionary
        # confidence_scores = {label: raw_score / max(raw_scores) for label, raw_score in all_scores.items()}
        confidence_scores = {label: softmax_score for label, softmax_score in zip(all_scores.keys(), softmax_scores)}

        # Determine the best label and its confidence score
        best_label = max(confidence_scores, key=confidence_scores.get)
        best_score = confidence_scores[best_label]

        # Only classify if the confidence score exceeds the threshold
        if all_scores[best_label] >= match_threshold:
            return best_label, best_score, confidence_scores, all_scores, "keyword_matching"

        return None

    def classify_document_with_confidence(self):
        """
        Classify document using keywords, then text-based classification, 
        and fall back to image-based classification if needed.
        """
        # Step 1: Keyword-based classification
        kw_result = self.classify_using_keywords()
        if kw_result:
            best_label, best_score, confidence_scores, all_scores, clf_type = kw_result
            return best_label, best_score, confidence_scores, all_scores, clf_type

        # Step 2: Text-based classification
        # Use first 100 characters for classification
        words_from_set = list(self.words_for_clf)
        words_for_txt = ' '.join(words_from_set)
        txt_result = self.classify_using_text(text=words_for_txt, labels=list(self.fallback_labels.keys()))
        if txt_result:
            best_label, best_score, confidence_scores, all_scores, clf_type = txt_result
            return best_label, best_score, confidence_scores, all_scores, clf_type


        # If lengthy, don't pass to image. Indicate that it's an unknown text heavy document, 
        if len(words_from_set) > 100:
            return 'unknown_text_type', 0, None, None, None
        
        # Step 3: Fallback to image-based classification
        img_result = self.classify_using_image(image_path=self.image_path, labels=list(self.fallback_labels.keys()))
        if img_result:
            best_label, best_score, confidence_scores, all_scores, clf_type = img_result
            return best_label, best_score, confidence_scores, all_scores, clf_type

        # Step 4: Final fallback
        return 'unknown', 0, None, None, None
    
    def process_image(self):
        model_use = get_model(self.page_label)
        api_key = os.environ.get("GOOGLE_GENAI_API_KEY")
        client = genai.Client(api_key=api_key)
        model_id = "gemini-2.0-flash"
        max_retries = 5
        backoff_factor = 2

        if os.path.exists(self.image_path):
            file_to_upload = self.image_path
        else:
            file_to_upload = download_fileobj_from_s3(self.image_path)
        
        # Determine the MIME type based on the file extension of self.image_path.
        mime_type, _ = mimetypes.guess_type(self.image_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1} of {max_retries}...")
            try:
                # Pass the mime_type argument to the upload call
                file = client.files.upload(
                    file=file_to_upload, 
                    config={'display_name': os.path.basename(self.image_path).split('.')[0],
                            'mime_type':mime_type}
                )
                prompt = (
                    "Extract the structured data from this document. "
                    "If SPII is requested, only return partial data. "
                    "If a field exists but contains no value, return an empty string."
                )
                response = client.models.generate_content(
                    model=model_id,
                    contents=[prompt, file],
                    config={
                        'response_mime_type': 'application/json',
                        'response_schema': model_use
                    }
                )
                print(response)
                if response.parsed:
                    info = {
                        'filename': self.image_path,
                        'model_version': response.model_version,
                    }
                    info.update(response.usage_metadata)
                    info = pd.json_normalize(info)

                    line_items = response.parsed.model_dump()
                    extracted = pd.DataFrame({
                        'key': list(line_items.keys()),
                        'value': list(line_items.values()),
                        'filename': self.image_path
                    })
                    extracted = extracted[['filename', 'key', 'value']]
                    return info, extracted
                else:
                    wait_time = backoff_factor ** attempt
                    print(f"Response not valid. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue

            except genai.errors.ClientError as e:
                if e.code == 429:
                    wait_time = backoff_factor ** attempt
                    print(f"Resource exhausted (429). Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise e

        print("Max retries reached. Could not process the image.")
        return None




def process_file(fp, save_to_db=False):
    p = PDFHandler(fp)

    df_pages = p.df_pages

    clf_results = []
    clf_confidence = []
    clf_types = []
    extraction_results = []
    info_results = []
    for _, row in tqdm(df_pages.iterrows()):
        # fp = rf"{row['preprocessed']}"
        # print(fp)
        c = ClassifyExtract(row)
        clf_type = c.clf_type
        page_label = c.page_label
        page_score = c.page_score
        clf_types.append(clf_type)
        clf_results.append(page_label)
        clf_confidence.append(page_score)
        print(page_label)
        if page_label not in ['unknown', 'unknown_text_type', 'unknown_tax_form_type']:
            info, res = c.process_image()
            res['page_label'] = page_label
            res['page_confidence'] = page_score
            res['page_num'] = row['page_number']
            extraction_results.append(res)
            info_results.append(info)

    df_pages['clf_type'] = clf_types
    df_pages['page_label'] = clf_results
    df_pages['page_confidence'] = clf_confidence
    df_extracted = pd.DataFrame()
    df_info = pd.DataFrame()
    if len(extraction_results) > 0:
        df_extracted = pd.concat(extraction_results)
    if len(info_results) > 0: 
        df_info = pd.concat(info_results)

    if extraction_results:
        df_extracted = pd.concat(extraction_results)
        
        # Fix non-serializable columns
        for col in df_extracted.columns:
            if df_extracted[col].apply(lambda x: isinstance(x, (list, dict, set))).any():
                df_extracted[col] = df_extracted[col].apply(lambda x: str(x) if isinstance(x, (list, dict, set)) else x)
        
        # Save to database if requested
        if save_to_db:
            try:
                from document_ui import store_df_to_db
                store_df_to_db(df_pages, 'pages')
                store_df_to_db(df_extracted, 'extracted2')
                store_df_to_db(df_info, 'call_info')
                print("Data saved to database successfully")
            except Exception as e:
                print(f"Error saving to database: {e}")
                import traceback
                traceback.print_exc()
        
        return df_pages, df_extracted, df_info
    else:
        return df_pages, None, None

    
# if __name__ == '__main__':
#     # from fast_processor import PDFHandler, ClassifyExtract
#     import cProfile
#     import pstats
#     import io
    
#     pr = cProfile.Profile()
#     pr.enable()

#     main(r'uploaded_samples\2022_TaxReturns.pdf')

#     pr.disable()
#     s = io.StringIO()
#     ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
#     ps.print_stats()

#     # Save the stats to a file for later use (optional)
#     with open("profiling_stats.txt", "w") as f:
#         f.write(s.getvalue())