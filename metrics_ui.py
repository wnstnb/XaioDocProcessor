import streamlit as st
import sqlite3
import pandas as pd


def extraction_performance():
    conn = sqlite3.connect('documents.db')
    query = '''
    SELECT key, 
        count(*) value_count,
           AVG(label_confidence) AS avg_label_confidence, 
           SUM(CASE WHEN label_confidence IS NULL THEN 1 ELSE 0 END) AS no_label_count, 
           AVG(value_confidence) AS avg_value_confidence, 
           SUM(CASE WHEN value_confidence IS NULL THEN 1 ELSE 0 END) AS no_value_count
    FROM extracted
    WHERE not lower(key) like 'tag_%'
    GROUP BY key
    '''
    df_results = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df_results)

def page_performance():
    conn = sqlite3.connect('documents.db')
    query = '''
    with most_recent_runs as (
        select page_label, 
            preprocessed,
            page_number,
            page_score, 
            row_number() over (partition by preprocessed order by created_at desc) as rn
        from pages
    )
    select page_label, count(*) page_count, avg(page_score) agg_avg_conf
    from most_recent_runs
    where rn = 1
    group by 1
    '''
    df_results = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df_results)

def clf_performance():
    conn = sqlite3.connect('documents.db')
    query = '''    
    select clf_type, 
        count(*) page_count, 
        AVG(page_score) agg_avg_conf
    from pages
    group by 1
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

with st.expander("Field Statistics"):
    st.info('Performance by field')
    extraction_performance()

