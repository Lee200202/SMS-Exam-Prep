/**
 * 成功嶺替代役新訓考古題與備考系統主邏輯
 * 具備隨機抽題模擬考、全題庫即時速查、背題遮罩、成績計算機與必備用品檢核表
 */

// Global App State
const AppState = {
  activeTab: 'quiz',
  isDark: false,
  questions: [],
  studyData: {},
  stats: {},
  mistakes: new Set(),
  bookmarks: new Set(),
  // Quiz State
  quiz: {
    active: false,
    mode: 'mock', // 'mock', 'quick', 'category', 'mistakes'
    questions: [],
    currentIndex: 0,
    answers: {}, // { index: answerValue }
    flags: new Set(),
    instantFeedback: false,
    timer: null,
    timeRemaining: 2400, // 40 minutes in seconds
    totalTime: 2400,
    startTime: null,
    isSubmitted: false
  },
  // Bank State
  bank: {
    searchTerm: '',
    typeFilter: 'all',
    categoryFilter: 'all',
    hideAnswers: false,
    currentPage: 1,
    pageSize: 20
  },
  // Checklist State
  checkedItems: new Set()
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  loadStoredPreferences();
  await loadData();
  setupEventListeners();
  renderCurrentTab();
  initChecklist();
  initCalculator();
  updateHeaderBadges();
  
  // Initialize Lucide icons if available
  if (window.lucide) {
    window.lucide.createIcons();
  }
});

// Load stored localStorage data
function loadStoredPreferences() {
  // Theme
  const savedTheme = localStorage.getItem('sms_theme');
  if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    AppState.isDark = true;
    document.documentElement.classList.add('dark');
  } else {
    AppState.isDark = false;
    document.documentElement.classList.remove('dark');
  }

  // Mistakes
  try {
    const savedMistakes = JSON.parse(localStorage.getItem('sms_mistakes') || '[]');
    AppState.mistakes = new Set(savedMistakes);
  } catch (e) {
    AppState.mistakes = new Set();
  }

  // Bookmarks
  try {
    const savedBookmarks = JSON.parse(localStorage.getItem('sms_bookmarks') || '[]');
    AppState.bookmarks = new Set(savedBookmarks);
  } catch (e) {
    AppState.bookmarks = new Set();
  }

  // Checklist
  try {
    const savedChecks = JSON.parse(localStorage.getItem('sms_checklist') || '[]');
    AppState.checkedItems = new Set(savedChecks);
  } catch (e) {
    AppState.checkedItems = new Set();
  }

  // URL Hash routing
  const hash = window.location.hash.replace('#', '');
  if (['quiz', 'bank', 'regulations', 'volunteer', 'rights', 'shooting', 'checklist'].includes(hash)) {
    AppState.activeTab = hash;
  }
}

// Load Questions & Study Data
async function loadData() {
  try {
    if (window.APP_QUESTIONS && window.APP_STUDY_DATA) {
      AppState.questions = window.APP_QUESTIONS.questions;
      AppState.stats = window.APP_QUESTIONS.stats;
      AppState.studyData = window.APP_STUDY_DATA;
      return;
    }

    // Fallback to fetch
    const [qRes, sRes] = await Promise.all([
      fetch('./data/questions.json'),
      fetch('./data/study_data.json')
    ]);
    const qData = await qRes.json();
    const sData = await sRes.json();

    AppState.questions = qData.questions;
    AppState.stats = qData.stats;
    AppState.studyData = sData;
  } catch (err) {
    console.error('Error loading data:', err);
  }
}

// Update Badges in Header
function updateHeaderBadges() {
  const totalCountEl = document.getElementById('stat-total-questions');
  const mistakeCountEl = document.getElementById('stat-mistake-count');
  if (totalCountEl) totalCountEl.textContent = AppState.questions.length || '262';
  if (mistakeCountEl) mistakeCountEl.textContent = AppState.mistakes.size;
}

// Setup Event Listeners
function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      switchTab(tab);
    });
  });

  // Theme Toggle
  const themeToggle = document.getElementById('btn-theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', toggleTheme);
  }

  // Question Bank Search & Filters
  const searchInput = document.getElementById('bank-search');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      AppState.bank.searchTerm = e.target.value.trim().toLowerCase();
      AppState.bank.currentPage = 1;
      renderQuestionBank();
    });
  }

  const typeFilter = document.getElementById('bank-type-filter');
  if (typeFilter) {
    typeFilter.addEventListener('change', (e) => {
      AppState.bank.typeFilter = e.target.value;
      AppState.bank.currentPage = 1;
      renderQuestionBank();
    });
  }

  const catFilter = document.getElementById('bank-cat-filter');
  if (catFilter) {
    catFilter.addEventListener('change', (e) => {
      AppState.bank.categoryFilter = e.target.value;
      AppState.bank.currentPage = 1;
      renderQuestionBank();
    });
  }

  const hideAnswerSwitch = document.getElementById('bank-hide-answers');
  if (hideAnswerSwitch) {
    hideAnswerSwitch.addEventListener('change', (e) => {
      AppState.bank.hideAnswers = e.target.checked;
      renderQuestionBank();
    });
  }

  // Listen to hash change
  window.addEventListener('hashchange', () => {
    const hash = window.location.hash.replace('#', '');
    if (['quiz', 'bank', 'regulations', 'volunteer', 'rights', 'shooting', 'checklist'].includes(hash)) {
      if (AppState.activeTab !== hash) {
        switchTab(hash, false);
      }
    }
  });
}

