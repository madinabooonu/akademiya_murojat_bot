# database.py
# Ma'lumotlar bazasi bilan ishlash

import sqlite3
import logging
import json
from config.config import DATABASE_NAME

logger = logging.getLogger(__name__)


def init_database():
    """Ma'lumotlar bazasini yaratish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # 1. Complaints jadvali (Yangi va mukammal struktura)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            faculty TEXT NOT NULL,
            direction TEXT NOT NULL,
            course TEXT NOT NULL,
            education_type TEXT,
            education_lang TEXT,
            complaint_type TEXT NOT NULL,
            subject_name TEXT,
            teacher_name TEXT,
            message TEXT NOT NULL,
            source TEXT DEFAULT 'bot',
            status TEXT DEFAULT 'new',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migratsiya: Agar eski baza bo'lsa va yangi ustunlar bo'lmasa qo'shamiz
    # (Faqat bitta joyda, clean kod uchun)
    for column, definition in [('uid', 'TEXT'), ('status', "TEXT DEFAULT 'new'"), ('source', "TEXT DEFAULT 'bot'")]:
        try:
            cursor.execute(f"ALTER TABLE complaints ADD COLUMN {column} {definition}")
        except: pass

    conn.commit()
    conn.close()

    # 2. Lesson Ratings jadvali
    init_lesson_rating_table()
    
    # 3. Dinamik konfiguratsiya jadvallari
    from database_models import init_dynamic_config
    init_dynamic_config()
    
    logger.info("Ma'lumotlar bazasi to'liq ishga tushirildi")

def upsert_user(user_data):
    """Foydalanuvchi ma'lumotlarini yangilash yoki qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (telegram_id, username, first_name, last_name, language_code, last_seen)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                language_code = excluded.language_code,
                last_seen = CURRENT_TIMESTAMP
        ''', (
            user_data.get('id'),
            user_data.get('username'),
            user_data.get('first_name'),
            user_data.get('last_name'),
            user_data.get('language_code')
        ))
        conn.commit()
    except Exception as e:
        logger.error(f"Error in upsert_user: {e}")
    finally:
        conn.close()

def log_error(level, message, traceback_str=None, context=None):
    """Tizim xatolarini bazaga yozish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO error_logs (level, message, traceback, context)
            VALUES (?, ?, ?, ?)
        ''', (level, message, traceback_str, json.dumps(context) if context else None))
        conn.commit()
    except Exception as e:
        print(f"Error logging to DB: {e}")
    finally:
        conn.close()

def record_activity(user_id, action, source='bot', details=None):
    """Foydalanuvchi harakatini qayd etish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO activity_logs (telegram_id, action, source, details)
            VALUES (?, ?, ?, ?)
        ''', (user_id, action, source, json.dumps(details) if details else None))
        conn.commit()
    except Exception as e:
        logger.error(f"Error recording activity: {e}")
    finally:
        conn.close()

def init_lesson_rating_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Jadval bormi yo'qligini tekshirish
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lesson_ratings'")
    table_exists = cursor.fetchone()

    if table_exists:
        # Bor bo'lsa, strukturasini tekshiramiz
        try:
            cursor.execute("SELECT q1 FROM lesson_ratings LIMIT 1")
        except sqlite3.OperationalError:
            # q1 yo'q ekan, demak eski struktura - uni yangisiga almashtiramiz
            cursor.execute("DROP TABLE lesson_ratings")
            logger.info("Eski lesson_ratings jadvali yangisiga almashtirish uchun o'chirildi")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lesson_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uid TEXT,
            telegram_id INTEGER,
            faculty TEXT,
            direction TEXT NOT NULL,
            course TEXT NOT NULL,
            education_type TEXT,
            education_lang TEXT,
            subject_name TEXT,
            teacher_name TEXT,
            ratings TEXT,
            comments TEXT,
            q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT, 
            q6 TEXT, q7 TEXT, q8 TEXT, q9 TEXT, q10 TEXT,
            total_score REAL,
            status TEXT DEFAULT 'new',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT DEFAULT 'bot'
        )
    ''')

    # Migration: Add missing columns if they don't exist
    for column, definition in [
        ('education_type', 'TEXT'), 
        ('education_lang', 'TEXT'), 
        ('source', "TEXT DEFAULT 'bot'"),
        ('ratings', 'TEXT'),
        ('comments', 'TEXT')
    ]:
        try:
            cursor.execute(f"ALTER TABLE lesson_ratings ADD COLUMN {column} {definition}")
        except sqlite3.OperationalError:
            pass # Column already exists
    conn.commit()
    conn.close()


import random
import string

def generate_uid(length=10):
    """Tasodifiy UID yaratish (Exceldagidek)"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def save_complaint(data):
    """Murojaatni bazaga saqlash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    uid = generate_uid()

    cursor.execute('''
        INSERT INTO complaints (uid, faculty, direction, course, education_type, education_lang, complaint_type, subject_name, teacher_name, message, source, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        uid,
        data.get('faculty'),
        data.get('direction'),
        data.get('course'),
        data.get('education_type', ''),
        data.get('education_language', data.get('education_lang', '')),
        data.get('complaint_type'),
        data.get('subject_name', ''),
        data.get('teacher_name', ''),
        data.get('message'),
        data.get('source', 'bot'),
        'new'
    ))

    conn.commit()
    conn.close()
    logger.info(f"Yangi murojaat saqlandi ({data.get('source', 'bot')}): {uid}")
    return uid


def get_all_complaints(limit=None):
    """Barcha murojaatlarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    if limit and isinstance(limit, int):
        cursor.execute('SELECT * FROM complaints ORDER BY created_at ASC LIMIT ?', (limit,))
    else:
        cursor.execute('SELECT * FROM complaints ORDER BY created_at ASC')
    
    complaints = cursor.fetchall()
    conn.close()

    return complaints

