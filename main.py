# main.py
# Asosiy bot fayli - barcha komponentlarni birlashtiradi

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Import qilish
# Import qilish
from config.config import BOT_TOKEN, LANGS, WEBAPP_URL
from database import init_database, upsert_user, log_error
from database_models import init_dynamic_config
from keyboards.keyboards import (
    get_main_menu_keyboard,
    get_webapp_inline_keyboard,
    get_language_keyboard,
    get_faculties_keyboard,
    get_dynamic_keyboard,
    get_education_type_keyboard,
    get_education_lang_keyboard,
    get_courses_keyboard,
    get_complaint_types_keyboard,
    get_back_keyboard
)
import utils.utils as utils

# Handlerlarni import qilish
from handlers.complaints.complaint import (
    start_complaint,
    handle_faculty_choice,
    handle_direction_choice,
    handle_education_type_choice,
    handle_education_lang_choice,
    handle_course_choice,
    handle_complaint_type_choice,
    handle_subject_entry,
    handle_teacher_entry,
    handle_complaint_message
)

from handlers.ratings.lesson_daily_rating import (
    start_lesson_daily_rating,
    handle_lesson_direction_choice,
    handle_lesson_course_choice,
    handle_subject_name,
    handle_teacher_name,
    handle_rating
)
from handlers.rules.rules import (
    show_rules_main,
    show_grading_rules,
    show_exam_rules,
    show_general_rules,
    download_pdf
)
from handlers.surveys.survey import (
    show_survey_main,
    show_teachers_survey,
    show_education_survey,
    show_employers_survey,
    open_survey_link,
    show_survey_results
)
from handlers.admins.admin import (
    show_admin_panel,
    show_statistics,
    view_complaints,
    export_to_excel_handler,
    export_to_daily_lesson_excel_handler,
    show_dashboard,
    show_export_menu,
    show_settings_menu  # YANGI
)
from handlers.admins.crud_settings import (
    show_admins_menu, list_admins, prompt_add_admin, handle_add_admin_id, handle_add_admin_name,
    prompt_delete_admin, handle_delete_admin,
    show_faculties_menu, list_faculties, prompt_add_faculty, handle_add_faculty_code, handle_add_faculty_name,
    prompt_delete_faculty, handle_delete_faculty,
    show_directions_menu, list_directions, prompt_add_direction, handle_add_direction_code,
    handle_add_direction_faculty, handle_add_direction_name, prompt_delete_direction, handle_delete_direction,
    show_questions_menu, list_questions, prompt_add_question, handle_add_question_text, handle_add_question_type,
    prompt_delete_question, handle_delete_question,
    show_surveys_menu, list_surveys, prompt_add_survey, handle_add_survey_title, handle_add_survey_url,
    prompt_delete_survey, handle_delete_survey
)

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Error loglarini bazaga yozish uchun maxsus Handler
class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            if record.levelno >= logging.ERROR:
                log_error(
                    level=record.levelname,
                    message=record.getMessage(),
                    traceback_str=record.exc_text or (logging.Formatter().formatException(record.exc_info) if record.exc_info else None),
                    context={"module": record.module, "funcName": record.funcName, "lineno": record.lineno}
                )
        except:
            pass

