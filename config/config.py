import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8136137840:AAF7_Wf9KU2epPkGKdsijfdx6zIwNzPVfc8")
ADMIN_IDS_STR = os.environ.get("ADMIN_IDS", "2015170305,1370651372")
ADMIN_IDS = [int(i.strip()) for i in ADMIN_IDS_STR.split(",") if i.strip()]

DATABASE_NAME = os.environ.get("DATABASE_PATH", 'education_system.db')

# Mini App URL (HTTPS kerak Telegram uchun)
WEBAPP_URL = os.environ.get("WEBAPP_URL", None)

SELECTED_LANGUAGE = 'uz'

LANGS = {
    'uz': '🇺🇿 O\'zbekcha',
    'ru': '🇷🇺 Русский',
    'en': '🇬🇧 English'
}

# Fakultetlar (Kodlar)
FACULTIES = {
    'iixm': 'faculty_iixm',
    'mshf': 'faculty_mshf',
    'islomshunoslik': 'faculty_islomshunoslik',
    'magistratura': 'faculty_magistratura'
}

# Yo'nalishlar (Kodlar)
DIRECTIONS_IIXM = {
    'ki': 'dir_ki',
    'axb': 'dir_axb',
    'jixm': 'dir_jixm',
    'yurist': 'dir_yurist',
    'journal': 'dir_journal',
    'turizm': 'dir_turizm',
    'xm': 'dir_xm',
    'islom_iqtisod': 'dir_islom_iqtisod',
}

DIRECTIONS_MSHF = {
    'psixology': 'dir_psixology',
    'filology': 'dir_filology',
    'matnshunoslik': 'dir_matnshunoslik',
}

DIRECTIONS_ISLOMSHUNOSLIK = {
    'islom': 'dir_islom',
    'din': 'dir_din',
    'islom_tarix': 'dir_islom_tarix',
}

DIRECTIONS_MAGISTR = {
    "axborot_xavfsizligi": "dir_axborot_xavfsizligi",
    "islom_huquqi": "dir_islom_huquqi",
    "ijtimoiy_diniy_jarayonlar": "dir_ijtimoiy_diniy_jarayonlar",
    "iqtisodiyot": "dir_iqtisodiyot",
    "islomshunoslik": "dir_islomshunoslik_mag",
    "lingvistika": "dir_lingvistika",
    "matnshunoslik": "dir_matnshunoslik_mag",
    "psixologiya": "dir_psixologiya_mag",
    "qiyosiy_dinshunoslik": "dir_qiyosiy_dinshunoslik",
    "tarix": "dir_tarix",
    "turizm": "dir_turizm_mag",
    "tashqi_iqtisodiy_faoliyat": "dir_tashqi_iqtisodiy_faoliyat",
    "xalqaro_munosabatlar": "dir_xalqaro_munosabatlar"
}

# Hamma yo'nalishlar bitta joyda (qulaylik uchun)
ALL_DIRECTIONS = {}
ALL_DIRECTIONS.update(DIRECTIONS_IIXM)
ALL_DIRECTIONS.update(DIRECTIONS_MSHF)
ALL_DIRECTIONS.update(DIRECTIONS_ISLOMSHUNOSLIK)
ALL_DIRECTIONS.update(DIRECTIONS_MAGISTR)


# Fakultet -> Yo'nalishlar mapping (Kodlar bo'yicha)
FACULTY_DIRECTIONS = {
    'iixm': DIRECTIONS_IIXM,
    'mshf': DIRECTIONS_MSHF,
    'islomshunoslik': DIRECTIONS_ISLOMSHUNOSLIK,
    'magistratura': DIRECTIONS_MAGISTR
}

EDUCATION_TYPE = {
    'kunduzgi': 'edu_kunduzgi',
    'sirtqi': 'edu_sirtqi',
    'kechki': 'edu_kechki',
    'masofaviy': 'edu_masofaviy'
}

EDUCATION_LANG = {
    'uzbek': 'lang_uzbek',
    'rus': 'lang_rus',
}


# Kurslar
COURSES = {
    '1': 'course_1',
    '2': 'course_2',
    '3': 'course_3',
    '4': 'course_4',
    'mag1': 'course_mag1',
    'mag2': 'course_mag2'
}

# Oddiy fakultetlar uchun kurslar (1-4)
COURSES_REGULAR = {
    '1': 'course_1',
    '2': 'course_2',
    '3': 'course_3',
    '4': 'course_4'
}

# Magistratura uchun kurslar (1-2 mag)
COURSES_MAGISTR = {
    'mag1': 'course_mag1',
    'mag2': 'course_mag2'
}

# Murojaat turlari
COMPLAINT_TYPES = {
    'teacher': 'comp_teacher',
    'technical': 'comp_technical',
    'lesson': 'comp_lesson'
}

# So'rovnoma havolalari
SURVEY_LINKS = {
    'teachers': "https://docs.google.com/forms/d/e/1FAIpQLScLaVr0ymp9MyuoLj-LAryP0IDyq_lQH98Wh6iXvMOKVJpmxA/viewform?usp=dialog",
    'education': "https://docs.google.com/forms/d/e/1FAIpQLSdEXAMPLE1/viewform?usp=dialog",
    'employers': "https://docs.google.com/forms/d/e/1FAIpQLSdEXAMPLE2/viewform?usp=dialog"
}

# PDF fayllar (Mutloq yo'l bilan)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_FILES = {
    'grading': os.path.join(BASE_DIR, 'media', 'baholash_jarayoni.pdf'),
    'exam': os.path.join(BASE_DIR, 'media', 'imtihon_jarayoni.pdf'),
    'rules': os.path.join(BASE_DIR, 'media', 'tartib_qoidalari.pdf')
}