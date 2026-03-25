# web_server.py
# Mini App uchun aiohttp web server

import os
import json
import logging
from aiohttp import web
from aiohttp.web import middleware
import sqlite3

from config.config import DATABASE_NAME
from database import save_complaint, save_lesson_rating

logger = logging.getLogger(__name__)

SHARED_BOT = None

# ============================================
# MIDDLEWARE
# ============================================

@middleware
async def cors_middleware(request, handler):
    """CORS headers qo'shish va OPTIONS so'rovlarini qayta ishlash"""
    if request.method == 'OPTIONS':
        response = web.Response()
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            # HTTP xatolarini (404, 403 va h.k.) o'z holicha o'tkazib yuboramiz
            # Faqat CORS headerlarini qo'shish kerak pastda
            response = ex
        except Exception as e:
            logger.error(f"Middleware error: {e}", exc_info=True)
            response = web.json_response({'error': str(e)}, status=500)
            
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# ============================================
# SECURITY HELPERS
# ============================================

def admin_required(handler):
    """Admin huquqini tekshirish uchun decorator"""
    async def wrapper(request):
        user_id = request.query.get('user_id')
        if not user_id:
            return web.json_response({'error': 'Unauthorized: No user_id'}, status=401)
        
        try:
            import utils.utils as utils
            if not utils.is_admin(int(user_id)):
                return web.json_response({'error': 'Forbidden: Not an admin'}, status=403)
        except (ValueError, TypeError):
            return web.json_response({'error': 'Invalid user_id'}, status=400)
            
        return await handler(request)
    return wrapper


# ============================================
# DATABASE HELPERS
# ============================================

def get_db_connection():
    """Database ulanish"""
    return sqlite3.connect(DATABASE_NAME)


def get_translations(lang_code='uz'):
    """Tarjimalarni olish (Bazadan + LOCALES fallback)"""
    from config.locales import LOCALES
    # Boshlang'ich tarjimalar locales.py dan
    translations = LOCALES.get(lang_code, LOCALES.get('uz', {})).copy()
    
    # Bazadan yuklash va ustiga yozish (agar mavjud bo'lsa)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM translations WHERE language_code = ?', (lang_code,))
        for key, value in cursor.fetchall():
            translations[key] = value
        conn.close()
    except Exception as e:
        logger.error(f"Error fetching translations from DB: {e}")
        
    return translations


def get_faculties_from_db():
    """Fakultetlarni olish"""
    from database_models import get_faculties_dict
    return [{'code': k, 'translation_key': v} for k, v in get_faculties_dict().items()]


def get_directions_from_db(faculty_code=None):
    """Yo'nalishlarni olish"""
    from database_models import get_directions_by_faculty, get_all_directions_dict
    if faculty_code:
        return [{'code': k, 'faculty_code': faculty_code, 'translation_key': v} for k, v in directions.items()]
    else:
        directions = get_all_directions_dict()
        return [{'code': k, 'translation_key': v} for k, v in directions.items()]


def get_courses_from_db(course_type=None):
    """Kurslarni olish"""
    from database_models import get_courses_dict
    courses = get_courses_dict(course_type)
    return [{'code': k, 'translation_key': v} for k, v in courses.items()]


def get_education_types_from_db():
    """Ta'lim turlarini olish"""
    from database_models import get_education_types_dict
    return [{'code': k, 'translation_key': v} for k, v in get_education_types_dict().items()]


def get_education_languages_from_db():
    """Ta'lim tillarini olish"""
    from database_models import get_education_languages_dict
    return [{'code': k, 'translation_key': v} for k, v in get_education_languages_dict().items()]


def get_complaint_types_from_db():
    """Murojaat turlarini olish"""
    from database_models import get_complaint_types_dict
    return [{'code': k, 'translation_key': v} for k, v in get_complaint_types_dict().items()]


def get_rating_questions_from_db():
    """Baholash savollarini olish"""
    from database_models import get_rating_questions
    return [
        {'question_number': q[0], 'translation_key': q[1], 'answer_type': q[2]}
        for q in get_rating_questions()
    ]


def get_survey_links_from_db():
    """So'rovnoma havolalarini olish"""
    from database_models import get_all_survey_links
    return [
        {'code': s[0], 'url': s[1], 'translation_key': s[2]}
        for s in get_all_survey_links()
        if s[3]  # only active (is_active = 1)
    ]


# Redundant code removed


# ============================================
# API ROUTES
# ============================================