# Handlerni qo'shish
logging.getLogger().addHandler(DatabaseLogHandler())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot ishga tushganda"""
    # Foydalanuvchini bazaga yozish/yangilash
    upsert_user(update.effective_user.to_dict())

    # Agar til tanlanmagan bo'lsa, til tanlashga yuboramiz
    if 'language' not in context.user_data:
        await update.message.reply_text(
            "Iltimos, tilni tanlang / Пожалуйста, выберите язык / Please select a language:",
            reply_markup=get_language_keyboard()
        )
        return

    lang = context.user_data.get('language', 'uz')
    
    # Agar URL kiritilmagan bo'lsa, vaqtinchalik xavfsiz URL qo'yish
    safe_webapp_url = WEBAPP_URL if WEBAPP_URL else "https://google.com"

    if lang == 'ru':
        welcome_text = (
            "👋 <b>Добро пожаловать в Академию!</b>\n\n"
            "📌 Наш проект полностью перешел на цифровой этап! 🚀\n"
            "Все обращения, предложения, оценки уроков и правила экзаменов теперь "
            "принимаются через единую и современную мини-платформу.\n\n"
            "<i>👇 Откройте систему, нажав на кнопку ниже:</i>"
        )
        menu_text = "Или воспользуйтесь бот-меню 👇"
    elif lang == 'en':
        welcome_text = (
            "👋 <b>Welcome to the Academy!</b>\n\n"
            "📌 Our project has fully transitioned to the digital stage! 🚀\n"
            "All appeals, suggestions, lesson ratings, and exam rules are now "
            "handled through a single, modern mini-platform.\n\n"
            "<i>👇 Open the system by clicking the button below:</i>"
        )
        menu_text = "Or use the bot menu 👇"
    else:
        welcome_text = (
            "👋 <b>Akademiyamizga Xush Kelibsiz!</b>\n\n"
            "📌 Loyihamiz to'liq raqamli bosqichga o'tdi! 🚀\n"
            "Barcha murojaatlar, takliflar, darslarni baholash va imtihon qoidalari endi "
            "yagona va zamonaviy mini-ilova orqali amalga oshiriladi.\n\n"
            "<i>👇 Pastdagi tugmani bosib, tizimga kiring:</i>"
        )
        menu_text = "Yoki bot menyusidan foydalaning 👇"

    await update.message.reply_text(
        welcome_text,
        parse_mode='HTML',
        reply_markup=get_webapp_inline_keyboard(context, webapp_url=safe_webapp_url)
    )
    
    await update.message.reply_text(
        menu_text,
        reply_markup=get_main_menu_keyboard(context, webapp_url=WEBAPP_URL)
    )


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Tarjimalarni tekshirish (chunki tugma matni tilga qarab o'zgaradi)
    # Eng yaxshi yo'l - har bir til uchun variantlarni tekshirish yoki callback_query ishlatish.
    # Lekin hozirgi strukturada utils.get_text orqali kalit so'zlarni solishtiramiz.
    
    # QAYD: Tugma matnini tekshirish biroz qiyinroq, chunki biz key'ni bilmaymiz.
    # Shuning uchun barcha tillardagi variantlarni tekshiramiz.
    
    # Keling, oddiyroq yo'l tutamiz: 
    # Hozircha hardcode qilingan stringlarni utils.get_text bilan almashtiramiz.
    
    if text == utils.get_text('btn_complaint', context):
        from database import record_activity
        record_activity(update.effective_user.id, 'nav_complaint', 'bot')
        await start_complaint(update, context)

    elif text == utils.get_text('btn_rules', context):
        await show_rules_main(update, context)

    elif text == utils.get_text('btn_survey', context):
        await show_survey_main(update, context)

    elif text == utils.get_text('btn_admin', context):
        await show_admin_panel(update, context)

    elif text == utils.get_text('btn_lesson_rating', context):
        await start_lesson_daily_rating(update, context)

    elif text == utils.get_text('btn_lang', context):
        await update.message.reply_text(
            utils.get_text('btn_lang', context) + ":",
            reply_markup=get_language_keyboard()
        )

    elif text == utils.get_text('btn_back_main', context) or text == utils.get_text('btn_back', context):
        await start(update, context)



async def handle_select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Til tanlash jarayonini boshqarish"""
    text = update.message.text
    
    # LANGS values (🇺🇿 O'zbekcha, 🇷🇺 Русский...) orqali kodni topamiz
    selected_lang_code = None
    for code, name in LANGS.items():
        if text == name:
            selected_lang_code = code
            break
            
    if selected_lang_code:
        context.user_data['language'] = selected_lang_code
        from database import record_activity
        record_activity(update.effective_user.id, f'select_lang_{selected_lang_code}', 'bot')
        # Tanlangandan keyin holatni tozalaymiz va asosiy menyuga o'tamiz
        context.user_data['state'] = ''
        await start(update, context)
    else:
        # Noto'g'ri tanlov
        await update.message.reply_text(
            "Iltimos, tugmalardan birini tanlang / Пожалуйста, выберите одну из кнопок"
        )


