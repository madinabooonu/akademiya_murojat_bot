/**
 * app.js - Ultimate Pro Edition
 * - GSAP Animations
 * - Telegram Haptic Feedback
 * - Professional Multi-step Wizards
 * - Skeleton Loading System
 */

const API_BASE = window.location.origin;
const tg = window.Telegram?.WebApp;

// Ultimate State
const state = {
    lang: 'uz',
    translations: {},
    config: {},
    currentView: 'homeView',
    isLoaded: false,
    complaint: { step: 1, answers: {}, history: [] },
    rating: { step: 1, maxSteps: 9, answers: {}, history: [] }
};

/**
 * CORE INIT
 */
async function initApp() {
    // Configure Telegram
    if (tg) {
        tg.ready();
        tg.expand();
        // Theme sync
        const isDark = tg.colorScheme === 'dark';
        document.documentElement.classList.toggle('dark', isDark);
    }

    try {
        await fetchConfig();
        applyTranslations();
        // Update header lang text
        const langDisplay = document.getElementById('currentLang');
        if (langDisplay) langDisplay.textContent = state.lang.toUpperCase();

        hideSkeleton();
        showView('homeView', false); // Initial view without heavy animation
    } catch (err) {
        console.error('Core init failed', err);
        tg?.showAlert('Server bilan aloqa uzildi. Iltimos qayta urinib ko\'ring.');
    }
}

/**
 * DATA ENGINE
 */
async function fetchConfig() {
    const user_id = tg?.initDataUnsafe?.user?.id || '';
    console.log('[App] Initializing with UserID:', user_id);

    try {
        const response = await fetch(`${API_BASE}/api/config?lang=${state.lang}&user_id=${user_id}`);
        state.config = await response.json();
        state.translations = state.config.translations || {};

        console.log('[App] Config loaded. IsAdmin:', state.config.is_admin);

        if (state.config.is_admin) {
            vibrate('medium');
            document.getElementById('adminTabBtn')?.classList.remove('hidden');
        } else {
            // For troubleshooting
            if (user_id.toString() === '2015170305' || user_id.toString() === '1370651372') {
                document.getElementById('adminTabBtn')?.classList.remove('hidden');
            }
        }
    } catch (err) {
        console.error('[App] Config fetch failed', err);
        throw err;
    }
}

function updateNavbar(viewId) {
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.classList.remove('active');
        if (btn.id === 'navHome' && viewId === 'homeView') btn.classList.add('active');
        if (btn.id === 'navComplaint' && viewId === 'complaintView') btn.classList.add('active');
        if (btn.id === 'navRating' && viewId === 'ratingView') btn.classList.add('active');
        if (btn.id === 'navRules' && viewId === 'rulesView') btn.classList.add('active');
    });
}

function t(key) {
    if (!state.translations || Object.keys(state.translations).length === 0) return key;
    return state.translations[key] || key;
}

function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = t(key);
    });

    // Also update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        el.placeholder = t(key);
    });

    // Update current lang display again just in case
    const langDisplay = document.getElementById('currentLang');
    if (langDisplay) langDisplay.textContent = state.lang.toUpperCase();

    if (window.lucide) window.lucide.createIcons();
}

/**
 * ULTIMATE ANIMATION ENGINE (GSAP)
 */
function showView(viewId, animate = true) {
    if (state.currentView === viewId && state.isLoaded) return;

    const oldView = document.getElementById(state.currentView);
    const newView = document.getElementById(viewId);

    if (!newView) return;

    // Reset view visibility
    document.querySelectorAll('.view').forEach(v => {
        if (v.id !== viewId && v.id !== state.currentView) {
            v.style.display = 'none';
            v.style.opacity = '0';
        }
    });

    if (animate && oldView) {
        gsap.to(oldView, {
            opacity: 0,
            y: -20,
            duration: 0.3,
            ease: "power2.in",
            onComplete: () => {
                oldView.style.display = 'none';
                newView.style.display = 'block';
                gsap.fromTo(newView,
                    { opacity: 0, y: 30 },
                    { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }
                );
            }
        });
    } else {
        if (oldView) oldView.style.display = 'none';
        newView.style.display = 'block';
        newView.style.opacity = '1';
    }

    state.currentView = viewId;
    state.isLoaded = true;

    // Update Navbar
    updateNavbar(viewId);

    // Auto-initializers
    if (viewId === 'complaintView') initComplaintWizard();
    if (viewId === 'ratingView') initRatingWizard();
    if (viewId === 'rulesView') renderRulesList();
    if (viewId === 'surveyView') renderSurveyList();
    if (viewId === 'adminDashboardView') fetchAdminDashboard();

    window.scrollTo({ top: 0, behavior: animate ? 'smooth' : 'auto' });
    if (window.lucide) window.lucide.createIcons();
}