async def api_health(request):
    """Health check"""
    return web.json_response({'status': 'ok', 'service': 'akademiya-miniapp'})


async def api_translations(request):
    """Tarjimalarni olish"""
    lang = request.match_info.get('lang', 'uz')
    translations = get_translations(lang)
    return web.json_response(translations)


async def api_faculties(request):
    """Fakultetlarni olish"""
    faculties = get_faculties_from_db()
    return web.json_response({'faculties': faculties})


async def api_directions(request):
    """Yo'nalishlarni olish"""
    faculty_code = request.match_info.get('faculty', None)
    directions = get_directions_from_db(faculty_code)
    return web.json_response({'directions': directions})


async def api_courses(request):
    """Kurslarni olish"""
    course_type = request.query.get('type', None)
    courses = get_courses_from_db(course_type)
    return web.json_response({'courses': courses})


async def api_education_types(request):
    """Ta'lim turlarini olish"""
    edu_types = get_education_types_from_db()
    return web.json_response({'education_types': edu_types})


async def api_education_languages(request):
    """Ta'lim tillarini olish"""
    edu_langs = get_education_languages_from_db()
    return web.json_response({'education_languages': edu_langs})


async def api_complaint_types(request):
    """Murojaat turlarini olish"""
    complaint_types = get_complaint_types_from_db()
    return web.json_response({'complaint_types': complaint_types})


async def api_rating_questions(request):
    """Baholash savollarini olish"""
    questions = get_rating_questions_from_db()
    return web.json_response({'questions': questions})


async def api_submit_rating(request):
    """Baholash yuborish"""
    try:
        data = await request.json()
        data['source'] = 'webapp'
        uid = save_lesson_rating(data)
        from database import record_activity
        record_activity(data.get('telegram_id'), 'submit_rating', 'webapp', {'uid': uid})
        return web.json_response({'success': True, 'uid': uid})
    except Exception as e:
        logger.error(f"Error submitting rating: {e}")
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def api_surveys(request):
    """So'rovnomalarni olish"""
    surveys = get_survey_links_from_db()
    return web.json_response({'surveys': surveys})


async def api_languages(request):
    """Faol tillarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT code, name FROM languages WHERE is_active = 1')
    languages = [{'code': row[0], 'name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return web.json_response({'languages': languages})


async def api_submit_complaint(request):
    """Murojaat yuborish"""
    try:
        data = await request.json()
        data['source'] = 'webapp'
        
        # Validatsiya
        required_fields = ['faculty', 'direction', 'course', 'complaint_type', 'message']
        for field in required_fields:
            if not data.get(field):
                return web.json_response(
                    {'success': False, 'error': f'Missing field: {field}'}, 
                    status=400
                )
        
        uid = save_complaint(data)
        from database import record_activity
        record_activity(data.get('telegram_id'), 'submit_complaint', 'webapp', {'uid': uid})
        
        return web.json_response({
            'success': True, 
            'uid': uid,
            'message': 'Murojaat muvaffaqiyatli qabul qilindi!'
        })
    except Exception as e:
        logger.error(f"Error submitting complaint: {e}")
        return web.json_response(
            {'success': False, 'error': str(e)}, 
            status=500
        )


async def api_config(request):
    """Barcha konfiguratsiyani birdan olish (optimizatsiya)"""
    lang = request.query.get('lang', 'uz')
    user_id = request.query.get('user_id')
    
    config = {
        'translations': get_translations(lang),
        'faculties': get_faculties_from_db(),
        'education_types': get_education_types_from_db(),
        'education_languages': get_education_languages_from_db(),
        'complaint_types': get_complaint_types_from_db(),
        'rating_questions': get_rating_questions_from_db(),
        'surveys': get_survey_links_from_db(),
        'directions': get_directions_from_db(),
        'courses': {
            'regular': get_courses_from_db('regular'),
            'magistr': get_courses_from_db('magistr')
        },
        'pdf_files': {
            'grading': 'media/baholash_jarayoni.pdf',
            'exam': 'media/imtihon_jarayoni.pdf',
            'rules': 'media/tartib_qoidalari.pdf'
        }
    }
    
    config['is_admin'] = False
    if user_id:
        try:
            import utils.utils as utils
            config['is_admin'] = utils.is_admin(int(user_id))
        except (ValueError, TypeError):
            pass
        
    return web.json_response(config)

async def api_admin_stats(request):
    from database import get_statistics
    stats = get_statistics()
    return web.json_response(stats)

async def api_admin_dashboard(request):
    from database import get_admin_dashboard_data
    stats = get_admin_dashboard_data()
    return web.json_response(stats)

async def api_admin_logs(request):
    """Xatolarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM error_logs ORDER BY timestamp DESC LIMIT 50')
    logs = [
        {
            'id': row[0],
            'timestamp': row[1],
            'level': row[2],
            'message': row[3],
            'traceback': row[4],
            'context': json.loads(row[5]) if row[5] else None
        } for row in cursor.fetchall()
    ]
    conn.close()
    return web.json_response({'logs': logs})

