import os
import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

load_dotenv()
# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define the database schema for reference (for generating SQL queries)
SCHEMA = r"""
Table: pages(
    /* Table that stores raw information about each page in 
    a document and information on whether/how each page was classified */
    filename TEXT,          /* File name of the uploaded document */
    preprocessed TEXT,      /* File path of a page's final preprocessed image */
    page_number INTEGER,    /* Page number in the document */
    image_width REAL,       /* Width of the page image */
    image_height REAL,      /* Height of the page image */
    lines TEXT,             /* Extracted lines of text */
    words TEXT,             /* Extracted words */
    bboxes TEXT,            /* Bounding boxes of words */
    normalized_bboxes TEXT, /* Normalized bounding boxes */
    tokens TEXT,            /* Extracted tokens */
    words_for_clf TEXT,     /* Words used for classification */
    processing_time REAL,   /* Time taken for processing */
    clf_type TEXT,          /* Type of classifier used */
    page_label TEXT,        /* Predicted label for the page */
    page_confidence REAL,        /* Confidence score for the label */
    created_at DATETIME default current_timestamp /* Timestamp of creation */
)
Table: extracted2(
    /* Table stores extracted key-value pairs from the document
       and contains structured information extracted from the pages
       in the document. */
    key TEXT,           /* Designated key extracted from the page (e.g., first_name, gross_revenue, etc.) */
    value TEXT,         /* Extracted value corresponding to the key */
    filename TEXT,      /* Foreign key to pages.preprocessed */
    page_label TEXT,    /* Type of page -- correspondes to pages.page_label */
    page_confidence REAL, /* Confidence score of page_label -- correspondes to pages.page_confidence */
    page_num INTEGER,   /* Page number in the document */
    created_at DATETIME default current_timestamp /* Timestamp of creation */
)
Table: entities(
    /* Table to store unique person or business entities */
    entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT,         /* 'person' or 'business' */
    entity_name TEXT,         /* Full name or business name */
    additional_info TEXT,     /* JSON or additional metadata (e.g., normalized address, EIN, SSN) */
    created_at DATETIME default current_timestamp /* Timestamp of creation */
)
Table: page_entity_crosswalk(
    /* Table to link pages to entities (supports many-to-many relationships) */
    crosswalk_id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_id INTEGER,          /* Foreign key to pages (e.g., pages.id) */
    entity_id INTEGER,        /* Foreign key to entities (entities.entity_id) */
    created_at DATETIME default current_timestamp /* Timestamp of creation */
)
"""

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

# --- Conversation Persistence Functions ---

def save_conversation(conversation, title="Conversation"):
    """Save a conversation (list of messages) to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    conversation_json = json.dumps(conversation)
    if title == "Conversation":
        title = f"Conversation on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    cursor.execute("INSERT INTO conversations (title, conversation) VALUES (%s, %s)", (title, conversation_json))
    conn.commit()
    cursor.close()
    conn.close()

def load_conversations():
    """Load all saved conversations from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, conversation, created_at FROM conversations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    conversations = []
    for row in rows:
        conversations.append({
            "id": row[0],
            "title": row[1],
            "conversation": json.loads(row[2]),
            "created_at": row[3]
        })
    return conversations

# --- Helper Functions for SQL Conversion ---

def cleanup_sql_query(raw_query: str) -> str:
    # Remove triple backticks or any code fences
    cleaned = re.sub(r"```(?:sql)?", "", raw_query)
    cleaned = re.sub(r"```", "", cleaned)
    return cleaned.strip()

