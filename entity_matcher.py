import os
import psycopg2
import psycopg2.extras
import json
from rapidfuzz import fuzz

# Configuration mapping document types to fields
DOCUMENT_FIELD_MAPPING = {
    "1040_p1": {
        "person": ["primary_first_name", "primary_last_name", "primary_ssn_last_4"],
        "address": ["full_address"]
    },
    "1040_sch_c": {
        "business": ["ein", "business_name", "street_address", "city_state"],
        "person": ["ssn_last_4"]
    },
    "1120S_p1": {
        "business": ["ein", "business_name", "street_address", "city_state"]
    },
    "1120_p1": {
        "business": ["ein", "business_name", "street_address", "city_state"]
    },
    "1065_p1": {
        "business": ["ein", "business_name", "street_address", "city_state"]
    },
    "1065_k1": {
        "business": ["business_ein", "business_name"],
        "person": ["shareholder_name", "ssn_last_4"]
    },
    "1120S_k1": {
        "business": ["business_ein", "business_name"],
        "person": ["shareholder_name", "ssn_last_4"]
    },
    "acord_28": {
        "business": ["named_insured_name", "named_insured_address"]
    },
    "acord_25": {
        "business": ["named_insured_name", "named_insured_address"]
    },
    "drivers_license": {
        "person": ["first_name", "last_name", "street_address", "city_state_zip", "dob"]
    },
    "passport": {
        "person": ["first_name", "last_name", "dob", "country"]
    },
    "lease_document": {
        "person": ["renter_name"]
    },
    "certificate_of_good_standing": {
        "business": ["business_name"]
    },
    "business_license": {
        "business": ["business_name"]
    },
    "1120S_bal_sheet": {
        "cross_page": True
    },
    "1065_bal_sheet": {
        "cross_page": True
    },
    "1120_bal_sheet": {
        "cross_page": True
    }
}

def normalize_value(val):
    if val:
        return val.strip().lower()
    return ""

def get_db_connection():
    """
    Establish a connection to your Supabase PostgreSQL database.
    """
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

def fetch_extracted_data(page_preprocessed, page_num):
    print(f"[DEBUG] Fetching extracted data for file: {page_preprocessed}, page: {page_num}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT key, value FROM extracted2 
        WHERE filename = %s AND page_num = %s
    """, (page_preprocessed, page_num))
    rows = cursor.fetchall()
    conn.close()
    data = {row[0]: row[1] for row in rows}
    print(f"[DEBUG] Extracted data: {data}")
    return data

def match_entity(entity_type, identifier_value, additional_info):
    print(f"[DEBUG] Matching entity for type: {entity_type} with identifier: {identifier_value}")
    conn = get_db_connection()
    cursor = conn.cursor()
    norm_identifier = normalize_value(identifier_value)
    query = """
        SELECT entity_id, additional_info FROM entities 
        WHERE entity_type = %s AND additional_info ILIKE %s
    """
    cursor.execute(query, (entity_type, f"%{norm_identifier}%"))
    result = cursor.fetchone()
    if result:
        entity_id = result[0]
        print(f"[DEBUG] Found existing entity (ID: {entity_id}) for {entity_type} with identifier: {identifier_value}")
    else:
        entity_name = additional_info.get("entity_name", "")
        info_json = json.dumps(additional_info)
        cursor.execute("""
            INSERT INTO entities (entity_type, entity_name, additional_info)
            VALUES (%s, %s, %s) RETURNING entity_id
        """, (entity_type, entity_name, info_json))
        conn.commit()
        entity_id = cursor.fetchone()[0]
        print(f"[DEBUG] Created new entity (ID: {entity_id}) for {entity_type} with identifier: {identifier_value}")
    conn.close()
    return entity_id

def create_crosswalk(page_id, entity_id):
    print(f"[DEBUG] Creating crosswalk entry for page_id: {page_id}, entity_id: {entity_id}")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO page_entity_crosswalk (page_id, entity_id)
        VALUES (%s, %s)
    """, (page_id, entity_id))
    conn.commit()
    conn.close()
    print(f"[DEBUG] Crosswalk entry created.")

