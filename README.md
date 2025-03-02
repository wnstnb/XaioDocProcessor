# XaioDocProcessor

**XaioDocProcessor** is a document processing platform designed to **parse, classify, and extract data** from complex financial and business forms, including tax documents and multi-page PDFs. Built for flexibility, Xaio can handle **structured, semi-structured, and mixed-document uploads**, with support for **both automated extraction and human-in-the-loop review**.

## Key Capabilities

- **Document Classification**: Page-level document type detection for mixed uploads, combining template matching, text classification, and image classification techniques.
- **Data Extraction**: Structured field extraction using rule-based logic, OCR, and hybrid parsing techniques.
- **Review Interface**: Human-in-the-loop validation and override tools for extracted data.
- **Adaptive Parsing**: Learns and adapts to new form variants over time.

## Technology Stack

| Layer         | Technology            |
| --------------| --------------------- |
| Backend       | Python (parsing & classification) |
| Backend UI    | Streamlit (reference only) |
| Frontend      | React + Next.js       |
| Styling       | Tailwind CSS          |
| Processing    | PDF parsing libraries, OCR, custom extraction logic |