async def api_admin_activity(request):
    """Oxirgi harakatlarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT telegram_id, action, source, timestamp 
        FROM activity_logs 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''')
    activity = [
        {
            'user_id': r[0],
            'action': r[1],
            'source': r[2],
            'time': r[3]
        } for r in cursor.fetchall()
    ]
    conn.close()
    return web.json_response({'activity': activity})

async def api_admin_settings_list(request):
    setting_type = request.match_info.get('type')
    if setting_type == 'admins':
        from database_models import get_all_admins
        return web.json_response({'items': get_all_admins()})
    elif setting_type == 'faculties':
        from database_models import get_all_faculties
        return web.json_response({'items': get_all_faculties()})
    elif setting_type == 'directions':
        from database_models import get_all_directions_dict
        return web.json_response({'items': get_all_directions_dict()})
    elif setting_type == 'questions':
        from database_models import get_rating_questions
        return web.json_response({'items': get_rating_questions()})
    return web.json_response({'error': 'Invalid type'}, status=400)
    
async def api_admin_delete_setting(request):
    """Admin sozlamalarini o'chirish"""
    setting_type = request.match_info.get('type')
    setting_id = request.match_info.get('id')
    
    try:
        if setting_type == 'admins':
            from database_models import remove_admin
            success = remove_admin(int(setting_id))
        elif setting_type == 'faculties':
            from database_models import delete_faculty
            success = delete_faculty(setting_id)
        elif setting_type == 'directions':
            from database_models import delete_direction
            success = delete_direction(setting_id)
        elif setting_type == 'questions':
            from database_models import delete_rating_question
            success = delete_rating_question(int(setting_id))
        else:
            return web.json_response({'error': 'Invalid type'}, status=400)
            
        if success:
            return web.json_response({'success': True})
        else:
            return web.json_response({'error': 'Not found or failed'}, status=404)
    except Exception as e:
        logger.error(f"Error deleting setting: {e}")
        return web.json_response({'error': str(e)}, status=500)

async def api_admin_translations_list(request):
    lang = request.query.get('lang', 'uz')
    try:
        from database_models import get_all_translations
        return web.json_response(get_all_translations(lang))
    except ImportError:
        # Fallback if not implemented
        return web.json_response({'error': 'Not implemented'}, status=501)

import asyncio

async def broadcast_task(bot, users, message_text):
    """Foydalanuvchilarga xabar jo'natish (Rate Limit bilan)"""
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=message_text, parse_mode='HTML')
            success += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {user_id}: {e}")
            failed += 1
            
        # Rate limit: ~30 msg/s for non-group messages -> 0.05s delay logic
        await asyncio.sleep(0.05)
        
    logger.info(f"Broadcast completed. Success: {success}, Failed: {failed}")