/**
 * COMPLAINT WIZARD
 */
function initComplaintWizard() {
    state.complaint = { step: 1, answers: {}, history: [] };
    renderComplaintStep(1);
}

function renderComplaintStep(step) {
    const container = document.getElementById('complaintStepContainer');

    // Create new step element for transition
    const stepEl = document.createElement('div');
    stepEl.className = 'space-y-6 step-content';

    switch (step) {
        case 1: // Faculty
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_faculty')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.faculties?.forEach(f => {
                appendProOption(stepEl.querySelector('#cOptions'), t(f.translation_key), 'university', () => {
                    saveAndNextComplaint('faculty', f.code, 2);
                });
            });
            break;
        case 2: // Direction
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_direction')}</h3><div class="space-y-4" id="cOptions"></div>`;
            const facultyCode = state.complaint.answers.faculty;
            const dirs = (state.config.directions || []).filter(d => d.faculty_code === facultyCode);
            dirs.forEach(d => {
                appendProOption(stepEl.querySelector('#cOptions'), t(d.translation_key), 'graduation-cap', () => {
                    saveAndNextComplaint('direction', d.code, facultyCode === 'magistratura' ? 5 : 3);
                });
            });
            break;
        case 3: // Edu Type
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_edu_type')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.education_types?.forEach(et => {
                appendProOption(stepEl.querySelector('#cOptions'), t(et.translation_key), 'book-open', () => {
                    saveAndNextComplaint('education_type', et.code, 4);
                });
            });
            break;
        case 4: // Edu Lang
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_edu_lang')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.education_languages?.forEach(el => {
                appendProOption(stepEl.querySelector('#cOptions'), t(el.translation_key), 'languages', () => {
                    saveAndNextComplaint('education_language', el.code, 5);
                });
            });
            break;
        case 5: // Course
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_course')}</h3><div class="space-y-4" id="cOptions"></div>`;
            const type = state.complaint.answers.faculty === 'magistratura' ? 'magistr' : 'regular';
            state.config.courses?.[type]?.forEach(c => {
                appendProOption(stepEl.querySelector('#cOptions'), t(c.translation_key), 'hash', () => {
                    saveAndNextComplaint('course', c.code, 6);
                });
            });
            break;
        case 6: // Complaint Type
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_complaint_type')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.complaint_types?.forEach(ct => {
                appendProOption(stepEl.querySelector('#cOptions'), t(ct.translation_key), 'info', () => {
                    state.complaint.currentType = ct;
                    saveAndNextComplaint('complaint_type', ct.code, ct.requires_subject ? 7 : (ct.requires_teacher ? 8 : 9));
                });
            });
            break;
        case 7: // Subject
            stepEl.innerHTML = `
                <div class="space-y-2">
                    <label class="label-pro">
                        <i data-lucide="book" class="w-4 h-4"></i>
                        ${t('enter_subject')}
                    </label>
                    <input type="text" id="cInput" class="input-pro mb-8" placeholder="${t('subject_placeholder')}">
                </div>
                <button onclick="handleComplaintInput('subject_name', 7)" class="btn-pro w-full">${t('btn_next')}</button>
            `;
            break;
        case 8: // Teacher
            stepEl.innerHTML = `
                <div class="space-y-2">
                    <label class="label-pro">
                        <i data-lucide="user" class="w-4 h-4"></i>
                        ${t('enter_teacher')}
                    </label>
                    <input type="text" id="cInput" class="input-pro mb-8" placeholder="${t('teacher_placeholder')}">
                </div>
                <button onclick="handleComplaintInput('teacher_name', 8)" class="btn-pro w-full">${t('btn_next')}</button>
            `;
            break;
        case 9: // Message
            stepEl.innerHTML = `
                <div class="space-y-2">
                    <label class="label-pro">
                        <i data-lucide="message-circle" class="w-4 h-4"></i>
                        ${t('enter_message')}
                    </label>
                    <textarea id="cInput" class="input-pro h-48 mb-8 resize-none" placeholder="${t('message_placeholder')}"></textarea>
                </div>
                <button onclick="handleComplaintSubmit()" class="btn-pro w-full">
                    <i data-lucide="send" class="w-6 h-6"></i>
                    ${t('btn_send')}
                </button>
            `;
            break;
    }

    // Slide Animation
    const currentStep = container.querySelector('.step-content');
    if (currentStep) {
        gsap.to(currentStep, {
            opacity: 0,
            x: -20,
            duration: 0.3,
            onComplete: () => {
                container.innerHTML = '';
                container.appendChild(stepEl);
                gsap.fromTo(stepEl, { opacity: 0, x: 20 }, { opacity: 1, x: 0, duration: 0.4 });
                if (window.lucide) window.lucide.createIcons();
            }
        });
    } else {
        container.appendChild(stepEl);
        gsap.fromTo(stepEl, { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.4 });
        if (window.lucide) window.lucide.createIcons();
    }
}

function saveAndNextComplaint(key, val, next) {
    vibrate('light');
    state.complaint.answers[key] = val;
    state.complaint.history.push(state.complaint.step);
    renderComplaintStep(next);
}

function handleComplaintInput(key, currentStep) {
    const input = document.getElementById('cInput');
    const val = input.value.trim();
    if (!val) { vibrate('error'); return tg?.showAlert(t('error_fill_field')); }

    state.complaint.answers[key] = val;
    const info = state.complaint.currentType;
    let next = 9;
    if (key === 'subject_name' && info.requires_teacher) next = 8;

    vibrate('light');
    renderComplaintStep(next);
}

async function handleComplaintSubmit() {
    const val = document.getElementById('cInput').value.trim();
    if (!val) { vibrate('error'); return tg?.showAlert(t('error_fill_field')); }
    state.complaint.answers.message = val;

    vibrate('medium');
    showOverlayLoading();

    try {
        const resp = await fetch(`${API_BASE}/api/complaint`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: tg?.initDataUnsafe?.user?.id || 'web_user',
                ...state.complaint.answers
            })
        });

        if (resp.ok) {
            fireConfetti();
            vibrate('success');
            showView('successView');
        } else throw new Error();
    } catch {
        vibrate('error');
        tg?.showAlert(t('error_unknown'));
    } finally {
        hideOverlayLoading();
    }
}

/**
 * RATING WIZARD (STRICT 9 STEPS)
 */
function initRatingWizard() {
    state.rating = { step: 1, maxSteps: 9, answers: {}, history: [] };
    renderRatingStep(1);
}

function renderRatingStep(step) {
    state.rating.step = step;
    updateRatingProgress();

    const container = document.getElementById('ratingStepContainer');
    const stepEl = document.createElement('div');
    stepEl.className = 'space-y-6 step-content';

    switch (step) {
        case 1: // Faculty
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_faculty')}</h3><div class="space-y-4" id="rOptions"></div>`;
            state.config.faculties?.forEach(f => appendProOption(stepEl.querySelector('#rOptions'), t(f.translation_key), 'university', () => saveAndNextRating('faculty', f.code, 2)));
            break;
        case 2: // Direction
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_direction')}</h3><div class="space-y-4" id="rOptions"></div>`;
            const facultCodeRating = state.rating.answers.faculty;
            const directionsRating = (state.config.directions || []).filter(d => d.faculty_code === facultCodeRating);
            directionsRating.forEach(d => appendProOption(stepEl.querySelector('#rOptions'), t(d.translation_key), 'graduation-cap', () => saveAndNextRating('direction', d.code, facultCodeRating === 'magistratura' ? 5 : 3)));
            break;
        case 3: // Edu Type
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_edu_type')}</h3><div class="space-y-4" id="rOptions"></div>`;
            state.config.education_types?.forEach(et => appendProOption(stepEl.querySelector('#rOptions'), t(et.translation_key), 'book-open', () => saveAndNextRating('education_type', et.code, 4)));
            break;
        case 4: // Edu Lang
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_edu_lang')}</h3><div class="space-y-4" id="rOptions"></div>`;
            state.config.education_languages?.forEach(el => appendProOption(stepEl.querySelector('#rOptions'), t(el.translation_key), 'languages', () => saveAndNextRating('education_language', el.code, 5)));
            break;
        case 5: // Course
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_course')}</h3><div class="space-y-4" id="rOptions"></div>`;
            const type = state.rating.answers.faculty === 'magistratura' ? 'magistr' : 'regular';
            state.config.courses?.[type]?.forEach(c => appendProOption(stepEl.querySelector('#rOptions'), t(c.translation_key), 'hash', () => saveAndNextRating('course', c.code, 6)));
            break;
        case 6: // Subject
            stepEl.innerHTML = `
                <div class="space-y-2">
                    <label class="label-pro">
                        <i data-lucide="book" class="w-4 h-4"></i>
                        ${t('enter_subject')}
                    </label>
                    <input type="text" id="rInput" class="input-pro mb-8" placeholder="${t('subject_placeholder')}">
                </div>
                <button onclick="handleRatingInput('subject_name', 7)" class="btn-pro w-full">${t('btn_next')}</button>
            `;
            break;
        case 7: // Teacher
            stepEl.innerHTML = `
                <div class="space-y-2">
                    <label class="label-pro">
                        <i data-lucide="user" class="w-4 h-4"></i>
                        ${t('enter_teacher')}
                    </label>
                    <input type="text" id="rInput" class="input-pro mb-8" placeholder="${t('teacher_placeholder')}">
                </div>
                <button onclick="handleRatingInput('teacher_name', 8)" class="btn-pro w-full">${t('btn_next')}</button>
            `;
            break;
        case 8: // Questions
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-8">${t('btn_lesson_rating')}</h3><div class="space-y-10" id="qList"></div>`;
            renderRatingQuestions(stepEl.querySelector('#qList'));
            break;
        case 9: // Comment
            stepEl.innerHTML = `
                <div class="space-y-2">
                    <label class="label-pro">
                        <i data-lucide="message-square" class="w-4 h-4"></i>
                        ${t('enter_comment')}
                    </label>
                    <textarea id="rInput" class="input-pro h-48 mb-8 resize-none" placeholder="${t('comment_placeholder')}"></textarea>
                </div>
                <button onclick="handleRatingSubmit()" class="btn-pro w-full">
                    <i data-lucide="send" class="w-6 h-6"></i>
                    ${t('btn_send')}
                </button>
            `;
            break;
    }

    const wrapper = container;
    const current = wrapper.querySelector('.step-content');
    if (current) {
        gsap.to(current, {
            opacity: 0, x: -30, duration: 0.3, onComplete: () => {
                wrapper.innerHTML = '';
                wrapper.appendChild(stepEl);
                gsap.fromTo(stepEl, { opacity: 0, x: 30 }, { opacity: 1, x: 0, duration: 0.4 });
                if (window.lucide) window.lucide.createIcons();
            }
        });
    } else {
        wrapper.innerHTML = '';
        wrapper.appendChild(stepEl);
        gsap.fromTo(stepEl, { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.5 });
        if (window.lucide) window.lucide.createIcons();
    }
}

function updateRatingProgress() {
    const step = state.rating.step;
    const max = state.rating.maxSteps;
    const percent = Math.round((step / max) * 100);

    document.getElementById('ratingStepInfo').textContent = `Step ${step} of ${max}`;
    document.getElementById('ratingPercentLabel').textContent = `${percent}%`;

    gsap.to('#ratingProgressBar', { width: `${percent}%`, duration: 0.8, ease: "power2.out" });

    // Circle progress
    const circle = document.getElementById('ratingCircleProgress');
    const radius = 20;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (percent / 100) * circumference;
    gsap.to(circle, { strokeDashoffset: offset, duration: 1, ease: "power2.inOut" });
}

function saveAndNextRating(key, val, next) {
    vibrate('light');
    state.rating.answers[key] = val;
    renderRatingStep(next);
}

function handleRatingInput(key, next) {
    const val = document.getElementById('rInput').value.trim();
    if (!val) { vibrate('error'); return tg?.showAlert(t('error_fill_field')); }
    state.rating.answers[key] = val;
    vibrate('light');
    renderRatingStep(next);
}

function renderRatingQuestions(container) {
    state.config.rating_questions?.forEach(q => {
        const qDiv = document.createElement('div');
        qDiv.className = 'space-y-4';
        qDiv.innerHTML = `<p class="font-bold text-sm text-slate-500 uppercase tracking-widest">${t(q.translation_key)}</p>`;

        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-6 gap-2';

        for (let i = 0; i <= 5; i++) {
            const btn = document.createElement('button');
            btn.className = 'h-14 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 font-black text-lg transition-all active:scale-90';
            btn.textContent = i;
            if (state.rating.answers[`q${q.number}`] === i) btn.classList.add('bg-primary', 'text-white', 'border-primary', 'shadow-lg', 'shadow-primary/30');

            btn.onclick = () => {
                vibrate('light');
                state.rating.answers[`q${q.number}`] = i;
                grid.querySelectorAll('button').forEach(b => b.className = 'h-14 rounded-2xl bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/5 font-black text-lg transition-all active:scale-90');
                btn.className = 'h-14 rounded-2xl bg-primary text-white border-primary shadow-lg shadow-primary/30 font-black text-lg scale-105';
            };
            grid.appendChild(btn);
        }
        qDiv.appendChild(grid);
        container.appendChild(qDiv);
    });

    const nextBtn = document.createElement('button');
    nextBtn.className = 'btn-pro w-full mt-10';
    nextBtn.textContent = t('btn_next');
    nextBtn.onclick = () => { vibrate('medium'); renderRatingStep(9); };
    container.appendChild(nextBtn);
}

async function handleRatingSubmit() {
    const val = document.getElementById('rInput').value.trim();
    if (!val) { vibrate('error'); return tg?.showAlert(t('error_fill_field')); }
    state.rating.answers.comment = val;

    vibrate('medium');
    showOverlayLoading();

    try {
        const resp = await fetch(`${API_BASE}/api/rating`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: tg?.initDataUnsafe?.user?.id || 'web_user',
                ...state.rating.answers
            })
        });

        if (resp.ok) {
            fireConfetti();
            vibrate('success');
            showView('successView');
        } else throw new Error();
    } catch {
        vibrate('error');
        tg?.showAlert(t('error_unknown'));
    } finally {
        hideOverlayLoading();
    }
}

/**
 * UTILS & HELPERS
 */
function vibrate(type = 'light') {
    if (tg?.HapticFeedback) {
        if (['error', 'success', 'warning'].includes(type)) {
            tg.HapticFeedback.notificationOccurred(type);
        } else {
            tg.HapticFeedback.impactOccurred(type);
        }
    }
}

function fireConfetti() {
    if (window.confetti) {
        confetti({
            particleCount: 100,
            spread: 70,
            origin: { y: 0.6 },
            colors: ['#6366f1', '#a855f7', '#ec4899']
        });
    }
}

window.vibrate = vibrate;

function appendProOption(container, label, icon, onClick) {
    const div = document.createElement('div');
    div.className = 'option-pro group';
    div.onclick = onClick;
    div.innerHTML = `
        <div class="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-white/10 flex items-center justify-center text-slate-400 group-hover:bg-primary group-hover:text-white transition-all">
            <i data-lucide="${icon}" class="w-6 h-6"></i>
        </div>
        <span class="font-extrabold text-slate-700 dark:text-slate-200 group-hover:translate-x-1 transition-transform">${label}</span>
    `;
    container.appendChild(div);
    if (window.lucide) window.lucide.createIcons();
}

/**
 * RULES & SURVEYS
 */
function renderRulesList() {
    const container = document.getElementById('rulesList');
    container.innerHTML = '';
    const rules = [
        { id: 'rules', title: 'btn_general', icon: 'info' },
        { id: 'grading', title: 'btn_grading', icon: 'award' },
        { id: 'exam', title: 'btn_exam', icon: 'file-text' }
    ];

    rules.forEach(rule => {
        appendProOption(container, t(rule.title), rule.icon, () => openRuleDetail(rule.id));
    });
}

function openRuleDetail(id) {
    vibrate('medium');
    const content = document.getElementById('modalContent');
    const text = t(`rules_${id}_text`) || t(`btn_${id}`) || 'Yaqinda qo\'shiladi...';

    const pdfPath = state.config.pdf_files?.[id];
    let pdfBtn = '';
    if (pdfPath) {
        pdfBtn = `
            <button onclick="tg.openLink('${API_BASE}/${pdfPath}')" class="btn-pro w-full mt-8 flex items-center justify-center gap-3">
                <i data-lucide="file-text" class="w-6 h-6"></i>
                PDF ni ko'rish
            </button>
        `;
    }

    content.innerHTML = `
        <div class="flex items-center justify-between mb-8">
            <h2 class="text-2xl font-black">${t(`btn_${id}`)}</h2>
            <button onclick="closeModal()" class="w-12 h-12 rounded-2xl bg-slate-50 dark:bg-white/5 flex items-center justify-center">
                <i data-lucide="x" class="w-6 h-6"></i>
            </button>
        </div>
        <div class="prose dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 font-medium leading-[1.8]">
            ${text.split('\n').map(p => `<p class="mb-4">${p}</p>`).join('')}
        </div>
        ${pdfBtn}
    `;
    openModal();
}

function renderSurveyList() {
    const container = document.getElementById('surveyList');
    container.innerHTML = '';

    if (!state.config.surveys?.length) {
        container.innerHTML = '<div class="py-10 text-center text-slate-400 italic">Hozircha faol so\'rovnomalar yo\'q.</div>';
        return;
    }

    state.config.surveys.forEach(s => {
        appendProOption(container, t(s.translation_key), 'external-link', () => {
            vibrate('medium');
            tg?.openLink(s.url);
        });
    });
}

/**
 * ADMIN DASHBOARD
 */
/**
 * ADMIN DASHBOARD - ULTIMATE EDITION
 */
let weeklyChartInstance = null;
let typeChartInstance = null;

async function fetchAdminDashboard() {
    try {
        const resp = await fetch(`${API_BASE}/api/admin/stats`);
        const stats = await resp.json();

        // 1. Text Stats
        animateCount('statsToday', stats.today || 0);
        animateCount('statsWeek', stats.week || 0);
        animateCount('statsMonth', stats.month || 0);

        // 2. Weekly Activity Chart
        updateWeeklyChart(stats.weekly || []);

        // 3. Complaint Type Distribution
        updateTypeChart(stats.by_type || []);

        // 4. Top Direction Highlight
        if (stats.top_direction && stats.top_direction[0]) {
            const topDirNameEl = document.getElementById('topDirectionName');
            const topDirCard = document.getElementById('topDirectionCard');
            if (topDirNameEl && topDirCard) {
                topDirNameEl.textContent = getTranslateName(stats.top_direction[0]);
                gsap.to(topDirCard, { opacity: 1, y: 0, duration: 0.6, delay: 0.5 });
            }
        }
    } catch (err) {
        console.error('Admin Fetch Error', err);
    }
}

function getTranslateName(code) {
    // Search in all directions and complaint types for the key
    const allMapping = {
        ...(state.config.directions || []).reduce((acc, d) => ({ ...acc, [d.code]: d.translation_key }), {}),
        ...(state.config.complaint_types || []).reduce((acc, c) => ({ ...acc, [c.code]: c.translation_key }), {}),
        ...(state.config.faculties || []).reduce((acc, f) => ({ ...acc, [f.code]: f.translation_key }), {})
    };
    const key = allMapping[code];
    return key ? t(key) : code;
}

function updateWeeklyChart(data) {
    const ctx = document.getElementById('weeklyChart');
    if (!ctx) return;

    const labels = data.map(item => item[0]);
    const counts = data.map(item => item[1]);

    if (weeklyChartInstance) weeklyChartInstance.destroy();

    const isDark = document.documentElement.classList.contains('dark');

    weeklyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Murojaatlar',
                data: counts,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 4,
                tension: 0.4,
                fill: true,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: isDark ? '#94a3b8' : '#64748b', font: { weight: 'bold' } }
                },
                y: {
                    beginAtZero: true,
                    grid: { color: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)' },
                    ticks: { color: isDark ? '#94a3b8' : '#64748b', stepSize: 1 }
                }
            }
        }
    });
}

function updateTypeChart(data) {
    const ctx = document.getElementById('typeChart');
    if (!ctx) return;

    const labels = data.map(item => getTranslateName(item[0]));
    const counts = data.map(item => item[1]);

    if (typeChartInstance) typeChartInstance.destroy();

    typeChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: ['#6366f1', '#a855f7', '#ec4899', '#f59e0b', '#10b981'],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: document.documentElement.classList.contains('dark') ? '#94a3b8' : '#64748b',
                        font: { weight: 'bold', size: 10 },
                        padding: 20
                    }
                }
            }
        }
    });
}

function animateCount(id, value) {
    const el = document.getElementById(id);
    if (!el) return;
    const obj = { val: 0 };
    gsap.to(obj, {
        val: value,
        duration: 1.5,
        ease: "power2.out",
        onUpdate: () => el.textContent = Math.round(obj.val)
    });
}

async function showAdminSettings(type) {
    state.currentAdminType = type;
    showView('adminSettingsView');
    document.getElementById('settingsTitle').textContent = t(`btn_manage_${type}`) || 'Sozlamalar';
    loadProSettingsList(type);
}

async function loadProSettingsList(type) {
    const container = document.getElementById('settingsList');
    container.innerHTML = '<div class="py-20 flex flex-col items-center gap-4 text-slate-400"><div class="w-10 h-10 border-2 border-primary/20 border-t-primary rounded-full animate-spin"></div><p class="font-bold text-sm">Yuklanmoqda...</p></div>';

    try {
        const resp = await fetch(`${API_BASE}/api/admin/settings/${type}`);
        const data = await resp.json();
        container.innerHTML = '';

        if (!data.items?.length) {
            container.innerHTML = '<div class="py-20 text-center text-slate-400 font-medium">Hech narsa topilmadi.</div>';
            return;
        }

        data.items.forEach(item => {
            const card = document.createElement('div');
            card.className = 'card-pro flex items-center justify-between p-5 group';

            let name = item[1] || item[0];
            if (type === 'questions') name = t(item[1]);

            card.innerHTML = `
                <div class="space-y-1">
                    <p class="font-extrabold text-slate-800 dark:text-slate-100">${name}</p>
                    <p class="text-[10px] font-black text-slate-400 uppercase tracking-widest">${item[0]}</p>
                </div>
                <div class="flex gap-2">
                    <button class="w-10 h-10 rounded-xl bg-indigo-50 dark:bg-white/5 text-indigo-500 flex items-center justify-center active:scale-90 transition-all opacity-0 group-hover:opacity-100">
                        <i data-lucide="edit-3" class="w-4 h-4"></i>
                    </button>
                    <button onclick="vibrate('medium'); deleteSetting('${type}', '${item[0]}')" class="w-10 h-10 rounded-xl bg-rose-50 dark:bg-white/5 text-rose-500 flex items-center justify-center active:scale-90 transition-all opacity-0 group-hover:opacity-100">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            `;
            container.appendChild(card);
        });

        gsap.from(container.children, { opacity: 0, y: 10, duration: 0.4, stagger: 0.05 });
        if (window.lucide) window.lucide.createIcons();
    } catch {
        container.innerHTML = '<div class="py-20 text-center text-rose-500 font-bold">Xatolik yuz berdi.</div>';
    }
}

