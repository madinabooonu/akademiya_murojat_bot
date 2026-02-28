from telegram import Update
from telegram.ext import ContextTypes
from keyboards.keyboards import (
    get_directions_keyboard,
    get_courses_keyboard,
    get_back_keyboard,
    get_main_menu_keyboard,
    get_yes_no_keyboard,
    get_rating_keyboard
)
from utils.utils import (
    get_direction_code,
    get_course_code,
    get_text,
    get_code_by_text,
    get_all_directions,
    get_courses
)
from config.config import ALL_DIRECTIONS, COURSES, FACULTIES
from database import save_lesson_rating


# Lesson daily rating savollari - ENDI BAZADAN OLINADI
def get_questions(context):
    """Savollarni bazadan olish"""
    try:
        from database_models import get_rating_questions
        questions = get_rating_questions()
        result = []
        for question_number, translation_key, answer_type in questions:
            result.append({
                'text': get_text(translation_key, context),
                'type': answer_type,
                'number': question_number
            })
        return result
    except Exception:
        # Fallback - eski usul
        return [
            {'text': get_text('rating_q1', context), 'type': 'scale', 'number': 1},
            {'text': get_text('rating_q2', context), 'type': 'scale', 'number': 2},
            {'text': get_text('rating_q3', context), 'type': 'scale', 'number': 3},
            {'text': get_text('rating_q4', context), 'type': 'scale', 'number': 4},
            {'text': get_text('rating_q5', context), 'type': 'scale', 'number': 5},
            {'text': get_text('rating_q6', context), 'type': 'yes_no', 'number': 6},
        ]

async def start_lesson_daily_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # context.user_data.clear() # TILNI SAQLASH UCHUN
    context.user_data['state'] = 'rating_direction'

    await update.message.reply_text(
        get_text('rating_intro', context) + "\n\n" + get_text('choose_direction', context),
        reply_markup=get_directions_keyboard(context)
    )


async def handle_lesson_direction_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    direction_text = update.message.text
    
    # 🔙 Orqaga tugmasi
    if direction_text == get_text('btn_back', context):
        from main import start
        return await start(update, context)

    # ALL_DIRECTIONS yuqorida import qilingan
    direction_code = get_code_by_text(direction_text, ALL_DIRECTIONS, context)

    if direction_code:
        context.user_data['direction'] = direction_code
        context.user_data['state'] = 'rating_course'

        await update.message.reply_text(
            f"✅ {direction_text}\n\n{get_text('choose_course', context)}",
            reply_markup=get_courses_keyboard(context)
        )
    else:
        await update.message.reply_text(
            f"⚠️ {get_text('choose_direction', context)}",
            reply_markup=get_directions_keyboard(context)
        )


async def handle_lesson_course_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    course_text = update.message.text

    # 🔙 Orqaga tugmasi
    if course_text == get_text('btn_back', context):
        context.user_data['state'] = 'rating_direction'
        return await update.message.reply_text(
            get_text('choose_direction', context),
            reply_markup=get_directions_keyboard(context)
        )

    # COURSES yuqorida import qilingan
    course_code = get_code_by_text(course_text, COURSES, context)

    if course_code:
        context.user_data['course'] = course_code
        context.user_data['state'] = 'rating_subject'

        await update.message.reply_text(
            get_text('enter_subject', context),
            reply_markup=get_back_keyboard(context)
        )
    else:
        await update.message.reply_text(
            f"⚠️ {get_text('choose_course', context)}",
            reply_markup=get_courses_keyboard(context)
        )


async def handle_subject_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subject_name = update.message.text

    if subject_name == get_text('btn_back', context):
        context.user_data['state'] = 'rating_course'
        return await update.message.reply_text(
            get_text('choose_course', context),
            reply_markup=get_courses_keyboard(context)
        )

    context.user_data['subject_name'] = subject_name
    context.user_data['state'] = 'rating_teacher'

    await update.message.reply_text(
        get_text('enter_teacher', context),
        reply_markup=get_back_keyboard(context)
    )


async def handle_teacher_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teacher_name = update.message.text

    if teacher_name == get_text('btn_back', context) or teacher_name == "🔙 Orqaga":
        context.user_data['state'] = 'rating_subject'
        return await update.message.reply_text(
            get_text('enter_subject', context),
            reply_markup=get_back_keyboard(context)
        )

    context.user_data['teacher_name'] = teacher_name
    context.user_data['question_index'] = 0
    context.user_data['state'] = 'rating_process'

    questions = get_questions(context)
    step_info = get_text('step_progress', context).format(step=1)
    
    await update.message.reply_text(
        f"🧑‍🏫 **DARS BAHOLASH**\n{get_text('stats_divider', context)}\n\n"
        f"{step_info}\n"
        f"❓ **{questions[0]['text']}**\n\n"
        f"📍 {get_text('rating_score_query', context) if questions[0]['type'] == 'scale' else get_text('rating_yes_no_query', context)}",
        reply_markup=get_rating_keyboard(context) if questions[0]['type'] == 'scale' else get_yes_no_keyboard(context),
        parse_mode='Markdown'
    )


