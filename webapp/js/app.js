/**
 * app.js - Telegram Mini App Logic
 * Version: 5.0.0-ELITE
 */

let tg = window.Telegram?.WebApp;
const API_BASE = window.location.origin;

// State management
let state = {
    user: null,
    config: {},
    complaint: {
        step: 1,
        maxSteps: 9,
        answers: {},
        currentType: null
    },
    rating: {
        step: 1,
        maxSteps: 8, // Reduced from 9
        answers: {}
    },
    view: 'homeView'
};

/**
 * INITIALIZATION
 */
document.addEventListener('DOMContentLoaded', init);

async function init() {
    if (tg) {
        tg.expand();
        tg.ready();
        tg.enableClosingConfirmation();
        // Set header color
        tg.setHeaderColor('#0f172a');
    }

    // Load translations and master data
    await fetchConfig();
    updateContent();
    showView('homeView');

    // Initialize Lucide icons
    if (window.lucide) window.lucide.createIcons();
}

async function fetchConfig() {
    try {
        const resp = await fetch(`${API_BASE}/api/config`);
        const data = await resp.json();
        state.config = data;
    } catch (e) {
        console.error("Config load failed", e);
    }
}

function updateContent() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        const text = t(key);
        if (text) el.textContent = text;
    });
}

function t(key) {
    if (!key) return '';
    return state.config.translations?.[key] || key;
}

/**
 * NAVIGATION
 */
function showView(viewId) {
    vibrate('light');

    // Hide all views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.remove('active');
        v.style.display = 'none';
    });

    // Show target view
    const target = document.getElementById(viewId);
    if (target) {
        target.style.display = 'block';
        setTimeout(() => target.classList.add('active'), 50);
    }

    // Update nav state
    document.querySelectorAll('.nav-elite-btn').forEach(btn => {
        btn.classList.toggle('active', btn.getAttribute('onclick').includes(viewId));
    });

    state.view = viewId;

    // Reset wizards if going back to home
    if (viewId === 'homeView') {
        // Optional reset logic
    } else if (viewId === 'complaintView') {
        initComplaintWizard();
    } else if (viewId === 'ratingView') {
        initRatingWizard();
    } else if (viewId === 'rulesView') {
        renderRulesList();
    } else if (viewId === 'surveyView') {
        renderSurveyList();
    } else if (viewId === 'adminDashboardView') {
        loadAdminStats();
    }
}

/**
 * COMPLAINT WIZARD
 */
function initComplaintWizard() {
    state.complaint = { step: 1, maxSteps: 9, answers: {}, currentType: null };
    renderComplaintStep(1);
}