def convert_to_sql(nl_query: str, schema: str) -> str:
    examples = """
    Examples of valid SQLite queries:

    1) "How many tables are in the DB?"
    SELECT COUNT(*) AS table_count FROM sqlite_master WHERE type='table';

    2) "What are the table names?"
    SELECT name FROM sqlite_master WHERE type='table';

    3) "[complex query] Show me all extracted data that we have on a person named something like notrealname."
    SELECT e.entity_name, e.entity_type, e.additional_info, ex.key, ex.value 
    FROM entities e 
    JOIN page_entity_crosswalk pec 
        ON e.entity_id = pec.entity_id 
    JOIN pages p ON pec.page_id = p.rowid 
    JOIN extracted2 ex ON p.preprocessed = ex.filename 
        AND p.page_number = ex.page_num 
        WHERE e.entity_type = 'person' AND lower(e.entity_name) LIKE '%notrealname%';

    4) "How many pages have I run today?"
    SELECT COUNT(DISTINCT filename) AS unique_documents_today FROM pages WHERE DATE(created_at) = DATE('now');

    5) "How many unique documents have been uploaded today?"
    SELECT COUNT(DISTINCT filename) AS unique_documents_today FROM pages WHERE DATE(created_at) = DATE('now');
    """

    prompt = f"""You are an expert data scientist. You think step-by-step, considering all relationships and meanings in the data, and you thoughtfully craft your SQL queries with precision.
    You are given a PostgreSQL database with the following schema:
    {schema}

    You can only produce valid PostgreSQL SQL queries, including SELECT queries as well as CRUD operations (e.g., CREATE, UPDATE, DELETE, DROP).
    If given a [complex query] tag, then take time to reconsider the schema as joining multiple tables is likely.
    Use information_schema for metadata queries. For example:
    {examples}

    Write a SQL query to answer the following question or perform the requested operation:
    \"\"\"{nl_query}\"\"\"
    Make sure your answer is a single valid PostgreSQL SQL query. Do not include any commentary.
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-4o",
        temperature=0,
    )
    allowed_prefixes = (
        "select", 
        "with", 
        "insert", 
        "update", 
        "delete", 
        "create", 
        "drop", 
        "alter", 
        "desc", 
        "show",
        "pragma"
    )
    sql_query = response.choices[0].message.content.strip()
    print(sql_query)
    sql_query = cleanup_sql_query(sql_query)
    if not sql_query.lower().startswith(allowed_prefixes):
        raise ValueError("Generated query does not start with a valid SQL command. Aborting for safety.")
    return sql_query

def run_sql_query(query: str) -> pd.DataFrame:
    """Execute the given SQL query on the SQLite database and return the results as a DataFrame."""
    conn = get_connection()
    try:
        if query.strip().lower().startswith(("select", "with")):
            df = pd.read_sql_query(query, conn)
        else:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            df = pd.DataFrame({"result": ["Query executed successfully"]})
    except Exception as e:
        df = pd.DataFrame({"error": [str(e)]})
    finally:
        conn.close()
    return df

# --- Main Chat UI ---
st.info('This is a chat interface with the database, focused on answering questions using SQL.')
# Sidebar: Display saved conversations
st.sidebar.header("Saved Conversations")
saved_conversations = load_conversations()
conversation_titles = [conv["title"] for conv in saved_conversations]

selected_conv_title = st.sidebar.selectbox("Select a saved conversation", ["-- New Conversation --"] + conversation_titles)
if selected_conv_title != "-- New Conversation --":
    # Load the selected conversation into session_state
    for conv in saved_conversations:
        if conv["title"] == selected_conv_title:
            st.session_state["chat_history"] = conv["conversation"]
            break

# Sidebar: Button to save current conversation
if st.sidebar.button("Save Current Conversation"):
    if "chat_history" in st.session_state and st.session_state["chat_history"]:
        save_conversation(st.session_state["chat_history"])
        st.sidebar.success("Conversation saved!")
    else:
        st.sidebar.warning("No conversation to save.")

# Display chat history using Streamlit's chat message elements
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for message in st.session_state["chat_history"]:
    role = message.get("role", "assistant")
    content = message.get("message") or message.get("content") or ""
    with st.chat_message(role):
        st.markdown(content)

# Get user input using the chat input widget
user_input = st.chat_input("Enter your query about the documents...")
if user_input:
    # Append user message to chat history
    st.session_state["chat_history"].append({"role": "user", "message": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    try:
        with st.spinner("Generating SQL query..."):
            sql_query = convert_to_sql(user_input, SCHEMA)
        assistant_message = f"SQL Query: `{sql_query}`"
        st.session_state["chat_history"].append({"role": "assistant", "message": assistant_message})
        with st.chat_message("assistant"):
            st.markdown(assistant_message)

        # Check if the query is a CRUD operation and ask for confirmation
        if sql_query.lower().startswith(("insert", "update", "delete", "create", "drop", "alter")):
            st.session_state["pending_sql_query"] = sql_query
            st.session_state["awaiting_confirmation"] = True
            st.session_state["chat_history"].append({"role": "assistant", "message": "This operation will modify the database. Do you want to proceed? (yes/no)"})
            with st.chat_message("assistant"):
                st.markdown("This operation will modify the database. Do you want to proceed? (yes/no)")
        else:
            with st.spinner("Running SQL query..."):
                result_df = run_sql_query(sql_query)
            result_text = result_df.to_string(index=False)
            result_message = f"Result:\n```\n{result_text}\n```"
            st.session_state["chat_history"].append({"role": "assistant", "message": result_message})
            with st.chat_message("assistant"):
                st.markdown(result_message)
    except Exception as e:
        error_message = f"Error generating SQL query: {e}"
        st.session_state["chat_history"].append({"role": "assistant", "message": error_message})
        with st.chat_message("assistant"):
            st.markdown(error_message)

# Handle confirmation input
if "awaiting_confirmation" in st.session_state and st.session_state["awaiting_confirmation"]:
    confirmation_input = st.chat_input("Please confirm the operation (yes/no):", key="confirmation")
    if confirmation_input:
        if confirmation_input.lower() == "yes":
            with st.spinner("Running SQL query..."):
                result_df = run_sql_query(st.session_state["pending_sql_query"])
            result_text = result_df.to_string(index=False)
            result_message = f"Result:\n```\n{result_text}\n```"
            st.session_state["chat_history"].append({"role": "assistant", "message": result_message})
            with st.chat_message("assistant"):
                st.markdown(result_message)
        else:
            st.session_state["chat_history"].append({"role": "assistant", "message": "Operation cancelled by the user."})
            with st.chat_message("assistant"):
                st.markdown("Operation cancelled by the user.")
        st.session_state["awaiting_confirmation"] = False
        st.session_state["pending_sql_query"] = None
        st.rerun()  # Rerun the app to clear the confirmation input