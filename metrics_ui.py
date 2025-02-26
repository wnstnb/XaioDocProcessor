import streamlit as st
import os
import psycopg2
import pandas as pd

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

def page_performance():
    conn = get_connection()
    query = '''
    WITH most_recent_runs AS (
        SELECT page_label, 
               preprocessed,
               page_number,
               page_confidence, 
               ROW_NUMBER() OVER (PARTITION BY preprocessed ORDER BY created_at DESC) AS rn
        FROM pages
    )
    SELECT page_label, COUNT(*) AS page_count, AVG(page_confidence) AS agg_avg_conf
    FROM most_recent_runs
    WHERE rn = 1
    GROUP BY page_label
    '''
    df_results = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df_results)

def clf_performance():
    conn = get_connection()
    query = '''    
    SELECT clf_type, 
           COUNT(*) AS page_count, 
           AVG(page_confidence) AS agg_avg_conf
    FROM pages
    GROUP BY clf_type
    '''
    df_results = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df_results)

st.info('This page shows performance metrics of classification and extraction methods.')

with st.expander("Page Statistics"):
    st.info('Performance by page (document) type.')
    page_performance()

with st.expander("Classifier Performance"):
    st.info('Performance by Classifier')
    clf_performance()
