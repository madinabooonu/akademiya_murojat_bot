# handlers/admins/crud_settings.py
# Admin CRUD operatsiyalari uchun handlerlar

from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import (
    get_settings_keyboard, get_crud_keyboard, get_back_keyboard,
    get_admin_keyboard, get_confirm_keyboard
)
import utils.utils as utils
from database_models import (
    get_all_admins, add_admin, remove_admin,
    get_all_faculties, add_faculty, delete_faculty,
    get_directions_by_faculty, add_direction, delete_direction,
    get_rating_questions, add_rating_question, update_rating_question, delete_rating_question,
    get_all_survey_links, add_survey_link, delete_survey_link,
    update_translation
)


async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sozlamalar menyusini ko'rsatish"""
    if not utils.is_admin(update.effective_user.id):
        await update.message.reply_text(utils.get_text('no_permission', context))
        return

    context.user_data['state'] = 'settings_menu'
    
    await update.message.reply_text(
        utils.get_text('settings_title', context),
        reply_markup=get_settings_keyboard(context)
    )


# ============================================
# ADMIN MANAGEMENT
# ============================================

async def show_admins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminlarni boshqarish menyusi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'admins_menu'
    context.user_data['crud_type'] = 'admins'
    
    await update.message.reply_text(
        utils.get_text('btn_manage_admins', context),
        reply_markup=get_crud_keyboard(context)
    )


async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Adminlar ro'yxatini ko'rsatish"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    admins = get_all_admins()
    
    if not admins:
        await update.message.reply_text(utils.get_text('admins_empty', context))
        return
    
    import html
    text = html.escape(utils.get_text('admins_list_title', context))
    for i, (telegram_id, name, is_active) in enumerate(admins, 1):
        status = "✅" if is_active else "❌"
        name_display = html.escape(name if name else "Noma'lum")
        text += f"{i}. {status} ID: <code>{telegram_id}</code> - {name_display}\n"
    
    await update.message.reply_text(text, parse_mode='HTML')


async def prompt_add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin qo'shish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'adding_admin_id'
    
    await update.message.reply_text(
        utils.get_text('admin_add_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_admin_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin ID kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_admins_menu(update, context)
    
    try:
        telegram_id = int(text)
        context.user_data['new_admin_id'] = telegram_id
        context.user_data['state'] = 'adding_admin_name'
        
        await update.message.reply_text(
            utils.get_text('admin_add_name_prompt', context),
            reply_markup=get_back_keyboard(context)
        )
    except ValueError:
        await update.message.reply_text(utils.get_text('invalid_telegram_id', context))


async def handle_add_admin_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin ismi kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await prompt_add_admin(update, context)
    
    telegram_id = context.user_data.get('new_admin_id')
    name = text if text != '-' else ""
    
    if add_admin(telegram_id, name):
        await update.message.reply_text(utils.get_text('admin_added', context))
    else:
        await update.message.reply_text(utils.get_text('admin_exists', context))
    
    # Tozalash va menyuga qaytish
    context.user_data.pop('new_admin_id', None)
    await show_admins_menu(update, context)


async def prompt_delete_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin o'chirish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'deleting_admin'
    
    # Avval ro'yxatni ko'rsatamiz
    await list_admins(update, context)
    
    await update.message.reply_text(
        utils.get_text('admin_delete_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_delete_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin o'chirish"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_admins_menu(update, context)
    
    try:
        telegram_id = int(text)
        
        if remove_admin(telegram_id):
            await update.message.reply_text(utils.get_text('admin_deleted', context))
        else:
            await update.message.reply_text(utils.get_text('admin_not_found', context))
    except ValueError:
        await update.message.reply_text(utils.get_text('invalid_telegram_id', context))
    
    await show_admins_menu(update, context)


# ============================================
# FACULTY MANAGEMENT
# ============================================

async def show_faculties_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultetlarni boshqarish menyusi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'faculties_menu'
    context.user_data['crud_type'] = 'faculties'
    
    await update.message.reply_text(
        utils.get_text('btn_manage_faculties', context),
        reply_markup=get_crud_keyboard(context)
    )


async def list_faculties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultetlar ro'yxatini ko'rsatish"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    faculties = get_all_faculties()
    
    if not faculties:
        await update.message.reply_text(utils.get_text('faculties_empty', context))
        return
    
    import html
    text = html.escape(utils.get_text('faculties_list_title', context))
    for code, translation_key, sort_order, is_active in faculties:
        status = "✅" if is_active else "❌"
        name = html.escape(utils.get_text(translation_key, context))
        text += f"{status} <code>{html.escape(code)}</code> - {name}\n"
    
    await update.message.reply_text(text, parse_mode='HTML')


async def prompt_add_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultet qo'shish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'adding_faculty_code'
    
    await update.message.reply_text(
        utils.get_text('faculty_add_code_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_faculty_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultet kodi kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_faculties_menu(update, context)
    
    context.user_data['new_faculty_code'] = text.lower()
    context.user_data['state'] = 'adding_faculty_name'
    
    await update.message.reply_text(
        utils.get_text('faculty_add_name_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_faculty_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultet nomi kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await prompt_add_faculty(update, context)
    
    code = context.user_data.get('new_faculty_code')
    translation_key = f'faculty_{code}'
    
    # Avval tarjimani qo'shamiz
    lang_code = context.user_data.get('language', 'uz')
    update_translation(translation_key, lang_code, text)
    
    # Keyin fakultetni qo'shamiz
    if add_faculty(code, translation_key):
        await update.message.reply_text(utils.get_text('faculty_added', context))
    else:
        await update.message.reply_text(utils.get_text('faculty_exists', context))
    
    context.user_data.pop('new_faculty_code', None)
    await show_faculties_menu(update, context)


async def prompt_delete_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultet o'chirish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'deleting_faculty'
    
    await list_faculties(update, context)
    
    await update.message.reply_text(
        utils.get_text('faculty_delete_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_delete_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fakultet o'chirish"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_faculties_menu(update, context)
    
    if delete_faculty(text.lower()):
        await update.message.reply_text(utils.get_text('faculty_deleted', context))
    else:
        await update.message.reply_text(utils.get_text('faculty_not_found', context))
    
    await show_faculties_menu(update, context)


# ============================================
# DIRECTION MANAGEMENT
# ============================================

async def show_directions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalishlarni boshqarish menyusi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'directions_menu'
    context.user_data['crud_type'] = 'directions'
    
    await update.message.reply_text(
        utils.get_text('btn_manage_directions', context),
        reply_markup=get_crud_keyboard(context)
    )


async def list_directions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalishlar ro'yxatini ko'rsatish"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    from database_models import get_all_directions_dict
    from utils.utils import get_all_directions
    
    directions = get_all_directions()
    
    if not directions:
        await update.message.reply_text(utils.get_text('directions_empty', context))
        return
    
    import html
    text = html.escape(utils.get_text('directions_list_title', context))
    for code, translation_key in directions.items():
        name = html.escape(utils.get_text(translation_key, context))
        text += f"• <code>{html.escape(code)}</code> - {name}\n"
    
    await update.message.reply_text(text, parse_mode='HTML')


async def prompt_add_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish qo'shish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'adding_direction_code'
    
    await update.message.reply_text(
        utils.get_text('direction_add_code_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_direction_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish kodi kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_directions_menu(update, context)
    
    context.user_data['new_direction_code'] = text.lower()
    context.user_data['state'] = 'adding_direction_faculty'
    
    # Fakultetlar ro'yxatini ko'rsatamiz
    await list_faculties(update, context)
    
    await update.message.reply_text(
        utils.get_text('direction_add_faculty_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_direction_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish fakulteti kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await prompt_add_direction(update, context)
    
    context.user_data['new_direction_faculty'] = text.lower()
    context.user_data['state'] = 'adding_direction_name'
    
    await update.message.reply_text(
        utils.get_text('direction_add_name_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_direction_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish nomi kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await handle_add_direction_code(update, context)
    
    code = context.user_data.get('new_direction_code')
    faculty_code = context.user_data.get('new_direction_faculty')
    translation_key = f'dir_{code}'
    
    # Tarjimani qo'shamiz
    lang_code = context.user_data.get('language', 'uz')
    update_translation(translation_key, lang_code, text)
    
    # Yo'nalishni qo'shamiz
    if add_direction(code, faculty_code, translation_key):
        await update.message.reply_text(utils.get_text('direction_added', context))
    else:
        await update.message.reply_text(utils.get_text('direction_exists', context))
    
    context.user_data.pop('new_direction_code', None)
    context.user_data.pop('new_direction_faculty', None)
    await show_directions_menu(update, context)


async def prompt_delete_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish o'chirish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'deleting_direction'
    
    await list_directions(update, context)
    
    await update.message.reply_text(
        utils.get_text('direction_delete_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_delete_direction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yo'nalish o'chirish"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_directions_menu(update, context)
    
    if delete_direction(text.lower()):
        await update.message.reply_text(utils.get_text('direction_deleted', context))
    else:
        await update.message.reply_text(utils.get_text('direction_not_found', context))
    
    await show_directions_menu(update, context)


# ============================================
# QUESTION MANAGEMENT
# ============================================

async def show_questions_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savollarni boshqarish menyusi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'questions_menu'
    context.user_data['crud_type'] = 'questions'
    
    await update.message.reply_text(
        utils.get_text('btn_manage_questions', context),
        reply_markup=get_crud_keyboard(context)
    )


async def list_questions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savollar ro'yxatini ko'rsatish"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    questions = get_rating_questions()
    
    if not questions:
        await update.message.reply_text(utils.get_text('questions_empty', context))
        return
    
    text = utils.get_text('questions_list_title', context)
    for question_number, translation_key, answer_type in questions:
        question_text = utils.get_text(translation_key, context)
        type_emoji = "📊" if answer_type == 'scale' else "✅❌"
        text += f"{question_number}. {type_emoji} {question_text}\n\n"
    
    await update.message.reply_text(text)


async def prompt_add_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savol qo'shish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'adding_question_text'
    
    await update.message.reply_text(
        utils.get_text('question_add_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_question_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savol matni kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_questions_menu(update, context)
    
    context.user_data['new_question_text'] = text
    context.user_data['state'] = 'adding_question_type'
    
    await update.message.reply_text(
        utils.get_text('question_add_type_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_question_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savol turi kiritilganda"""
    text = update.message.text.lower()
    
    if text == utils.get_text('btn_back', context).lower():
        return await prompt_add_question(update, context)
    
    if text not in ['scale', 'yes_no']:
        await update.message.reply_text(utils.get_text('invalid_input', context))
        return
    
    question_text = context.user_data.get('new_question_text')
    
    # Savol raqamini topamiz
    questions = get_rating_questions()
    new_number = len(questions) + 1
    translation_key = f'rating_q{new_number}'
    
    # Tarjimani qo'shamiz
    lang_code = context.user_data.get('language', 'uz')
    update_translation(translation_key, lang_code, f"{new_number}) {question_text}")
    
    # Savolni qo'shamiz
    add_rating_question(new_number, translation_key, text)
    
    await update.message.reply_text(utils.get_text('question_added', context))
    
    context.user_data.pop('new_question_text', None)
    await show_questions_menu(update, context)


async def prompt_delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savol o'chirish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'deleting_question'
    
    await list_questions(update, context)
    
    await update.message.reply_text(
        utils.get_text('question_delete_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_delete_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Savol o'chirish"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_questions_menu(update, context)
    
    try:
        question_number = int(text)
        if delete_rating_question(question_number):
            await update.message.reply_text(utils.get_text('question_deleted', context))
        else:
            await update.message.reply_text(utils.get_text('question_not_found', context))
    except ValueError:
        await update.message.reply_text(utils.get_text('invalid_input', context))
    
    await show_questions_menu(update, context)


# ============================================
# SURVEY MANAGEMENT (NEW)
# ============================================

async def show_surveys_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnomalarni boshqarish menyusi"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'surveys_menu'
    context.user_data['crud_type'] = 'surveys'
    
    await update.message.reply_text(
        utils.get_text('btn_manage_surveys', context),
        reply_markup=get_crud_keyboard(context)
    )


async def list_surveys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnomalar ro'yxatini ko'rsatish"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    surveys = get_all_survey_links()
    
    if not surveys:
        await update.message.reply_text(utils.get_text('surveys_empty', context))
        return
    
    import html
    text = html.escape(utils.get_text('surveys_list_title', context))
    for code, url, translation_key, is_active in surveys:
        status = "✅" if is_active else "❌"
        # translation_key bo'lsa uni ishlatamiz, bo'lmasa codeni o'zini
        name = html.escape(utils.get_text(translation_key, context) if translation_key else code)
        text += f"{status} <code>{html.escape(code)}</code>\n📝 {name}\n🔗 {html.escape(url)}\n\n"
    
    await update.message.reply_text(text, parse_mode='HTML', disable_web_page_preview=True)


async def prompt_add_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnoma qo'shish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'adding_survey_title'
    
    await update.message.reply_text(
        utils.get_text('survey_add_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_survey_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnoma nomi kiritilganda"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_surveys_menu(update, context)
    
    context.user_data['new_survey_title'] = text
    context.user_data['state'] = 'adding_survey_url'
    
    await update.message.reply_text(
        utils.get_text('survey_add_url_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_add_survey_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnoma URL'i kiritilganda"""
    url = update.message.text
    
    if url == utils.get_text('btn_back', context):
        return await prompt_add_survey(update, context)
    
    title = context.user_data.get('new_survey_title')
    # Kodni nomidan yasab olamiz (faqat ingliz harflari va sonlar)
    import re
    code = re.sub(r'[^a-zA-Z0-9]', '_', title).lower()[:20]
    translation_key = f'survey_{code}_title'
    
    # Tarjimani qo'shamiz (barcha tillar uchun hozircha bir xil nom)
    lang_code = context.user_data.get('language', 'uz')
    update_translation(translation_key, lang_code, title)
    
    # So'rovnomani bazaga qo'shamiz
    if add_survey_link(code, url, translation_key):
        await update.message.reply_text(utils.get_text('survey_added', context))
    else:
        await update.message.reply_text(utils.get_text('survey_exists', context))
    
    context.user_data.pop('new_survey_title', None)
    await show_surveys_menu(update, context)


async def prompt_delete_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnomani o'chirish uchun so'rash"""
    if not utils.is_admin(update.effective_user.id):
        return
    
    context.user_data['state'] = 'deleting_survey'
    
    await list_surveys(update, context)
    
    await update.message.reply_text(
        utils.get_text('survey_delete_prompt', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_delete_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """So'rovnomani o'chirish"""
    text = update.message.text
    
    if text == utils.get_text('btn_back', context):
        return await show_surveys_menu(update, context)
    
    if delete_survey_link(text.lower()):
        await update.message.reply_text(utils.get_text('survey_deleted', context))
    else:
        await update.message.reply_text(utils.get_text('survey_not_found', context))
    
    await show_surveys_menu(update, context)