async def handle_complaint_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Murojaat jarayonini boshqarish"""
    state = context.user_data.get('state', '')
    text = update.message.text

    # 🔙 Orqaga tugmasi (Mantiqiy zanjir)
    if text == utils.get_text('btn_back', context):
        if state == 'choosing_faculty':
            await start(update, context)
        
        elif state == 'choosing_direction':
            await start_complaint(update, context)

        elif state == 'choosing_education_type':
            # Fakultetni aniqlaymiz va yo'nalishlar keyboardini qayta chiqaramiz
            faculty_code = context.user_data.get('faculty')
            directions = utils.get_directions_by_faculty(faculty_code)
            context.user_data['state'] = 'choosing_direction'
            faculty_name = utils.get_faculty_name(faculty_code, context)
            await update.message.reply_text(
                f"🏛 {faculty_name}\n\n{utils.get_text('choose_direction', context)}",
                reply_markup=get_dynamic_keyboard(directions, context)
            )

        elif state == 'choosing_education_lang':
            context.user_data['state'] = 'choosing_education_type'
            await update.message.reply_text(
                utils.get_text('choose_edu_type', context),
                reply_markup=get_education_type_keyboard(context)
            )

        elif state == 'choosing_course':
            faculty = context.user_data.get('faculty', '')
            if faculty == 'magistratura':
                # Magistratura - yo'nalish tanlashga qaytadi
                directions = context.user_data.get('directions_map', {})
                faculty_name = utils.get_faculty_name(faculty, context)
                context.user_data['state'] = 'choosing_direction'
                await update.message.reply_text(
                    f"🏛 {faculty_name}\n\n{utils.get_text('choose_direction', context)}",
                    reply_markup=get_dynamic_keyboard(directions, context)
                )
            else:
                context.user_data['state'] = 'choosing_education_lang'
                await update.message.reply_text(
                    utils.get_text('choose_edu_lang', context),
                    reply_markup=get_education_lang_keyboard(context)
                )


        elif state == 'choosing_complaint_type':
            context.user_data['state'] = 'choosing_course'
            await update.message.reply_text(
                utils.get_text('choose_course', context),
                reply_markup=get_courses_keyboard(context)
            )

        elif state == 'entering_subject':
            context.user_data['state'] = 'choosing_complaint_type'
            await update.message.reply_text(
                utils.get_text('choose_complaint_type', context),
                reply_markup=get_complaint_types_keyboard(context)
            )

        elif state == 'entering_teacher':
            context.user_data['state'] = 'entering_subject'
            await update.message.reply_text(
                utils.get_text('enter_subject', context),
                reply_markup=get_back_keyboard(context)
            )

        elif state == 'entering_message':
            complaint_type = context.user_data.get('complaint_type')
            if complaint_type == 'teacher':
                context.user_data['state'] = 'entering_teacher'
                await update.message.reply_text(
                    utils.get_text('enter_teacher', context),
                    reply_markup=get_back_keyboard(context)
                )
            else:
                context.user_data['state'] = 'choosing_complaint_type'
                await update.message.reply_text(
                    utils.get_text('choose_complaint_type', context),
                    reply_markup=get_complaint_types_keyboard(context)
                )
        return

    # =============================
    # 🔽 Murojaat jarayoni oqimi
    # =============================

    # 1️⃣ Fakultet tanlash
    if state == 'choosing_faculty':
        await handle_faculty_choice(update, context)
        return

    # 2️⃣ Yo‘nalish tanlash
    elif state == 'choosing_direction':
        await handle_direction_choice(update, context)
        return

    # 2️⃣ Ta'lim yo'nalishini
    elif state == 'choosing_education_type':
        await handle_education_type_choice(update, context)
        return

    # 2️⃣ Ta'lim tilini tanlash
    elif state == 'choosing_education_lang':
        await handle_education_lang_choice(update, context)
        return

                   # 3️⃣ Kurs tanlash
    elif state == 'choosing_course':
        await handle_course_choice(update, context)
        return

    # 4️⃣ Murojaat turi
    elif state == 'choosing_complaint_type':
        await handle_complaint_type_choice(update, context)
        return

    # 5️⃣ Fan kiritish
    elif state == 'entering_subject':
        await handle_subject_entry(update, context)
        return

    # 6️⃣ O‘qituvchi ismi kiritish
    elif state == 'entering_teacher':
        await handle_teacher_entry(update, context)
        return

    # 7️⃣ Murojaat matnini kiritish
    elif state == 'entering_message':
        await handle_complaint_message(update, context)
        return



async def handle_rules_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tartib qoidalar jarayonini boshqarish"""
    state = context.user_data.get('state', '')
    text = update.message.text

    if text == utils.get_text('btn_grading', context):
        await show_grading_rules(update, context)

    elif text == utils.get_text('btn_exam', context):
        await show_exam_rules(update, context)

    elif text == utils.get_text('btn_general', context):
        await show_general_rules(update, context)

    elif text == utils.get_text('btn_download_pdf', context):
        await download_pdf(update, context)

    elif text == utils.get_text('btn_back', context):
        if state == 'rules_main':
            await start(update, context)
        else:
            # Har qanday qoida ichidan asosiy qoidalar menyusiga qaytamiz
            await show_rules_main(update, context)


