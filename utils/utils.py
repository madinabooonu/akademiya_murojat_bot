# utils.py
# Yordamchi funksiyalar - TO'LIQ KESHLANGAN (Maksimal tezlik)

from telegram import KeyboardButton, ReplyKeyboardMarkup
import logging

logger = logging.getLogger(__name__)

# ============================================
# GLOBAL KESHLAR (Xotirada saqlanadi)
# ============================================
TRANSLATION_CACHE = {}
ADMIN_CACHE = set()
FACULTIES_CACHE = {}
DIRECTIONS_CACHE = {} # {faculty_code: {dir_code: trans_key}}
ALL_DIRECTIONS_CACHE = {} # {dir_code: trans_key}
EDU_TYPES_CACHE = {}
EDU_LANGS_CACHE = {}
COURSES_CACHE = {}
COMPLAINT_TYPES_CACHE = {}
SURVEY_LINKS_CACHE = {}
LANGS_CACHE = {}

# ============================================
# DATA LOOKUP (FAQAT KESHDAN)
# ============================================

def get_faculties():
    return FACULTIES_CACHE

def get_all_directions():
    return ALL_DIRECTIONS_CACHE

def get_directions_by_faculty(faculty_code: str):
    return DIRECTIONS_CACHE.get(faculty_code, {})

def get_education_types():
    return EDU_TYPES_CACHE

def get_education_languages():
    return EDU_LANGS_CACHE

def get_courses(course_type=None):
    if not course_type:
        return COURSES_CACHE
    return {k: v for k, v in COURSES_CACHE.items() if (course_type == 'magistr' and 'mag' in k) or (course_type == 'regular' and 'mag' not in k)}

def get_complaint_types():
    return COMPLAINT_TYPES_CACHE

def get_survey_links():
    return SURVEY_LINKS_CACHE

def get_active_languages():
    return LANGS_CACHE

def is_admin(user_id):
    return user_id in ADMIN_CACHE

def lang(context) -> str:
    return context.user_data.get('language', 'uz')

def get_main_menu_buttons():
    """Asosiy menyu tugmalari ( FAQAT KESHDAN)"""
    keys = ['btn_complaint', 'btn_rules', 'btn_survey', 'btn_lesson_rating', 'btn_admin', 'btn_lang', 'btn_back_main']
    buttons = set()
    
    for lang_code in TRANSLATION_CACHE:
        lang_cache = TRANSLATION_CACHE.get(lang_code, TRANSLATION_CACHE.get('uz', {}))
        for key in keys:
            if key in lang_cache:
                buttons.add(lang_cache[key])
    
    return list(buttons)

# Qolgan yordamchi funksiyalar (Lokalizatsiya uchun)
def get_faculty_name(code, context):
    trans_key = FACULTIES_CACHE.get(code)
    return get_text(trans_key, context) if trans_key else "Noma'lum"

def get_direction_name(code, context):
    trans_key = ALL_DIRECTIONS_CACHE.get(code)
    return get_text(trans_key, context) if trans_key else "Noma'lum"

def get_course_name(code, context):
    trans_key = COURSES_CACHE.get(code)
    return get_text(trans_key, context) if trans_key else "Noma'lum"

def get_complaint_type_name(code, context):
    trans_key = COMPLAINT_TYPES_CACHE.get(code)
    return get_text(trans_key, context) if trans_key else "Noma'lum"

# ============================================
# REVERSE LOOKUP (Matndan kodga)
# ============================================

def get_faculty_code(text, context):
    return get_code_by_text(text, FACULTIES_CACHE, context)

def get_direction_code(text, context):
    return get_code_by_text(text, ALL_DIRECTIONS_CACHE, context)

def get_education_type_code(text, context):
    return get_code_by_text(text, EDU_TYPES_CACHE, context)

def get_education_lang_code(text, context):
    return get_code_by_text(text, EDU_LANGS_CACHE, context)

def get_course_code(text, context):
    return get_code_by_text(text, COURSES_CACHE, context)

def get_complaint_type_code(text, context):
    return get_code_by_text(text, COMPLAINT_TYPES_CACHE, context)

# ============================================
# LOKALIZATSIYA FUNKSIYALARI
# ============================================

def get_text(key: str, context) -> str:
    """Tarjimani keshdan olish"""
    lang_code = context.user_data.get('language', 'uz')
    lang_cache = TRANSLATION_CACHE.get(lang_code, TRANSLATION_CACHE.get('uz', {}))
    
    if key in lang_cache:
        return lang_cache[key]
    
    # Fallback locales.py
    from config.locales import LOCALES
    return LOCALES.get(lang_code, LOCALES['uz']).get(key, key)

def get_code_by_text(text: str, code_map: dict, context) -> str:
    """Matndan kodni topish (Kesh orqali)"""
    for code, trans_key in code_map.items():
        if text == get_text(trans_key, context):
            return code
    return None

# ============================================
# KESHNI YUKLASH (OXIRIDA)
# ============================================

def load_translations_to_cache():
    """
    Barcha dinamik ma'lumotlarni xotiraga yuklaydi (Tezlik uchun).
    Bot ishga tushganda bir marta chaqiriladi.
    """
    global TRANSLATION_CACHE, ADMIN_CACHE, FACULTIES_CACHE, DIRECTIONS_CACHE, \
           ALL_DIRECTIONS_CACHE, EDU_TYPES_CACHE, EDU_LANGS_CACHE, COURSES_CACHE, \
           COMPLAINT_TYPES_CACHE, SURVEY_LINKS_CACHE, LANGS_CACHE
           
    try:
        from database_models import (
            get_active_languages, get_all_translations, get_admin_ids,
            get_faculties_dict, get_all_directions_dict, get_courses_dict,
            get_education_types_dict, get_education_languages_dict,
            get_complaint_types_dict, get_survey_links_dict
        )
        
        # 1. Adminlar
        ADMIN_CACHE = set(get_admin_ids())
        
        # 2. Tarjimalar
        LANGS_CACHE = get_active_languages()
        for lang_code in LANGS_CACHE.keys():
            TRANSLATION_CACHE[lang_code] = get_all_translations(lang_code)
        
        # Fallback locales.py
        from config.locales import LOCALES
        for lang_code, translations in LOCALES.items():
            if lang_code not in TRANSLATION_CACHE:
                TRANSLATION_CACHE[lang_code] = translations.copy()
            else:
                for k, v in translations.items():
                    if k not in TRANSLATION_CACHE[lang_code]:
                        TRANSLATION_CACHE[lang_code][k] = v
        
        # 3. Fakultetlar
        FACULTIES_CACHE = get_faculties_dict()
        
        # 4. Yo'nalishlar (Strukturaviy)
        ALL_DIRECTIONS_CACHE = get_all_directions_dict()
        
        # Yo'nalishlarni fakultetlar bo'yicha guruhlash
        from database_models import get_directions_by_faculty
        for f_code in FACULTIES_CACHE.keys():
            DIRECTIONS_CACHE[f_code] = get_directions_by_faculty(f_code)
            
        # 5. Boshqa sozlamalar
        EDU_TYPES_CACHE = get_education_types_dict()
        EDU_LANGS_CACHE = get_education_languages_dict()
        COURSES_CACHE = get_courses_dict()
        COMPLAINT_TYPES_CACHE = get_complaint_types_dict()
        SURVEY_LINKS_CACHE = get_survey_links_dict()

        logger.info("Barcha ma'lumotlar keshga yuklandi.")
    except Exception as e:
        logger.error(f"Keshni yuklashda xatolik: {e}")