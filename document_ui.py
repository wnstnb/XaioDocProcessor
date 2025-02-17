import streamlit as st
import os
from fast_processor_gemini import PDFHandler, ClassifyExtract, process_file
import pandas as pd
from PIL import Image
from datetime import datetime
import sqlite3
import json
import pytz
import numpy as np

# st.set_page_config(
#     page_title="Form Sage UI",
#     page_icon="🪄",
#     layout="wide",
# )

# pg = st.navigation([
#     st.Page("document_ui.py", title="Document UI", icon="🗃️"),
#     st.Page("metrics_ui.py", title="Metrics UI", icon="📊"),
#     # st.Page(page2, title="Second page", icon=":material/favorite:"),
# ])


def clear_cache():
    st.cache_data.clear()
    st.success("Cache cleared!")

# Initialize the database
def init_db():
    conn = sqlite3.connect('documents.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            filename TEXT,
            preprocessed TEXT,
            page_number INTEGER,
            image_width REAL,
            image_height REAL,
            lines TEXT,
            words TEXT,
            bboxes TEXT,
            normalized_bboxes TEXT,
            tokens TEXT,
            words_for_clf TEXT,
            processing_time REAL,
            clf_type TEXT,
            page_label TEXT,
            page_confidence REAL,
            created_at datetime default current_timestamp
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted (
            key TEXT,
            label TEXT,
            label_bbox TEXT,
            label_confidence REAL,
            value TEXT,
            value_bbox TEXT,
            value_confidence REAL,
            page_num INTEGER,
            annotated_image_path TEXT,
            filename TEXT,
            created_at datetime default current_timestamp
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted2 (
            key TEXT,
            label TEXT,
            filename TEXT,
            page_num INTEGER,
            created_at datetime default current_timestamp
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS call_info (
            filename TEXT,
            model_version TEXT,
            cached_content_token_count INTEGER,
            candidates_token_count INTEGER,
            prompt_token_count INTEGER,
            total_token_count INTEGER,
            created_at datetime default current_timestamp
        )
    ''')
    conn.commit()
    conn.close()

def store_df_to_db(df, table_name):
    conn = sqlite3.connect('documents.db')
    # Convert non-serializable columns to JSON strings
    # convert_these = [
    #     'lines',
    #     'words',
    #     'bboxes',
    #     'normalized_bboxes',
    #     'tokens',
    #     'words_for_clf'
    # ]
    df1 = df.copy()
    for col in df1.columns:
        if df1[col].apply(lambda x: isinstance(x, (list, dict, set))).any():
            # df[col] = df[col].apply(lambda x: str(x))
            df1[col] = df1[col].apply(lambda x: str(x) if isinstance(x, set) else json.dumps(x) if isinstance(x, (list, dict)) else x)

    df1['created_at'] = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    df1.to_sql(table_name, conn, if_exists='append', index=False)
    conn.close()

# Cache the PDF processing function
@st.cache_data
def process_pdf(upload_path):
    # Get the extracted data from the PDF
    df_pages, df_extracted, df_info = process_file(upload_path)
    
    # Store the extracted data in the database
    store_df_to_db(df_pages, 'pages')
    store_df_to_db(df_extracted, 'extracted2')
    store_df_to_db(df_info, 'call_info')
    return df_pages, df_extracted, df_info


# def main():

# Ensure the 'uploaded_samples' directory exists
upload_dir = "uploaded_samples"
os.makedirs(upload_dir, exist_ok=True)

# Move the file uploader to the sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
    # Add a button to clear cache
    if st.button("Clear Cache"):
        clear_cache()

if not uploaded_file:
    st.info("👈 Upload a PDF or Image in the sidebar to get started.")

if uploaded_file:
    # Save the uploaded file to 'uploaded_samples'
    upload_path = os.path.join(upload_dir, uploaded_file.name)
    with open(upload_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    dt_start = datetime.now()
    # Use cached results for processing the PDF
    # with st.spinner("Processing PDF..."):
    df_pages, df_extracted, df_info = process_pdf(upload_path)

    # if df_extracted is not None:
    dt_end = datetime.now()
    time_taken = dt_end - dt_start
    page_nums = df_extracted['page_num'].unique() if df_extracted is not None else []
    st.success(f'Doc pages: {len(df_pages)} | Extracted pages: {len(page_nums)} | Time taken: {time_taken} | Per page: {time_taken/max(1,len(page_nums))}')
    # Add a page navigation sidebar
    selected_page = st.sidebar.selectbox("Select a Page", options=page_nums)

    with st.expander("Info"):
        st.dataframe(df_info)
    with st.expander("Pages"):
        st.dataframe(df_pages)
    # with st.expander("Pages"):
    #     st.dataframe(df_pages.dtypes)
    with st.expander("Extracted Data"):
        st.dataframe(df_extracted)
    # with st.expander("Extracted Data"):
    #     st.dataframe(df_extracted.dtypes)
    with st.expander("Page Words"):
        st.text(df_pages['lines'].values)
    
    col1, col2 = st.columns(2)
    with col1:
        # Display extracted data for the selected page
        st.write(f"Extracted Data for Page {selected_page}:")
        page_data = df_extracted[df_extracted['page_num'] == selected_page]
        st.dataframe(page_data[['key','value','page_label','page_num']])

    with col2:
        # Display bounding boxes for the selected page
        st.write(f"Image for Page {selected_page}:")
        selected_page_row = df_extracted[df_extracted['page_num'] == selected_page].iloc[0]
        print(selected_page_row)
        annotated_image_path = selected_page_row.get('filename')

        if annotated_image_path:
            st.image(annotated_image_path)

    # else:
    #     st.write("No data extracted from the uploaded PDF.")

# if __name__ == "__main__":
# # pg.run()
    
#     main()

