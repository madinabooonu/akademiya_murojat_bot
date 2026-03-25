# database_models.py
# Dinamik konfiguratsiya uchun bazaviy CRUD operatsiyalari

import sqlite3
import logging
from config.config import DATABASE_NAME

logger = logging.getLogger(__name__)


# ============================================
# DEFAULT DATA (Eski config.py dan olingan)
# ============================================

DEFAULT_ADMINS = [
    (2015170305, "Admin 1", 1),
    (1370651372, "Admin 2", 1),
]

DEFAULT_LANGUAGES = [
    ('uz', "🇺🇿 O'zbekcha", 1),
    ('ru', '🇷🇺 Русский', 1),
    ('en', '🇬🇧 English', 1),
]

DEFAULT_FACULTIES = [
    ('iixm', 'faculty_iixm', 1, 1),
    ('mshf', 'faculty_mshf', 2, 1),
    ('islomshunoslik', 'faculty_islomshunoslik', 3, 1),
    ('magistratura', 'faculty_magistratura', 4, 1),
]

DEFAULT_DIRECTIONS = [
    # IIXM
    ('ki', 'iixm', 'dir_ki', 1, 1),
    ('axb', 'iixm', 'dir_axb', 2, 1),
    ('jixm', 'iixm', 'dir_jixm', 3, 1),
    ('yurist', 'iixm', 'dir_yurist', 4, 1),
    ('journal', 'iixm', 'dir_journal', 5, 1),
    ('turizm', 'iixm', 'dir_turizm', 6, 1),
    ('xm', 'iixm', 'dir_xm', 7, 1),
    ('islom_iqtisod', 'iixm', 'dir_islom_iqtisod', 8, 1),
    # MSHF
    ('psixology', 'mshf', 'dir_psixology', 1, 1),
    ('filology', 'mshf', 'dir_filology', 2, 1),
    ('matnshunoslik', 'mshf', 'dir_matnshunoslik', 3, 1),
    # Islomshunoslik
    ('islom', 'islomshunoslik', 'dir_islom', 1, 1),
    ('din', 'islomshunoslik', 'dir_din', 2, 1),
    ('islom_tarix', 'islomshunoslik', 'dir_islom_tarix', 3, 1),
    # Magistratura
    ('axborot_xavfsizligi', 'magistratura', 'dir_axborot_xavfsizligi', 1, 1),
    ('islom_huquqi', 'magistratura', 'dir_islom_huquqi', 2, 1),
    ('ijtimoiy_diniy_jarayonlar', 'magistratura', 'dir_ijtimoiy_diniy_jarayonlar', 3, 1),
    ('iqtisodiyot', 'magistratura', 'dir_iqtisodiyot', 4, 1),
    ('islomshunoslik_mag', 'magistratura', 'dir_islomshunoslik_mag', 5, 1),
    ('lingvistika', 'magistratura', 'dir_lingvistika', 6, 1),
    ('matnshunoslik_mag', 'magistratura', 'dir_matnshunoslik_mag', 7, 1),
    ('psixologiya_mag', 'magistratura', 'dir_psixologiya_mag', 8, 1),
    ('qiyosiy_dinshunoslik', 'magistratura', 'dir_qiyosiy_dinshunoslik', 9, 1),
    ('tarix', 'magistratura', 'dir_tarix', 10, 1),
    ('turizm_mag', 'magistratura', 'dir_turizm_mag', 11, 1),
    ('tashqi_iqtisodiy_faoliyat', 'magistratura', 'dir_tashqi_iqtisodiy_faoliyat', 12, 1),
    ('xalqaro_munosabatlar', 'magistratura', 'dir_xalqaro_munosabatlar', 13, 1),
]

DEFAULT_EDUCATION_TYPES = [
    ('kunduzgi', 'edu_kunduzgi', 1, 1),
    ('sirtqi', 'edu_sirtqi', 2, 1),
    ('kechki', 'edu_kechki', 3, 1),
    ('masofaviy', 'edu_masofaviy', 4, 1),
]

DEFAULT_EDUCATION_LANGUAGES = [
    ('uzbek', 'lang_uzbek', 1),
    ('rus', 'lang_rus', 1),
]

DEFAULT_COURSES = [
    ('1', 'course_1', 'regular', 1, 1),
    ('2', 'course_2', 'regular', 2, 1),
    ('3', 'course_3', 'regular', 3, 1),
    ('4', 'course_4', 'regular', 4, 1),
    ('mag1', 'course_mag1', 'magistr', 5, 1),
    ('mag2', 'course_mag2', 'magistr', 6, 1),
]