def save_lesson_rating(data):
    """Dars bahosini saqlash (Hammasi bitta qatorda)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    uid = generate_uid()
    # Handle both 'answers' (bot) and 'ratings' (webapp)
    answers = data.get('answers', data.get('ratings', data))
    telegram_id = data.get('telegram_id', data.get('user_id'))
    
    # Fakultetni topish (Yo'nalish kodiga qarab)
    faculty_code = ""
    try:
        cursor.execute("SELECT faculty_code FROM directions WHERE code = ?", (data['direction'],))
        row = cursor.fetchone()
        if row:
            faculty_code = row[0]
    except: pass

    # Umumiy ballni hisoblash (Faqat raqamli javoblar uchun)
    scores = []
    # Check both integer and string keys for 1-10, plus 'q1'-'q10'
    for i in range(1, 11):
        for key in [i, str(i), f'q{i}']:
            val = answers.get(key)
            if val is not None:
                try:
                    if str(val).isdigit():
                        scores.append(float(val))
                        break # Found for this question
                except: pass
    total_score = round(sum(scores)/len(scores), 2) if scores else 0

    cursor.execute('''
        INSERT INTO lesson_ratings (
            uid, telegram_id, faculty, direction, course, 
            education_type, education_lang,
            subject_name, teacher_name, 
            ratings, comments,
            q1, q2, q3, q4, q5, q6, q7, q8, q9, q10,
            total_score, status, source
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        uid,
        data.get('telegram_id'),
        data.get('faculty', faculty_code),
        data['direction'],
        data['course'],
        data.get('education_type', ''),
        data.get('education_language', ''),
        data.get('subject_name', ''),
        data.get('teacher_name', ''),
        json.dumps(answers),
        data.get('comment', ''),
        str(answers.get('1', answers.get(1, answers.get('q1', '')))),
        str(answers.get('2', answers.get(2, answers.get('q2', '')))),
        str(answers.get('3', answers.get(3, answers.get('q3', '')))),
        str(answers.get('4', answers.get(4, answers.get('q4', '')))),
        str(answers.get('5', answers.get(5, answers.get('q5', '')))),
        str(answers.get('6', answers.get(6, answers.get('q6', '')))),
        str(answers.get('7', answers.get(7, answers.get('q7', '')))),
        str(answers.get('8', answers.get(8, answers.get('q8', '')))),
        str(answers.get('9', answers.get(9, answers.get('q9', '')))),
        str(answers.get('10', answers.get(10, answers.get('q10', '')))),
        total_score,
        'new',
        data.get('source', 'bot')
    ))

    conn.commit()
    conn.close()
    logger.info(f"Yangi dars bahosi saqlandi (1-qator): {uid}")
    return uid

def get_all_lesson_ratings(limit=None):
    """Barcha dars baholarini olish"""
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    if limit and isinstance(limit, int):
        cursor.execute('SELECT * FROM lesson_ratings ORDER BY created_at DESC LIMIT ?', (limit,))
    else:
        cursor.execute('SELECT * FROM lesson_ratings ORDER BY created_at DESC')
    
    records = cursor.fetchall()
    conn.close()

    return records


def get_statistics():
    """Statistikalarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    stats = {}

    # Umumiy soni
    cursor.execute('SELECT COUNT(*) FROM complaints')
    stats['total'] = cursor.fetchone()[0]

    # Yo'nalishlar bo'yicha
    cursor.execute('SELECT direction, COUNT(*) FROM complaints GROUP BY direction ORDER BY COUNT(*) DESC')
    stats['by_direction'] = cursor.fetchall()

    # Murojaat turlari bo'yicha
    cursor.execute('SELECT complaint_type, COUNT(*) FROM complaints GROUP BY complaint_type ORDER BY COUNT(*) DESC')
    stats['by_type'] = cursor.fetchall()

    # Kurslar bo'yicha
    cursor.execute('SELECT course, COUNT(*) FROM complaints GROUP BY course ORDER BY COUNT(*) DESC')
    stats['by_course'] = cursor.fetchall()

    # So'nggi 7 kun
    cursor.execute('''
        SELECT DATE(created_at), COUNT(*) 
        FROM complaints 
        WHERE created_at >= date("now", "-7 days") 
        GROUP BY DATE(created_at) 
        ORDER BY DATE(created_at)
    ''')
    stats['weekly'] = cursor.fetchall()

    # Bugungi
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE DATE(created_at) = DATE('now')")
    stats['today'] = cursor.fetchone()[0]

    # Haftalik
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE created_at >= date('now', '-7 days')")
    stats['week'] = cursor.fetchone()[0]

    # Oylik
    cursor.execute("SELECT COUNT(*) FROM complaints WHERE created_at >= date('now', '-30 days')")
    stats['month'] = cursor.fetchone()[0]

    # Eng faol yo'nalish
    cursor.execute("SELECT direction, COUNT(*) as c FROM complaints GROUP BY direction ORDER BY c DESC LIMIT 1")
    row = cursor.fetchone()
    stats['top_direction'] = row if row else (None, 0)

    # Hozirgi vaqt
    from datetime import datetime
    stats['now'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn.close()

    return stats

def get_admin_dashboard_data():
    """Premium Dashboard uchun barcha statlarni yig'ish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    data = {}
    
    # 1. KPI Stats
    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        data['totalUsers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = DATE('now')")
        data['todayUsers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(total_score) FROM lesson_ratings")
        data['avgScore'] = round(cursor.fetchone()[0] or 0.0, 1)
        
        cursor.execute("SELECT COUNT(*) FROM complaints")
        data['totalAppeals'] = cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Error in dashboard KPIs: {e}")
        data.update({'totalUsers': 0, 'todayUsers': 0, 'avgScore': 0.0, 'totalAppeals': 0})
    
    # 2. Weekly Activity (7 days)
    import datetime
    labels = []
    users_counts = []
    appeals_counts = []
    
    for i in range(6, -1, -1):
        dt = (datetime.datetime.now() - datetime.timedelta(days=i))
        date_str = dt.strftime('%Y-%m-%d')
        day_name = dt.strftime('%a')
        labels.append(day_name)
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE DATE(created_at) = ?", (date_str,))
        users_counts.append(cursor.fetchone()[0])
        
        cursor.execute("SELECT COUNT(*) FROM complaints WHERE DATE(created_at) = ?", (date_str,))
        appeals_counts.append(cursor.fetchone()[0])
        
    data['weekly'] = {
        'labels': labels,
        'users': users_counts,
        'appeals': appeals_counts
    }
    
    # 3. Appeal Types (Distribution)
    cursor.execute("SELECT complaint_type, COUNT(*) FROM complaints GROUP BY complaint_type ORDER BY COUNT(*) DESC")
    type_rows = cursor.fetchall()
    data['types_distribution'] = {row[0]: row[1] for row in type_rows}
    data['types'] = [row[1] for row in type_rows[:4]] + [0] * (4 - len(type_rows[:4]))
    
    # 4. Faculty Distribution (for Donut Chart)
    cursor.execute("SELECT faculty, COUNT(*) FROM complaints GROUP BY faculty ORDER BY COUNT(*) DESC LIMIT 5")
    faculty_rows = cursor.fetchall()
    data['faculty_distribution'] = {row[0] if row[0] else "Noma'lum": row[1] for row in faculty_rows}

    # 5. Hourly Activity (Last 24 hours)
    hourly_labels = []
    hourly_counts = []
    for i in range(23, -1, -1):
        target_time = (datetime.datetime.now() - datetime.timedelta(hours=i)).strftime('%Y-%m-%d %H')
        cursor.execute("SELECT COUNT(*) FROM activity_logs WHERE strftime('%Y-%m-%d %H', timestamp) = ?", (target_time,))
        hourly_counts.append(cursor.fetchone()[0])
        hourly_labels.append(f"{target_time.split(' ')[1]}:00")
    data['hourly_activity'] = {'labels': hourly_labels, 'counts': hourly_counts}

    # 6. Source Distribution
    cursor.execute("SELECT source, COUNT(*) FROM activity_logs GROUP BY source")
    source_rows = cursor.fetchall()
    data['source_distribution'] = {row[0]: row[1] for row in source_rows}
    
    # 7. Recent Appeals
    cursor.execute('''
        SELECT id, complaint_type, 'User ' || id, DATE(created_at), status 
        FROM complaints 
        ORDER BY created_at DESC LIMIT 10
    ''')
    
    recent = []
    for row in cursor.fetchall():
        recent.append({
            'id': row[0],
            'type': row[1],
            'user': row[2],
            'date': row[3],
            'status': row[4]
        })
    data['recent'] = recent
    
    conn.close()
    return data

def get_all_users():
    """Barcha foydalanuvchilarning ID larini olish (broadcast uchun)"""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT telegram_id FROM users")
        # Ensure we return valid integers (users with actual IDs)
        users = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []
