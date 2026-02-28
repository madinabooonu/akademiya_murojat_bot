# handlers/complaint.py
# Murojaat bilan bog'liq handlerlar

from telegram import Update
from telegram.ext import ContextTypes

from config.config import COURSES, COMPLAINT_TYPES, FACULTIES, EDUCATION_TYPE, EDUCATION_LANG, ALL_DIRECTIONS
from database import save_complaint
from keyboards.keyboards import (
    get_courses_keyboard,
    get_complaint_types_keyboard,
    get_back_keyboard,
    get_main_menu_keyboard, get_faculties_keyboard, get_dynamic_keyboard, get_education_type_keyboard,
    get_education_lang_keyboard
)
from utils.utils import (
    get_course_code,
    get_complaint_type_code,
    get_direction_name,
    get_course_name,
    get_complaint_type_name, get_faculty_code, get_faculty_name,
    get_text,
    get_code_by_text,
    get_directions_by_faculty
)


async def start_complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['state'] = 'choosing_faculty'

    await update.message.reply_text(
        get_text('choose_faculty', context),
        reply_markup=get_faculties_keyboard(context)
    )


# ============================
# Fakultet tanlash
# ============================
async def handle_faculty_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    faculty_text = update.message.text
    
    # 🔙 Orqaga tugmasi
    if faculty_text == get_text('btn_back', context):
        from main import start
        return await start(update, context)

    faculty_code = get_code_by_text(faculty_text, FACULTIES, context)

    if not faculty_code:
        await update.message.reply_text(
            f"⚠️ {get_text('choose_faculty', context)}",
            reply_markup=get_faculties_keyboard(context)
        )
        return

    context.user_data['faculty'] = faculty_code
    context.user_data['state'] = 'choosing_direction'

    # Shu fakultetga tegishli yo'nalishlar
    directions = get_directions_by_faculty(faculty_code)
    context.user_data['directions_map'] = directions

    await update.message.reply_text(
        f"🏛 **{faculty_text}**\n{get_text('stats_divider', context)}\n\n"
        f"📍 {get_text('choose_direction', context)}",
        reply_markup=get_dynamic_keyboard(directions, context),
        parse_mode='Markdown'
    )


# ============================
# Yo'nalish tanlash
# ============================
async def handle_direction_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    direction_text = update.message.text
    directions = context.user_data.get('directions_map', {})

    # 🔙 Orqaga tugmasi
    if direction_text == get_text('btn_back', context):
        context.user_data['state'] = 'choosing_faculty'
        return await start_complaint(update, context)

    # Matndan kodni topamiz
    direction_code = None
    for code, trans_key in directions.items():
        if direction_text == get_text(trans_key, context):
            direction_code = code
            break

    if not direction_code:
        faculty_code = context.user_data.get('faculty')
        faculty_name = get_faculty_name(faculty_code, context)
        await update.message.reply_text(
            f"⚠️ {get_text('choose_direction', context)}",
            reply_markup=get_dynamic_keyboard(directions, context)
        )
        return

    # Tanlangan yo'nalishni saqlaymiz
    context.user_data['direction'] = direction_code
    
    # Magistratura uchun ta'lim turi va tilini so'ramaymiz - to'g'ridan to'g'ri kurs tanlashga o'tamiz
    faculty = context.user_data.get('faculty', '')
    if faculty == 'magistratura':
        context.user_data['state'] = 'choosing_course'
        await update.message.reply_text(
            f"📘 {direction_text}\n\n{get_text('choose_course', context)}",
            reply_markup=get_courses_keyboard(context)
        )
    else:
        # Oddiy fakultetlar uchun ta'lim turini so'raymiz
        context.user_data['state'] = 'choosing_education_type'
        await update.message.reply_text(
           f"📘 **{direction_text}**\n{get_text('stats_divider', context)}\n\n"
           f"📍 {get_text('choose_edu_type', context)}",
            reply_markup=get_education_type_keyboard(context),
            parse_mode='Markdown'
        )