def match_entities_for_page(page):
    # Normalize the document type label to lowercase for matching
    doc_type = page.get("page_label", "").strip().lower()
    print(f"[DEBUG] Processing page: {page.get('id', 'unknown id')} for document type: {doc_type}")
    
    mapping = DOCUMENT_FIELD_MAPPING.get(doc_type)
    if not mapping:
        print("[DEBUG] No mapping found for document type. Skipping.")
        return

    # Retrieve extracted data for this page
    data = fetch_extracted_data(page['preprocessed'], page['page_number'])
    associations = []

    # If cross_page flag is set, merge data from all pages in the file.
    if mapping.get("cross_page"):
        print("[DEBUG] Cross page flag detected. Merging data from all pages in file.")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT preprocessed, page_number FROM pages WHERE filename = %s
        """, (page['filename'],))
        pages_in_file = cursor.fetchall()
        conn.close()
        merged_data = {}
        for preprocessed, page_num in pages_in_file:
            page_data = fetch_extracted_data(preprocessed, page_num)
            merged_data.update(page_data)
        data = merged_data
        print(f"[DEBUG] Merged data: {data}")

    # --- Handling for each document type based on updated mapping ---
    # 1040_p1 (Personal Tax Return)
    if doc_type == "1040_p1":
        first = normalize_value(data.get("primary_first_name", ""))
        last = normalize_value(data.get("primary_last_name", ""))
        ssn = normalize_value(data.get("primary_ssn_last_4", ""))
        if ssn:
            entity_info = {"entity_name": f"{first} {last}", "ssn_last_4": ssn,
                           "address": data.get("full_address", "")}
            entity_id = match_entity("person", ssn, entity_info)
            associations.append(entity_id)

    # 1040_sch_c (Sole Proprietorship Tax Form)
    if doc_type == "1040_sch_c":
        ein = normalize_value(data.get("ein", ""))
        if ein:
            entity_info = {"entity_name": data.get("business_name", ""), "ein": ein,
                           "address": f"{data.get('street_address', '')} {data.get('city_state', '')}"}
            entity_id = match_entity("business", ein, entity_info)
            associations.append(entity_id)
        ssn = normalize_value(data.get("ssn_last_4", ""))
        if ssn:
            owner = data.get("owner_name", "")
            entity_info = {"entity_name": owner, "ssn_last_4": ssn}
            entity_id = match_entity("person", ssn, entity_info)
            associations.append(entity_id)

    # 1120S_p1, 1120_p1, 1065_p1 (Business Tax Forms)
    if doc_type in ["1120s_p1", "1120_p1", "1065_p1"]:
        ein = normalize_value(data.get("ein", ""))
        if ein:
            entity_info = {"entity_name": data.get("business_name", ""), "ein": ein,
                           "address": f"{data.get('street_address', '')} {data.get('city_state', '')}"}
            entity_id = match_entity("business", ein, entity_info)
            associations.append(entity_id)

    # 1065_k1, 1120s_k1 (K1 Forms)
    if doc_type in ["1065_k1", "1120s_k1"]:
        # Business part
        ein = normalize_value(data.get("business_ein", "")) or normalize_value(data.get("ein", ""))
        if ein:
            entity_info = {"entity_name": data.get("business_name", ""), "ein": ein}
            entity_id = match_entity("business", ein, entity_info)
            associations.append(entity_id)
        # Person part
        ssn = normalize_value(data.get("ssn_last_4", ""))
        if ssn:
            shareholder = data.get("shareholder_name", "")
            entity_info = {"entity_name": shareholder, "ssn_last_4": ssn}
            entity_id = match_entity("person", ssn, entity_info)
            associations.append(entity_id)

    # acord28, acord25 (Insurance Certificates)
    if doc_type in ["acord_28", "acord_25"]:
        business_name = data.get("named_insured_name", "")
        address = data.get("named_insured_address", "")
        if business_name:
            entity_info = {"entity_name": business_name, "address": address}
            entity_id = match_entity("business", business_name, entity_info)
            associations.append(entity_id)

    # drivers_license (Driver's License)
    if doc_type == "drivers_license":
        first = normalize_value(data.get("first_name", ""))
        last = normalize_value(data.get("last_name", ""))
        address = data.get("street_address", "") + " " + data.get("city_state_zip", "")
        dob = normalize_value(data.get("dob", ""))
        if first and last and dob:
            identifier = f"{first}{last}{dob}"
            entity_info = {"entity_name": f"{first} {last}", "dob": dob, "address": address}
            entity_id = match_entity("person", identifier, entity_info)
            associations.append(entity_id)
        else:
            print("[DEBUG] Incomplete data for drivers_license matching.")

    # passport (Passport)
    if doc_type == "passport":
        first = normalize_value(data.get("first_name", ""))
        last = normalize_value(data.get("last_name", ""))
        dob = normalize_value(data.get("dob", ""))
        country = normalize_value(data.get("country", ""))
        if first and last and dob:
            identifier = f"{first}{last}{dob}"
            entity_info = {"entity_name": f"{first} {last}", "dob": dob, "country": country}
            entity_id = match_entity("person", identifier, entity_info)
            associations.append(entity_id)
        else:
            print("[DEBUG] Incomplete data for passport matching.")

    # lease_document (Lease Document)
    if doc_type == "lease_document":
        renter = data.get("renter_name", "")
        if renter:
            entity_info = {"entity_name": renter}
            entity_id = match_entity("person", renter, entity_info)
            associations.append(entity_id)
        else:
            print("[DEBUG] No renter_name found for lease_document.")

    # certificate_of_good_standing (Certificate of Good Standing)
    if doc_type == "certificate_of_good_standing":
        business_name = data.get("business_name", "")
        if business_name:
            entity_info = {"entity_name": business_name}
            entity_id = match_entity("business", business_name, entity_info)
            associations.append(entity_id)
        else:
            print("[DEBUG] No business_name found for certificate_of_good_standing.")

    # business_license (Business License)
    if doc_type == "business_license":
        business_name = data.get("business_name", "")
        if business_name:
            entity_info = {"entity_name": business_name}
            entity_id = match_entity("business", business_name, entity_info)
            associations.append(entity_id)
        else:
            print("[DEBUG] No business_name found for business_license.")

    # For balance sheets, we assume merged data may now contain keys for a business.
    if doc_type in ["1120s_bal_sheet", "1065_bal_sheet", "1120_bal_sheet"]:
        ein = normalize_value(data.get("ein", ""))
        business_name = data.get("business_name", "")
        if ein or business_name:
            entity_info = {"entity_name": business_name, "ein": ein}
            entity_id = match_entity("business", ein or business_name, entity_info)
            associations.append(entity_id)
        else:
            print("[DEBUG] No identifying business info found in balance sheet.")

    for entity_id in associations:
        print(f"[DEBUG] Creating crosswalk for page id {page.get('id')} and entity id {entity_id}")
        create_crosswalk(page['id'], entity_id)

def match_entities_for_file(filename):
    print(f"[DEBUG] Matching entities for file: {filename}")
    conn = get_db_connection()
    cursor = conn.cursor()
    # Assuming the pages table now uses "id" as the primary key
    cursor.execute("SELECT id, * FROM pages WHERE filename = %s", (filename,))
    pages = cursor.fetchall()
    col_names = [desc[0] for desc in cursor.description]
    conn.close()

    print(f"[DEBUG] Found {len(pages)} pages for file: {filename}")
    for row in pages:
        page = dict(zip(col_names, row))
        print(f"[DEBUG] Processing page with id: {page.get('id')}, page number: {page.get('page_number')}")
        match_entities_for_page(page)   