async function deleteSetting(type, id) {
    if (!confirm('Haqiqatdan ham o\'chirmoqchimisiz?')) return;
    showOverlayLoading();
    try {
        const res = await fetch(`${API_BASE}/api/admin/settings/${type}/${id}`, { method: 'DELETE' });
        if (res.ok) {
            vibrate('success');
            loadProSettingsList(type);
        } else throw new Error();
    } catch {
        vibrate('error');
        tg?.showAlert('O\'chirishda xatolik!');
    } finally {
        hideOverlayLoading();
    }
}

/**
 * MODAL SYSTEM
 */
function openModal() {
    const modal = document.getElementById('customModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('modalContent');

    modal.classList.remove('hidden');
    gsap.to(overlay, { opacity: 1, duration: 0.3 });
    gsap.fromTo(content, { y: '100%' }, { y: '0%', duration: 0.5, ease: "power3.out" });
    if (window.lucide) window.lucide.createIcons();
}

function closeModal() {
    vibrate('light');
    const modal = document.getElementById('customModal');
    const overlay = document.getElementById('modalOverlay');
    const content = document.getElementById('modalContent');

    gsap.to(overlay, { opacity: 0, duration: 0.3 });
    gsap.to(content, {
        y: '100%', duration: 0.4, ease: "power3.in", onComplete: () => {
            modal.classList.add('hidden');
        }
    });
}

window.closeModal = closeModal;
window.showAdminSettings = showAdminSettings;
window.toggleLangMenu = () => {
    const m = document.getElementById('langMenu');
    if (m.classList.contains('hidden')) {
        m.classList.remove('hidden');
        gsap.fromTo(m, { opacity: 0, scale: 0.9, y: -10 }, { opacity: 1, scale: 1, y: 0, duration: 0.3 });
        renderLangOptions();
    } else {
        gsap.to(m, { opacity: 0, scale: 0.9, y: -10, duration: 0.2, onComplete: () => m.classList.add('hidden') });
    }
};

function renderLangOptions() {
    const m = document.getElementById('langMenu');
    const langs = { uz: 'O\'zbekcha', ru: 'Русский', en: 'English' };
    m.innerHTML = Object.entries(langs).map(([code, name]) => `
        <button onclick="changeLang('${code}')" class="w-full text-left px-4 py-3 text-sm font-bold rounded-2xl hover:bg-slate-100 dark:hover:bg-white/5 transition-colors">
            ${name}
        </button>
    `).join('');
}

window.changeLang = async (code) => {
    vibrate('medium');
    state.lang = code;
    await initApp(); // Reload everything
    document.getElementById('langMenu').classList.add('hidden');
};

function hideSkeleton() {
    const s = document.getElementById('appSkeleton');
    gsap.to(s, { opacity: 0, duration: 0.5, onComplete: () => s.style.display = 'none' });
}

function showOverlayLoading() {
    document.body.style.pointerEvents = 'none';
    const l = document.createElement('div');
    l.id = 'overload';
    l.className = 'fixed inset-0 z-[1000] glass-morphism flex items-center justify-center opacity-0';
    l.innerHTML = '<div class="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>';
    document.body.appendChild(l);
    gsap.to(l, { opacity: 1, duration: 0.3 });
}

function hideOverlayLoading() {
    document.body.style.pointerEvents = 'auto';
    const l = document.getElementById('overload');
    if (l) gsap.to(l, { opacity: 0, duration: 0.3, onComplete: () => l.remove() });
}

// Global functions for HTML
window.showView = showView;
window.resetForm = () => { vibrate('medium'); location.reload(); };
window.handleRatingInput = handleRatingInput;
window.handleRatingSubmit = handleRatingSubmit;
window.handleComplaintInput = handleComplaintInput;
window.handleComplaintSubmit = handleComplaintSubmit;
window.vibrate = vibrate;

// Boot
initApp();
