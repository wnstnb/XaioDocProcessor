import streamlit as st

st.markdown("""
## 📄 Overview
This application allows you to upload PDFs or images of specific document types, and extract structured data from them using the Gemini 2.0 Flash API. The extracted data is displayed in a user-friendly format, and you can also view uploaded images for debugging.

## ✨ Features
- **📁 File Upload:** Upload PDF or image files for processing.
- **🔍 Data Extraction:** Extract structured data from the uploaded documents.
- **🖼️ Image and Data Comparison:** View images and extracted data side by side.
- **📊 Data Display:** Display the extracted data in a tabular format.
- **💬 Text-to-SQL:** Interact with the database using a chat UI for a more intuitive experience.
- **🔗 Entity Matching:** Automatically match and link extracted data to unique entities (e.g., persons or businesses).

## 🛠️ How It Works
1. **Upload a File:** Use the file uploader in the sidebar to upload a PDF or image file.
2. **Processing:** The uploaded file is processed using the Gemini 2.0 Flash API to extract structured data.
3. **Display Results:** The extracted data is displayed in two columns: one for the output data and one for the image of the page.
4. **Get Overall Stats:** Use natural language to interact with the database and get stats on performance and activity.

## 📋 Usage
1. **Upload a File:**
    - Click on the "Upload a PDF or Image" button in the sidebar.
    - Select a PDF or image file from your computer.
2. **View Results:**
    - The extracted data will be displayed in the main area.
    - Use the page navigation in the sidebar to select different pages.

## 📈 Flow Chart
""")
with st.expander("Here is a flowchart depicting how this all works:"):
    st.image("flowchart.png")
st.markdown("""
## 🧑‍💻 Technical Details
- **🔧 Backend:** The backend processing is handled by the `fast_processor_gemini.py` script.
- **📚 Libraries Used:**
    - `streamlit` for the web interface.
    - `pandas` for data manipulation.
    - `Pillow` for image processing.
    - `google-genai` for interacting with the Gemini 2.0 Flash API.
    - `paddleocr` for OCR processing.
    - `transformers` for text and image classification.
- **🤖 One-Shot Models Used:**
    - `facebook/bart-large-mnli` for text-based zero-shot classification.
    - `openai/clip-vit-base-patch32` for image-based zero-shot classification.
    - `gemini-2.0-flash` for data extraction.
    - `gpt-4o` for conversational NL-to-SQL conversion
- **💾 Database:**
    - The application uses SQLite for storing extracted data and processing results.
""")