async def handle_survey_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnoma jarayonini boshqarish"""
    state = context.user_data.get('state', '')
    text = update.message.text

    if text == utils.get_text('btn_survey_teachers', context):
        await show_teachers_survey(update, context)

    elif text == utils.get_text('btn_survey_edu', context):
        await show_education_survey(update, context)

    elif text == utils.get_text('btn_survey_emp', context):
        await show_employers_survey(update, context)

    elif text == utils.get_text('btn_survey_link', context):
        await open_survey_link(update, context)

    elif text == utils.get_text('btn_back', context):
        if state == 'survey_main':
            await start(update, context)
        else:
            await show_survey_main(update, context)


async def handle_admin_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel jarayonini boshqarish"""
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text(utils.get_text('no_permission', context))
        return

    text = update.message.text

    if text == utils.get_text('btn_stats', context):
        await show_statistics(update, context)

    elif text == utils.get_text('btn_view_complaints', context):
        await view_complaints(update, context)

    elif text == utils.get_text('btn_export_menu', context):
        await show_export_menu(update, context)

    elif text == utils.get_text('btn_dashboard', context):
        await show_dashboard(update, context)
    
    elif text == utils.get_text('btn_settings', context):
        await show_settings_menu(update, context)
    
    elif text == utils.get_text('btn_back_main', context):
        await start(update, context)