DEFAULT_COMPLAINT_TYPES = [
    ('teacher', 'comp_teacher', 1, 1, 1),
    ('technical', 'comp_technical', 0, 0, 1),
    ('lesson', 'comp_lesson', 0, 0, 1),
]

DEFAULT_RATING_QUESTIONS = [
    (1, 'rating_q1', 'scale', 1),
    (2, 'rating_q2', 'scale', 1),
    (3, 'rating_q3', 'scale', 1),
    (4, 'rating_q4', 'scale', 1),
    (5, 'rating_q5', 'scale', 1),
    (6, 'rating_q6', 'yes_no', 1),
]

DEFAULT_SURVEY_LINKS = [
    ('teachers', 'https://docs.google.com/forms/d/e/1FAIpQLScLaVr0ymp9MyuoLj-LAryP0IDyq_lQH98Wh6iXvMOKVJpmxA/viewform?usp=dialog', 'survey_teachers_title', 1),
    ('education', 'https://docs.google.com/forms/d/e/1FAIpQLSdEXAMPLE1/viewform?usp=dialog', 'survey_edu_title', 1),
    ('employers', 'https://docs.google.com/forms/d/e/1FAIpQLSdEXAMPLE2/viewform?usp=dialog', 'survey_emp_title', 1),
]


# ============================================
# TABLE CREATION
# ============================================

def init_dynamic_config():
    """Dinamik konfiguratsiya va monitoring jadvallarini yaratish"""
    create_dynamic_tables()
    seed_default_data()
    seed_translations()

