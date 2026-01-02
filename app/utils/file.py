# app/utils/file.py

# read SQL file
def open_sql_file(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_template = f.read()
        #print(f"✅ SQL file {file_path} read successfully.")
        return sql_template
    except Exception as e:
        print(f"❌ An error occurred while reading SQL file {file_path}: {e}")
        return ""
