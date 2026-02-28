# keyboards.py
# ReplyKeyboard klaviaturalari - DINAMIK (bazadan o'qiydi)

from telegram import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
import utils.utils as utils


def get_language_keyboard():
    """Til tanlash klaviaturasi (BAZADAN, 2 tugma bir qator)"""
    languages = list(utils.get_active_languages().values())
    keyboard = []
    for i in range(0, len(languages), 2):
        row = [KeyboardButton(languages[i])]
        if i + 1 < len(languages):
            row.append(KeyboardButton(languages[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_main_menu_keyboard(context, webapp_url=None):
    """Asosiy menyu klaviaturasi (Dinamik, 2 tugma bir qator)"""
    from config.config import WEBAPP_URL as DEFAULT_URL
    url = webapp_url or DEFAULT_URL
    
    buttons = [
        utils.get_text('btn_complaint', context),
        utils.get_text('btn_rules', context),
        utils.get_text('btn_survey', context),
        utils.get_text('btn_lesson_rating', context),
        utils.get_text('btn_admin', context),
        utils.get_text('btn_lang', context)
    ]

    if url:
        buttons.insert(0, "🌐 Mini App")

    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_directions_keyboard(context):
    """Yo'nalishlar klaviaturasi (BAZADAN, 2 tugma bir qator)"""
    all_directions = list(utils.get_all_directions().values())
    keyboard = []
    for i in range(0, len(all_directions), 2):
        row = [KeyboardButton(utils.get_text(all_directions[i], context))]
        if i + 1 < len(all_directions):
            row.append(KeyboardButton(utils.get_text(all_directions[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_dynamic_keyboard(items: dict, context, prefix="dir_"):
    """Dinamik keyboard yaratish (2 tugma bir qator)"""
    values = list(items.values())
    keyboard = []
    for i in range(0, len(values), 2):
        row = [KeyboardButton(utils.get_text(values[i], context))]
        if i + 1 < len(values):
            row.append(KeyboardButton(utils.get_text(values[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_faculties_keyboard(context):
    """Fakultetlar klaviaturasi (2 tugma bir qator)"""
    faculties = list(utils.get_faculties().values())
    keyboard = []
    for i in range(0, len(faculties), 2):
        row = [KeyboardButton(utils.get_text(faculties[i], context))]
        if i + 1 < len(faculties):
            row.append(KeyboardButton(utils.get_text(faculties[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_education_type_keyboard(context):
    """Ta'lim turi klaviaturasi (2 tugma bir qator)"""
    edu_types = list(utils.get_education_types().values())
    keyboard = []
    for i in range(0, len(edu_types), 2):
        row = [KeyboardButton(utils.get_text(edu_types[i], context))]
        if i + 1 < len(edu_types):
            row.append(KeyboardButton(utils.get_text(edu_types[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_education_lang_keyboard(context):
    """Ta'lim tili klaviaturasi (2 tugma bir qator)"""
    edu_langs = list(utils.get_education_languages().values())
    keyboard = []
    for i in range(0, len(edu_langs), 2):
        row = [KeyboardButton(utils.get_text(edu_langs[i], context))]
        if i + 1 < len(edu_langs):
            row.append(KeyboardButton(utils.get_text(edu_langs[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_courses_keyboard(context):
    """Kurslar klaviaturasi - fakultetga qarab (2 tugma bir qator)"""
    faculty = context.user_data.get('faculty', '')
    if faculty == 'magistratura':
        courses = list(utils.get_courses('magistr').values())
    else:
        courses = list(utils.get_courses('regular').values())
    keyboard = []
    for i in range(0, len(courses), 2):
        row = [KeyboardButton(utils.get_text(courses[i], context))]
        if i + 1 < len(courses):
            row.append(KeyboardButton(utils.get_text(courses[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_complaint_types_keyboard(context):
    """Murojaat turlari klaviaturasi (2 tugma bir qator)"""
    complaint_types = list(utils.get_complaint_types().values())
    keyboard = []
    for i in range(0, len(complaint_types), 2):
        row = [KeyboardButton(utils.get_text(complaint_types[i], context))]
        if i + 1 < len(complaint_types):
            row.append(KeyboardButton(utils.get_text(complaint_types[i + 1], context)))
        keyboard.append(row)
    keyboard.append([KeyboardButton(utils.get_text('btn_back', context))])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# Qolgan statik klaviaturalar ham 2tadan qilamiz

def get_rules_keyboard(context):
    buttons = [
        utils.get_text('btn_grading', context),
        utils.get_text('btn_exam', context),
        utils.get_text('btn_general', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_rules_detail_keyboard(context):
    buttons = [
        utils.get_text('btn_download_pdf', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = [[KeyboardButton(b)] for b in buttons]  # bu ham 2taga bo‘lishi mumkin
    if len(buttons) > 1:
        keyboard = [[KeyboardButton(buttons[0]), KeyboardButton(buttons[1])]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_survey_keyboard(context):
    buttons = [
        utils.get_text('btn_survey_teachers', context),
        utils.get_text('btn_survey_edu', context),
        utils.get_text('btn_survey_emp', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_survey_links_keyboard(context):
    buttons = [
        utils.get_text('btn_survey_link', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = [[KeyboardButton(b) for b in buttons]]  # 2tadan
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_admin_keyboard(context):
    buttons = [
        utils.get_text('btn_stats', context),
        utils.get_text('btn_view_complaints', context),
        utils.get_text('btn_export_menu', context),
        utils.get_text('btn_dashboard', context),
        utils.get_text('btn_settings', context),
        utils.get_text('btn_back_main', context)
    ]
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_export_menu_keyboard(context):
    buttons = [
        utils.get_text('btn_export_excel', context),
        utils.get_text('btn_export_lesson', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_yes_no_keyboard(context):
    return ReplyKeyboardMarkup([
        [
            KeyboardButton(utils.get_text('btn_yes', context)),
            KeyboardButton(utils.get_text('btn_no', context))
        ],
        [KeyboardButton(utils.get_text('btn_back', context))]
    ], resize_keyboard=True)


def get_rating_keyboard(context):
    """0-5 ball klaviaturasi"""
    keyboard = [
        [KeyboardButton("0"), KeyboardButton("1"), KeyboardButton("2")],
        [KeyboardButton("3"), KeyboardButton("4"), KeyboardButton("5")],
        [KeyboardButton(utils.get_text('btn_back', context))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard(context):
    return ReplyKeyboardMarkup([[KeyboardButton(utils.get_text('btn_back', context))]], resize_keyboard=True)


# ADMIN CRUD KEYBOARDS

def get_settings_keyboard(context):
    buttons = [
        utils.get_text('btn_manage_admins', context),
        utils.get_text('btn_manage_faculties', context),
        utils.get_text('btn_manage_directions', context),
        utils.get_text('btn_manage_questions', context),
        utils.get_text('btn_manage_languages', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_crud_keyboard(context):
    buttons = [
        utils.get_text('btn_add', context),
        utils.get_text('btn_list', context),
        utils.get_text('btn_delete', context),
        utils.get_text('btn_back', context)
    ]
    keyboard = []
    for i in range(0, len(buttons), 2):
        row = [KeyboardButton(buttons[i])]
        if i + 1 < len(buttons):
            row.append(KeyboardButton(buttons[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_confirm_keyboard(context):
    buttons = [
        utils.get_text('btn_confirm', context),
        utils.get_text('btn_cancel', context)
    ]
    keyboard = [[KeyboardButton(buttons[0]), KeyboardButton(buttons[1])]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
