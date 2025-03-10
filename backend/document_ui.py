import streamlit as st
import os
from fast_processor_gemini import PDFHandler, ClassifyExtract, process_file
import pandas as pd
from PIL import Image
from datetime import datetime
import json
import pytz
import numpy as np
from entity_matcher import match_entities_for_file
import psycopg2
import psycopg2.extras
import boto3  # NEW: Import boto3 for generating S3 URLs
from s3_utils import upload_fileobj_to_s3

# --- Helper to generate presigned S3 URL ---
def get_s3_url(object_key, bucket_name="form-sage-storage", expiration=3600):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-2"
    )
    return s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': object_key},
        ExpiresIn=expiration
    )

# --- Supabase Connection using psycopg2 ---
def get_connection():
    user = os.environ.get("SUPABASE_USER")
    password = os.environ.get("SUPABASE_PASSWORD")
    host = os.environ.get("SUPABASE_HOST")
    port = os.environ.get("SUPABASE_PORT", 5432)
    dbname = os.environ.get("SUPABASE_DBNAME")
    conn = psycopg2.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        dbname=dbname
    )
    return conn


def store_df_to_db(df, table_name):
    """
    Convert non-serializable columns to strings and store the DataFrame into the given table.
    Uses psycopg2.extras.execute_values for a bulk insert.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    df1 = df.copy()
    # Convert lists, dicts, and sets to JSON strings
    for col in df1.columns:
        if df1[col].apply(lambda x: isinstance(x, (list, dict, set))).any():
            df1[col] = df1[col].apply(lambda x: str(x) if isinstance(x, set)
                                      else json.dumps(x) if isinstance(x, (list, dict))
                                      else x)
    # Add a created_at column
    df1['created_at'] = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
    
    columns = list(df1.columns)
    # Construct an INSERT statement dynamically
    query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES %s"
    # Create a list of tuples representing each row
    values = [tuple(row) for row in df1.to_numpy()]
    
    psycopg2.extras.execute_values(cursor, query, values)
    conn.commit()
    cursor.close()
    conn.close()

@st.cache_data
def process_pdf(upload_path):
    # Process the PDF and extract data using your pipeline
    df_pages, df_extracted, df_info = process_file(upload_path)
    
    # Store the extracted data into the Supabase database
    store_df_to_db(df_pages, 'pages')
    store_df_to_db(df_extracted, 'extracted2')
    store_df_to_db(df_info, 'call_info')
    
    # Run entity matching on the file
    match_entities_for_file(os.path.basename(upload_path))
    
    return df_pages, df_extracted, df_info

# # Ensure the 'uploaded_samples' directory exists
# upload_dir = "uploaded_samples"
# os.makedirs(upload_dir, exist_ok=True)

# # --- Fetch list of uploaded files from Supabase ---
# conn = get_connection()
# query_files = '''
# with p1 as (
#     SELECT DISTINCT created_at, filename 
#     FROM pages ORDER BY created_at DESC
# )
# select filename from p1
# '''
# all_files = pd.read_sql_query(query_files, conn)
# conn.close()

# with st.sidebar:
#     clear_button = st.button("♻️ Clear Cache", type="primary")
#     if clear_button:
#         st.cache_data.clear()
#         st.success("Cache cleared!")
    
#     uploaded_file = st.file_uploader("Upload a PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
#     selected_file = st.selectbox("Select a File", options=all_files['filename'].values if not all_files.empty else [],index=None)

# if not uploaded_file and not selected_file:
#     st.info("👈 Upload a PDF/Image, or Select a File from the sidebar to get started.")

# # --- Processing New Uploads ---
# if uploaded_file:
#     dt_start = datetime.now()
#     # Save the uploaded file locally (temporary storage)
#     upload_path = os.path.join(upload_dir, uploaded_file.name)
#     with open(upload_path, "wb") as f:
#         f.write(uploaded_file.getbuffer())
    
#     # Upload the raw file to S3 using upload_fileobj_to_s3.
#     # Open the file in binary mode and pass it to the helper.
#     with open(upload_path, "rb") as file_obj:
#         raw_s3_key = upload_fileobj_to_s3(file_obj, object_key=f"raw_uploads/{os.path.basename(upload_path)}")
#     # st.write(f"Raw file uploaded to S3 as: {raw_s3_key}")
    
#     df_pages, df_extracted, df_info = process_pdf(upload_path)


# # --- Loading Existing File Data ---
# if selected_file:
#     dt_start = datetime.now()
#     conn = get_connection()
    
#     query_pages = f'''
#     WITH p1 AS (
#         SELECT *,
#                ROW_NUMBER() OVER (PARTITION BY preprocessed ORDER BY created_at DESC) rn
#         FROM pages
#         WHERE filename = '{selected_file}'
#     )
#     SELECT * FROM p1 WHERE rn = 1  
#     '''
#     df_pages = pd.read_sql_query(query_pages, conn)
    
#     query_extracted = f'''
#     WITH e3 AS (
#         SELECT p.filename AS base_file, e2.*, 
#                ROW_NUMBER() OVER (PARTITION BY e2.filename, e2.key ORDER BY created_at DESC) rn 
#         FROM extracted2 e2
#         JOIN (SELECT filename, preprocessed FROM pages) p ON e2.filename = p.preprocessed
#         WHERE p.filename = '{selected_file}'
#     )
#     SELECT * FROM e3 WHERE rn = 1
#     '''
#     df_extracted = pd.read_sql_query(query_extracted, conn)
    
#     query_info = f'''
#     WITH i1 AS (
#         SELECT p.filename AS base_file, i.*, 
#                ROW_NUMBER() OVER (PARTITION BY i.filename ORDER BY created_at DESC) rn 
#         FROM call_info i 
#         JOIN (SELECT filename, preprocessed FROM pages) p ON i.filename = p.preprocessed
#         WHERE p.filename = '{selected_file}'
#     )
#     SELECT * FROM i1 WHERE rn = 1
#     '''
#     df_info = pd.read_sql_query(query_info, conn)
#     conn.close()

# if uploaded_file or selected_file:
#     dt_end = datetime.now()
#     time_taken = dt_end - dt_start
#     page_nums = sorted(df_extracted['page_num'].unique()) if df_extracted is not None else []
#     st.success(f'Doc pages: {len(df_pages)} | Extracted pages: {len(page_nums)} | Time taken: {time_taken} | Per page: {time_taken / max(1, len(page_nums))}')
    
#     col1, col2 = st.columns(2)
#     with col1:
#         selected_page = st.selectbox(
#             "Select a Page", 
#             options=page_nums, 
#             format_func=lambda x: f'Page {x} - {df_extracted[df_extracted["page_num"] == x].iloc[0]["page_label"]}' if x in df_extracted['page_num'].values else f'Page {x}',
#             index=0
#         )
#         st.write(f"Extracted Data for Page {selected_page}:")
#         page_data = df_extracted[df_extracted['page_num'] == selected_page]
#         st.dataframe(page_data[['key', 'value', 'page_label', 'page_num']], hide_index=True, use_container_width=True)
    
#     with col2:
#         show_debug_info = st.toggle("Show Debug Info", value=False)
#         if show_debug_info:
#             with st.expander("Info"):
#                 st.dataframe(df_info, hide_index=True)
#             with st.expander("Pages"):
#                 st.dataframe(df_pages)
#             with st.expander("Extracted Data"):
#                 st.dataframe(df_extracted)
#             with st.expander("Page Words"):
#                 st.text(df_pages['lines'].values)
#         st.write(f"Image for Page {selected_page}:")
#         # Get the S3 object key stored in the 'filename' field (which now holds the S3 reference)
#         selected_page_row = df_extracted[df_extracted['page_num'] == selected_page].iloc[0]
#         local_path = selected_page_row.get('filename')  # e.g. debug_images/25_acord_25/page_1/preprocessed.png

#         if local_path:
#             # If your S3 upload uses the exact same path as local_path, use it directly
#             # Otherwise, prepend a prefix or adjust the path as needed
#             s3_object_key = local_path  # or f"my_prefix/{local_path}"

#             # Generate a presigned URL and display
#             s3_url = get_s3_url(s3_object_key)
#             st.image(s3_url, caption=f"Page {selected_page}")