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
    WITH page_data AS (
        SELECT 
            annotated_image_path,
            page_label, 
            count(key) total_keys,
            sum(case when label_confidence != 0 then 1 else 0 end) as found_keys,
            avg(label_confidence) as avg_conf
        from extracted
        left join pages on pages.filename = extracted.filename and pages.page_number = extracted.page_num
        group by 1
    )
    
    select page_label, 
        count(*) page_count, 
        round(AVG(found_keys / total_keys) * 100, 2) avg_labels_found, 
        AVG(avg_conf) agg_avg_conf 
    from page_data
    group by 1
    '''
    df_results = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df_results)

def clf_performance():
    conn = sqlite3.connect('documents.db')
    query = '''
    WITH page_data AS (
        SELECT 
            page_label, 
            annotated_image_path,
            count(key) total_keys,
            sum(case when label_confidence != 0 then 1 else 0 end) as found_keys,
            avg(label_confidence) as avg_conf
        from extracted
        left join pages on pages.preprocessed = extracted.annotated_image_path
        group by 1
    )
    
    select page_label, 
        count(*) page_count, 
        round(AVG(found_keys / total_keys) * 100, 2) avg_labels_found, 
        AVG(avg_conf) agg_avg_conf 
    from page_data
    group by 1
    '''
    df_results = pd.read_sql_query(query, conn)
    conn.close()
    st.dataframe(df_results)

with st.expander("Page Performance"):
    page_performance()

with st.expander("Extraction Performance"):
    extraction_performance()