def create_dynamic_tables():
    """Dinamik konfiguratsiya jadvallarini yaratish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
            name TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Languages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Translations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_code TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            UNIQUE(language_code, key)
        )
    ''')

    # Faculties table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faculties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            translation_key TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Directions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS directions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            faculty_code TEXT NOT NULL,
            translation_key TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Education types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            translation_key TEXT NOT NULL,
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Education languages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education_languages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            translation_key TEXT NOT NULL,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            translation_key TEXT NOT NULL,
            course_type TEXT DEFAULT 'regular',
            sort_order INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Complaint types table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS complaint_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            translation_key TEXT NOT NULL,
            requires_subject INTEGER DEFAULT 0,
            requires_teacher INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Rating questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rating_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_number INTEGER UNIQUE NOT NULL,
            translation_key TEXT NOT NULL,
            answer_type TEXT DEFAULT 'scale',
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Survey links table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            translation_key TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Monitoring: Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language_code TEXT,
            is_active INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Monitoring: Error logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            level TEXT,
            message TEXT,
            traceback TEXT,
            context TEXT
        )
    ''')
    
    # Monitoring: Activity logs table (New)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER,
            action TEXT NOT NULL,
            source TEXT DEFAULT 'bot',
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Dinamik konfiguratsiya jadvallari yaratildi")


def seed_default_data():
    """Default ma'lumotlarni bazaga yuklash (agar mavjud bo'lmasa)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Admins
    for telegram_id, name, is_active in DEFAULT_ADMINS:
        cursor.execute('''
            INSERT OR IGNORE INTO admins (telegram_id, name, is_active)
            VALUES (?, ?, ?)
        ''', (telegram_id, name, is_active))

    # Languages
    for code, name, is_active in DEFAULT_LANGUAGES:
        cursor.execute('''
            INSERT OR IGNORE INTO languages (code, name, is_active)
            VALUES (?, ?, ?)
        ''', (code, name, is_active))

    # Faculties
    for code, translation_key, sort_order, is_active in DEFAULT_FACULTIES:
        cursor.execute('''
            INSERT OR IGNORE INTO faculties (code, translation_key, sort_order, is_active)
            VALUES (?, ?, ?, ?)
        ''', (code, translation_key, sort_order, is_active))

    # Directions
    for code, faculty_code, translation_key, sort_order, is_active in DEFAULT_DIRECTIONS:
        cursor.execute('''
            INSERT OR IGNORE INTO directions (code, faculty_code, translation_key, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (code, faculty_code, translation_key, sort_order, is_active))

    # Education types
    for code, translation_key, sort_order, is_active in DEFAULT_EDUCATION_TYPES:
        cursor.execute('''
            INSERT OR IGNORE INTO education_types (code, translation_key, sort_order, is_active)
            VALUES (?, ?, ?, ?)
        ''', (code, translation_key, sort_order, is_active))

    # Education languages
    for code, translation_key, is_active in DEFAULT_EDUCATION_LANGUAGES:
        cursor.execute('''
            INSERT OR IGNORE INTO education_languages (code, translation_key, is_active)
            VALUES (?, ?, ?)
        ''', (code, translation_key, is_active))

    # Courses
    for code, translation_key, course_type, sort_order, is_active in DEFAULT_COURSES:
        cursor.execute('''
            INSERT OR IGNORE INTO courses (code, translation_key, course_type, sort_order, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (code, translation_key, course_type, sort_order, is_active))

    # Complaint types
    for code, translation_key, requires_subject, requires_teacher, is_active in DEFAULT_COMPLAINT_TYPES:
        cursor.execute('''
            INSERT OR IGNORE INTO complaint_types (code, translation_key, requires_subject, requires_teacher, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (code, translation_key, requires_subject, requires_teacher, is_active))

    # Rating questions (Cleanup duplicates before seeding)
    try:
        cursor.execute("DELETE FROM rating_questions WHERE rowid NOT IN (SELECT mn FROM (SELECT MIN(rowid) as mn FROM rating_questions GROUP BY question_number))")
    except: pass

    for question_number, translation_key, answer_type, is_active in DEFAULT_RATING_QUESTIONS:
        cursor.execute('''
            INSERT OR IGNORE INTO rating_questions (question_number, translation_key, answer_type, is_active)
            VALUES (?, ?, ?, ?)
        ''', (question_number, translation_key, answer_type, is_active))

    # Survey links
    for code, url, translation_key, is_active in DEFAULT_SURVEY_LINKS:
        cursor.execute('''
            INSERT OR IGNORE INTO survey_links (code, url, translation_key, is_active)
            VALUES (?, ?, ?, ?)
        ''', (code, url, translation_key, is_active))

    conn.commit()
    conn.close()
    logger.info("Default ma'lumotlar bazaga yuklandi")


def seed_translations():
    """Tarjimalarni bazaga yuklash (locales.py dan)"""
    from config.locales import LOCALES
    
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    for lang_code, translations in LOCALES.items():
        for key, value in translations.items():
            cursor.execute('''
                INSERT OR IGNORE INTO translations (language_code, key, value)
                VALUES (?, ?, ?)
            ''', (lang_code, key, value))

    conn.commit()
    conn.close()
    logger.info("Tarjimalar bazaga yuklandi")


# ============================================
# CRUD: ADMINS
# ============================================

def get_all_admins():
    """Barcha adminlarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT telegram_id, name, is_active FROM admins ORDER BY id')
    admins = cursor.fetchall()
    conn.close()
    return admins


def get_admin_ids():
    """Faqat faol admin ID larni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT telegram_id FROM admins WHERE is_active = 1')
    admin_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return admin_ids


def trigger_cache_reload():
    """Keshni yangilashni bildirish (utils orqali)"""
    try:
        import utils.utils as utils
        utils.load_translations_to_cache()
    except Exception:
        pass


def add_admin(telegram_id, name=""):
    """Yangi admin qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO admins (telegram_id, name, is_active)
            VALUES (?, ?, 1)
        ''', (telegram_id, name))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    if result: trigger_cache_reload()
    return result


def remove_admin(telegram_id):
    """Adminni o'chirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM admins WHERE telegram_id = ?', (telegram_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0: trigger_cache_reload()
    return affected > 0


def toggle_admin_status(telegram_id):
    """Admin statusini o'zgartirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE admins SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END
        WHERE telegram_id = ?
    ''', (telegram_id,))
    conn.commit()
    conn.close()
    trigger_cache_reload()


# ============================================
# CRUD: LANGUAGES
# ============================================

def get_all_languages():
    """Barcha tillarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, name, is_active FROM languages ORDER BY id')
    languages = cursor.fetchall()
    conn.close()
    return languages


def get_active_languages():
    """Faqat faol tillarni olish (dict format)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, name FROM languages WHERE is_active = 1')
    languages = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return languages


# ============================================
# CRUD: FACULTIES
# ============================================

def get_all_faculties():
    """Barcha fakultetlarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, translation_key, sort_order, is_active FROM faculties WHERE is_active = 1 ORDER BY sort_order')
    faculties = cursor.fetchall()
    conn.close()
    return faculties


def get_faculties_dict():
    """Fakultetlarni dict formatda olish (eski config.py format)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, translation_key FROM faculties WHERE is_active = 1 ORDER BY sort_order')
    faculties = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return faculties


def add_faculty(code, translation_key, sort_order=0):
    """Yangi fakultet qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO faculties (code, translation_key, sort_order, is_active)
            VALUES (?, ?, ?, 1)
        ''', (code, translation_key, sort_order))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    if result: trigger_cache_reload()
    return result


