from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
import os
from fast_processor_gemini import process_file  # Import your processing function
import boto3
import psycopg2
import pandas as pd
from typing import List, Optional
from chat_ui import convert_to_sql, run_sql_query, save_conversation, load_conversations, SCHEMA


app = FastAPI()

# Enable CORS if your frontend is hosted on a different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, you can allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure a temporary directory exists for uploads
UPLOAD_DIR = "uploaded_samples"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str

class Message(BaseModel):
    role: str
    content: str

class SaveConversationRequest(BaseModel):
    conversation: List[Message]
    title: Optional[str] = "Conversation"

@app.get("/conversations")
def get_conversations():
    """
    Example returning a list of saved conversations.
    Format: [{ id, title, conversation, created_at }, ...]
    """
    conversations = load_conversations()  # e.g. from chat_ui.py
    # load_conversations returns a list of { "id", "title", "conversation", "created_at" }
    return conversations

@app.post("/save-conversation")
def save_conversation_endpoint(req: SaveConversationRequest):
    """
    Save a conversation to the DB. Optionally includes a custom title.
    Expects JSON:
      {
        "conversation": [
          {"role": "user", "content": "Hello"},
          {"role": "assistant", "content": "Hi there!"}
        ],
        "title": "My Great Chat"
      }
    """
    print("everything:", req)
    print("Received conversation type:", type(req.conversation))
    
    # Debug each message in the conversation
    for i, msg in enumerate(req.conversation):
        print(f"Message {i} type: {type(msg)}")
        print(f"Message {i} content: {msg}")
    
    try:
        # Make sure we're passing a list of dictionaries, not custom objects
        conversation_data = [{"role": msg.role, "content": msg.content} for msg in req.conversation]
        save_conversation(conversation_data, title=req.title)
        return {"status": "ok", "message": "Conversation saved"}
    except Exception as e:
        print("Error saving conversation:", e)
        import traceback
        traceback.print_exc()  # Print the full stack trace
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-to-sql")
async def convert_to_sql_endpoint(request: QueryRequest):
    """
    Converts a natural language query to a SQL query.
    Expects a JSON payload: { "query": "your natural language query" }
    Returns a JSON object with the generated SQL query.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query is empty.")
    try:
        sql_query = convert_to_sql(request.query, SCHEMA)
        return {"sqlQuery": sql_query}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-sql")
async def run_sql_endpoint(request: QueryRequest):
    """
    Executes the given SQL query against your database.
    Expects a JSON payload: { "query": "SQL query" }
    Returns the query result as a string.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query is empty.")
    try:
        df = run_sql_query(request.query)
        # Convert the DataFrame to a string (you may modify the formatting as needed)
        result_text = df.to_string(index=False)
        return {"result": result_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Function to generate pre-signed URLs
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

@app.get("/list-files")
def list_files():
    conn = get_connection()
    query = """
    WITH p1 AS (
        SELECT DISTINCT created_at, filename 
        FROM pages
        ORDER BY created_at DESC
    )
    SELECT filename FROM p1
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Return just the list of filenames
    return df["filename"].tolist()

@app.get("/get-file")
def get_file(filename: str):
    conn = get_connection()
    
    query_pages = f"""
    WITH p1 AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY preprocessed ORDER BY created_at DESC) rn
        FROM pages
        WHERE filename = '{filename}'
    )
    SELECT * FROM p1 WHERE rn = 1
    """
    df_pages = pd.read_sql_query(query_pages, conn)
    
    query_extracted = f"""
    WITH e3 AS (
        SELECT p.filename AS base_file, e2.*,
               ROW_NUMBER() OVER (PARTITION BY e2.filename, e2.key ORDER BY created_at DESC) rn
        FROM extracted2 e2
        JOIN (SELECT filename, preprocessed FROM pages) p ON e2.filename = p.preprocessed
        WHERE p.filename = '{filename}'
    )
    SELECT * FROM e3 WHERE rn = 1
    """
    df_extracted = pd.read_sql_query(query_extracted, conn)
    
    query_info = f"""
    WITH i1 AS (
        SELECT p.filename AS base_file, i.*,
               ROW_NUMBER() OVER (PARTITION BY i.filename ORDER BY created_at DESC) rn
        FROM call_info i
        JOIN (SELECT filename, preprocessed FROM pages) p ON i.filename = p.preprocessed
        WHERE p.filename = '{filename}'
    )
    SELECT * FROM i1 WHERE rn = 1
    """
    df_info = pd.read_sql_query(query_info, conn)
    conn.close()

    # Convert each to records
    pages = df_pages.to_dict(orient="records")
    for page in pages:
        page["s3_url"] = get_s3_url(page["preprocessed"])
    extracted = df_extracted.to_dict(orient="records")
    info = df_info.to_dict(orient="records")

    return {
        "filename": filename,
        "pages": pages,
        "extracted": extracted,
        "info": info
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        df_pages, df_extracted, df_info = process_file(file_path)

        # Fix non-serializable columns
        for df in [df_pages, df_extracted, df_info]:
            for col in df.columns:
                if df[col].apply(lambda x: isinstance(x, (list, dict, set))).any():
                    df[col] = df[col].apply(lambda x: str(x) if isinstance(x, (list, dict, set)) else x)
        
        # for page in df_pages.to_dict(orient="records"):
        #     page["s3_url"] = get_s3_url(page["preprocessed"])

        pages = df_pages.to_dict(orient="records")
        for page in pages:
            page["s3_url"] = get_s3_url(page["preprocessed"])

        extracted = df_extracted.to_dict(orient="records") if df_extracted is not None else []
        info = df_info.to_dict(orient="records") if df_info is not None else []

        print(extracted[0])
        
        return JSONResponse({
            "filename": file.filename,
            "pages": pages,
            "extracted": extracted,
            "info": info,
            "message": "File processed successfully"
        })
    except Exception as e:
        # Log the exception details
        import traceback
        print("Error in /upload endpoint:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