async def api_admin_broadcast(request):
    """Barcha foydalanuvchilarga xabar jo'natish endpoint'i"""
    if not SHARED_BOT:
        return web.json_response({'error': 'Bot instance not available'}, status=500)
        
    try:
        data = await request.json()
        message_text = data.get('message')
        
        if not message_text:
            return web.json_response({'error': 'Message is required'}, status=400)
            
        from database import get_all_users
        users = get_all_users()
        
        if not users:
            return web.json_response({'error': 'No users found'}, status=404)
            
        # Run broadcast in background
        asyncio.create_task(broadcast_task(SHARED_BOT, users, message_text))
        
        return web.json_response({
            'success': True,
            'message': f"Xabar {len(users)} ta foydalanuvchiga jo'natish boshlandi."
        })
    except Exception as e:
        logger.error(f"Error in broadcast API: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def index_handler(request):
    """Asosiy index.html ni yuborish"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, 'webapp', 'index.html')
    
    logger.info(f"Index request. Path: {index_path} (Exists: {os.path.exists(index_path)})")
    
    if os.path.exists(index_path):
        return web.FileResponse(index_path)
    
    # Debug information for logs
    try:
        files = os.listdir(os.path.join(base_dir, 'webapp'))
        debug_msg = f"index.html topilmadi. Webapp ichida bor: {files}"
    except:
        debug_msg = f"index.html va webapp folder topilmadi. Root: {os.listdir(base_dir)}"
        
    logger.error(debug_msg)
    return web.Response(text=debug_msg, status=404)


async def admin_premium_handler(request):
    """Premium Admin Dashboard handler"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, 'webapp', 'admin_premium.html')
    if os.path.exists(path):
        return web.FileResponse(path)
    return web.Response(text="admin_premium.html not found", status=404)


async def admin_stats_page_handler(request):
    """Elite Admin Statistics Dashboard handler"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, 'webapp', 'admin_stats.html')
    if os.path.exists(path):
        return web.FileResponse(path)
    return web.Response(text="admin_stats.html not found", status=404)


# ============================================
# WEBAPP SERVER
# ============================================

def create_webapp_server():
    """Web server yaratish"""
    app = web.Application(middlewares=[cors_middleware])
    
    # API routes
    app.router.add_get('/api/health', api_health)
    app.router.add_get('/api/translations/{lang}', api_translations)
    app.router.add_get('/api/faculties', api_faculties)
    app.router.add_get('/api/directions', api_directions)
    app.router.add_get('/api/directions/{faculty}', api_directions)
    app.router.add_get('/api/courses', api_courses)
    app.router.add_get('/api/education-types', api_education_types)
    app.router.add_get('/api/education-languages', api_education_languages)
    app.router.add_get('/api/complaint-types', api_complaint_types)
    app.router.add_post('/api/complaint', api_submit_complaint)
    app.router.add_get('/api/rating-questions', api_rating_questions)
    app.router.add_post('/api/rating', api_submit_rating)
    app.router.add_get('/api/surveys', api_surveys)
    app.router.add_get('/api/languages', api_languages)
    app.router.add_get('/api/config', api_config)
    
    # Admin API routes (PROTECTED)
    app.router.add_get('/api/admin/stats', admin_required(api_admin_stats))
    app.router.add_get('/api/admin/dashboard', admin_required(api_admin_dashboard))
    app.router.add_get('/api/admin/logs', admin_required(api_admin_logs))
    app.router.add_get('/api/admin/activity', admin_required(api_admin_activity))
    app.router.add_get('/api/admin/settings/{type}', admin_required(api_admin_settings_list))
    app.router.add_delete('/api/admin/settings/{type}/{id}', admin_required(api_admin_delete_setting))
    app.router.add_get('/api/admin/translations', admin_required(api_admin_translations_list))
    app.router.add_post('/api/admin/broadcast', admin_required(api_admin_broadcast))
    
    # Root route for index.html
    app.router.add_get('/', index_handler)
    app.router.add_get('/admin/premium', admin_premium_handler)
    app.router.add_get('/admin/stats', admin_stats_page_handler)

    # Static files (CSS, JS, assets)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    webapp_path = os.path.join(base_dir, 'webapp')
    
    if os.path.exists(webapp_path):
        for folder in ['js', 'css', 'assets', 'img', 'pdf']:
            folder_path = os.path.join(webapp_path, folder)
            if os.path.exists(folder_path):
                # add_static ishlatiladi, lekin absolute path bilan
                app.router.add_static(f'/{folder}', folder_path)
                logger.info(f"Registered static: /{folder} -> {folder_path}")
        
        # Barcha fayllarni birinchi darajadan serve qilish
        app.router.add_static('/static', webapp_path, name='static_root')
        
        # Media folderini serve qilish (PDFlar uchun)
        media_path = os.path.join(base_dir, 'media')
        if os.path.exists(media_path):
            app.router.add_static('/media', media_path)
            logger.info(f"Registered static: /media -> {media_path}")
    
    return app


async def start_web_server(bot=None, host='0.0.0.0', port=8080):
    """Web serverni ishga tushirish"""
    global SHARED_BOT
    SHARED_BOT = bot
    
    # Debug paths at startup
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Starting server. Base DIR: {base_dir}")
    logger.info(f"Root contents: {os.listdir(base_dir)}")
    
    app = create_webapp_server()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    logger.info(f"Mini App web server LATEST VERSION 5.0 ishga tushdi: http://{host}:{port}")
    return runner