function renderComplaintStep(step) {
    state.complaint.step = step;
    const container = document.getElementById('complaintStepContainer');
    container.innerHTML = '';

    const stepEl = document.createElement('div');
    stepEl.className = 'space-y-6 animate-bounce-in';

    switch (step) {
        case 1: // Faculty
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_faculty')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.faculties?.forEach(f => appendProOption(stepEl.querySelector('#cOptions'), t(f.translation_key), 'university', () => saveAndNextComplaint('faculty', f.code, 2)));
            break;
        case 2: // Direction
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_direction')}</h3><div class="space-y-4" id="cOptions"></div>`;
            const facultyCode = state.complaint.answers.faculty;
            const directions = (state.config.directions || []).filter(d => d.faculty_code === facultyCode);
            directions.forEach(d => appendProOption(stepEl.querySelector('#cOptions'), t(d.translation_key), 'graduation-cap', () => saveAndNextComplaint('direction', d.code, facultyCode === 'magistratura' ? 5 : 3)));
            break;
        case 3: // Edu Type
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_edu_type')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.education_types?.forEach(et => appendProOption(stepEl.querySelector('#cOptions'), t(et.translation_key), 'book-open', () => saveAndNextComplaint('education_type', et.code, 4)));
            break;
        case 4: // Edu Lang
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_edu_lang')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.education_languages?.forEach(el => appendProOption(stepEl.querySelector('#cOptions'), t(el.translation_key), 'languages', () => saveAndNextComplaint('education_language', el.code, 5)));
            break;
        case 5: // Course
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_course')}</h3><div class="space-y-4" id="cOptions"></div>`;
            const type = state.complaint.answers.faculty === 'magistratura' ? 'magistr' : 'regular';
            state.config.courses?.[type]?.forEach(c => appendProOption(stepEl.querySelector('#cOptions'), t(c.translation_key), 'hash', () => saveAndNextComplaint('course', c.code, 6)));
            break;
        case 6: // Complaint Type
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_complaint_type')}</h3><div class="space-y-4" id="cOptions"></div>`;
            state.config.complaint_types?.forEach(ct => appendProOption(stepEl.querySelector('#cOptions'), t(ct.translation_key), 'alert-circle', () => {
                state.complaint.currentType = ct;
                saveAndNextComplaint('complaint_type', ct.code, ct.requires_subject ? 7 : (ct.requires_teacher ? 8 : 9));
            }));
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
                        <i data-lucide="message-square" class="w-4 h-4"></i>
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

    container.appendChild(stepEl);
    if (window.lucide) window.lucide.createIcons();
}

function saveAndNextComplaint(key, val, next) {
    vibrate('light');
    state.complaint.answers[key] = val;
    renderComplaintStep(next);
}

function handleComplaintInput(key, currentStep) {
    const val = document.getElementById('cInput').value.trim();
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
 * RATING WIZARD
 */
function initRatingWizard() {
    state.rating = { step: 1, maxSteps: 8, answers: {} };
    renderRatingStep(1);
}

function renderRatingStep(step) {
    state.rating.step = step;
    updateRatingProgress();

    const container = document.getElementById('ratingStepContainer');
    container.innerHTML = '';

    const stepEl = document.createElement('div');
    stepEl.className = 'space-y-6 animate-bounce-in';

    switch (step) {
        case 1: // Faculty
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_faculty')}</h3><div class="space-y-4" id="rOptions"></div>`;
            state.config.faculties?.forEach(f => appendProOption(stepEl.querySelector('#rOptions'), t(f.translation_key), 'university', () => saveAndNextRating('faculty', f.code, 2)));
            break;
        case 2: // Direction
            stepEl.innerHTML = `<h3 class="text-xl font-bold mb-6">${t('choose_direction')}</h3><div class="space-y-4" id="rOptions"></div>`;
            const facultyCode = state.rating.answers.faculty;
            const directions = (state.config.directions || []).filter(d => d.faculty_code === facultyCode);
            directions.forEach(d => appendProOption(stepEl.querySelector('#rOptions'), t(d.translation_key), 'graduation-cap', () => saveAndNextRating('direction', d.code, facultyCode === 'magistratura' ? 5 : 3)));
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
    }

    container.appendChild(stepEl);
    if (window.lucide) window.lucide.createIcons();
}

function updateRatingProgress() {
    const step = state.rating.step;
    const max = 8;
    const percent = Math.round((step / max) * 100);
    const progressEl = document.getElementById('ratingProgressBar');
    const labelEl = document.getElementById('ratingPercentLabel');
    if (progressEl) progressEl.style.width = `${percent}%`;
    if (labelEl) labelEl.textContent = `${percent}%`;
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
        qDiv.className = 'space-y-4 q-card p-4 rounded-2xl bg-white/5 border border-white/5';
        qDiv.innerHTML = `<p class="font-bold text-sm text-slate-300">${t(q.translation_key)}</p>`;

        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-6 gap-2';

        for (let i = 0; i <= 5; i++) {
            const btn = document.createElement('button');
            btn.className = 'h-12 rounded-xl bg-white/5 border border-white/10 text-sm font-bold transition-all';
            btn.textContent = i;
            if (state.rating.answers[`q${q.number}`] === i) {
                btn.className = 'h-12 rounded-xl bg-primary text-white border-primary shadow-lg shadow-primary/30 text-sm font-bold';
            }
            btn.onclick = () => {
                vibrate('light');
                state.rating.answers[`q${q.number}`] = i;
                renderRatingQuestions(container); // Refresh to show selection
            };
            grid.appendChild(btn);
        }
        qDiv.appendChild(grid);
        container.appendChild(qDiv);
    });

    // Add Final Submit Button
    const submitBtn = document.createElement('button');
    submitBtn.className = 'btn-pro w-full mt-10';
    submitBtn.innerHTML = `<i data-lucide="send" class="w-6 h-6"></i> ${t('btn_send')}`;
    submitBtn.onclick = handleRatingSubmit;
    container.appendChild(submitBtn);
    if (window.lucide) window.lucide.createIcons();
}

