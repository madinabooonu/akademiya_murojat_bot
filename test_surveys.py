import sqlite3
import json

conn = sqlite3.connect('akademiya.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM survey_links;")
rows = cursor.fetchall()
print("Survey Links Table:")
for r in rows:
    print(r)

cursor.execute("SELECT * FROM translations WHERE key LIKE 'survey_%';")
rows = cursor.fetchall()
print("\nRelated Translations:")
for r in rows:
    print(r)
conn.close()
