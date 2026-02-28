# handlers/admin.py
# Admin panel bilan bog'liq handlerlar

import logging
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import get_admin_keyboard, get_export_menu_keyboard, get_settings_keyboard
from utils.utils import is_admin, get_direction_name, get_course_name, get_complaint_type_name, get_faculty_name, get_text
from database import get_all_complaints, get_statistics
from config.export import export_to_excel , export_to_excel_for_lesson_ratings

# CRUD settings importlari
from handlers.admins.crud_settings import show_settings_menu

logger = logging.getLogger(__name__)


async def show_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panelni ko'rsatish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    context.user_data['state'] = 'admin_panel'

    await update.message.reply_text(
        get_text('admin_panel_title', context),
        reply_markup=get_admin_keyboard(context)
    )


async def show_export_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Excel export menyusini ko'rsatish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    context.user_data['state'] = 'admin_export_menu'

    await update.message.reply_text(
        get_text('export_menu_title', context),
        reply_markup=get_export_menu_keyboard(context)
    )


def generate_progress_bar(count, total, length=10):
    """Matnli progress bar yaratish"""
    if total == 0: return "░" * length
    filled_len = int(round(length * count / float(total)))
    per = round(100.0 * count / float(total), 1)
    bar = '█' * filled_len + '░' * (length - filled_len)
    return f"`{bar}` {per}%"

async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Statistikalarni professional ko'rinishda ko'rsatish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    stats = get_statistics()
    total = stats['total']
    
    # Header
    stats_text = f"{get_text('stats_header_main', context)}\n"
    stats_text += f"{get_text('stats_divider', context)}\n\n"
    stats_text += f"{get_text('stats_total_line', context).format(total=total)}\n"

    # Directions
    if stats['by_direction']:
        stats_text += f"{get_text('stats_header_directions', context)}\n"
        for direction, count in stats['by_direction']:
            bar = generate_progress_bar(count, total)
            stats_text += f"• *{get_direction_name(direction, context)}*\n  {bar} `{count}` ta\n"

    # Types
    if stats['by_type']:
        stats_text += f"{get_text('stats_header_types', context)}\n"
        for complaint_type, count in stats['by_type']:
            bar = generate_progress_bar(count, total)
            stats_text += f"• *{get_complaint_type_name(complaint_type, context)}*\n  {bar} `{count}` ta\n"

    # Courses
    if stats['by_course']:
        stats_text += f"{get_text('stats_header_courses', context)}\n"
        for course, count in stats['by_course']:
            bar = generate_progress_bar(count, total)
            stats_text += f"• *{get_course_name(course, context)}*\n  {bar} `{count}` ta\n"

    # Weekly
    stats_text += f"{get_text('stats_header_weekly', context)}\n"
    if stats['weekly']:
        for date_str, count in stats['weekly']:
            stats_text += f"🗓 `{date_str}`: *{count} ta*\n"
    else:
        stats_text += f"  {get_text('no_data', context)}\n"

    stats_text += f"\n{get_text('stats_divider', context)}\n"
    stats_text += f"✨ _Hisobot vaqti: {stats.get('now', 'Hozir')}_"

    await update.message.reply_text(stats_text, parse_mode='Markdown')


async def view_complaints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Murojaatlarni ko'rish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    complaints = get_all_complaints(limit=10)

    if not complaints:
        response = get_text('no_complaints', context)
    else:
        response = get_text('last_10_complaints', context) + "\n"
        for comp in complaints:
            # Schema: id[0], faculty[1], direction[2], course[3], edu_type[4], edu_lang[5], 
            #         complaint_type[6], subject[7], teacher[8], message[9], date[10]
            response += f"🆔 ID: {comp[0]}\n"
            response += f"🏛 {get_faculty_name(comp[1], context)}\n"
            response += f"🎯 {get_direction_name(comp[2], context)}\n"
            response += f"📚 {get_course_name(comp[3], context)}\n"
            response += f"📝 {get_complaint_type_name(comp[6], context)}\n"

            if comp[7]:  # Fan nomi
                response += f"📖 Fan: {comp[7]}\n"
            if comp[8]:  # O'qituvchi
                response += f"👨‍🏫 O'qituvchi: {comp[8]}\n"

            msg = comp[9] if comp[9] else ""
            response += f"💬 Xabar: {msg[:100]}...\n" if len(msg) > 100 else f"💬 Xabar: {msg}\n"
            response += f"📅 Sana: {comp[10]}\n"
            response += "─" * 30 + "\n"

    await update.message.reply_text(response)


async def export_to_excel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Excel faylga export qilish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    try:
        await update.message.reply_text(get_text('excel_preparing', context))

        filename = export_to_excel()

        if filename:
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=filename,
                    caption="📊 Excel Report"
                )
            await update.message.reply_text(get_text('excel_success', context))
        else:
            await update.message.reply_text(get_text('excel_error', context))

    except Exception as e:
        logger.error(f"Excel export xatosi: {e}")
        await update.message.reply_text(get_text('excel_error', context))

async def export_to_daily_lesson_excel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Excel faylga export qilish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    try:
        await update.message.reply_text(get_text('excel_preparing', context))

        filename = export_to_excel_for_lesson_ratings()

        if filename:
            with open(filename, 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename=filename,
                    caption="📊 Daily Lesson Ratings"
                )
            await update.message.reply_text(get_text('excel_success', context))
        else:
            await update.message.reply_text(get_text('excel_error', context))

    except Exception as e:
        logger.error(f"Excel export xatosi: {e}")
        await update.message.reply_text(get_text('excel_error', context))


async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dashboardni professional ko'rinishda ko'rsatish"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(get_text('no_permission', context))
        return

    stats = get_statistics()

    dashboard_text = f"📈 **AKADEMIYA MONITORING DASHBOARD** 📈\n"
    dashboard_text += f"{get_text('stats_divider', context)}\n\n"
    
    dashboard_text += f"📅 **BUGUN:** `{stats['today']}` ta\n"
    dashboard_text += f"🗓 **SHU HAFTA:** `{stats['week']}` ta\n"
    dashboard_text += f"📅 **SHU OY:** `{stats['month']}` ta\n\n"

    if stats['top_direction'] and stats['top_direction'][0]:
        dashboard_text += f"🏆 **ENG FAOL YO'NALISH:**\n"
        dashboard_text += f"✨ {get_direction_name(stats['top_direction'][0], context)} (`{stats['top_direction'][1]}` ta)\n"

    dashboard_text += f"\n{get_text('stats_divider', context)}\n"
    dashboard_text += f"🚀 _Tizim barqaror ishlamoqda_"

    await update.message.reply_text(dashboard_text, parse_mode='Markdown')