async function handleRatingSubmit() {
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
 * UTILS
 */
function appendProOption(container, label, icon, onClick) {
    const opt = document.createElement('div');
    opt.className = 'option-card elite-glass p-5 flex items-center justify-between group cursor-pointer transition-all active:scale-95 border-white/5';
    opt.onclick = onClick;
    opt.innerHTML = `
        <div class="flex items-center gap-4">
            <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center text-primary group-hover:bg-primary group-hover:text-white transition-all">
                <i data-lucide="${icon}" class="w-5 h-5"></i>
            </div>
            <span class="font-bold text-sm tracking-tight text-slate-700 dark:text-slate-200">${label}</span>
        </div>
        <i data-lucide="chevron-right" class="w-4 h-4 text-slate-400 group-hover:translate-x-1 transition-transform"></i>
    `;
    container.appendChild(opt);
    if (window.lucide) window.lucide.createIcons();
}

function vibrate(type = 'light') {
    if (tg?.HapticFeedback) {
        if (['error', 'success', 'warning'].includes(type)) {
            tg.HapticFeedback.notificationOccurred(type);
        } else {
            tg.HapticFeedback.impactOccurred(type);
        }
    }
}

function showOverlayLoading() {
    // Implement loading overlay if needed
}

function hideOverlayLoading() {
    // Implement loading overlay hiding if needed
}

function fireConfetti() {
    if (window.confetti) {
        confetti({
            particleCount: 150,
            spread: 70,
            origin: { y: 0.6 }
        });
    }
}

function resetForm() {
    showView('homeView');
}

/**
 * OTHER VIEWS
 */
function renderRulesList() {
    const list = document.getElementById('rulesList');
    list.innerHTML = '';

    const rules = [
        { id: 'rules', title: 'btn_rules', icon: 'shield-check' },
        { id: 'grading', title: 'btn_grading', icon: 'award' },
        { id: 'exam', title: 'btn_exam', icon: 'file-text' }
    ];

    rules.forEach(rule => {
        const pdfFile = state.config.pdf_files?.[rule.id];
        appendProOption(list, t(rule.title), rule.icon, () => {
            if (pdfFile) {
                tg?.openLink(`${API_BASE}/${pdfFile}`);
            } else {
                tg?.showAlert(t('error_unknown'));
            }
        });
    });
}

async function renderSurveyList() {
    const list = document.getElementById('surveyList');
    list.innerHTML = `<div class="p-8 text-center text-slate-500">${t('loading')}</div>`;

    try {
        const resp = await fetch(`${API_BASE}/api/surveys`);
        const data = await resp.json();
        list.innerHTML = '';

        if (data.surveys?.length) {
            data.surveys.forEach(s => {
                let icon = 'external-link';
                if (s.code === 'teachers') icon = 'user-check';
                else if (s.code === 'education') icon = 'book';
                else if (s.code === 'employers') icon = 'briefcase';

                const label = t(s.translation_key) || s.code || 'Survey';
                appendProOption(list, label, icon, () => {
                    tg?.openLink(s.url);
                });
            });
        } else {
            list.innerHTML = `<div class="p-12 text-center text-slate-500 font-medium">${t('no_surveys')}</div>`;
        }
    } catch (e) {
        list.innerHTML = `<div class="p-12 text-center text-red-400 font-medium">${t('error_unknown')}</div>`;
    }
}

function loadAdminStats() {
    // Admin stats logic...
}