def update_faculty(code, translation_key=None, sort_order=None, is_active=None):
    """Fakultetni yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if translation_key is not None:
        updates.append('translation_key = ?')
        values.append(translation_key)
    if sort_order is not None:
        updates.append('sort_order = ?')
        values.append(sort_order)
    if is_active is not None:
        updates.append('is_active = ?')
        values.append(is_active)
    
    if updates:
        values.append(code)
        cursor.execute(f'UPDATE faculties SET {", ".join(updates)} WHERE code = ?', values)
        conn.commit()
        trigger_cache_reload()
    
    conn.close()


def delete_faculty(code):
    """Fakultetni o'chirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM faculties WHERE code = ?', (code,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0: trigger_cache_reload()
    return affected > 0


# ============================================
# CRUD: DIRECTIONS
# ============================================

def get_directions_by_faculty(faculty_code):
    """Fakultetga tegishli yo'nalishlarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT code, translation_key FROM directions 
        WHERE faculty_code = ? AND is_active = 1 
        ORDER BY sort_order
    ''', (faculty_code,))
    directions = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return directions


def get_all_directions_dict():
    """Barcha yo'nalishlarni dict formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, translation_key FROM directions WHERE is_active = 1')
    directions = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return directions


def get_all_directions_with_faculty():
    """Barcha yo'nalishlarni faculty_code bilan birga list formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT code, faculty_code, translation_key FROM directions
        WHERE is_active = 1
        ORDER BY faculty_code, sort_order
    ''')
    directions = [
        {'code': row[0], 'faculty_code': row[1], 'translation_key': row[2]}
        for row in cursor.fetchall()
    ]
    conn.close()
    return directions


def add_direction(code, faculty_code, translation_key, sort_order=0):
    """Yangi yo'nalish qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO directions (code, faculty_code, translation_key, sort_order, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (code, faculty_code, translation_key, sort_order))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    if result: trigger_cache_reload()
    return result


def update_direction(code, faculty_code=None, translation_key=None, sort_order=None, is_active=None):
    """Yo'nalishni yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if faculty_code is not None:
        updates.append('faculty_code = ?')
        values.append(faculty_code)
    if translation_key is not None:
        updates.append('translation_key = ?')
        values.append(translation_key)
    if sort_order is not None:
        updates.append('sort_order = ?')
        values.append(sort_order)
    if is_active is not None:
        updates.append('is_active = ?')
        values.append(is_active)
    
    if updates:
        values.append(code)
        cursor.execute(f'UPDATE directions SET {", ".join(updates)} WHERE code = ?', values)
        conn.commit()
        trigger_cache_reload()
    
    conn.close()


def delete_direction(code):
    """Yo'nalishni o'chirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM directions WHERE code = ?', (code,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0: trigger_cache_reload()
    return affected > 0


# ============================================
# CRUD: EDUCATION TYPES
# ============================================

def get_education_types_dict():
    """Ta'lim turlarini dict formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, translation_key FROM education_types WHERE is_active = 1 ORDER BY sort_order')
    edu_types = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return edu_types


# ============================================
# CRUD: EDUCATION LANGUAGES
# ============================================

def get_education_languages_dict():
    """Ta'lim tillarini dict formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, translation_key FROM education_languages WHERE is_active = 1')
    edu_langs = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return edu_langs


# ============================================
# CRUD: COURSES
# ============================================

def get_courses_dict(course_type=None):
    """Kurslarni dict formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    if course_type:
        cursor.execute('''
            SELECT code, translation_key FROM courses 
            WHERE is_active = 1 AND course_type = ? 
            ORDER BY sort_order
        ''', (course_type,))
    else:
        cursor.execute('SELECT code, translation_key FROM courses WHERE is_active = 1 ORDER BY sort_order')
    
    courses = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return courses


def get_regular_courses():
    """Oddiy kurslarni olish (1-4)"""
    return get_courses_dict('regular')


def get_magistr_courses():
    """Magistratura kurslarini olish"""
    return get_courses_dict('magistr')


# ============================================
# CRUD: COMPLAINT TYPES
# ============================================

def get_complaint_types_dict():
    """Murojaat turlarini dict formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, translation_key FROM complaint_types WHERE is_active = 1')
    complaint_types = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return complaint_types


