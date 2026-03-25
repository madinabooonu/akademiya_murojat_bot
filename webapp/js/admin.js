// Configuration
const API_BASE = '/api/admin';
const URL_PARAMS = new URLSearchParams(window.location.search);
const USER_ID = URL_PARAMS.get('user_id');

// Chart Instances
let trendChart, sourceChart, facultyChart;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    if (!USER_ID) {
        showError("Authentication required. Please open from bot admin menu.");
        return;
    }

    initNavigation();
    loadDashboard();

    // Auto-refresh every 30 seconds
    setInterval(loadDashboard, 30000);

    document.getElementById('refresh-btn').onclick = loadDashboard;
});

function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.tab-content');

    navItems.forEach(item => {
        item.onclick = () => {
            const tab = item.getAttribute('data-tab');

            navItems.forEach(n => n.classList.remove('active'));
            sections.forEach(s => s.classList.remove('active'));

            item.classList.add('active');
            document.getElementById(tab).classList.add('active');

            if (tab === 'activity') loadActivity();
            if (tab === 'errors') loadLogs();
        };
    });
}

// Data Fetching
async function loadDashboard() {
    const btn = document.getElementById('refresh-btn');
    btn.querySelector('i').classList.add('fa-spin');

    try {
        const response = await fetch(`${API_BASE}/dashboard?user_id=${USER_ID}`);
        if (!response.ok) throw new Error("API Error");
        const data = await response.json();

        updateKPIs(data);
        renderCharts(data);

        document.getElementById('update-time').innerHTML = `<i class="fas fa-clock-rotate-left"></i> ${data.update_time}`;
    } catch (err) {
        console.error(err);
    } finally {
        setTimeout(() => btn.querySelector('i').classList.remove('fa-spin'), 600);
    }
}

function updateKPIs(data) {
    animateCounter('total-users', data.total_users);
    animateCounter('total-complaints', data.total_complaints);
    animateCounter('dau-count', data.dau);

    document.getElementById('new-users').innerHTML = `<i class="fas fa-arrow-trend-up"></i> +${data.new_users_today} bugun`;
    document.getElementById('complaints-today').innerHTML = `<i class="fas fa-paper-plane"></i> ${data.complaints_today} bugun`;

    const errStatus = document.getElementById('error-status');
    if (data.error_count > 0) {
        errStatus.textContent = `${data.error_count} xato aniqlandi`;
        errStatus.className = "trend danger";
    } else {
        errStatus.textContent = "Tizim barqaror";
        errStatus.className = "trend";
        errStatus.style.color = "var(--success)";
    }
}