async def handle_admin_export_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Excel export jarayonini boshqarish"""
    text = update.message.text

    if text == utils.get_text('btn_export_excel', context):
        await export_to_excel_handler(update, context)

    elif text == utils.get_text('btn_export_lesson', context):
        await export_to_daily_lesson_excel_handler(update, context)

    elif text == utils.get_text('btn_back', context):
        await show_admin_panel(update, context)


# ============================================
# CRUD FLOW HANDLERS
# ============================================

async def handle_settings_menu_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalar menyusi oqimi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    text = update.message.text
    
    if text == utils.get_text('btn_manage_admins', context):
        await show_admins_menu(update, context)
    elif text == utils.get_text('btn_manage_faculties', context):
        await show_faculties_menu(update, context)
    elif text == utils.get_text('btn_manage_directions', context):
        await show_directions_menu(update, context)
    elif text == utils.get_text('btn_manage_questions', context):
        await show_questions_menu(update, context)
    elif text == utils.get_text('btn_manage_surveys', context):
        await show_surveys_menu(update, context)
    elif text == utils.get_text('btn_back', context):
        await show_admin_panel(update, context)


async def handle_admins_crud_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminlar CRUD oqimi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    text = update.message.text
    
    if text == utils.get_text('btn_add', context):
        await prompt_add_admin(update, context)
    elif text == utils.get_text('btn_list', context):
        await list_admins(update, context)
    elif text == utils.get_text('btn_delete', context):
        await prompt_delete_admin(update, context)
    elif text == utils.get_text('btn_back', context):
        await show_settings_menu(update, context)


async def handle_faculties_crud_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultetlar CRUD oqimi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    text = update.message.text
    
    if text == utils.get_text('btn_add', context):
        await prompt_add_faculty(update, context)
    elif text == utils.get_text('btn_list', context):
        await list_faculties(update, context)
    elif text == utils.get_text('btn_delete', context):
        await prompt_delete_faculty(update, context)
    elif text == utils.get_text('btn_back', context):
        await show_settings_menu(update, context)


async def handle_directions_crud_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalishlar CRUD oqimi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    text = update.message.text
    
    if text == utils.get_text('btn_add', context):
        await prompt_add_direction(update, context)
    elif text == utils.get_text('btn_list', context):
        await list_directions(update, context)
    elif text == utils.get_text('btn_delete', context):
        await prompt_delete_direction(update, context)
    elif text == utils.get_text('btn_back', context):
        await show_settings_menu(update, context)


async def handle_questions_crud_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savollar CRUD oqimi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    text = update.message.text
    
    if text == utils.get_text('btn_add', context):
        await prompt_add_question(update, context)
    elif text == utils.get_text('btn_list', context):
        await list_questions(update, context)
    elif text == utils.get_text('btn_delete', context):
        await prompt_delete_question(update, context)
    elif text == utils.get_text('btn_back', context):
        await show_settings_menu(update, context)


async def handle_surveys_crud_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnomalar CRUD oqimi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    text = update.message.text
    
    if text == utils.get_text('btn_add', context):
        await prompt_add_survey(update, context)
    elif text == utils.get_text('btn_list', context):
        await list_surveys(update, context)
    elif text == utils.get_text('btn_delete', context):
        await prompt_delete_survey(update, context)
    elif text == utils.get_text('btn_back', context):
        await show_settings_menu(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha matnli xabarlarni boshqarish"""
    text = update.message.text
    state = context.user_data.get('state', '')

    # Foydalanuvchini bazaga yozish/yangilash
    upsert_user(update.effective_user.to_dict())

    # 1. Global: Til tanlash (Har qanday holatda ishlaydi)
    if text in LANGS.values():
        await handle_select_language(update, context)
        return

    # 2. Global: Asosiy menyu tugmalari
    # Har bir tildagi variantlarni tekshirish kerak (Endi utils orqali)
    main_menu_buttons = utils.get_main_menu_buttons()

    if text in main_menu_buttons:
        # Menyu tugmasi bosilsa, holatdan qat'iy nazar menyuga ishlov beramiz
        await handle_main_menu(update, context)
        return

    # 3. Holatga qarab boshqarish
    if not state:
        await start(update, context)
        return

    # Murojaat jarayoni
    if state in ['choosing_faculty','choosing_direction',
                 'choosing_education_type', 'choosing_education_lang', 'choosing_course', 'choosing_complaint_type',
                 'entering_subject', 'entering_teacher', 'entering_message']:
        await handle_complaint_flow(update, context)
        return

    # Tartib qoidalar
    rules_states = ['rules_main', 'rules_grading', 'rules_exam', 'rules_general']
    if state in rules_states or text in [utils.get_text('btn_grading', context), utils.get_text('btn_exam', context), utils.get_text('btn_general', context)]:
        await handle_rules_flow(update, context)
        return

    # So'rovnoma
    if state in ['survey_main', 'survey_teachers', 'survey_education', 'survey_employers']:
        await handle_survey_flow(update, context)
        return

    # Admin panel
    if state == 'admin_panel':
        await handle_admin_flow(update, context)
        return
    
    if state == 'admin_export_menu':
        await handle_admin_export_flow(update, context)
        return

    # ============================================
    # CRUD SETTINGS STATES
    # ============================================
    
    # Sozlamalar menyusi
    if state == 'settings_menu':
        await handle_settings_menu_flow(update, context)
        return
    
    # Admin CRUD
    if state == 'admins_menu':
        await handle_admins_crud_flow(update, context)
        return
    if state == 'adding_admin_id':
        await handle_add_admin_id(update, context)
        return
    if state == 'adding_admin_name':
        await handle_add_admin_name(update, context)
        return
    if state == 'deleting_admin':
        await handle_delete_admin(update, context)
        return
    
    # Faculty CRUD
    if state == 'faculties_menu':
        await handle_faculties_crud_flow(update, context)
        return
    if state == 'adding_faculty_code':
        await handle_add_faculty_code(update, context)
        return
    if state == 'adding_faculty_name':
        await handle_add_faculty_name(update, context)
        return
    if state == 'deleting_faculty':
        await handle_delete_faculty(update, context)
        return
    
    # Direction CRUD
    if state == 'directions_menu':
        await handle_directions_crud_flow(update, context)
        return
    if state == 'adding_direction_code':
        await handle_add_direction_code(update, context)
        return
    if state == 'adding_direction_faculty':
        await handle_add_direction_faculty(update, context)
        return
    if state == 'adding_direction_name':
        await handle_add_direction_name(update, context)
        return
    if state == 'deleting_direction':
        await handle_delete_direction(update, context)
        return
    
    # Question CRUD
    if state == 'questions_menu':
        await handle_questions_crud_flow(update, context)
        return
    if state == 'adding_question_text':
        await handle_add_question_text(update, context)
        return
    if state == 'adding_question_type':
        await handle_add_question_type(update, context)
        return
    if state == 'deleting_question':
        await handle_delete_question(update, context)
        return
    
    # Survey CRUD
    if state == 'surveys_menu':
        await handle_surveys_crud_flow(update, context)
        return
    if state == 'adding_survey_title':
        await handle_add_survey_title(update, context)
        return
    if state == 'adding_survey_url':
        await handle_add_survey_url(update, context)
        return
    if state == 'deleting_survey':
        await handle_delete_survey(update, context)
        return

    # Kunlik darsni baholash jarayoni
    if state == 'rating_direction':
        await handle_lesson_direction_choice(update, context)
        return
    if state == 'rating_course':
        await handle_lesson_course_choice(update, context)
        return
    if state == 'rating_subject':
        await handle_subject_name(update, context)
        return
    if state == 'rating_teacher':
        await handle_teacher_name(update, context)
        return
    if state == 'rating_process':
        await handle_rating(update, context)
        return

    # Default - asosiy menyuga qaytish
    await start(update, context)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin komandasi"""
    await utils.show_admin_panel(update, context)


def main():
    """Asosiy funksiya - botni ishga tushirish"""
    import asyncio
    from web_server import start_web_server
    
    # Ma'lumotlar bazasini yaratish
    init_database()
    logger.info("Ma'lumotlar bazasi ishga tushirildi")

    # Dinamik konfiguratsiyani yuklash
    init_dynamic_config()
    logger.info("Dinamik konfiguratsiya yuklandi")
    
    # Tarjimalarni xotiraga (keshga) yuklash
    utils.load_translations_to_cache()
    logger.info("Tarjimalar keshga yuklandi")

    # Bot applicationni yaratish - timeout sozlamalari bilan
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .build()
    )

    # Command handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("admin", admin_command))

    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Botni va web serverni birgalikda ishga tushirish
    async def run_all():
        # Portni xostingdan olamiz (faqat bittasini ishlatish kerak, masalan Render'da PORT beriladi)
        import os
        port = int(os.environ.get('PORT', 8085))
        
        # Web serverni ishga tushirish
        runner = await start_web_server(bot=application.bot, host='0.0.0.0', port=port)
        logger.info(f"Mini App web server {port} portda ishga tushdi")
        
        # Botni ishga tushirish
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        logger.info("Bot ishga tushdi...")
        
        # Mantiqiy to'xtatish uchun singal kutamiz
        try:
            while True:
                await asyncio.sleep(3600)  # 1 soat kutamiz
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
            await runner.cleanup()

    # Asosiy tsiklni ishga tushirish
    logger.info("Bot va Mini App serveri ishga tushmoqda...")
    asyncio.run(run_all())

if __name__ == '__main__':
    main()