# ============================
# Talim turini tanlash
# ============================
async def handle_education_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    edu_type_text = update.message.text
    
    # 🔙 Orqaga tugmasi
    if edu_type_text == get_text('btn_back', context):
        # Yo'nalish tanlashga qaytadi
        directions = context.user_data.get('directions_map', {})
        faculty_code = context.user_data.get('faculty')
        faculty_name = get_faculty_name(faculty_code, context)
        context.user_data['state'] = 'choosing_direction'
        return await update.message.reply_text(
            f"🏛 {faculty_name}\n\n{get_text('choose_direction', context)}",
            reply_markup=get_dynamic_keyboard(directions, context)
        )

    edu_type_code = get_code_by_text(edu_type_text, EDUCATION_TYPE, context)

    if not edu_type_code:
        await update.message.reply_text(
            f"⚠️ {get_text('choose_edu_type', context)}",
            reply_markup=get_education_type_keyboard(context)
        )
        return

    # Ta’lim turini saqlaymiz
    context.user_data['education_type'] = edu_type_code
    context.user_data['state'] = 'choosing_education_lang'

    await update.message.reply_text(
        f"🎓 **{edu_type_text}**\n{get_text('stats_divider', context)}\n\n"
        f"📍 {get_text('choose_edu_lang', context)}",
        reply_markup=get_education_lang_keyboard(context),
        parse_mode='Markdown'
    )

async def handle_education_lang_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_text = update.message.text
    
    # 🔙 Orqaga tugmasi
    if lang_text == get_text('btn_back', context):
        context.user_data['state'] = 'choosing_education_type'
        return await update.message.reply_text(
            get_text('choose_edu_type', context),
            reply_markup=get_education_type_keyboard(context)
        )

    lang_code = get_code_by_text(lang_text, EDUCATION_LANG, context)

    if not lang_code:
        await update.message.reply_text(
            f"⚠️ {get_text('choose_edu_lang', context)}",
            reply_markup=get_education_lang_keyboard(context)
        )
        return

    context.user_data['education_language'] = lang_code
    context.user_data['state'] = 'choosing_course'

    await update.message.reply_text(
        f"🌐 {lang_text}\n\n{get_text('choose_course', context)}",
        reply_markup=get_courses_keyboard(context)
    )


async def handle_course_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from config.config import COURSES_REGULAR, COURSES_MAGISTR
    course_text = update.message.text
    faculty = context.user_data.get('faculty', '')
    
    # 🔙 Orqaga tugmasi - Magistratura uchun yo'nalishga, boshqalar uchun til tanlashga
    if course_text == get_text('btn_back', context):
        if faculty == 'magistratura':
            # Magistratura - yo'nalish tanlashga qaytadi
            directions = context.user_data.get('directions_map', {})
            faculty_name = get_faculty_name(faculty, context)
            context.user_data['state'] = 'choosing_direction'
            return await update.message.reply_text(
                f"🏛 {faculty_name}\n\n{get_text('choose_direction', context)}",
                reply_markup=get_dynamic_keyboard(directions, context)
            )
        else:
            context.user_data['state'] = 'choosing_education_lang'
            return await update.message.reply_text(
                get_text('choose_edu_lang', context),
                reply_markup=get_education_lang_keyboard(context)
            )

    # Fakultetga qarab tegishli kurslarni tekshirish
    if faculty == 'magistratura':
        courses = COURSES_MAGISTR
    else:
        courses = COURSES_REGULAR
    
    course_code = get_code_by_text(course_text, courses, context)

    if not course_code:
        await update.message.reply_text(
            f"⚠️ {get_text('choose_course', context)}",
            reply_markup=get_courses_keyboard(context)
        )
        return
    
    # CRITICAL FIX: This code was previously unreachable (after return)
    context.user_data['course'] = course_code
    context.user_data['state'] = 'choosing_complaint_type'

    await update.message.reply_text(
        get_text('choose_complaint_type', context),
        reply_markup=get_complaint_types_keyboard(context)
    )


