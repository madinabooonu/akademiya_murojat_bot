import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from database import init_database, get_all_complaints, get_statistics, save_complaint, save_lesson_rating
import sqlite3
from config.config import DATABASE_NAME

def verify():
    print("--- Initializing Database ---")
    init_database()
    
    # 1. Test Bot Complaint
    print("\n--- Testing Bot Complaint ---")
    bot_data = {
        'faculty': 'iixm',
        'direction': 'ki',
        'course': '1',
        'complaint_type': 'technical',
        'message': 'Test bot complaint',
        'source': 'bot'
    }
    uid_bot = save_complaint(bot_data)
    print(f"Bot Complaint saved with UID: {uid_bot}")
    
    # 2. Test Webapp Complaint
    print("\n--- Testing Webapp Complaint ---")
    web_data = {
        'faculty': 'mshf',
        'direction': 'psixology',
        'course': '2',
        'complaint_type': 'teacher',
        'subject_name': 'Math',
        'teacher_name': 'John Doe',
        'message': 'Test webapp complaint',
        'source': 'webapp'
    }
    uid_web = save_complaint(web_data)
    print(f"Webapp Complaint saved with UID: {uid_web}")
    
    # 3. Test Rating
    print("\n--- Testing Rating ---")
    rating_data = {
        'direction': 'ki',
        'course': '1',
        'ratings': {1: 5, 2: 4, 6: 1},
        'source': 'webapp'
    }
    uid_rating = save_lesson_rating(rating_data)
    print(f"Rating saved with UID: {uid_rating}")
    
    # Verify in DB
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    print("\n--- Final Database Verification ---")
    cursor.execute("SELECT uid, source, message FROM complaints ORDER BY created_at DESC LIMIT 2")
    rows = cursor.fetchall()
    for row in rows:
        print(f"Complaint: UID={row[0]}, Source={row[1]}, Msg={row[2]}")
        if not row[0]:
            print("ERROR: Missing UID!")
            
    cursor.execute("SELECT uid, source, ratings FROM lesson_ratings ORDER BY created_at DESC LIMIT 1")
    row = cursor.fetchone()
    if row:
        print(f"Rating: UID={row[0]}, Source={row[1]}, Ratings={row[2]}")
        if not row[0]:
            print("ERROR: Missing UID!")
            
    conn.close()

if __name__ == "__main__":
    verify()
