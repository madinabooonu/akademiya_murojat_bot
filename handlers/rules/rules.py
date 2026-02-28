# handlers/rules.py
# Tartib qoidalar bilan bog'liq handlerlar

import os
from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import get_rules_keyboard, get_rules_detail_keyboard
from config.config import PDF_FILES
import utils.utils as utils


async def show_rules_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tartib qoidalar asosiy menyusi"""
    context.user_data['state'] = 'rules_main'

    await update.message.reply_text(
        f"📋 <b>{utils.get_text('rules_main', context)}</b>\n"
        f"{utils.get_text('stats_divider', context)}",
        reply_markup=get_rules_keyboard(context),
        parse_mode='HTML'
    )


async def show_grading_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Baholash jarayoni"""
    context.user_data['state'] = 'rules_grading'
    context.user_data['current_pdf'] = 'grading'

    text = utils.get_text('rules_grading_text', context)

    await update.message.reply_text(
        text,
        reply_markup=get_rules_detail_keyboard(context)
    )


async def show_exam_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Imtihon jarayoni"""
    context.user_data['state'] = 'rules_exam'
    context.user_data['current_pdf'] = 'exam'

    text = utils.get_text('rules_exam_text', context)

    await update.message.reply_text(
        text,
        reply_markup=get_rules_detail_keyboard(context)
    )


async def show_general_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Umumiy tartib qoidalar"""
    context.user_data['state'] = 'rules_general'
    context.user_data['current_pdf'] = 'rules'

    text = utils.get_text('rules_general_text', context)

    await update.message.reply_text(
        text,
        reply_markup=get_rules_detail_keyboard(context)
    )


async def download_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """PDF faylni yuklash"""
    pdf_type = context.user_data.get('current_pdf')

    if not pdf_type:
        await update.message.reply_text(utils.get_text('error_no_rules_type', context))
        return

    pdf_path = PDF_FILES.get(pdf_type)
    
    if not pdf_path:
        # Fallback to general rules if still somehow missing
        from config.config import BASE_DIR
        pdf_path = os.path.join(BASE_DIR, 'media', 'tartib_qoidalari.pdf')

    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as pdf_file:
            await update.message.reply_document(
                document=pdf_file,
                filename=os.path.basename(pdf_path),
                caption=utils.get_text('btn_download_pdf', context)
            )
    else:
        import logging
        logging.getLogger(__name__).error(f"Rule PDF not found: {pdf_path}")
        await update.message.reply_text(get_text('error_pdf_not_found', context))