def get_complaint_type_info(code):
    """Murojaat turi haqida to'liq ma'lumot"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT code, translation_key, requires_subject, requires_teacher 
        FROM complaint_types WHERE code = ?
    ''', (code,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            'code': result[0],
            'translation_key': result[1],
            'requires_subject': bool(result[2]),
            'requires_teacher': bool(result[3])
        }
    return None


# ============================================
# CRUD: RATING QUESTIONS
# ============================================

def get_rating_questions():
    """Baholash savollarini olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question_number, translation_key, answer_type 
        FROM rating_questions 
        WHERE is_active = 1 
        ORDER BY question_number
    ''')
    questions = cursor.fetchall()
    conn.close()
    return questions


def add_rating_question(question_number, translation_key, answer_type='scale'):
    """Yangi savol qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO rating_questions (question_number, translation_key, answer_type, is_active)
        VALUES (?, ?, ?, 1)
    ''', (question_number, translation_key, answer_type))
    conn.commit()
    conn.close()
    trigger_cache_reload()


def update_rating_question(question_number, translation_key=None, answer_type=None, is_active=None):
    """Savolni yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if translation_key is not None:
        updates.append('translation_key = ?')
        values.append(translation_key)
    if answer_type is not None:
        updates.append('answer_type = ?')
        values.append(answer_type)
    if is_active is not None:
        updates.append('is_active = ?')
        values.append(is_active)
    
    if updates:
        values.append(question_number)
        cursor.execute(f'UPDATE rating_questions SET {", ".join(updates)} WHERE question_number = ?', values)
        conn.commit()
        trigger_cache_reload()
    
    conn.close()


def delete_rating_question(question_number):
    """Savolni o'chirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rating_questions WHERE question_number = ?', (question_number,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0: trigger_cache_reload()
    return affected > 0


# ============================================
# CRUD: SURVEY LINKS
# ============================================

def get_survey_links_dict():
    """So'rovnoma havolalarini dict formatda olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, url FROM survey_links WHERE is_active = 1')
    links = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return links


def update_survey_link(code, url):
    """So'rovnoma havolasini yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE survey_links SET url = ? WHERE code = ?', (url, code))
    conn.commit()
    conn.close()
    trigger_cache_reload()


def add_survey_link(code, url, translation_key=None):
    """Yangi so'rovnoma qo'shish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO survey_links (code, url, translation_key, is_active)
            VALUES (?, ?, ?, 1)
        ''', (code, url, translation_key))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    if result: trigger_cache_reload()
    return result


def delete_survey_link(code):
    """So'rovnomani o'chirish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM survey_links WHERE code = ?', (code,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0: trigger_cache_reload()
    return affected > 0


def get_all_survey_links():
    """Barcha so'rovnomalarni ro'yxat ko'rinishida olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT code, url, translation_key, is_active FROM survey_links')
    surveys = cursor.fetchall()
    conn.close()
    return surveys


# ============================================
# CRUD: TRANSLATIONS
# ============================================

def get_translation(key, lang_code='uz'):
    """Bitta tarjimani olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT value FROM translations 
        WHERE language_code = ? AND key = ?
    ''', (lang_code, key))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else key


def get_all_translations(lang_code):
    """Bir tildagi barcha tarjimalarni olish"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT key, value FROM translations 
        WHERE language_code = ?
    ''', (lang_code,))
    translations = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return translations


def update_translation(key, lang_code, value):
    """Tarjimani yangilash va keshni yangilash"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO translations (language_code, key, value)
        VALUES (?, ?, ?)
    ''', (lang_code, key, value))
    conn.commit()
    conn.commit()
    conn.close()
    trigger_cache_reload()


def add_translation(key, lang_code, value):
    """Yangi tarjima qo'shish"""
    return update_translation(key, lang_code, value)


# ============================================
# INITIALIZATION
# ============================================

def init_dynamic_config():
    """Dinamik konfiguratsiyani to'liq ishga tushirish"""
    create_dynamic_tables()
    seed_default_data()
    seed_translations()
    logger.info("Dinamik konfiguratsiya muvaffaqiyatli ishga tushirildi")