// Switch Tab
function switchTab(tab, updateHash = true) {
  AppState.activeTab = tab;
  if (updateHash) {
    window.location.hash = tab;
  }

  document.querySelectorAll('.nav-tab').forEach(btn => {
    if (btn.dataset.tab === tab) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  document.querySelectorAll('.tab-content').forEach(section => {
    section.classList.add('hidden');
  });

  const targetSection = document.getElementById(`tab-${tab}-content`);
  if (targetSection) {
    targetSection.classList.remove('hidden');
  }

  renderCurrentTab();

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Toggle Dark Mode
function toggleTheme() {
  AppState.isDark = !AppState.isDark;
  if (AppState.isDark) {
    document.documentElement.classList.add('dark');
    localStorage.setItem('sms_theme', 'dark');
  } else {
    document.documentElement.classList.remove('dark');
    localStorage.setItem('sms_theme', 'light');
  }
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Render active tab view
function renderCurrentTab() {
  switch (AppState.activeTab) {
    case 'quiz':
      renderQuizView();
      break;
    case 'bank':
      renderQuestionBank();
      break;
    case 'regulations':
      renderRegulations();
      break;
    case 'volunteer':
      renderVolunteer();
      break;
    case 'rights':
      renderRightsAndManagement();
      break;
    case 'shooting':
      renderShootingGuide();
      break;
    case 'checklist':
      renderChecklist();
      break;
  }
}

/* ==========================================================================
   QUIZ ENGINE
   ========================================================================== */

function renderQuizView() {
  const container = document.getElementById('tab-quiz-content');
  if (!container) return;

  if (AppState.quiz.active) {
    if (AppState.quiz.isSubmitted) {
      renderQuizResults();
    } else {
      renderActiveQuiz();
    }
  } else {
    renderQuizSetup();
  }
}

// Quiz Setup Screen
function renderQuizSetup() {
  const container = document.getElementById('tab-quiz-content');
  const mistakeCount = AppState.mistakes.size;

  container.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Welcome Banner -->
      <div class="bg-gradient-to-r from-emerald-600 via-teal-600 to-slate-800 rounded-2xl p-6 sm:p-8 text-white shadow-lg relative overflow-hidden">
        <div class="relative z-10 space-y-3">
          <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur rounded-full text-xs font-semibold tracking-wide uppercase">
            <i data-lucide="shield-check" class="w-4 h-4"></i> 成功嶺基礎訓練必考核心
          </div>
          <h2 class="text-2xl sm:text-3xl font-extrabold tracking-tight">替代役新訓學科鑑測 模擬測驗系統</h2>
          <p class="text-emerald-100 text-sm sm:text-base max-w-2xl leading-relaxed">
            全台最完整的役男期末筆試題庫，支援隨機亂數抽題、倒數計時、選項打亂與錯題複習。助你拿下 95+ 高分，搶佔理想服勤單位！
          </p>
          <div class="flex flex-wrap gap-4 pt-2 text-xs sm:text-sm text-emerald-100">
            <span class="flex items-center gap-1.5"><i data-lucide="check-circle" class="w-4 h-4 text-emerald-300"></i> 收錄 262 題真題</span>
            <span class="flex items-center gap-1.5"><i data-lucide="shuffle" class="w-4 h-4 text-emerald-300"></i> 隨機抽題與洗牌</span>
            <span class="flex items-center gap-1.5"><i data-lucide="award" class="w-4 h-4 text-emerald-300"></i> 學科佔比 35%</span>
          </div>
        </div>
        <i data-lucide="compass" class="absolute -right-6 -bottom-10 w-48 h-48 text-white/10 pointer-events-none"></i>
      </div>

      <!-- Mode Selection Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
        <!-- Mode 1: Standard Mock Exam -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-emerald-500 transition cursor-pointer shadow-sm group" onclick="startQuiz('mock')">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-3 bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="timer" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-semibold rounded-full">推薦首選</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">成功嶺期末標準模擬考</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
              比照實體鑑測標準：是非題 25 題 + 選擇題 25 題，限時 40 分鐘。考完統一交卷結算成績與落點分析。
            </p>
          </div>
          <button class="mt-6 w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium rounded-xl transition flex items-center justify-center gap-2 shadow-sm">
            <span>開始全真模擬考 (50題)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Mode 2: Quick Random Practice -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-teal-500 transition cursor-pointer shadow-sm group" onclick="startQuiz('quick')">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-3 bg-teal-100 dark:bg-teal-950 text-teal-600 dark:text-teal-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="zap" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-teal-500/10 text-teal-600 dark:text-teal-400 font-semibold rounded-full">零碎時間</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">隨機快速刷題 (20題)</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
              隨機抽取 20 題混合是非與選擇題，做一題立即顯示答案與詳解，答錯自動加入錯題筆記本。
            </p>
          </div>
          <button class="mt-6 w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-xl transition flex items-center justify-center gap-2 shadow-sm">
            <span>開始快速刷題 (20題)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Mode 3: Mistakes Review -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-rose-500 transition cursor-pointer shadow-sm group ${mistakeCount === 0 ? 'opacity-60 cursor-not-allowed' : ''}" ${mistakeCount > 0 ? 'onclick="startQuiz(\'mistakes\')"' : ''}>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-3 bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="alert-circle" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-rose-500/10 text-rose-600 dark:text-rose-400 font-semibold rounded-full">
                目前累積 ${mistakeCount} 題
              </span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">錯題專屬筆記本重測</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
              針對你在平常練習或模擬考中答錯的題目進行加強特訓，答對自動移出錯題本，直到全部掌握。
            </p>
          </div>
          <button class="mt-6 w-full py-2.5 ${mistakeCount > 0 ? 'bg-rose-600 hover:bg-rose-700' : 'bg-slate-400'} text-white font-medium rounded-xl transition flex items-center justify-center gap-2 shadow-sm" ${mistakeCount === 0 ? 'disabled' : ''}>
            <span>${mistakeCount > 0 ? '重測所有錯題' : '目前尚無錯題記錄'}</span>
            <i data-lucide="refresh-cw" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Mode 4: Category Specific -->
        <div class="glass-panel p-6 rounded-2xl flex flex-col justify-between hover:border-amber-500 transition shadow-sm">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-3 bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 rounded-xl">
                <i data-lucide="layers" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-400 font-semibold rounded-full">章節專精</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">專項章節測驗</h3>
            <p class="text-slate-600 dark:text-slate-400 text-sm">挑選你較弱的章節進行集中突破：</p>
            <select id="custom-cat-select" class="w-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-800 dark:text-slate-200 outline-none focus:border-amber-500">
              <option value="regulations">⚖️ 替代役實施條例 (${AppState.stats.categories?.regulations || 101}題)</option>
              <option value="volunteer">🤝 志願服務法 (${AppState.stats.categories?.volunteer || 12}題)</option>
              <option value="rights">🎖️ 役男權益與撫卹保險 (${AppState.stats.categories?.rights || 72}題)</option>
              <option value="management">📋 服勤管理與獎懲規定 (${AppState.stats.categories?.management || 43}題)</option>
              <option value="shooting">🎯 射擊打靶與全民國防 (${AppState.stats.categories?.shooting || 11}題)</option>
            </select>
          </div>
          <button onclick="startCategoryQuiz()" class="mt-6 w-full py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-medium rounded-xl transition flex items-center justify-center gap-2 shadow-sm">
            <span>開始專項刷題</span>
            <i data-lucide="play" class="w-4 h-4"></i>
          </button>
        </div>
      </div>

      <!-- Quick Custom Setup Box -->
      <div class="glass-panel p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 text-xs sm:text-sm text-slate-600 dark:text-slate-400">
        <div class="flex items-center gap-4 flex-wrap">
          <label class="flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" id="opt-shuffle-q" checked class="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4">
            <span>隨機打亂題目順序</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" id="opt-shuffle-opt" checked class="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4">
            <span>隨機打亂選項順序</span>
          </label>
        </div>
        <button onclick="resetAllMistakes()" class="text-rose-500 hover:text-rose-600 transition flex items-center gap-1 font-medium">
          <i data-lucide="trash-2" class="w-3.5 h-3.5"></i> 清空錯題本記錄
        </button>
      </div>
    </div>
  `;
}

// Start Quiz logic
function startQuiz(mode) {
  const shuffleQ = document.getElementById('opt-shuffle-q')?.checked ?? true;
  const shuffleOpt = document.getElementById('opt-shuffle-opt')?.checked ?? true;

  let selectedQuestions = [];

  if (mode === 'mock') {
    // 50 questions: 25 TF + 25 MC
    const tfList = AppState.questions.filter(q => q.type === 'true_false');
    const mcList = AppState.questions.filter(q => q.type === 'multiple_choice');

    const pickedTF = pickRandom(tfList, 25);
    const pickedMC = pickRandom(mcList, 25);

    selectedQuestions = [...pickedTF, ...pickedMC];
    if (shuffleQ) {
      shuffleArray(selectedQuestions);
    }

    AppState.quiz.timeRemaining = 2400; // 40 min
    AppState.quiz.totalTime = 2400;
    AppState.quiz.instantFeedback = false;
  } else if (mode === 'quick') {
    // 20 random questions with instant feedback
    selectedQuestions = pickRandom(AppState.questions, 20);
    if (shuffleQ) shuffleArray(selectedQuestions);
    AppState.quiz.timeRemaining = 1200; // 20 min
    AppState.quiz.totalTime = 1200;
    AppState.quiz.instantFeedback = true;
  } else if (mode === 'mistakes') {
    const mistakeIds = Array.from(AppState.mistakes);
    selectedQuestions = AppState.questions.filter(q => mistakeIds.includes(q.id));
    if (shuffleQ) shuffleArray(selectedQuestions);
    AppState.quiz.timeRemaining = selectedQuestions.length * 60;
    AppState.quiz.totalTime = selectedQuestions.length * 60;
    AppState.quiz.instantFeedback = true;
  }

  // Clone and prepare options for MC questions
  AppState.quiz.questions = selectedQuestions.map(orig => {
    const q = JSON.parse(JSON.stringify(orig));
    if (q.type === 'multiple_choice' && shuffleOpt && q.options) {
      // Map options to objects with original index
      const optObjects = q.options.map((text, idx) => ({ text, isCorrect: idx === q.answer }));
      shuffleArray(optObjects);
      q.options = optObjects.map(o => o.text);
      q.answer = optObjects.findIndex(o => o.isCorrect);
    }
    return q;
  });

  AppState.quiz.active = true;
  AppState.quiz.mode = mode;
  AppState.quiz.currentIndex = 0;
  AppState.quiz.answers = {};
  AppState.quiz.flags = new Set();
  AppState.quiz.isSubmitted = false;
  AppState.quiz.startTime = Date.now();

  // Start Timer
  clearInterval(AppState.quiz.timer);
  AppState.quiz.timer = setInterval(() => {
    if (AppState.quiz.timeRemaining > 0) {
      AppState.quiz.timeRemaining--;
      updateTimerDisplay();
    } else {
      submitQuiz();
    }
  }, 1000);

  renderActiveQuiz();
}

function startCategoryQuiz() {
  const catSelect = document.getElementById('custom-cat-select');
  const cat = catSelect ? catSelect.value : 'regulations';

  const catQuestions = AppState.questions.filter(q => q.category === cat);
  const count = Math.min(catQuestions.length, 25);
  const selectedQuestions = pickRandom(catQuestions, count);

  AppState.quiz.questions = selectedQuestions.map(orig => JSON.parse(JSON.stringify(orig)));
  AppState.quiz.active = true;
  AppState.quiz.mode = 'category';
  AppState.quiz.currentIndex = 0;
  AppState.quiz.answers = {};
  AppState.quiz.flags = new Set();
  AppState.quiz.isSubmitted = false;
  AppState.quiz.instantFeedback = true;
  AppState.quiz.timeRemaining = count * 60;
  AppState.quiz.totalTime = count * 60;
  AppState.quiz.startTime = Date.now();

  clearInterval(AppState.quiz.timer);
  AppState.quiz.timer = setInterval(() => {
    if (AppState.quiz.timeRemaining > 0) {
      AppState.quiz.timeRemaining--;
      updateTimerDisplay();
    } else {
      submitQuiz();
    }
  }, 1000);

  renderActiveQuiz();
}

// Render Active Quiz Interface
function renderActiveQuiz() {
  const container = document.getElementById('tab-quiz-content');
  const currentQ = AppState.quiz.questions[AppState.quiz.currentIndex];
  if (!currentQ) return;

  const total = AppState.quiz.questions.length;
  const currIdx = AppState.quiz.currentIndex;
  const answeredCount = Object.keys(AppState.quiz.answers).length;
  const progressPercent = Math.round(((currIdx + 1) / total) * 100);
  const isFlagged = AppState.quiz.flags.has(currIdx);
  const userAnswer = AppState.quiz.answers[currIdx];
  const isAnswered = userAnswer !== undefined;

  const categoryLabels = {
    regulations: '⚖️ 替代役條例',
    volunteer: '🤝 志願服務法',
    rights: '🎖️ 役男權益',
    management: '📋 服勤獎懲',
    shooting: '🎯 射擊國防'
  };

  container.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Quiz Top Bar -->
      <div class="glass-panel p-4 rounded-2xl flex flex-wrap items-center justify-between gap-4 sticky top-16 z-20 shadow-md">
        <!-- Progress Info -->
        <div class="flex items-center gap-3">
          <span class="text-xs sm:text-sm font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">
            第 ${currIdx + 1} / ${total} 題
          </span>
          <span class="text-xs text-slate-500 dark:text-slate-400">已作答 ${answeredCount} 題</span>
        </div>

        <!-- Timer & Actions -->
        <div class="flex items-center gap-3">
          <div id="quiz-timer-box" class="flex items-center gap-1.5 font-mono text-sm sm:text-base font-bold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 px-3 py-1 rounded-lg">
            <i data-lucide="clock" class="w-4 h-4 text-emerald-500"></i>
            <span id="quiz-timer-text">${formatTime(AppState.quiz.timeRemaining)}</span>
          </div>

          <button onclick="toggleFlag(${currIdx})" class="px-3 py-1.5 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition ${isFlagged ? 'bg-amber-100 border-amber-400 text-amber-800 dark:bg-amber-950 dark:text-amber-300' : 'border-slate-300 dark:border-slate-700 text-slate-600 dark:text-slate-400'}">
            <i data-lucide="flag" class="w-3.5 h-3.5"></i>
            <span>${isFlagged ? '已標記' : '標記此題'}</span>
          </button>

          <button onclick="confirmSubmitQuiz()" class="px-4 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs sm:text-sm font-semibold rounded-lg shadow transition flex items-center gap-1">
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>交卷結算</span>
          </button>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
          <div class="bg-emerald-500 h-full transition-all duration-300" style="width: ${progressPercent}%"></div>
        </div>
      </div>

      <!-- Main Question Card -->
      <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm">
        <!-- Question Meta -->
        <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 rounded-md font-medium ${currentQ.type === 'true_false' ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300' : 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300'}">
              ${currentQ.type === 'true_false' ? '是非題' : '四選一選擇題'}
            </span>
            <span class="px-2.5 py-1 rounded-md bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              ${categoryLabels[currentQ.category] || '法規常識'}
            </span>
            ${currentQ.exam_tag ? `<span class="px-2.5 py-1 rounded-md bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-bold border border-amber-300 dark:border-amber-800">${currentQ.exam_tag}</span>` : ''}
          </div>
          <span class="text-slate-400 font-mono text-xs">ID: ${currentQ.id}</span>
        </div>

        <!-- Question Stem -->
        <div class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white leading-relaxed">
          ${currentQ.question}
        </div>

        <!-- Options Area -->
        <div class="space-y-3 pt-2">
          ${renderQuizOptions(currentQ, currIdx, userAnswer)}
        </div>

        <!-- Instant Feedback Area -->
        ${AppState.quiz.instantFeedback && isAnswered ? renderInstantExplanation(currentQ, userAnswer) : ''}
      </div>

      <!-- Bottom Nav Buttons -->
      <div class="flex items-center justify-between gap-4">
        <button onclick="navigateQuiz(${currIdx - 1})" class="px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-medium transition flex items-center gap-2 ${currIdx === 0 ? 'opacity-40 cursor-not-allowed' : ''}" ${currIdx === 0 ? 'disabled' : ''}>
          <i data-lucide="chevron-left" class="w-4 h-4"></i>
          <span>上一題</span>
        </button>

        <!-- Question Palette Modal/Dropdown Toggle -->
        <button onclick="togglePaletteModal()" class="px-4 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-medium text-xs sm:text-sm flex items-center gap-1.5 hover:bg-slate-200 dark:hover:bg-slate-700 transition">
          <i data-lucide="grid" class="w-4 h-4"></i>
          <span>答題卡快速跳題</span>
        </button>

        <button onclick="navigateQuiz(${currIdx + 1})" class="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-medium transition flex items-center gap-2 ${currIdx === total - 1 ? 'opacity-40 cursor-not-allowed' : ''}" ${currIdx === total - 1 ? 'disabled' : ''}>
          <span>下一題</span>
          <i data-lucide="chevron-right" class="w-4 h-4"></i>
        </button>
      </div>

      <!-- Question Palette Matrix Card (Inline) -->
      <div id="quiz-palette-container" class="glass-panel p-5 rounded-2xl space-y-3">
        <div class="flex items-center justify-between">
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">答題卡總覽</h4>
          <div class="flex items-center gap-3 text-xs text-slate-500">
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-emerald-500 inline-block"></span> 已答</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-slate-200 dark:bg-slate-700 inline-block"></span> 未答</span>
            <span class="flex items-center gap-1"><span class="w-3 h-3 rounded-full bg-amber-400 inline-block"></span> 標記</span>
          </div>
        </div>
        <div class="grid grid-cols-8 sm:grid-cols-10 md:grid-cols-12 gap-2">
          ${AppState.quiz.questions.map((q, idx) => {
            const answered = AppState.quiz.answers[idx] !== undefined;
            const flagged = AppState.quiz.flags.has(idx);
            const isCurrent = idx === currIdx;

            let colorClass = 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 hover:bg-slate-200';
            if (answered) colorClass = 'bg-emerald-600 text-white hover:bg-emerald-700';
            if (flagged) colorClass = 'bg-amber-400 text-slate-950 font-bold hover:bg-amber-500';

            return `
              <button onclick="navigateQuiz(${idx})" class="palette-btn w-full aspect-square text-xs font-semibold rounded-lg flex items-center justify-center relative ${colorClass} ${isCurrent ? 'ring-2 ring-emerald-500 ring-offset-2 dark:ring-offset-slate-900 scale-105' : ''}">
                ${idx + 1}
              </button>
            `;
          }).join('')}
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

// Render options depending on question type
function renderQuizOptions(q, currIdx, userAnswer) {
  if (q.type === 'true_false') {
    const isAnswered = userAnswer !== undefined;
    const isO = userAnswer === 'O';
    const isX = userAnswer === 'X';

    let oStyle = isO ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 ring-2 ring-emerald-500' : 'border-slate-200 dark:border-slate-700 hover:border-emerald-300';
    let xStyle = isX ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 ring-2 ring-emerald-500' : 'border-slate-200 dark:border-slate-700 hover:border-emerald-300';

    if (AppState.quiz.instantFeedback && isAnswered) {
      if (q.answer === 'O') {
        oStyle = 'border-emerald-500 bg-emerald-100 dark:bg-emerald-950/60 ring-2 ring-emerald-500 text-emerald-800 dark:text-emerald-200 font-bold';
      } else {
        xStyle = 'border-emerald-500 bg-emerald-100 dark:bg-emerald-950/60 ring-2 ring-emerald-500 text-emerald-800 dark:text-emerald-200 font-bold';
      }
      if (userAnswer !== q.answer) {
        if (userAnswer === 'O') oStyle = 'border-rose-500 bg-rose-100 dark:bg-rose-950/60 ring-2 ring-rose-500 text-rose-800';
        if (userAnswer === 'X') xStyle = 'border-rose-500 bg-rose-100 dark:bg-rose-950/60 ring-2 ring-rose-500 text-rose-800';
      }
    }

    return `
      <div class="grid grid-cols-2 gap-4">
        <button onclick="selectQuizAnswer('O')" class="option-btn p-5 rounded-2xl border text-center font-bold text-lg sm:text-xl transition flex flex-col items-center justify-center gap-2 ${oStyle}">
          <span class="text-3xl text-emerald-600 dark:text-emerald-400">⭕</span>
          <span>正確 (O)</span>
        </button>
        <button onclick="selectQuizAnswer('X')" class="option-btn p-5 rounded-2xl border text-center font-bold text-lg sm:text-xl transition flex flex-col items-center justify-center gap-2 ${xStyle}">
          <span class="text-3xl text-rose-600 dark:text-rose-400">❌</span>
          <span>錯誤 (X)</span>
        </button>
      </div>
    `;
  } else {
    // Multiple Choice
    const labels = ['A', 'B', 'C', 'D'];
    const isAnswered = userAnswer !== undefined;

    return q.options.map((optText, optIdx) => {
      const isSelected = userAnswer === optIdx;
      let optStyle = isSelected ? 'border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 ring-2 ring-emerald-500' : 'border-slate-200 dark:border-slate-700 hover:border-emerald-300';

      if (AppState.quiz.instantFeedback && isAnswered) {
        if (optIdx === q.answer) {
          optStyle = 'border-emerald-500 bg-emerald-100 dark:bg-emerald-950/60 ring-2 ring-emerald-500 text-emerald-900 dark:text-emerald-100 font-bold';
        } else if (isSelected && optIdx !== q.answer) {
          optStyle = 'border-rose-500 bg-rose-100 dark:bg-rose-950/60 ring-2 ring-rose-500 text-rose-800 font-bold';
        }
      }

      return `
        <button onclick="selectQuizAnswer(${optIdx})" class="option-btn w-full p-4 rounded-2xl border text-left text-sm sm:text-base font-medium transition flex items-start gap-3.5 ${optStyle}">
          <span class="w-7 h-7 rounded-xl bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 font-bold text-xs flex items-center justify-center shrink-0">
            ${labels[optIdx] || optIdx + 1}
          </span>
          <span class="flex-1 pt-0.5 leading-snug">${optText}</span>
        </button>
      `;
    }).join('');
  }
}

// Render Instant Explanation
function renderInstantExplanation(q, userAnswer) {
  const isCorrect = (q.type === 'true_false' && userAnswer === q.answer) || (q.type === 'multiple_choice' && userAnswer === q.answer);
  const correctText = q.type === 'true_false' ? (q.answer === 'O' ? '⭕ 正確 (O)' : '❌ 錯誤 (X)') : `選項 (${['A','B','C','D'][q.answer]}) ${q.options[q.answer]}`;

  return `
    <div class="p-4 rounded-2xl border ${isCorrect ? 'bg-emerald-50 border-emerald-300 text-emerald-900 dark:bg-emerald-950/40 dark:border-emerald-800 dark:text-emerald-200' : 'bg-rose-50 border-rose-300 text-rose-900 dark:bg-rose-950/40 dark:border-rose-800 dark:text-rose-200'} space-y-2">
      <div class="flex items-center gap-2 font-bold text-sm sm:text-base">
        <i data-lucide="${isCorrect ? 'check-circle' : 'x-circle'}" class="w-5 h-5"></i>
        <span>${isCorrect ? '恭喜答對！' : '很可惜答錯了！'}</span>
        <span class="text-xs font-normal ml-auto">標準答案：<strong class="font-bold underline">${correctText}</strong></span>
      </div>
      ${q.explanation ? `<p class="text-xs sm:text-sm opacity-90 leading-relaxed"><strong class="font-semibold">【詳解依據】</strong> ${q.explanation}</p>` : ''}
    </div>
  `;
}

// Record Quiz Answer
function selectQuizAnswer(val) {
  const currIdx = AppState.quiz.currentIndex;
  AppState.quiz.answers[currIdx] = val;

  const currentQ = AppState.quiz.questions[currIdx];
  const isCorrect = (currentQ.type === 'true_false' && val === currentQ.answer) || (currentQ.type === 'multiple_choice' && val === currentQ.answer);

  // Auto record mistakes in mistakes notebook
  if (!isCorrect) {
    AppState.mistakes.add(currentQ.id);
    saveMistakes();
  } else if (AppState.quiz.mode === 'mistakes') {
    // If in mistake mode and answered correctly, remove from mistake list
    AppState.mistakes.delete(currentQ.id);
    saveMistakes();
  }

  updateHeaderBadges();
  renderActiveQuiz();
}

// Navigation between quiz questions
function navigateQuiz(index) {
  if (index < 0 || index >= AppState.quiz.questions.length) return;
  AppState.quiz.currentIndex = index;
  renderActiveQuiz();
}

function toggleFlag(index) {
  if (AppState.quiz.flags.has(index)) {
    AppState.quiz.flags.delete(index);
  } else {
    AppState.quiz.flags.add(index);
  }
  renderActiveQuiz();
}

function updateTimerDisplay() {
  const timerTextEl = document.getElementById('quiz-timer-text');
  if (timerTextEl) {
    timerTextEl.textContent = formatTime(AppState.quiz.timeRemaining);
  }
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function confirmSubmitQuiz() {
  const answeredCount = Object.keys(AppState.quiz.answers).length;
  const total = AppState.quiz.questions.length;
  const unanswered = total - answeredCount;

  let msg = '確定要交卷結算成績嗎？';
  if (unanswered > 0) {
    msg = `您還有 ${unanswered} 題尚未作答！確定要提前交卷結算成績嗎？`;
  }

  if (confirm(msg)) {
    submitQuiz();
  }
}

function submitQuiz() {
  clearInterval(AppState.quiz.timer);
  AppState.quiz.isSubmitted = true;
  renderQuizResults();
}

// Quiz Results Screen
function renderQuizResults() {
  const container = document.getElementById('tab-quiz-content');
  const questions = AppState.quiz.questions;
  const answers = AppState.quiz.answers;
  const total = questions.length;

  let correctCount = 0;
  const categoryStats = {};

  questions.forEach((q, idx) => {
    const userAns = answers[idx];
    const isCorrect = (q.type === 'true_false' && userAns === q.answer) || (q.type === 'multiple_choice' && userAns === q.answer);

    if (isCorrect) correctCount++;

    if (!categoryStats[q.category]) {
      categoryStats[q.category] = { total: 0, correct: 0 };
    }
    categoryStats[q.category].total++;
    if (isCorrect) categoryStats[q.category].correct++;

    // Track mistakes
    if (!isCorrect) {
      AppState.mistakes.add(q.id);
    }
  });

  saveMistakes();
  updateHeaderBadges();

  const score = Math.round((correctCount / total) * 100);
  const timeUsed = AppState.quiz.totalTime - AppState.quiz.timeRemaining;

  // Trigger celebration confetti if score >= 80
  if (score >= 80 && window.confetti) {
    window.confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    });
  }

  const categoryNames = {
    regulations: '⚖️ 替代役實施條例',
    volunteer: '🤝 志願服務法',
    rights: '🎖️ 役男權益與保險',
    management: '📋 服勤生活獎懲',
    shooting: '🎯 射擊打靶國防'
  };

  container.innerHTML = `
    <div class="max-w-4xl mx-auto space-y-6">
      <!-- Result Banner -->
      <div class="glass-panel p-6 sm:p-10 rounded-3xl text-center space-y-4 shadow-lg border-2 ${score >= 80 ? 'border-emerald-500' : score >= 60 ? 'border-amber-500' : 'border-rose-500'}">
        <div class="inline-flex items-center justify-center p-4 rounded-full ${score >= 80 ? 'bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400' : score >= 60 ? 'bg-amber-100 text-amber-600' : 'bg-rose-100 text-rose-600'}">
          <i data-lucide="${score >= 80 ? 'trophy' : score >= 60 ? 'award' : 'alert-triangle'}" class="w-12 h-12"></i>
        </div>

        <h2 class="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white">
          得分：${score} 分
        </h2>

        <p class="text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-md mx-auto">
          ${score >= 90 ? '🌟 精英役男！學科測驗表現頂尖，選役別高分勝券在握！' : score >= 80 ? '👏 表現非常優異！建議複習少數錯題，維持穩定水準！' : score >= 60 ? '⚠️ 順利及格，但部分法規與時數細節仍需加強，以免鑑測失分！' : '❌ 尚未達到及格標準，建議利用題庫與重點整理加強複習！'}
        </p>

        <!-- Summary Metrics -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 max-w-2xl mx-auto">
          <div class="p-3 rounded-xl bg-slate-100 dark:bg-slate-800">
            <span class="text-xs text-slate-500 dark:text-slate-400">總題數</span>
            <div class="text-lg font-bold text-slate-900 dark:text-white">${total} 題</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-100 dark:bg-slate-800">
            <span class="text-xs text-slate-500 dark:text-slate-400">答對題數</span>
            <div class="text-lg font-bold text-emerald-600 dark:text-emerald-400">${correctCount} 題</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-100 dark:bg-slate-800">
            <span class="text-xs text-slate-500 dark:text-slate-400">答錯題數</span>
            <div class="text-lg font-bold text-rose-600 dark:text-rose-400">${total - correctCount} 題</div>
          </div>
          <div class="p-3 rounded-xl bg-slate-100 dark:bg-slate-800">
            <span class="text-xs text-slate-500 dark:text-slate-400">耗費時間</span>
            <div class="text-lg font-bold text-slate-900 dark:text-white">${formatTime(timeUsed)}</div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-wrap items-center justify-center gap-3 pt-4">
          <button onclick="startQuiz('${AppState.quiz.mode}')" class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl transition flex items-center gap-2 shadow">
            <i data-lucide="refresh-cw" class="w-4 h-4"></i>
            <span>重新測驗</span>
          </button>
          ${total - correctCount > 0 ? `
            <button onclick="retakeMistakesFromThisQuiz()" class="px-6 py-2.5 bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-xl transition flex items-center gap-2 shadow">
              <i data-lucide="alert-circle" class="w-4 h-4"></i>
              <span>只重測本次錯題 (${total - correctCount})</span>
            </button>
          ` : ''}
          <button onclick="AppState.quiz.active = false; renderQuizView();" class="px-6 py-2.5 border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold rounded-xl transition">
            返回測驗大廳
          </button>
        </div>
      </div>

      <!-- Category Breakdown -->
      <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <i data-lucide="bar-chart-2" class="w-5 h-5 text-emerald-500"></i> 各章節落點分析
        </h3>
        <div class="space-y-3">
          ${Object.entries(categoryStats).map(([cat, stat]) => {
            const pct = Math.round((stat.correct / stat.total) * 100);
            return `
              <div class="space-y-1">
                <div class="flex justify-between text-xs sm:text-sm">
                  <span class="font-medium text-slate-700 dark:text-slate-300">${categoryNames[cat] || cat}</span>
                  <span class="font-bold ${pct >= 80 ? 'text-emerald-500' : pct >= 60 ? 'text-amber-500' : 'text-rose-500'}">${stat.correct} / ${stat.total} (${pct}%)</span>
                </div>
                <div class="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                  <div class="h-full ${pct >= 80 ? 'bg-emerald-500' : pct >= 60 ? 'bg-amber-500' : 'bg-rose-500'}" style="width: ${pct}%"></div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- Review Questions List -->
      <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
        <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <i data-lucide="file-text" class="w-5 h-5 text-emerald-500"></i> 完整試題解析與回顧
        </h3>
        <div class="space-y-4">
          ${questions.map((q, idx) => {
            const userAns = answers[idx];
            const isCorrect = (q.type === 'true_false' && userAns === q.answer) || (q.type === 'multiple_choice' && userAns === q.answer);

            let userAnsText = '未作答';
            let correctAnsText = '';
            if (q.type === 'true_false') {
              if (userAns) userAnsText = userAns === 'O' ? '⭕ 正確 (O)' : '❌ 錯誤 (X)';
              correctAnsText = q.answer === 'O' ? '⭕ 正確 (O)' : '❌ 錯誤 (X)';
            } else {
              const labels = ['A', 'B', 'C', 'D'];
              if (userAns !== undefined) userAnsText = `(${labels[userAns]}) ${q.options[userAns]}`;
              correctAnsText = `(${labels[q.answer]}) ${q.options[q.answer]}`;
            }

            return `
              <div class="p-4 rounded-xl border ${isCorrect ? 'border-emerald-200 bg-emerald-50/40 dark:border-emerald-900 dark:bg-emerald-950/20' : 'border-rose-200 bg-rose-50/40 dark:border-rose-900 dark:bg-rose-950/20'} space-y-2">
                <div class="flex items-start justify-between gap-2">
                  <span class="text-xs font-bold px-2 py-0.5 rounded ${isCorrect ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200' : 'bg-rose-100 text-rose-800 dark:bg-rose-900 dark:text-rose-200'}">
                    第 ${idx + 1} 題 · ${isCorrect ? '答對' : '答錯'}
                  </span>
                  <span class="text-xs text-slate-400">ID: ${q.id}</span>
                </div>
                <div class="text-sm font-semibold text-slate-900 dark:text-slate-100">${q.question}</div>
                <div class="text-xs space-y-1 pt-1">
                  <div>你的作答：<span class="${isCorrect ? 'text-emerald-600 font-bold' : 'text-rose-600 font-bold'}">${userAnsText}</span></div>
                  ${!isCorrect ? `<div>正確答案：<span class="text-emerald-600 font-bold">${correctAnsText}</span></div>` : ''}
                  ${q.explanation ? `<div class="text-slate-600 dark:text-slate-400 pt-1"><strong>【解析】</strong> ${q.explanation}</div>` : ''}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function retakeMistakesFromThisQuiz() {
  const questions = AppState.quiz.questions;
  const answers = AppState.quiz.answers;
  const wrongQuestions = questions.filter((q, idx) => {
    const userAns = answers[idx];
    return !((q.type === 'true_false' && userAns === q.answer) || (q.type === 'multiple_choice' && userAns === q.answer));
  });

  if (wrongQuestions.length === 0) return;

  AppState.quiz.questions = wrongQuestions.map(q => JSON.parse(JSON.stringify(q)));
  AppState.quiz.currentIndex = 0;
  AppState.quiz.answers = {};
  AppState.quiz.flags = new Set();
  AppState.quiz.isSubmitted = false;
  AppState.quiz.instantFeedback = true;
  AppState.quiz.timeRemaining = wrongQuestions.length * 60;
  AppState.quiz.totalTime = wrongQuestions.length * 60;
  AppState.quiz.startTime = Date.now();

  clearInterval(AppState.quiz.timer);
  AppState.quiz.timer = setInterval(() => {
    if (AppState.quiz.timeRemaining > 0) {
      AppState.quiz.timeRemaining--;
      updateTimerDisplay();
    } else {
      submitQuiz();
    }
  }, 1000);

  renderActiveQuiz();
}

function resetAllMistakes() {
  if (confirm('確定要清空所有答錯的題目記錄嗎？')) {
    AppState.mistakes.clear();
    saveMistakes();
    updateHeaderBadges();
    renderQuizSetup();
  }
}

function saveMistakes() {
  localStorage.setItem('sms_mistakes', JSON.stringify(Array.from(AppState.mistakes)));
}

function saveBookmarks() {
  localStorage.setItem('sms_bookmarks', JSON.stringify(Array.from(AppState.bookmarks)));
}

/* ==========================================================================
   QUESTION BANK VIEWER
   ========================================================================== */

function renderQuestionBank() {
  const container = document.getElementById('bank-list-container');
  if (!container) return;

  const { searchTerm, typeFilter, categoryFilter, hideAnswers, currentPage, pageSize } = AppState.bank;

  // Filter questions
  let filtered = AppState.questions.filter(q => {
    if (typeFilter !== 'all' && q.type !== typeFilter) return false;
    if (categoryFilter !== 'all' && q.category !== categoryFilter) return false;
    if (searchTerm) {
      const inQ = q.question.toLowerCase().includes(searchTerm);
      const inOpt = q.options ? q.options.some(o => o.toLowerCase().includes(searchTerm)) : false;
      const inExpl = q.explanation ? q.explanation.toLowerCase().includes(searchTerm) : false;
      if (!inQ && !inOpt && !inExpl) return false;
    }
    return true;
  });

  const countBadge = document.getElementById('bank-filtered-count');
  if (countBadge) countBadge.textContent = filtered.length;

  const totalPages = Math.ceil(filtered.length / pageSize) || 1;
  const page = Math.min(currentPage, totalPages);
  const startIdx = (page - 1) * pageSize;
  const pageQuestions = filtered.slice(startIdx, startIdx + pageSize);

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="glass-panel p-12 text-center rounded-2xl text-slate-500 dark:text-slate-400 space-y-3">
        <i data-lucide="search-x" class="w-12 h-12 mx-auto text-slate-400"></i>
        <h4 class="text-base font-semibold">沒有找到相符的題目</h4>
        <p class="text-xs">請嘗試更改搜尋關鍵字或清除篩選條件。</p>
      </div>
    `;
    renderPagination(1, 1);
    if (window.lucide) window.lucide.createIcons();
    return;
  }

  const categoryNames = {
    regulations: '⚖️ 替代役條例',
    volunteer: '🤝 志願服務法',
    rights: '🎖️ 役男權益',
    management: '📋 服勤獎懲',
    shooting: '🎯 射擊國防'
  };

  container.innerHTML = pageQuestions.map((q, idx) => {
    const isBookmarked = AppState.bookmarks.has(q.id);
    const isMistake = AppState.mistakes.has(q.id);
    const itemNum = startIdx + idx + 1;

    let ansDisplay = '';
    if (q.type === 'true_false') {
      ansDisplay = `<span class="inline-flex items-center gap-1 font-bold ${q.answer === 'O' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">${q.answer === 'O' ? '⭕ 正確 (O)' : '❌ 錯誤 (X)'}</span>`;
    } else {
      const labels = ['A', 'B', 'C', 'D'];
      ansDisplay = `<span class="font-bold text-emerald-600 dark:text-emerald-400">(${labels[q.answer]}) ${q.options[q.answer]}</span>`;
    }

    return `
      <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-4 shadow-sm hover:shadow transition relative" id="bank-card-${q.id}">
        <!-- Top Tags & Bookmark -->
        <div class="flex items-center justify-between flex-wrap gap-2 text-xs">
          <div class="flex items-center gap-2">
            <span class="font-mono font-bold text-slate-400">#${itemNum}</span>
            <span class="px-2 py-0.5 rounded font-medium ${q.type === 'true_false' ? 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300' : 'bg-purple-100 text-purple-700 dark:bg-purple-950 dark:text-purple-300'}">
              ${q.type === 'true_false' ? '是非' : '選擇'}
            </span>
            <span class="px-2 py-0.5 rounded bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400">
              ${categoryNames[q.category] || '法規'}
            </span>
            ${q.exam_tag ? `<span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 text-[10px] font-bold border border-amber-300 dark:border-amber-800">${q.exam_tag}</span>` : ''}
            ${isMistake ? '<span class="px-2 py-0.5 rounded bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300 text-[10px] font-semibold">曾答錯</span>' : ''}
          </div>

          <div class="flex items-center gap-2">
            <button onclick="toggleBookmark('${q.id}')" class="p-1 text-slate-400 hover:text-amber-500 transition ${isBookmarked ? 'text-amber-500' : ''}" title="收藏題目">
              <i data-lucide="${isBookmarked ? 'bookmark-check' : 'bookmark'}" class="w-4 h-4"></i>
            </button>
            <button onclick="copyQuestion('${q.id}')" class="p-1 text-slate-400 hover:text-emerald-500 transition" title="複製題目">
              <i data-lucide="copy" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

        <!-- Question Body -->
        <div class="text-sm sm:text-base font-bold text-slate-900 dark:text-slate-100 leading-relaxed">
          ${highlightText(q.question, searchTerm)}
        </div>

        <!-- Options for MC -->
        ${q.type === 'multiple_choice' ? `
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm text-slate-700 dark:text-slate-300">
            ${q.options.map((opt, oIdx) => `
              <div class="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 flex items-start gap-2 ${oIdx === q.answer && !hideAnswers ? 'border-emerald-400 bg-emerald-50/60 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 font-semibold' : ''}">
                <span class="font-bold text-slate-400 shrink-0">(${['A','B','C','D'][oIdx]})</span>
                <span class="flex-1">${highlightText(opt, searchTerm)}</span>
              </div>
            `).join('')}
          </div>
        ` : ''}

        <!-- Answer & Explanation -->
        <div class="pt-2 border-t border-slate-100 dark:border-slate-800/80">
          <div class="answer-wrapper ${hideAnswers ? 'answer-masked' : 'answer-unmasked'}" onclick="this.classList.toggle('answer-masked'); this.classList.toggle('answer-unmasked');">
            <div class="text-xs sm:text-sm flex flex-wrap items-center gap-2">
              <span class="font-semibold text-slate-500">標準答案：</span>
              ${ansDisplay}
            </div>
            ${q.explanation ? `
              <div class="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">
                <strong>【解析】</strong> ${highlightText(q.explanation, searchTerm)}
              </div>
            ` : ''}
            ${hideAnswers ? `<span class="text-[10px] text-emerald-500 italic block mt-1">（點擊此區塊解除模糊遮罩查看答案）</span>` : ''}
          </div>
        </div>
      </div>
    `;
  }).join('');

  renderPagination(page, totalPages);
  if (window.lucide) window.lucide.createIcons();
}

function renderPagination(page, totalPages) {
  const container = document.getElementById('bank-pagination');
  if (!container) return;

  container.innerHTML = `
    <div class="flex items-center justify-between text-xs sm:text-sm text-slate-500 dark:text-slate-400">
      <span>第 ${page} / ${totalPages} 頁</span>
      <div class="flex items-center gap-2">
        <button onclick="changeBankPage(${page - 1})" class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40" ${page <= 1 ? 'disabled' : ''}>
          上一頁
        </button>
        <button onclick="changeBankPage(${page + 1})" class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40" ${page >= totalPages ? 'disabled' : ''}>
          下一頁
        </button>
      </div>
    </div>
  `;
}

function changeBankPage(newPage) {
  AppState.bank.currentPage = newPage;
  renderQuestionBank();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleBookmark(id) {
  if (AppState.bookmarks.has(id)) {
    AppState.bookmarks.delete(id);
  } else {
    AppState.bookmarks.add(id);
  }
  saveBookmarks();
  renderQuestionBank();
}

function copyQuestion(id) {
  const q = AppState.questions.find(item => item.id === id);
  if (!q) return;

  let text = `${q.question}\n`;
  if (q.type === 'multiple_choice') {
    q.options.forEach((opt, idx) => {
      text += `(${['A','B','C','D'][idx]}) ${opt}\n`;
    });
    text += `答案：(${['A','B','C','D'][q.answer]}) ${q.options[q.answer]}`;
  } else {
    text += `答案：${q.answer === 'O' ? '⭕ 正確' : '❌ 錯誤'}`;
  }

  navigator.clipboard.writeText(text).then(() => {
    alert('題目與答案已複製到剪貼簿！');
  });
}

function highlightText(text, keyword) {
  if (!keyword || !text) return text;
  const regex = new RegExp(`(${escapeRegex(keyword)})`, 'gi');
  return text.replace(regex, '<mark class="bg-amber-200 dark:bg-amber-900 text-slate-900 dark:text-white px-0.5 rounded">$1</mark>');
}

function escapeRegex(string) {
  return string.replace(/[/\-\\^$*+?.()|[\]{}]/g, '\\$&');
}

/* ==========================================================================
   STUDY GUIDES: REGULATIONS, VOLUNTEER, RIGHTS, SHOOTING
   ========================================================================== */

function renderRegulations() {
  const data = AppState.studyData.regulations;
  const container = document.getElementById('regulations-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-6">
      <div class="p-6 bg-gradient-to-r from-slate-900 to-slate-800 text-white rounded-2xl space-y-2 shadow">
        <h3 class="text-xl font-bold flex items-center gap-2 text-emerald-400">
          <i data-lucide="scale" class="w-6 h-6"></i> ${data.title}
        </h3>
        <p class="text-sm text-slate-300">${data.description}</p>
      </div>

      ${data.sections.map(sec => `
        <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
          <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-emerald-500 pl-3">
            ${sec.title}
          </h4>

          ${sec.content ? `
            <div class="space-y-2 text-sm text-slate-700 dark:text-slate-300">
              ${sec.content.map(c => `<p class="leading-relaxed">${c.replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-700 dark:text-emerald-400 font-bold">$1</strong>')}</p>`).join('')}
            </div>
          ` : ''}

          ${sec.table ? `
            <div class="overflow-x-auto">
              <table class="w-full text-left text-xs sm:text-sm border-collapse">
                <thead>
                  <tr class="border-b border-slate-200 dark:border-slate-700 bg-slate-100/70 dark:bg-slate-800/70 text-slate-800 dark:text-slate-200">
                    ${sec.table.headers.map(h => `<th class="py-2.5 px-3 font-bold">${h}</th>`).join('')}
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                  ${sec.table.rows.map(row => `
                    <tr class="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                      <td class="py-2.5 px-3 font-semibold text-slate-900 dark:text-white">${row[0]}</td>
                      <td class="py-2.5 px-3 font-bold text-emerald-600 dark:text-emerald-400">${row[1]}</td>
                      <td class="py-2.5 px-3 text-slate-600 dark:text-slate-400">${row[2]}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : ''}

          ${sec.points ? `
            <ul class="list-disc list-inside space-y-2 text-sm text-slate-700 dark:text-slate-300">
              ${sec.points.map(p => `<li>${p.replace(/\*\*(.*?)\*\*/g, '<strong class="text-slate-900 dark:text-white font-bold">$1</strong>')}</li>`).join('')}
            </ul>
          ` : ''}
        </div>
      `).join('')}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function renderVolunteer() {
  const data = AppState.studyData.volunteer;
  const container = document.getElementById('volunteer-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-6">
      <div class="p-6 bg-gradient-to-r from-teal-800 to-slate-900 text-white rounded-2xl space-y-2 shadow">
        <h3 class="text-xl font-bold flex items-center gap-2 text-teal-300">
          <i data-lucide="hand-heart" class="w-6 h-6"></i> ${data.title}
        </h3>
        <p class="text-sm text-slate-300">${data.description}</p>
      </div>

      ${data.sections.map(sec => `
        <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
          <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-teal-500 pl-3">
            ${sec.title}
          </h4>

          ${sec.content ? `
            <div class="space-y-2 text-sm text-slate-700 dark:text-slate-300">
              ${sec.content.map(c => `<p class="leading-relaxed">${c.replace(/\*\*(.*?)\*\*/g, '<strong class="text-teal-700 dark:text-teal-400 font-bold">$1</strong>')}</p>`).join('')}
            </div>
          ` : ''}

          ${sec.items ? `
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              ${sec.items.map(item => `
                <div class="p-4 rounded-xl border border-teal-200 dark:border-teal-900/60 bg-teal-50/40 dark:bg-teal-950/20 space-y-2">
                  <span class="inline-block px-2.5 py-0.5 rounded-full text-xs font-bold bg-teal-500 text-white shadow-sm">
                    ${item.badge}
                  </span>
                  <h5 class="text-sm font-bold text-slate-900 dark:text-white">${item.title}</h5>
                  <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                    ${item.desc.replace(/\*\*(.*?)\*\*/g, '<strong class="text-teal-600 dark:text-teal-400 font-bold">$1</strong>')}
                  </p>
                </div>
              `).join('')}
            </div>
          ` : ''}
        </div>
      `).join('')}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function renderRightsAndManagement() {
  const data = AppState.studyData.rights_and_management;
  const container = document.getElementById('rights-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-6">
      <div class="p-6 bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-2xl space-y-2 shadow">
        <h3 class="text-xl font-bold flex items-center gap-2 text-blue-300">
          <i data-lucide="shield" class="w-6 h-6"></i> ${data.title}
        </h3>
        <p class="text-sm text-slate-300">${data.description}</p>
      </div>

      <!-- Grade Breakdown Calculator -->
      <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm border border-emerald-500/30">
        <div class="flex items-center justify-between">
          <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <i data-lucide="calculator" class="w-5 h-5 text-emerald-500"></i> ${data.grade_breakdown.title}
          </h4>
          <span class="text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2 py-1 rounded-md font-semibold">分發關鍵</span>
        </div>
        <p class="text-xs text-slate-500">${data.grade_breakdown.desc}</p>

        <!-- Components List -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
          ${data.grade_breakdown.components.map(c => `
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 space-y-1">
              <div class="flex justify-between items-center">
                <span class="text-sm font-bold text-slate-900 dark:text-white">${c.name}</span>
                <span class="px-2 py-0.5 rounded bg-emerald-500 text-white text-xs font-bold">佔比 ${c.ratio}</span>
              </div>
              <p class="text-xs text-slate-500 dark:text-slate-400">${c.desc}</p>
            </div>
          `).join('')}
        </div>

        <!-- Interactive Score Calculator -->
        <div class="mt-4 p-5 rounded-xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-800 space-y-4">
          <div class="flex items-center justify-between">
            <h5 class="text-xs font-bold uppercase tracking-wider text-emerald-800 dark:text-emerald-300">新訓鑑測成績試算機 (247T/257T最新配分標準)</h5>
            <span class="text-[11px] text-slate-500 dark:text-slate-400">總成績佔分發比重不得低於 40%</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div>
              <label class="text-xs text-slate-600 dark:text-slate-400 block mb-1">學科筆試 (35%)</label>
              <input type="number" id="calc-academic" min="0" max="100" value="92" oninput="calculateTotalScore()" class="w-full px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-bold">
            </div>
            <div>
              <label class="text-xs text-slate-600 dark:text-slate-400 block mb-1">3000m體能 (15%)</label>
              <input type="number" id="calc-run" min="0" max="100" value="90" oninput="calculateTotalScore()" class="w-full px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-bold">
            </div>
            <div>
              <label class="text-xs text-slate-600 dark:text-slate-400 block mb-1">徒手基教 (20%)</label>
              <input type="number" id="calc-drill" min="0" max="100" value="85" oninput="calculateTotalScore()" class="w-full px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-bold">
            </div>
            <div>
              <label class="text-xs text-slate-600 dark:text-slate-400 block mb-1">EMT-1救護 (20%)</label>
              <input type="number" id="calc-emt" min="0" max="100" value="88" oninput="calculateTotalScore()" class="w-full px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-bold">
            </div>
            <div class="col-span-2 sm:col-span-1">
              <label class="text-xs text-slate-600 dark:text-slate-400 block mb-1">平時內務 (10%)</label>
              <input type="number" id="calc-life" min="0" max="100" value="80" oninput="calculateTotalScore()" class="w-full px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-sm font-bold">
            </div>
          </div>
          <div class="flex flex-wrap items-center justify-between pt-2 border-t border-emerald-200 dark:border-emerald-800 gap-2">
            <span class="text-sm font-bold text-slate-700 dark:text-slate-300">總體綜合鑑測預估成績：</span>
            <span id="calc-result-badge" class="text-lg sm:text-xl font-black text-emerald-600 dark:text-emerald-400">88.30 分 (優等)</span>
          </div>
        </div>
      </div>

      <!-- Rights List -->
      <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm">
        <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-blue-500 pl-3">
          役男法定身分權益保障
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          ${data.rights.map(r => `
            <div class="p-3.5 rounded-xl bg-blue-50/30 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              ${r.replace(/\*\*(.*?)\*\*/g, '<strong class="text-blue-700 dark:text-blue-400 font-bold block mb-1">$1</strong>')}
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Punishments List -->
      <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm">
        <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-rose-500 pl-3">
          役男服勤違規懲處基準 (替代役管理法規)
        </h4>
        <div class="space-y-2">
          ${data.punishments.map(p => `
            <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 text-xs sm:text-sm text-slate-700 dark:text-slate-300 flex items-center gap-2">
              <i data-lucide="alert-octagon" class="w-4 h-4 text-rose-500 shrink-0"></i>
              <span>${p.replace(/\*\*(.*?)\*\*/g, '<strong class="text-rose-600 dark:text-rose-400 font-bold">$1</strong>')}</span>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function calculateTotalScore() {
  const acad = parseFloat(document.getElementById('calc-academic')?.value || '0');
  const run = parseFloat(document.getElementById('calc-run')?.value || '0');
  const drill = parseFloat(document.getElementById('calc-drill')?.value || '0');
  const emt = parseFloat(document.getElementById('calc-emt')?.value || '0');
  const life = parseFloat(document.getElementById('calc-life')?.value || '0');

  // 247T official distribution: Academic 35%, Run 15%, Drill 20%, EMT 20%, Life 10%
  const total = (acad * 0.35) + (run * 0.15) + (drill * 0.20) + (emt * 0.20) + (life * 0.10);
  const badge = document.getElementById('calc-result-badge');
  if (badge) {
    let rank = '待加強';
    if (total >= 90) rank = '特優 (選役別第一志願穩)';
    else if (total >= 85) rank = '優等 (選役別優勢大)';
    else if (total >= 75) rank = '良好';
    else if (total >= 60) rank = '及格';

    badge.textContent = `${total.toFixed(2)} 分 (${rank})`;
  }
}

function initCalculator() {
  calculateTotalScore();
}

function renderShootingGuide() {
  const data = AppState.studyData.shooting;
  const container = document.getElementById('shooting-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-6">
      <div class="p-6 bg-gradient-to-r from-emerald-900 to-slate-900 text-white rounded-2xl space-y-2 shadow">
        <h3 class="text-xl font-bold flex items-center gap-2 text-emerald-400">
          <i data-lucide="crosshair" class="w-6 h-6"></i> ${data.title}
        </h3>
        <p class="text-sm text-slate-300">${data.description}</p>
      </div>

      <!-- T65K2 Rifle Specs -->
      ${data.t65k2_specs ? `
        <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm border-l-4 border-teal-500">
          <h4 class="text-base font-bold text-teal-600 dark:text-teal-400 flex items-center gap-2">
            <i data-lucide="target" class="w-5 h-5"></i> ${data.t65k2_specs.title}
          </h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            ${data.t65k2_specs.facts.map(f => `
              <div class="p-3 rounded-xl bg-teal-50/40 dark:bg-teal-950/20 border border-teal-100 dark:border-teal-900/60 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                ${f.replace(/\*\*(.*?)\*\*/g, '<strong class="text-teal-700 dark:text-teal-300 font-bold block mb-0.5">$1</strong>')}
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Safety Rules -->
      <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm border-l-4 border-rose-500">
        <h4 class="text-base font-bold text-rose-600 dark:text-rose-400 flex items-center gap-2">
          <i data-lucide="shield-alert" class="w-5 h-5"></i> 靶場最高三大安全鐵則（違者嚴辦）
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          ${data.rules.map(r => `
            <div class="p-3.5 rounded-xl bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900 text-xs sm:text-sm text-rose-900 dark:text-rose-200">
              ${r.replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold block mb-1">$1</strong>')}
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Eight Steps Mnemonic -->
      <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
        <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-emerald-500 pl-3">
          射擊八大要領口訣：「托、抵、握、貼、瞄、停、扣、報」
        </h4>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          ${data.eight_steps.map((s, idx) => `
            <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2">
              <div class="flex items-center gap-2">
                <span class="w-8 h-8 rounded-full bg-emerald-600 text-white font-extrabold text-sm flex items-center justify-center shadow">
                  ${s.step}
                </span>
                <span class="text-xs font-bold text-slate-800 dark:text-slate-200">${s.action}</span>
              </div>
              <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">${s.desc}</p>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Malfunction Clearance -->
      <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
        <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-amber-500 pl-3">
          步槍故障排除五大步驟：「拍、拉、看、瞄、射」
        </h4>
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-3">
          ${data.malfunction.map(m => `
            <div class="p-3.5 rounded-xl border border-amber-200 dark:border-amber-900/60 bg-amber-50/30 dark:bg-amber-950/20 text-center space-y-1">
              <span class="w-7 h-7 rounded-full bg-amber-500 text-white font-bold text-xs inline-flex items-center justify-center mx-auto mb-1">
                ${m.step}
              </span>
              <p class="text-xs text-slate-700 dark:text-slate-300 font-medium">${m.desc}</p>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- Commands Sequence -->
      <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
        <h4 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-indigo-500 pl-3">
          靶場標準實彈射擊口令與動作流程
        </h4>
        <div class="space-y-2.5">
          ${data.commands.map((cmd, idx) => `
            <div class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 flex items-start gap-3 text-xs sm:text-sm">
              <span class="px-2 py-0.5 bg-indigo-600 text-white rounded font-bold shrink-0 text-xs">
                步驟 ${idx + 1}
              </span>
              <div>
                <strong class="font-bold text-slate-900 dark:text-white">${cmd.cmd}</strong>：
                <span class="text-slate-600 dark:text-slate-400">${cmd.desc}</span>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

/* ==========================================================================
   PACKING CHECKLIST
   ========================================================================== */

function initChecklist() {
  updateChecklistProgress();
}

function renderChecklist() {
  const data = AppState.studyData.packing_list;
  const container = document.getElementById('checklist-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Header with Action Buttons -->
      <div class="p-6 bg-gradient-to-r from-emerald-800 via-teal-900 to-slate-900 text-white rounded-2xl space-y-3 shadow">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="space-y-1">
            <h3 class="text-xl font-bold flex items-center gap-2 text-emerald-300">
              <i data-lucide="clipboard-check" class="w-6 h-6"></i> ${data.title}
            </h3>
            <p class="text-sm text-slate-300">${data.description}</p>
          </div>
          <div class="flex items-center gap-2 no-print">
            <button onclick="checkAllChecklist(true)" class="px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white rounded-lg text-xs font-semibold transition">
              全部勾選
            </button>
            <button onclick="checkAllChecklist(false)" class="px-3 py-1.5 bg-white/20 hover:bg-white/30 text-white rounded-lg text-xs font-semibold transition">
              全部清除
            </button>
            <button onclick="window.print()" class="px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-lg text-xs font-semibold transition flex items-center gap-1">
              <i data-lucide="printer" class="w-3.5 h-3.5"></i> 列印清單
            </button>
          </div>
        </div>

        <!-- Global Progress Bar -->
        <div class="space-y-1.5 pt-2">
          <div class="flex justify-between text-xs font-medium text-emerald-200">
            <span>備妥進度</span>
            <span id="checklist-progress-text">0 / 0 (0%)</span>
          </div>
          <div class="w-full bg-white/20 h-2.5 rounded-full overflow-hidden">
            <div id="checklist-progress-bar" class="bg-emerald-400 h-full transition-all duration-300" style="width: 0%"></div>
          </div>
        </div>
      </div>

      <!-- Categories Accordion / Cards -->
      <div class="space-y-5">
        ${data.categories.map(cat => `
          <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-4 shadow-sm">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center justify-between">
              <span>${cat.name}</span>
              ${cat.id === 'contraband' ? '<span class="px-2 py-0.5 rounded bg-rose-500 text-white text-xs font-bold">嚴禁入營</span>' : ''}
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              ${cat.items.map(item => {
                const isChecked = AppState.checkedItems.has(item.id);
                return `
                  <label class="p-3 rounded-xl border ${isChecked ? 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/20' : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30'} flex items-start gap-3 cursor-pointer hover:border-emerald-300 transition select-none ${item.is_danger ? 'hover:border-rose-300' : ''}">
                    <input type="checkbox" onchange="toggleChecklistItem('${item.id}')" ${isChecked ? 'checked' : ''} class="rounded text-emerald-600 focus:ring-emerald-500 w-4 h-4 mt-0.5 shrink-0">
                    <div class="space-y-0.5 flex-1">
                      <div class="text-xs sm:text-sm font-semibold ${isChecked ? 'line-through text-slate-400 dark:text-slate-500' : 'text-slate-900 dark:text-slate-100'} ${item.is_danger ? 'text-rose-600 dark:text-rose-400' : ''}">
                        ${item.name}
                        ${item.must ? '<span class="ml-1 text-[10px] px-1.5 py-0.2 bg-rose-500 text-white rounded font-bold">必備</span>' : ''}
                      </div>
                      <p class="text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 leading-snug">${item.tip}</p>
                    </div>
                  </label>
                `;
              }).join('')}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  updateChecklistProgress();
  if (window.lucide) window.lucide.createIcons();
}

function toggleChecklistItem(id) {
  if (AppState.checkedItems.has(id)) {
    AppState.checkedItems.delete(id);
  } else {
    AppState.checkedItems.add(id);
  }
  localStorage.setItem('sms_checklist', JSON.stringify(Array.from(AppState.checkedItems)));
  updateChecklistProgress();
  renderChecklist();
}

function checkAllChecklist(check) {
  const data = AppState.studyData.packing_list;
  if (!data) return;

  if (check) {
    data.categories.forEach(cat => {
      cat.items.forEach(item => AppState.checkedItems.add(item.id));
    });
  } else {
    AppState.checkedItems.clear();
  }
  localStorage.setItem('sms_checklist', JSON.stringify(Array.from(AppState.checkedItems)));
  updateChecklistProgress();
  renderChecklist();
}

function updateChecklistProgress() {
  const data = AppState.studyData.packing_list;
  if (!data) return;

  let totalItems = 0;
  data.categories.forEach(cat => {
    // Exclude contraband from preparation items
    if (cat.id !== 'contraband') {
      totalItems += cat.items.length;
    }
  });

  let checkedCount = 0;
  data.categories.forEach(cat => {
    if (cat.id !== 'contraband') {
      cat.items.forEach(item => {
        if (AppState.checkedItems.has(item.id)) checkedCount++;
      });
    }
  });

  const percent = totalItems > 0 ? Math.round((checkedCount / totalItems) * 100) : 0;
  const textEl = document.getElementById('checklist-progress-text');
  const barEl = document.getElementById('checklist-progress-bar');
  if (textEl) textEl.textContent = `${checkedCount} / ${totalItems} 項已備妥 (${percent}%)`;
  if (barEl) barEl.style.width = `${percent}%`;
}

/* ==========================================================================
   UTILITY FUNCTIONS
   ========================================================================== */

function pickRandom(arr, count) {
  const shuffled = [...arr];
  shuffleArray(shuffled);
  return shuffled.slice(0, Math.min(count, shuffled.length));
}

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}