async def handle_complaint_type_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Murojaat turi tanlanganida"""
    complaint_type_text = update.message.text

    # 🔙 Orqaga tugmasi
    if complaint_type_text == get_text('btn_back', context):
        context.user_data['state'] = 'choosing_course'
        return await update.message.reply_text(
            get_text('choose_course', context),
            reply_markup=get_courses_keyboard(context)
        )

    complaint_type_code = get_code_by_text(complaint_type_text, COMPLAINT_TYPES, context)

    if not complaint_type_code:
        await update.message.reply_text(
             f"⚠️ {get_text('choose_complaint_type', context)}",
             reply_markup=get_complaint_types_keyboard(context)
        )
        return

    if complaint_type_code:
        context.user_data['complaint_type'] = complaint_type_code

        if complaint_type_code == 'teacher':
            context.user_data['state'] = 'entering_subject'
            await update.message.reply_text(
                get_text('enter_subject', context),
                reply_markup=get_back_keyboard(context)
            )
        else:
            context.user_data['state'] = 'entering_message'
            await ask_complaint_message(update, context)


async def handle_subject_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fan nomi kiritilganida"""
    subject_name = update.message.text
    
    # 🔙 Orqaga tugmasi
    if subject_name == get_text('btn_back', context):
        context.user_data['state'] = 'choosing_complaint_type'
        return await update.message.reply_text(
            get_text('choose_complaint_type', context),
            reply_markup=get_complaint_types_keyboard(context)
        )

    context.user_data['subject_name'] = subject_name
    context.user_data['state'] = 'entering_teacher'

    await update.message.reply_text(
        f"📚 {get_text('enter_subject', context)}\n└ {subject_name}\n\n"
        f"👨‍🏫 {get_text('enter_teacher', context)}",
        reply_markup=get_back_keyboard(context)
    )


async def handle_teacher_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'qituvchi ismi kiritilganida"""
    teacher_name = update.message.text
    
    # 🔙 Orqaga tugmasi
    if teacher_name == get_text('btn_back', context):
        context.user_data['state'] = 'entering_subject'
        return await update.message.reply_text(
            get_text('enter_subject', context),
            reply_markup=get_back_keyboard(context)
        )

    context.user_data['teacher_name'] = teacher_name
    context.user_data['state'] = 'entering_message'

    await ask_complaint_message(update, context)


async def ask_complaint_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Murojaat xabarini so'rash"""
    faculty_name = get_faculty_name(context.user_data['faculty'], context)
    direction_name = get_direction_name(context.user_data['direction'], context)
    course_name = get_course_name(context.user_data['course'], context)
    complaint_type_name = get_complaint_type_name(context.user_data['complaint_type'], context)

    text = (
        f"📝 **MUROJAAT MA'LUMOTLARI**\n"
        f"{get_text('stats_divider', context)}\n\n"
        f"🏛 **Fakultet:** `{faculty_name}`\n"
        f"🎯 **Yo'nalish:** `{direction_name}`\n"
        f"📚 **Kurs:** `{course_name}`\n"
        f"📋 **Tur:** `{complaint_type_name}`\n"
    )

    if context.user_data['complaint_type'] == 'teacher':
        text += f"📖 **Fan:** `{context.user_data.get('subject_name', '')}`\n"
        text += f"👨‍🏫 **O'qituvchi:** `{context.user_data.get('teacher_name', '')}`\n"

    text += (
        f"\n{get_text('stats_divider', context)}\n"
        f"{get_text('anonymous_notice', context)}\n\n"
        f"📍 {get_text('enter_message', context)}"
    )

    await update.message.reply_text(text, reply_markup=get_back_keyboard(context), parse_mode='Markdown')


async def handle_complaint_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Murojaat xabari kiritilganida"""
    message_text = update.message.text

    # Ma'lumotlarni to'plash
    complaint_data = {
        'faculty': context.user_data.get('faculty', ''),
        'direction': context.user_data.get('direction', ''),
        'course': context.user_data.get('course', ''),
        'education_type': context.user_data.get('education_type', ''),
        'education_language': context.user_data.get('education_language', ''),
        'complaint_type': context.user_data.get('complaint_type', ''),
        'message': message_text,
        'source': 'bot'
    }

    if context.user_data.get('complaint_type') == 'teacher':
        complaint_data['subject_name'] = context.user_data.get('subject_name', '')
        complaint_data['teacher_name'] = context.user_data.get('teacher_name', '')

    # Bazaga saqlash
    save_complaint(complaint_data)

    # Tasdiqlash xabari
    confirmation_text = (
        f"{get_text('complaint_accepted', context)}\n"
        f"{get_text('stats_divider', context)}\n\n"
        f"{get_text('complaint_success_footer', context)}\n\n"
        f"🚀 _Rahmat!_"
    )

    await update.message.reply_text(
        confirmation_text,
        reply_markup=get_main_menu_keyboard(context),
        parse_mode='Markdown'
    )

    # Contextni tozalash
    keys_to_remove = [
        'state', 'faculty', 'direction', 'course', 'education_type', 
        'education_language', 'complaint_type', 'subject_name', 
        'teacher_name', 'directions_map'
    ]
    for key in keys_to_remove:
        context.user_data.pop(key, None)