function renderCharts(data) {
    const ctxMain = document.getElementById('mainTrendChart').getContext('2d');
    const ctxSource = document.getElementById('sourceChart').getContext('2d');
    const ctxFaculty = document.getElementById('facultyChart').getContext('2d');

    // 1. Trend Chart (Activities & Registrations)
    const dates = data.daily_activities.map(i => i.date);
    const actData = data.daily_activities.map(i => i.count);
    const regData = data.daily_registrations.map(i => i.count);

    if (trendChart) trendChart.destroy();
    trendChart = new Chart(ctxMain, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Activities',
                    data: actData,
                    borderColor: '#6366f1',
                    fill: true,
                    backgroundColor: createGradient(ctxMain, 'rgba(99, 102, 241, 0.2)'),
                    tension: 0.4
                },
                {
                    label: 'Registrations',
                    data: regData,
                    borderColor: '#a855f7',
                    borderDash: [5, 5],
                    tension: 0.4
                }
            ]
        },
        options: getChartOptions()
    });

    // 2. Source Breakdown
    const sources = data.source_breakdown.map(i => i.source);
    const sCounts = data.source_breakdown.map(i => i.count);

    if (sourceChart) sourceChart.destroy();
    sourceChart = new Chart(ctxSource, {
        type: 'doughnut',
        data: {
            labels: sources,
            datasets: [{
                data: sCounts,
                backgroundColor: ['#6366f1', '#22d3ee', '#a855f7'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', padding: 20 } } }
        }
    });

    // 3. Faculty Bar
    const faculties = data.top_faculties.map(i => i.faculty);
    const fCounts = data.top_faculties.map(i => i.count);

    if (facultyChart) facultyChart.destroy();
    facultyChart = new Chart(ctxFaculty, {
        type: 'bar',
        data: {
            labels: faculties,
            datasets: [{
                data: fCounts,
                backgroundColor: '#22d3ee',
                borderRadius: 10
            }]
        },
        options: getChartOptions(false)
    });
}

async function loadActivity() {
    const res = await fetch(`${API_BASE}/activity?user_id=${USER_ID}`);
    const data = await res.json();
    const tbody = document.querySelector('#activityTable tbody');
    tbody.innerHTML = '';

    data.activity.forEach(row => {
        tbody.innerHTML += `
            <tr>
                <td style="color: var(--text-muted)">${formatTime(row.time)}</td>
                <td style="font-weight: 600">ID: ${row.user_id}</td>
                <td><span class="badge ${getActionClass(row.action)}">${row.action}</span></td>
                <td><span class="badge badge-${row.source}">${row.source.toUpperCase()}</span></td>
            </tr>
        `;
    });
}

async function loadLogs() {
    const res = await fetch(`${API_BASE}/logs?user_id=${USER_ID}`);
    const data = await res.json();
    const tbody = document.querySelector('#errorTable tbody');
    tbody.innerHTML = '';

    document.getElementById('total-errors-badge').textContent = `${data.logs.length} Xato topildi`;

    data.logs.forEach(log => {
        tbody.innerHTML += `
            <tr>
                <td style="color: var(--text-muted)">${formatTime(log.timestamp)}</td>
                <td><span class="badge badge-error">${log.level}</span></td>
                <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${log.message}</td>
                <td><small>${JSON.stringify(log.context || {}).slice(0, 30)}...</small></td>
                <td><button class="badge" style="background: var(--primary); color: white; border: none; cursor: pointer" onclick='showErrorDetail(${JSON.stringify(log)})'>VIEW</button></td>
            </tr>
        `;
    });
}

// Helpers
function createGradient(ctx, color) {
    const grad = ctx.createLinearGradient(0, 0, 0, 400);
    grad.addColorStop(0, color);
    grad.addColorStop(1, 'rgba(0,0,0,0)');
    return grad;
}

function getChartOptions(showLegend = false) {
    return {
        responsive: true,
        plugins: { legend: { display: showLegend, labels: { color: '#94a3b8' } } },
        scales: {
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#64748b' } },
            x: { grid: { display: false }, ticks: { color: '#64748b' } }
        }
    };
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    let current = 0;
    const step = Math.ceil(target / 30);
    const timer = setInterval(() => {
        current += step;
        if (current >= target) {
            el.textContent = target;
            clearInterval(timer);
        } else {
            el.textContent = current;
        }
    }, 20);
}

function formatTime(dStr) {
    const d = new Date(dStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getActionClass(action) {
    if (action.includes('submit')) return 'badge-new';
    if (action.includes('error')) return 'badge-error';
    return '';
}

function showErrorDetail(log) {
    const modal = document.getElementById('errorModal');
    const body = document.getElementById('modalBody');
    body.innerHTML = `
        <div style="background: #0f172a; padding: 20px; border-radius: 16px; border: 1px solid var(--glass-border)">
            <p style="margin-bottom: 20px; color: var(--danger); font-weight: 700;">[${log.level}] ${log.message}</p>
            <p style="color: var(--text-muted); margin-bottom: 10px;">Traceback:</p>
            <pre style="margin-bottom: 20px;">${log.traceback || 'N/A'}</pre>
            <p style="color: var(--text-muted); margin-bottom: 10px;">Context:</p>
            <pre>${JSON.stringify(log.context, null, 2)}</pre>
        </div>
    `;
    modal.style.display = 'block';

    document.querySelector('.close').onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; }
}

function showError(msg) {
    document.body.innerHTML = `
        <div style="height: 100vh; display: flex; align-items: center; justify-content: center; flex-direction: column; text-align: center; gap: 20px">
            <i class="fas fa-lock" style="font-size: 4rem; color: var(--danger)"></i>
            <h1>${msg}</h1>
            <p style="color: var(--text-muted)">Please access this dashboard only through the official bot admin panel.</p>
        </div>
    `;
}