async def handle_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        i = context.user_data.get('question_index', 0)
        rating_text = update.message.text
        if not rating_text:
            return

        questions = get_questions(context)
        current_question = questions[i] if i < len(questions) else None

        # --- Safety Check ---
        if not current_question:
            context.user_data['state'] = 'rating_teacher'
            return await update.message.reply_text(
                get_text('enter_teacher', context),
                reply_markup=get_back_keyboard(context)
            )

        # --- Orqaga qaytish ---
        back_text = get_text('btn_back', context)
        if rating_text == back_text or rating_text == "🔙 Orqaga" or rating_text.lower() == "orqaga":
            if i == 0:
                context.user_data['state'] = 'rating_teacher'
                return await update.message.reply_text(
                    get_text('enter_teacher', context),
                    reply_markup=get_back_keyboard(context)
                )
            else:
                context.user_data['question_index'] -= 1
                idx = context.user_data['question_index']
                prev_q = questions[idx]
                step_info = get_text('step_progress', context).format(step=idx + 1)
                query_text = get_text('rating_score_query', context) if prev_q['type'] == 'scale' else get_text('rating_yes_no_query', context)
                keyboard = get_rating_keyboard(context) if prev_q['type'] == 'scale' else get_yes_no_keyboard(context)
                await update.message.reply_text(
                    f"🧑‍🏫 **DARS BAHOLASH**\n{get_text('stats_divider', context)}\n\n"
                    f"{step_info}\n"
                    f"❓ **{prev_q['text']}**\n\n"
                    f"📍 {query_text}",
                    reply_markup=keyboard,
                    parse_mode='Markdown'
                )
                return

        # --- Savol turi tekshiruvi ---
        clean_rating = rating_text.strip()
        
        if current_question['type'] == 'yes_no':
            yes_text = get_text('btn_yes', context)
            no_text = get_text('btn_no', context)
            
            # Kirishni normallashtirish (kichik harflar va har xil variantlar)
            lower_rating = clean_rating.lower()
            if lower_rating == yes_text.lower() or lower_rating == "ha" or lower_rating == "yes" or lower_rating == "да":
                final_answer = yes_text
            elif lower_rating == no_text.lower() or lower_rating.startswith("yo") or lower_rating == "no" or lower_rating == "нет":
                final_answer = no_text
            else:
                return await update.message.reply_text(
                    f"⚠️ {get_text('error_yes_no', context)}",
                    reply_markup=get_yes_no_keyboard(context)
                )
        else:
            # Scale turi - 1-5 ball
            if clean_rating not in ["1", "2", "3", "4", "5"]:
                return await update.message.reply_text(
                    get_text('error_select_number', context),
                    reply_markup=get_rating_keyboard(context)
                )
            final_answer = clean_rating

        # Javobni vaqtinchalik saqlaymiz
        if 'answers' not in context.user_data:
            context.user_data['answers'] = {}
        
        context.user_data['answers'][current_question['number']] = final_answer

        # Keyingi savolga o'tish
        context.user_data['question_index'] += 1
        next_idx = context.user_data['question_index']

        # Agar savollar tugasa
        if next_idx >= len(questions):
            # Hammasini bittada saqlash
            try:
                save_lesson_rating({
                    'telegram_id': update.effective_user.id,
                    'direction': context.user_data.get('direction', ''),
                    'course': context.user_data.get('course', ''),
                    'subject_name': context.user_data.get('subject_name', ''),
                    'teacher_name': context.user_data.get('teacher_name', ''),
                    'answers': context.user_data['answers']
                })
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Error saving lesson rating: {e}")

            # Yakuniy xabar
            confirmation_text = (
                f"{get_text('rating_thanks', context)}\n"
                f"{get_text('stats_divider', context)}\n\n"
                f"{get_text('rating_success_footer', context)}\n\n"
                f"🚀 _Rahmat!_"
            )
            await update.message.reply_text(
                confirmation_text,
                reply_markup=get_main_menu_keyboard(context),
                parse_mode='Markdown'
            )
            
            # Holatni tozalash va asosiy menyuga qaytarish
            keys_to_remove = ['state', 'direction', 'course', 'subject_name', 'teacher_name', 'question_index', 'answers']
            for key in keys_to_remove:
                context.user_data.pop(key, None)
            
            # State'ni bo'shatib qo'yamiz
            context.user_data['state'] = ''
            return

        # Keyingi savol
        next_q = questions[next_idx]
        step_info = get_text('step_progress', context).format(step=next_idx + 1)
        query_text = get_text('rating_score_query', context) if next_q['type'] == 'scale' else get_text('rating_yes_no_query', context)
        keyboard = get_rating_keyboard(context) if next_q['type'] == 'scale' else get_yes_no_keyboard(context)
        
        await update.message.reply_text(
            f"🧑‍🏫 **DARS BAHOLASH**\n{get_text('stats_divider', context)}\n\n"
            f"{step_info}\n"
            f"❓ **{next_q['text']}**\n\n"
            f"📍 {query_text}",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Critical error in handle_rating: {e}")
        # Xatolik bo'lsa hech bo'lmasa foydalanuvchiga xabar beramiz
        await update.message.reply_text(
            "⚠️ Xatolik yuz berdi. Iltimos, asosiy menyuga qayting.",
            reply_markup=get_main_menu_keyboard(context)
        )
        context.user_data['state'] = ''
