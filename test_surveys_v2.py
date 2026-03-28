import sqlite3
import os

db_files = ['education_system.db', 'akademiya.db', 'akademiya_murojat_bot.db']

for db_file in db_files:
    if not os.path.exists(db_file):
        print(f"--- {db_file} NOT FOUND ---")
        continue
    
    print(f"--- Checking {db_file} ---")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Tables: {tables}")
        
        if 'survey_links' in tables:
            cursor.execute("SELECT * FROM survey_links;")
            rows = cursor.fetchall()
            print("Survey Links Content:")
            for r in rows:
                print(r)
        
        if 'translations' in tables:
            cursor.execute("SELECT * FROM translations WHERE key LIKE 'survey_%';")
            rows = cursor.fetchall()
            print("Related Translations Count:", len(rows))
            for r in rows[:5]:
                print(r)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    print("-" * 30)
