/**
 * 成功嶺替代役新訓考古題與備考系統主邏輯
 * 模組化四大分頁架構：首頁導覽 / 新訓特區 / EMT-1特區 / 用品檢核表
 * 具備隨機抽題模擬考、全題庫即時速查、背題遮罩、成績計算機與必備用品檢核表
 */

// Global App State
const AppState = {
  activeTab: 'home', // 'home', 'recruit', 'emt', 'checklist'
  isDark: false,
  questions: [],
  studyData: {},
  stats: {},
  mistakes: new Set(),
  bookmarks: new Set(),
  // Recruit Training Module State (新訓特區子分頁)
  recruit: {
    activeSubTab: 'quiz' // 'quiz', 'bank', 'regulations', 'volunteer', 'rights', 'shooting'
  },
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
  checkedItems: new Set(),
  // EMT-1 Module State (完全獨立於替代役法規題庫，零重疊)
  emt: {
    activeSubTab: 'quiz', // 'quiz', 'bank', 'study', 'resources'
    questions: [],
    studyData: null,
    mistakes: new Set(),
    bookmarks: new Set(),
    quiz: {
      active: false,
      mode: 'practice20', // 'mock50', 'practice20', 'category', 'mistakes'
      selectedCategory: 'all',
      questions: [],
      currentIndex: 0,
      answers: {},
      flags: new Set(),
      instantFeedback: true,
      timer: null,
      timeRemaining: 3000,
      totalTime: 3000,
      startTime: null,
      isSubmitted: false,
      shuffleQuestions: true,
      shuffleOptions: true
    },
    bank: {
      searchTerm: '',
      categoryFilter: 'all',
      hideAnswers: false,
      currentPage: 1,
      pageSize: 15
    }
  }
};

// Initialize Application
document.addEventListener('DOMContentLoaded', async () => {
  loadStoredPreferences();
  await loadData();
  setupEventListeners();
  updateChecklistProgress();
  initCalculator();
  updateHeaderBadges();

  // Initial Route Check
  const hash = window.location.hash.replace('#', '');
  if (hash) {
    handleRoute(hash);
  } else {
    switchTab('home', false);
  }
  
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

  // EMT-1 Mistakes
  try {
    const savedEmtMistakes = JSON.parse(localStorage.getItem('sms_emt_mistakes') || '[]');
    AppState.emt.mistakes = new Set(savedEmtMistakes);
  } catch (e) {
    AppState.emt.mistakes = new Set();
  }

  // EMT-1 Bookmarks
  try {
    const savedEmtBookmarks = JSON.parse(localStorage.getItem('sms_emt_bookmarks') || '[]');
    AppState.emt.bookmarks = new Set(savedEmtBookmarks);
  } catch (e) {
    AppState.emt.bookmarks = new Set();
  }
}

// Load Questions & Study Data
async function loadData() {
  try {
    if (window.APP_QUESTIONS && window.APP_STUDY_DATA) {
      AppState.questions = window.APP_QUESTIONS.questions;
      AppState.stats = window.APP_QUESTIONS.stats;
      AppState.studyData = window.APP_STUDY_DATA;
    } else {
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
    }

    // Load EMT-1 Module Data (完全獨立於替代役新訓題庫)
    if (window.APP_EMT_QUESTIONS && window.APP_EMT_STUDY_DATA) {
      AppState.emt.questions = window.APP_EMT_QUESTIONS.questions;
      AppState.emt.studyData = window.APP_EMT_STUDY_DATA;
    } else {
      try {
        const [eqRes, esRes] = await Promise.all([
          fetch('./data/emt_questions.json'),
          fetch('./data/emt_study_data.json')
        ]);
        const eqData = await eqRes.json();
        const esData = await esRes.json();
        AppState.emt.questions = eqData.questions;
        AppState.emt.studyData = esData;
      } catch (err) {
        console.warn('Fallback loading EMT data failed:', err);
      }
    }
  } catch (err) {
    console.error('Error loading data:', err);
  }
}

// Update Badges in Header
function updateHeaderBadges() {
  const totalCountEl = document.getElementById('stat-total-questions');
  const mistakeCountEl = document.getElementById('stat-mistake-count');
  const total = (AppState.questions.length || 272) + (AppState.emt.questions.length || 96);
  const totalMistakes = AppState.mistakes.size + AppState.emt.mistakes.size;
  if (totalCountEl) totalCountEl.textContent = total;
  if (mistakeCountEl) mistakeCountEl.textContent = totalMistakes;
  const recruitMistakesEl = document.getElementById('recruit-stat-mistakes');
  if (recruitMistakesEl) recruitMistakesEl.innerHTML = `${AppState.mistakes.size} <span class="text-xs font-normal">題</span>`;
}

// Header Mistakes Button Click Handler
function handleHeaderMistakesClick() {
  if (AppState.activeTab === 'emt') {
    if (AppState.emt.mistakes.size === 0) {
      alert('目前尚無 EMT-1 錯題記錄！進行測驗答錯後將自動累積至錯題本。');
      return;
    }
    switchEmtSubTab('quiz');
    startEmtQuiz('mistakes');
  } else {
    switchTab('recruit');
    switchRecruitSubTab('quiz');
    if (AppState.mistakes.size === 0) {
      alert('目前尚無新訓錯題記錄！進行模擬測驗答錯後將自動累積至錯題本。');
      return;
    }
    startQuiz('mistakes');
  }
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
    handleRoute(hash);
  });
}

// Handle Route from URL Hash
function handleRoute(hash) {
  if (hash === 'home') {
    switchTab('home', false);
  } else if (hash === 'recruit') {
    switchTab('recruit', false);
  } else if (['quiz', 'bank', 'regulations', 'volunteer', 'rights', 'shooting'].includes(hash)) {
    switchTab('recruit', false);
    switchRecruitSubTab(hash, false);
  } else if (hash === 'emt') {
    switchTab('emt', false);
  } else if (['emt-quiz', 'emt-bank', 'emt-study', 'emt-resources'].includes(hash)) {
    switchTab('emt', false);
    switchEmtSubTab(hash.replace('emt-', ''), false);
  } else if (hash === 'checklist') {
    switchTab('checklist', false);
  } else {
    switchTab('home', false);
  }
}

// Switch Primary Tab
function switchTab(tab, updateHash = true) {
  AppState.activeTab = tab;
  if (updateHash) {
    if (tab === 'recruit') {
      window.location.hash = AppState.recruit.activeSubTab || 'quiz';
    } else {
      window.location.hash = tab;
    }
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
    case 'home':
      renderHomeSection();
      break;
    case 'recruit':
      renderRecruitSection();
      break;
    case 'emt':
      renderEmtSection();
      break;
    case 'checklist':
      renderChecklist();
      break;
  }
}

/* ==========================================================================
   TAB 1: HOME PAGE & PROJECT GUIDE (首頁導覽與專案緣起)
   ========================================================================== */

function renderHomeSection() {
  const container = document.getElementById('home-content-body');
  if (!container) return;

  const totalQuestions = (AppState.questions.length || 272) + (AppState.emt.questions.length || 96);
  const recruitCount = AppState.questions.length || 272;
  const emtCount = AppState.emt.questions.length || 96;

  container.innerHTML = `
    <!-- 1. Hero Welcome Banner -->
    <div class="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-950 p-6 sm:p-10 text-white shadow-xl border border-emerald-500/20">
      <div class="absolute -right-12 -bottom-12 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div class="relative z-10 space-y-6">
        <div class="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/20 border border-emerald-400/30 text-emerald-300 text-xs font-bold tracking-wide">
          <i data-lucide="shield-check" class="w-4 h-4"></i> 🇹🇼 成功嶺替代役新訓 · 備考與全方位通關導航系統
        </div>

        <div class="space-y-3">
          <h1 class="text-2xl sm:text-4xl font-black tracking-tight text-white leading-tight">
            成功嶺替代役新訓 <br class="sm:hidden">考古題題庫與備考指南
          </h1>
          <p class="text-sm sm:text-base text-emerald-100/90 max-w-3xl leading-relaxed">
            掌握學科鑑測 35%~45% 關鍵佔比 · 取得 EMT-1 國家初級救護技術員證照 · 避開過時法規陷阱 · 實戰裝備無痛打包。一站式整合線上隨機模擬考、全題庫速查翻牌背題、十大學習資源直連與標楷體 PDF 離線下載。
          </p>
        </div>

        <!-- 4 Key Value Pills -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-1">
          <div class="p-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-[11px] text-emerald-200">全站題庫總數</div>
            <div class="text-base sm:text-xl font-black text-white">${totalQuestions} <span class="text-xs font-normal">題</span></div>
          </div>
          <div class="p-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-[11px] text-teal-200">最新法規版本</div>
            <div class="text-base sm:text-xl font-black text-emerald-300">112-115年 <span class="text-xs font-normal">修法</span></div>
          </div>
          <div class="p-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-[11px] text-amber-200">雙核心模擬考</div>
            <div class="text-base sm:text-xl font-black text-amber-300">60 / 70分 <span class="text-xs font-normal">及格</span></div>
          </div>
          <div class="p-3 rounded-2xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-[11px] text-cyan-200">精美排版試卷</div>
            <div class="text-base sm:text-xl font-black text-cyan-300">標楷體 <span class="text-xs font-normal">PDF</span></div>
          </div>
        </div>

        <!-- Fast Navigation Call to Action Buttons -->
        <div class="flex items-center gap-3 flex-wrap pt-2">
          <button onclick="switchTab('recruit')" class="px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs sm:text-sm shadow-lg hover:shadow-emerald-500/30 transition flex items-center gap-2 group">
            <i data-lucide="award" class="w-4 h-4 group-hover:scale-110 transition"></i>
            <span>進入新訓題庫特區 (${recruitCount}題)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <button onclick="switchTab('emt')" class="px-5 py-3 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-bold text-xs sm:text-sm shadow-lg hover:shadow-teal-500/30 transition flex items-center gap-2 group">
            <i data-lucide="heart-pulse" class="w-4 h-4 group-hover:scale-110 transition"></i>
            <span>進入 EMT-1 救護特區 (${emtCount}題)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
          <button onclick="switchTab('checklist')" class="px-4 py-3 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs sm:text-sm border border-white/20 transition flex items-center gap-2">
            <i data-lucide="clipboard-check" class="w-4 h-4 text-emerald-400"></i>
            <span>新訓用品檢核表</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 2. 專案緣起與建站初衷 (Why We Built This Website) -->
    <div class="space-y-4">
      <div class="flex items-center justify-between flex-wrap gap-2 border-l-4 border-emerald-500 pl-3">
        <div>
          <h2 class="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
            專案緣起與初衷：為何需要這個備考系統？
          </h2>
          <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
            成功嶺不是只有出操與體能，學科筆試更是決定你役期下單位分發與證照取得的核心關鍵。
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Reason 1: 役別甄選分發 -->
        <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm border border-emerald-500/20 flex flex-col justify-between">
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm">
              <span class="w-7 h-7 rounded-lg bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-sm font-black">1</span>
              <span>役別甄選與分發的關鍵命脈 (佔總成績 35%~45%)</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">每錯 1 題，分發名次可能落後數十名</h3>
            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              成功嶺新訓成績通常由<strong>學科筆試 (35%~45%)</strong>、基本教練、生活評分與體能組成。其中，學科筆試是最能透過「事前充分準備」拉開差距的唯一項目！1 分之差往往決定你能否如願留在中央機關、戶籍地附近，或是分發至偏遠外島繁重單位。
            </p>
          </div>
          <div class="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-emerald-700 dark:text-emerald-400 font-semibold flex items-center gap-1">
            <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
            <span>目標：穩拿 95 分以上，取得優先選填志願權！</span>
          </div>
        </div>

        <!-- Reason 2: EMT-1 國家證照 -->
        <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm border border-teal-500/20 flex flex-col justify-between">
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-teal-600 dark:text-teal-400 font-bold text-sm">
              <span class="w-7 h-7 rounded-lg bg-teal-100 dark:bg-teal-950 flex items-center justify-center text-sm font-black">2</span>
              <span>全民必考 EMT-1 國家初級救護技術員證照</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">40 小時紮實急救訓練，70 分及格門檻</h3>
            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              因應社會韌性與全民防衛政策，替代役役男在新訓全員修習 40 小時 EMT-1 初級救護技術員課程，且<strong>筆試成績必須達到 70 分合格</strong>才能獲頒正式合格證書。這不僅是新訓的評鑑標準，更是結訓退役後可終身受用的國家法定自救與救人專業專長。
            </p>
          </div>
          <div class="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-teal-700 dark:text-teal-400 font-semibold flex items-center gap-1">
            <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
            <span>目標：一次考過 70 分及格線，順利考取國家證照！</span>
          </div>
        </div>

        <!-- Reason 3: 破除舊題庫法規過時 -->
        <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm border border-amber-500/20 flex flex-col justify-between">
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-amber-600 dark:text-amber-400 font-bold text-sm">
              <span class="w-7 h-7 rounded-lg bg-amber-100 dark:bg-amber-950 flex items-center justify-center text-sm font-black">3</span>
              <span>破除舊版考古題法規過時、答案錯誤之痛點</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">全面對齊 112~115 年內政部最新法規公布</h3>
            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              坊間役男傳承的 Google 文件或網路講義，常殘留 10 年前的過時法條（如已廢止之舊制替代役類別、舊版請假規則、過期罰則以及爭議錯答）。本專案逐條<strong>比對全國法規資料庫官方最新公布條文</strong>，題題附帶最新法規依據與可點擊超連結，徹底避免「背了舊答案卻在考場被扣分」。
            </p>
          </div>
          <div class="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-amber-700 dark:text-amber-400 font-semibold flex items-center gap-1">
            <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
            <span>優勢：題題皆有最新官方條文超連結，正確率 100%！</span>
          </div>
        </div>

        <!-- Reason 4: 一站式現代數位工具 -->
        <div class="glass-panel p-6 rounded-2xl space-y-3 shadow-sm border border-indigo-500/20 flex flex-col justify-between">
          <div class="space-y-2">
            <div class="flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-bold text-sm">
              <span class="w-7 h-7 rounded-lg bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-sm font-black">4</span>
              <span>全方位現代數位備考體驗，拒絕死記硬背</span>
            </div>
            <h3 class="text-base font-bold text-slate-900 dark:text-white">隨機模擬考 + 選項打亂 + 遮蔽翻牌 + 標楷體 PDF</h3>
            <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 leading-relaxed">
              告別枯燥的 PDF 純文字背題！本系統提供：<strong>全真限時模擬考（計時+及格判定）</strong>、<strong>(A)(B)(C)(D)選項隨機打亂（防止位置記憶死背）</strong>、<strong>遮蔽答案翻牌自測模式</strong>、<strong>錯題本自動累積重測</strong>，以及<strong>可直接列印帶入成功嶺內閱讀的雙欄標楷體 PDF</strong>。
            </p>
          </div>
          <div class="pt-3 border-t border-slate-100 dark:border-slate-800 text-xs text-indigo-700 dark:text-indigo-400 font-semibold flex items-center gap-1">
            <i data-lucide="check-circle" class="w-3.5 h-3.5"></i>
            <span>便利：手機隨開隨測，離線亦可無縫複習！</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 網站核心四大功能模組導覽 (Feature Guide Cards) -->
    <div class="space-y-4">
      <div class="border-l-4 border-emerald-500 pl-3">
        <h2 class="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
          網站核心四大功能模組導覽
        </h2>
        <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
          全站依功能劃分為四大頂層模組，滿足從考前背題、模擬測驗到入營行李整備的所有需求。
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Module Card 1: 成功嶺新訓特區 -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-emerald-500 transition shadow-sm group border border-emerald-500/20">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="award" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold rounded-full">新訓必通</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">🎖️ 成功嶺新訓特區</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              收錄是非題 131 題 + 選擇題 141 題（共 272 題真題）。涵蓋替代役實施條例、志願服務法、役男權益與打靶射擊全攻略，支援 50 題限時模擬考（60分及格）。
            </p>
          </div>
          <button onclick="switchTab('recruit')" class="mt-5 w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm">
            <span>前往新訓特區</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Module Card 2: EMT-1 專區 -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-teal-500 transition shadow-sm group border border-teal-500/20">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-teal-100 dark:bg-teal-950 text-teal-600 dark:text-teal-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="heart-pulse" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-teal-500/10 text-teal-600 dark:text-teal-400 font-bold rounded-full">國家證照</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">🚑 EMT-1 救護特區</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              收錄 96 題單選選擇題，完全對齊消防署 40 小時教材與 7 大核心單元。支援 50 題全真模擬考（70分及格）、選項隨機打亂、生命徵象與鋼瓶計算公式。
            </p>
          </div>
          <button onclick="switchTab('emt')" class="mt-5 w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm">
            <span>前往 EMT-1 專區</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Module Card 3: 用品檢核表 -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-amber-500 transition shadow-sm group border border-amber-500/20">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="clipboard-check" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold rounded-full">行李打包</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">🎒 新訓用品檢核表</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              彙整官方規定、成功嶺役男群組記事本與 Dcard 262186096 評級（重度/中度/輕度建議品）。支援即時勾選進度儲存、違禁品提醒與避坑指南。
            </p>
          </div>
          <button onclick="switchTab('checklist')" class="mt-5 w-full py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm">
            <span>查看行李檢核表</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Module Card 4: 離線必備 PDF 專區 -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500 transition shadow-sm group border border-cyan-500/20">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-cyan-100 dark:bg-cyan-950 text-cyan-600 dark:text-cyan-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="file-down" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-bold rounded-full">離線紙本</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">📄 離線必備 PDF 專區</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              標準公文排版，答案粗體高亮、法條解析與出處完備。含新訓題庫 (24頁)、EMT-1 題庫 (19頁) 與新訓用品檢核表 (6頁)，可直接下載帶入成功嶺自修。
            </p>
          </div>
          <div class="mt-5 grid grid-cols-3 gap-1.5">
            <a href="pdf/替代役新訓題庫_全集彙編_標楷體版.pdf" download class="py-2 px-1 bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold rounded-xl transition text-center shadow-sm" title="下載新訓題庫 PDF">
              新訓題庫
            </a>
            <a href="pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf" download class="py-2 px-1 bg-teal-600 hover:bg-teal-700 text-white text-[11px] font-bold rounded-xl transition text-center shadow-sm" title="下載 EMT-1 題庫 PDF">
              EMT-1
            </a>
            <a href="pdf/成功嶺替代役新訓_必備用品建議檢核表_標楷體版.pdf" download class="py-2 px-1 bg-indigo-600 hover:bg-indigo-700 text-white text-[11px] font-bold rounded-xl transition text-center shadow-sm" title="下載新訓用品建議檢核表 PDF">
              用品檢核
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. 四階段滿分備考路線圖 (Recommended Study Roadmap) -->
    <div class="space-y-4">
      <div class="border-l-4 border-emerald-500 pl-3">
        <h2 class="text-xl sm:text-2xl font-black text-slate-900 dark:text-white">
          四階段滿分備考路線圖 (推薦學習路徑)
        </h2>
        <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400">
          按照學長姐實證經驗推薦的四步複習法，從法律條理到考場反射，穩健邁向第一志願！
        </p>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Step 1 -->
        <div class="glass-panel p-5 rounded-2xl space-y-2 border-t-4 border-t-emerald-500 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-600 dark:text-emerald-400">第一階段</span>
            <span class="w-6 h-6 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 flex items-center justify-center text-xs font-bold">1</span>
          </div>
          <h4 class="font-bold text-sm text-slate-900 dark:text-white">精讀核心法規條例</h4>
          <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            通讀《替代役實施條例》、《志願服務法》與衛福部《救護技術員管理辦法》，理解法條立法理由、罰則與時限數字。
          </p>
        </div>

        <!-- Step 2 -->
        <div class="glass-panel p-5 rounded-2xl space-y-2 border-t-4 border-t-teal-500 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-teal-600 dark:text-teal-400">第二階段</span>
            <span class="w-6 h-6 rounded-full bg-teal-100 dark:bg-teal-950 text-teal-700 dark:text-teal-300 flex items-center justify-center text-xs font-bold">2</span>
          </div>
          <h4 class="font-bold text-sm text-slate-900 dark:text-white">題庫速查遮蔽翻牌</h4>
          <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            進入題庫速查，勾選「遮蔽答案（背題模式）」，逐題自我檢驗，答錯或模糊題立即點星號加入收藏。
          </p>
        </div>

        <!-- Step 3 -->
        <div class="glass-panel p-5 rounded-2xl space-y-2 border-t-4 border-t-amber-500 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-amber-600 dark:text-amber-400">第三階段</span>
            <span class="w-6 h-6 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 flex items-center justify-center text-xs font-bold">3</span>
          </div>
          <h4 class="font-bold text-sm text-slate-900 dark:text-white">全真模考與錯題攻堅</h4>
          <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            進行 50 題限時模擬考，體驗打亂選項之真實考感；反覆刷「錯題本」直到所有錯題完全清空。
          </p>
        </div>

        <!-- Step 4 -->
        <div class="glass-panel p-5 rounded-2xl space-y-2 border-t-4 border-t-cyan-500 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-cyan-600 dark:text-cyan-400">第四階段</span>
            <span class="w-6 h-6 rounded-full bg-cyan-100 dark:bg-cyan-950 text-cyan-700 dark:text-cyan-300 flex items-center justify-center text-xs font-bold">4</span>
          </div>
          <h4 class="font-bold text-sm text-slate-900 dark:text-white">裝備檢核與紙本入營</h4>
          <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
            按用品檢核表將必備證件、藥品、文具打包齊全；下載兩份標楷體 PDF 印出成冊，入營自修無懈可擊！
          </p>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

/* ==========================================================================
   TAB 2: RECRUIT TRAINING MODULE (成功嶺新訓特區 - 統一子分頁架構)
   ========================================================================== */

function renderRecruitSection() {
  const mistakesEl = document.getElementById('recruit-stat-mistakes');
  if (mistakesEl) {
    mistakesEl.innerHTML = `${AppState.mistakes.size} <span class="text-xs font-normal">題</span>`;
  }
  switchRecruitSubTab(AppState.recruit.activeSubTab, false);
}

function switchRecruitSubTab(subTab, updateHash = true) {
  AppState.recruit.activeSubTab = subTab;
  if (updateHash) {
    window.location.hash = subTab;
  }

  // Update sub-navigation buttons
  document.querySelectorAll('.recruit-subtab-btn').forEach(btn => {
    if (btn.dataset.subtab === subTab) {
      btn.className = 'recruit-subtab-btn px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap bg-emerald-600 text-white shadow-md font-semibold text-xs sm:text-sm';
    } else {
      btn.className = 'recruit-subtab-btn px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold text-xs sm:text-sm';
    }
  });

  // Hide all sub-views, show target
  document.querySelectorAll('.recruit-sub-view').forEach(view => {
    view.classList.add('hidden');
  });

  const targetView = document.getElementById(`recruit-sub-${subTab}`);
  if (targetView) {
    targetView.classList.remove('hidden');
  }

  // Render content into current sub-tab
  renderRecruitCurrentSubTab();

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function renderRecruitCurrentSubTab() {
  switch (AppState.recruit.activeSubTab) {
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
      ${q.source ? `
        <div class="text-[11px] pt-1 border-t border-black/10 dark:border-white/10 flex items-center gap-1.5 opacity-85">
          <i data-lucide="link" class="w-3 h-3 text-emerald-500"></i>
          <span>出處來源：</span>
          ${q.source_url ? `<a href="${q.source_url}" target="_blank" rel="noopener noreferrer" class="underline font-semibold hover:text-emerald-600 dark:hover:text-emerald-300 inline-flex items-center gap-1">${q.source} <i data-lucide="external-link" class="w-2.5 h-2.5"></i></a>` : `<span>${q.source}</span>`}
        </div>
      ` : ''}
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
                  ${q.source ? `
                    <div class="text-[11px] text-slate-400 pt-0.5 flex items-center gap-1">
                      <i data-lucide="link" class="w-3 h-3 text-emerald-500"></i>
                      <span>來源：</span>
                      ${q.source_url ? `<a href="${q.source_url}" target="_blank" rel="noopener noreferrer" class="text-emerald-600 dark:text-emerald-400 underline">${q.source}</a>` : q.source}
                    </div>
                  ` : ''}
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
            ${q.source ? `
              <div class="text-[11px] text-slate-400 dark:text-slate-500 mt-1.5 pt-1.5 border-t border-slate-100 dark:border-slate-800/80 flex items-center gap-1.5">
                <i data-lucide="link" class="w-3.5 h-3.5 text-emerald-500 shrink-0"></i>
                <span class="shrink-0 font-medium">出處來源：</span>
                ${q.source_url ? `<a href="${q.source_url}" target="_blank" rel="noopener noreferrer" class="text-emerald-600 dark:text-emerald-400 hover:underline inline-flex items-center gap-1">${q.source} <i data-lucide="external-link" class="w-3 h-3"></i></a>` : `<span>${q.source}</span>`}
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
   STUDY GUIDES: REGULATIONS, VOLUNTEER, RIGHTS, SHOOTING, CHECKLIST
   ========================================================================== */

function renderRegulations() {
  const data = AppState.studyData.regulations;
  const container = document.getElementById('regulations-content-body');
  if (!container || !data) return;

  const lawMetaItems = data.law_meta ? [
    { title: '《替代役實施條例》', badge: '110.01.27修正公布', text: data.law_meta.latest_amend || '保險與撫卹請求權消滅時效延長為10年；增訂國保保費由役政機關編列預算' },
    { title: '《役男申請服替代役辦法》', badge: '113.12.25最新修正', text: data.law_meta.apply_rules || '家庭因素第11條：家屬年齡由60歲提高至65歲以上；因病生活不能自理需專人照顧標準' },
    { title: '《替代役役男請假規則》', badge: '111.05.30最新修正', text: data.law_meta.leave_rules || '「陪產檢及陪產假」合計7日（15日內請畢）；婚假14日（3個月內請畢）；刪除事假8小時折算1日' },
    { title: '主管機關組織改制', badge: '112.09.20生效', text: data.law_meta.org_reform || '內政部役政署組織改造，主管機關改制為「內政部替代役訓練及管理中心」與「內政部役政司」' }
  ] : [];

  const keyPoints = data.key_points_full ? data.key_points_full.items : [];
  const fullAct = data.full_act ? data.full_act : null;

  container.innerHTML = `
    <div class="space-y-8">
      <!-- Header Banner -->
      <div class="p-6 sm:p-8 bg-gradient-to-r from-slate-900 via-slate-800 to-emerald-950 text-white rounded-3xl space-y-3 shadow-lg">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-semibold">
          <i data-lucide="scale" class="w-4 h-4"></i> 法律條文與重點完全收錄
        </div>
        <h3 class="text-2xl sm:text-3xl font-black text-white">
          ${data.title}
        </h3>
        <p class="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">${data.description}</p>
      </div>

      <!-- Law Meta Cards -->
      ${lawMetaItems.length > 0 ? `
        <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm border border-emerald-500/30">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="sparkles" class="w-5 h-5 text-emerald-500"></i> 最新法規修正依據與主管機關異動速覽 (2024-2026標準)
            </h4>
            <span class="text-xs text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950 px-2.5 py-1 rounded-full font-bold border border-emerald-200 dark:border-emerald-800">
              全國法規資料庫最新校訂
            </span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            ${lawMetaItems.map(item => `
              <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-sm font-bold text-slate-900 dark:text-white">${item.title}</span>
                  <span class="text-[11px] px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-semibold shrink-0">${item.badge}</span>
                </div>
                <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">${item.text}</p>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Core Summary Sections -->
      <div class="space-y-6">
        <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
          <i data-lucide="bookmark-check" class="w-5 h-5 text-emerald-500"></i> 鑑測高頻核心法規表格速查
        </h4>

        ${data.sections.map(sec => `
          <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm">
            <h5 class="text-base font-bold text-slate-900 dark:text-white border-l-4 border-emerald-500 pl-3">
              ${sec.title}
            </h5>

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
                        <td class="py-2.5 px-3 text-slate-600 dark:text-slate-400">${row[2] || ''}</td>
                      </tr>
                    `).join('')}
                  </tbody>
                </table>
              </div>
            ` : ''}
          </div>
        `).join('')}
      </div>

      <!-- Google Doc Complete Key Points (52 items) -->
      ${keyPoints.length > 0 ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-emerald-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="list-ordered" class="w-5 h-5 text-emerald-500"></i> ${data.key_points_full.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">完整收錄 Google 雲端文件「重點整理」全部條列內容，一字不漏完全列出</p>
            </div>
            <span class="text-xs px-2.5 py-1 bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold rounded-full">共 ${keyPoints.length} 項</span>
          </div>

          <div class="space-y-2.5">
            ${keyPoints.map((item, idx) => {
              const isHeader = item.startsWith('*') || item.startsWith('☞') || item.startsWith('現行役期');
              if (isHeader) {
                return `
                  <div class="p-3 rounded-xl bg-emerald-50/60 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800/60 text-xs sm:text-sm font-bold text-emerald-900 dark:text-emerald-200">
                    ${item}
                  </div>
                `;
              }
              return `
                <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-800/40 flex items-start gap-3 hover:border-emerald-400 transition text-xs sm:text-sm leading-relaxed">
                  <span class="px-2 py-0.5 rounded bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-mono font-bold text-xs shrink-0 mt-0.5">
                    #${idx + 1}
                  </span>
                  <div class="text-slate-800 dark:text-slate-200 flex-1">
                    ${item.replace(/\b(\d+年|\d+歲|\d+日|\d+個月|\d+週|\d+小時|\d+萬|10年)\b/g, '<strong class="text-emerald-600 dark:text-emerald-400 font-extrabold">$1</strong>')}
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Full Act Articles (Articles 1 to 63) -->
      ${fullAct ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-slate-200 dark:border-slate-800">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="book-text" class="w-5 h-5 text-emerald-500"></i> ${fullAct.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">依據 ${fullAct.amend_date}，全案第 1 條至第 63 條無刪減完整條文</p>
            </div>
            <button onclick="toggleAllAct('reg-act')" class="px-3 py-1.5 text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-emerald-500 hover:text-white rounded-lg transition">
              全部展開 / 收合
            </button>
          </div>

          <div class="space-y-4" id="reg-act-container">
            ${fullAct.chapters.map((chap, cIdx) => `
              <details class="group rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 overflow-hidden" ${cIdx === 0 ? 'open' : ''}>
                <summary class="p-4 cursor-pointer font-bold text-sm sm:text-base text-slate-900 dark:text-white flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 select-none">
                  <span class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
                    ${chap.chapter}
                  </span>
                  <span class="text-xs text-slate-400 font-normal">(${chap.articles.length} 條)</span>
                </summary>
                <div class="p-4 space-y-3 bg-white/40 dark:bg-slate-900/30 divide-y divide-slate-100 dark:divide-slate-800/60 text-xs sm:text-sm">
                  ${chap.articles.map(art => `
                    <div class="pt-3 first:pt-0 space-y-1">
                      <div class="font-bold text-emerald-700 dark:text-emerald-400">${art.article}</div>
                      ${art.content.map(p => `<p class="text-slate-700 dark:text-slate-300 leading-relaxed">${p}</p>`).join('')}
                    </div>
                  `).join('')}
                </div>
              </details>
            `).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function renderVolunteer() {
  const data = AppState.studyData.volunteer;
  const container = document.getElementById('volunteer-content-body');
  if (!container || !data) return;

  const fullAct = data.full_act ? data.full_act : null;

  container.innerHTML = `
    <div class="space-y-8">
      <!-- Header Banner -->
      <div class="p-6 sm:p-8 bg-gradient-to-r from-teal-900 via-slate-900 to-teal-950 text-white rounded-3xl space-y-3 shadow-lg">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-teal-500/20 text-teal-300 rounded-full text-xs font-semibold">
          <i data-lucide="hand-heart" class="w-4 h-4"></i> 志願服務法規與訓練規範
        </div>
        <h3 class="text-2xl sm:text-3xl font-black text-white">
          ${data.title}
        </h3>
        <p class="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">${data.description}</p>
      </div>

      <!-- Core Summary Cards -->
      <div class="space-y-6">
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

      <!-- Full Act Articles (Articles 1 to 25) -->
      ${fullAct ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-teal-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="book-text" class="w-5 h-5 text-teal-500"></i> ${fullAct.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">依據 ${fullAct.amend_date}，全案第 1 條至第 25 條無刪減完整條文</p>
            </div>
            <button onclick="toggleAllAct('vol-act')" class="px-3 py-1.5 text-xs font-semibold bg-slate-100 dark:bg-slate-800 hover:bg-teal-500 hover:text-white rounded-lg transition">
              全部展開 / 收合
            </button>
          </div>

          <div class="space-y-4" id="vol-act-container">
            ${fullAct.chapters.map((chap, cIdx) => `
              <details class="group rounded-2xl border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 overflow-hidden" ${cIdx === 0 ? 'open' : ''}>
                <summary class="p-4 cursor-pointer font-bold text-sm sm:text-base text-slate-900 dark:text-white flex items-center justify-between hover:bg-slate-100 dark:hover:bg-slate-800 select-none">
                  <span class="flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-teal-500"></span>
                    ${chap.chapter}
                  </span>
                  <span class="text-xs text-slate-400 font-normal">(${chap.articles.length} 條)</span>
                </summary>
                <div class="p-4 space-y-3 bg-white/40 dark:bg-slate-900/30 divide-y divide-slate-100 dark:divide-slate-800/60 text-xs sm:text-sm">
                  ${chap.articles.map(art => `
                    <div class="pt-3 first:pt-0 space-y-1">
                      <div class="font-bold text-teal-700 dark:text-teal-400">${art.article}</div>
                      ${art.content.map(p => `<p class="text-slate-700 dark:text-slate-300 leading-relaxed">${p}</p>`).join('')}
                    </div>
                  `).join('')}
                </div>
              </details>
            `).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function renderRightsAndManagement() {
  const data = AppState.studyData.rights_and_management;
  const footnotes = AppState.studyData.footnotes ? AppState.studyData.footnotes.notes : [];
  const container = document.getElementById('rights-content-body');
  if (!container || !data) return;

  const rightsPoints = data.rights_points_full ? data.rights_points_full.items : [];
  const mgmtPoints = data.management_points_full ? data.management_points_full.items : [];

  container.innerHTML = `
    <div class="space-y-8">
      <!-- Header Banner -->
      <div class="p-6 sm:p-8 bg-gradient-to-r from-blue-900 via-indigo-900 to-slate-900 text-white rounded-3xl space-y-3 shadow-lg">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-semibold">
          <i data-lucide="shield" class="w-4 h-4"></i> 役男權益與服勤法規完全指南
        </div>
        <h3 class="text-2xl sm:text-3xl font-black text-white">
          ${data.title}
        </h3>
        <p class="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">${data.description}</p>
      </div>

      <!-- Salary Structure Card -->
      ${data.salary_structure ? `
        <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm border border-indigo-500/30">
          <div class="flex items-center justify-between">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="banknote" class="w-5 h-5 text-indigo-500"></i> ${data.salary_structure.title}
            </h4>
            <span class="text-xs text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950 px-2.5 py-1 rounded-full font-bold border border-indigo-200 dark:border-indigo-800">
              113年兵力結構調薪
            </span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1">
            ${data.salary_structure.data.map(item => `
              <div class="p-4 rounded-xl border border-indigo-100 dark:border-indigo-900/60 bg-indigo-50/40 dark:bg-indigo-950/20 space-y-1.5">
                <div class="text-xs font-bold text-slate-800 dark:text-slate-200">${item.tier}</div>
                <div class="text-base font-extrabold text-indigo-600 dark:text-indigo-400">${item.amount}</div>
                <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">${item.detail}</p>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

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

      <!-- Google Doc Rights Points (53 items) -->
      ${rightsPoints.length > 0 ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-blue-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="shield-check" class="w-5 h-5 text-blue-500"></i> ${data.rights_points_full.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">完整收錄 Google 雲端文件「權益部分」全 53 條條列內容，包含身分、薪資、撫卹、就醫補助</p>
            </div>
            <span class="text-xs px-2.5 py-1 bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 font-bold rounded-full">共 53 項</span>
          </div>

          <div class="space-y-2.5">
            ${rightsPoints.map((item, idx) => `
              <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-800/40 flex items-start gap-3 hover:border-blue-400 transition text-xs sm:text-sm leading-relaxed">
                <span class="px-2 py-0.5 rounded bg-blue-100 dark:bg-blue-950 text-blue-800 dark:text-blue-300 font-mono font-bold text-xs shrink-0 mt-0.5">
                  #${idx + 1}
                </span>
                <div class="text-slate-800 dark:text-slate-200 flex-1">
                  ${item.replace(/\b(\d+年|\d+歲|\d+日|\d+個月|\d+週|\d+小時|\d+元|\d+基數|10年)\b/g, '<strong class="text-blue-600 dark:text-blue-400 font-bold">$1</strong>')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Google Doc Management Points (40 items) -->
      ${mgmtPoints.length > 0 ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-indigo-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="clipboard-list" class="w-5 h-5 text-indigo-500"></i> ${data.management_points_full.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">完整收錄 Google 雲端文件「替代役訓練服勤管理部分」全 40 條條列內容，包含請假、獎懲、申訴、管理幹部</p>
            </div>
            <span class="text-xs px-2.5 py-1 bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 font-bold rounded-full">共 40 項</span>
          </div>

          <div class="space-y-2.5">
            ${mgmtPoints.map((item, idx) => `
              <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-800/40 flex items-start gap-3 hover:border-indigo-400 transition text-xs sm:text-sm leading-relaxed">
                <span class="px-2 py-0.5 rounded bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 font-mono font-bold text-xs shrink-0 mt-0.5">
                  #${idx + 1}
                </span>
                <div class="text-slate-800 dark:text-slate-200 flex-1">
                  ${item.replace(/\b(\d+年|\d+歲|\d+日|\d+個月|\d+週|\d+小時|\d+元|\d+基數|10年)\b/g, '<strong class="text-indigo-600 dark:text-indigo-400 font-bold">$1</strong>')}
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- Footnotes [1] to [25] Section -->
      ${footnotes.length > 0 ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-amber-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="help-circle" class="w-5 h-5 text-amber-500"></i> 歷年新訓學科考題註腳與法規陷阱精解 [1] 至 [25] 全覽
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">完整還原 Google 文件作者學長詳細註解，剖析出題陷阱與最新法條修訂原由</p>
            </div>
            <span class="text-xs px-2.5 py-1 bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-bold rounded-full">共 25 條註解</span>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            ${footnotes.map(fn => `
              <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-amber-50/30 dark:bg-amber-950/10 space-y-1.5 text-xs sm:text-sm">
                <div class="font-bold text-amber-700 dark:text-amber-400 flex items-center gap-1.5">
                  <span class="px-2 py-0.5 rounded bg-amber-500 text-white font-mono text-xs">
                    ${fn.num > 0 ? `[${fn.num}]` : '特別提醒'}
                  </span>
                </div>
                <p class="text-slate-700 dark:text-slate-300 leading-relaxed">${fn.text}</p>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function renderShootingGuide() {
  const data = AppState.studyData.shooting;
  const container = document.getElementById('shooting-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-8">
      <!-- Header Banner -->
      <div class="p-6 sm:p-8 bg-gradient-to-r from-emerald-950 via-slate-900 to-slate-950 text-white rounded-3xl space-y-3 shadow-lg">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 text-emerald-300 rounded-full text-xs font-semibold">
          <i data-lucide="crosshair" class="w-4 h-4"></i> T65K2步槍射擊與靶場紀律
        </div>
        <h3 class="text-2xl sm:text-3xl font-black text-white">
          ${data.title}
        </h3>
        <p class="text-sm sm:text-base text-slate-300 max-w-3xl leading-relaxed">${data.description}</p>
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

function calculateTotalScore() {
  const academic = parseFloat(document.getElementById('calc-academic')?.value || 0);
  const run = parseFloat(document.getElementById('calc-run')?.value || 0);
  const drill = parseFloat(document.getElementById('calc-drill')?.value || 0);
  const emt = parseFloat(document.getElementById('calc-emt')?.value || 0);
  const life = parseFloat(document.getElementById('calc-life')?.value || 0);

  const total = (academic * 0.35) + (run * 0.15) + (drill * 0.20) + (emt * 0.20) + (life * 0.10);
  const badge = document.getElementById('calc-result-badge');
  if (badge) {
    let rank = '甲等';
    if (total >= 90) rank = '特優';
    else if (total >= 80) rank = '優等';
    else if (total >= 70) rank = '甲等';
    else if (total >= 60) rank = '乙等';
    else rank = '待加強';
    badge.textContent = `${total.toFixed(2)} 分 (${rank})`;
  }
}

function initCalculator() {
  calculateTotalScore();
}

function renderChecklist() {
  const data = AppState.studyData.packing_list;
  const container = document.getElementById('checklist-content-body');
  if (!container || !data) return;

  container.innerHTML = `
    <div class="space-y-8">
      <!-- Header with Action Buttons -->
      <div class="p-6 sm:p-8 bg-gradient-to-r from-emerald-800 via-teal-900 to-slate-900 text-white rounded-3xl space-y-4 shadow-lg">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="inline-flex items-center gap-2 px-3 py-1 bg-white/20 text-emerald-300 rounded-full text-xs font-semibold">
              <i data-lucide="clipboard-check" class="w-4 h-4"></i> 2024年8月最新實測整理
            </div>
            <h3 class="text-2xl sm:text-3xl font-black text-white">
              ${data.title}
            </h3>
            <p class="text-sm text-slate-300 max-w-2xl">${data.description}</p>
          </div>
          <div class="flex items-center gap-2 no-print">
            <button onclick="checkAllChecklist(true)" class="px-3 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-xs font-semibold transition">
              全部勾選
            </button>
            <button onclick="checkAllChecklist(false)" class="px-3 py-2 bg-white/20 hover:bg-white/30 text-white rounded-xl text-xs font-semibold transition">
              全部清除
            </button>
            <a href="pdf/成功嶺替代役新訓_必備用品建議檢核表_標楷體版.pdf" download class="px-3.5 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1.5 shadow" title="下載新訓用品建議檢核表 PDF">
              <i data-lucide="file-down" class="w-3.5 h-3.5"></i> 下載用品清單 PDF
            </a>
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
      <div class="space-y-6">
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
                  <label class="p-3.5 rounded-xl border ${isChecked ? 'border-emerald-500 bg-emerald-50/40 dark:bg-emerald-950/20' : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30'} flex items-start gap-3 cursor-pointer hover:border-emerald-300 transition select-none ${item.is_danger ? 'hover:border-rose-300' : ''}">
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

function toggleAllAct(containerId) {
  const container = document.getElementById(`${containerId}-container`);
  if (!container) return;
  const details = container.querySelectorAll('details');
  if (!details.length) return;
  const anyOpen = Array.from(details).some(d => d.open);
  details.forEach(d => { d.open = !anyOpen; });
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


/* ==========================================================================
   EMT-1 (初級救護技術員) 獨立專區模組
   與既有替代役法規題庫 100% 分開，具備專屬測驗引擎、選項隨機分配、
   全真題庫速查、十大學習資源清單與急救核心法規講義
   ========================================================================== */

function renderEmtSection() {
  const container = document.getElementById('emt-content-body');
  if (!container) return;

  const totalQuestions = AppState.emt.questions.length || 96;
  const mistakeCount = AppState.emt.mistakes.size;
  const activeSubTab = AppState.emt.activeSubTab || 'quiz';

  container.innerHTML = `
    <!-- EMT Hero Banner -->
    <div class="p-6 sm:p-8 bg-gradient-to-r from-teal-900 via-emerald-900 to-slate-900 text-white rounded-3xl shadow-xl space-y-4 border border-teal-500/30 relative overflow-hidden">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
        <div class="space-y-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 bg-teal-500/20 text-teal-300 rounded-full text-xs font-bold border border-teal-500/30">
            <i data-lucide="shield-plus" class="w-4 h-4"></i> 成功嶺替代役 · 初級救護技術員 (EMT-1) 專區
          </div>
          <h2 class="text-2xl sm:text-3xl font-black tracking-tight text-white flex items-center gap-2">
            🚑 EMT-1 全真題庫與法規備考特區
          </h2>
          <p class="text-xs sm:text-sm text-teal-100/90 max-w-2xl leading-relaxed">
            依法定 40 小時訓練教材與歷屆鑑測真題編修，收錄 7 大章節、96 題單選選擇題，支援選項隨機分配、即時詳解、背題翻牌及標楷體 PDF 下載。
          </p>
        </div>

        <!-- Hero Stats & Action Badges -->
        <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
          <div class="px-3.5 py-2 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-xs text-teal-200">題庫總數</div>
            <div class="text-lg font-black text-white">${totalQuestions} <span class="text-xs font-normal">題</span></div>
          </div>
          <div class="px-3.5 py-2 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-xs text-teal-200">合格門檻</div>
            <div class="text-lg font-black text-emerald-300">70 <span class="text-xs font-normal">分</span></div>
          </div>
          <div class="px-3.5 py-2 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 text-center">
            <div class="text-xs text-rose-200">錯題累積</div>
            <div class="text-lg font-black text-rose-300">${mistakeCount} <span class="text-xs font-normal">題</span></div>
          </div>
          <a href="pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf" download class="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-xs font-bold shadow-md transition flex items-center gap-2" title="下載 EMT-1 題庫 PDF">
            <i data-lucide="file-down" class="w-4 h-4"></i>
            <span>下載 EMT-1 題庫 PDF</span>
          </a>
        </div>
      </div>
    </div>

    <!-- EMT Sub-Navigation Tabs -->
    <div class="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-200 dark:border-slate-800 no-scrollbar text-xs sm:text-sm font-semibold">
      <button onclick="switchEmtSubTab('quiz')" class="px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap ${activeSubTab === 'quiz' ? 'bg-teal-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'}">
        <i data-lucide="zap" class="w-4 h-4"></i>
        <span>⚡ 專屬隨機測驗 / 模擬考</span>
      </button>
      <button onclick="switchEmtSubTab('bank')" class="px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap ${activeSubTab === 'bank' ? 'bg-teal-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'}">
        <i data-lucide="book-open" class="w-4 h-4"></i>
        <span>🔍 全真題庫速查 (${totalQuestions}題)</span>
      </button>
      <button onclick="switchEmtSubTab('study')" class="px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap ${activeSubTab === 'study' ? 'bg-teal-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'}">
        <i data-lucide="file-text" class="w-4 h-4"></i>
        <span>📖 核心法規與急救精華</span>
      </button>
      <button onclick="switchEmtSubTab('resources')" class="px-4 py-2 rounded-xl transition flex items-center gap-2 whitespace-nowrap ${activeSubTab === 'resources' ? 'bg-teal-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'}">
        <i data-lucide="external-link" class="w-4 h-4"></i>
        <span>🌐 十大學習資源清單</span>
      </button>
    </div>

    <!-- EMT Sub-tab Content Container -->
    <div id="emt-subtab-container" class="pt-2"></div>
  `;

  renderEmtCurrentSubTab();
  if (window.lucide) window.lucide.createIcons();
}

function switchEmtSubTab(subTab) {
  AppState.emt.activeSubTab = subTab;
  renderEmtSection();
}

function renderEmtCurrentSubTab() {
  const container = document.getElementById('emt-subtab-container');
  if (!container) return;

  switch (AppState.emt.activeSubTab) {
    case 'quiz':
      renderEmtQuizView();
      break;
    case 'bank':
      renderEmtBank();
      break;
    case 'study':
      renderEmtStudy();
      break;
    case 'resources':
      renderEmtResources();
      break;
  }
}

/* ==========================================================================
   EMT-1 QUIZ ENGINE (完全獨立於替代役法規題庫，選項隨機分配)
   ========================================================================== */

function renderEmtQuizView() {
  const container = document.getElementById('emt-subtab-container');
  if (!container) return;

  if (AppState.emt.quiz.active) {
    if (AppState.emt.quiz.isSubmitted) {
      renderEmtQuizResults();
    } else {
      renderActiveEmtQuiz();
    }
  } else {
    renderEmtQuizSetup();
  }
}

function renderEmtQuizSetup() {
  const container = document.getElementById('emt-subtab-container');
  if (!container) return;

  const totalCount = AppState.emt.questions.length || 96;
  const mistakeCount = AppState.emt.mistakes.size;

  container.innerHTML = `
    <div class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <!-- Mode 1: 50 Questions Full Mock Exam -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-teal-500 transition cursor-pointer shadow-sm group border border-teal-500/20" onclick="startEmtQuiz('mock50')">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-teal-100 dark:bg-teal-950 text-teal-600 dark:text-teal-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="award" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-teal-500/10 text-teal-600 dark:text-teal-400 font-bold rounded-full">全真鑑測</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">50題 期末全真模擬考</h3>
            <p class="text-slate-600 dark:text-slate-400 text-xs sm:text-sm leading-relaxed">
              完全比照成功嶺期末鑑測標準：隨機抽取 50 題選擇題，限時 50 分鐘，70 分及格，選項隨機打亂分配。
            </p>
          </div>
          <button class="mt-6 w-full py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm">
            <span>開始全真鑑測 (50題)</span>
            <i data-lucide="arrow-right" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Mode 2: 20 Questions Quick Practice -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-emerald-500 transition cursor-pointer shadow-sm group border border-emerald-500/20" onclick="startEmtQuiz('practice20')">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="zap" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold rounded-full">即做即批</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">20題 高頻速測練習</h3>
            <p class="text-slate-600 dark:text-slate-400 text-xs sm:text-sm leading-relaxed">
              隨機抽取 20 題核心精華題，做一題立即顯示答案、詳細解析與法規出處，答錯自動加入專屬錯題本。
            </p>
          </div>
          <button class="mt-6 w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm">
            <span>開始精選速刷 (20題)</span>
            <i data-lucide="play" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Mode 3: Mistakes Review -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-rose-500 transition cursor-pointer shadow-sm group border border-rose-500/20 ${mistakeCount === 0 ? 'opacity-60 cursor-not-allowed' : ''}" ${mistakeCount > 0 ? 'onclick="startEmtQuiz(\'mistakes\')"' : ''}>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-rose-100 dark:bg-rose-950 text-rose-600 dark:text-rose-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="alert-circle" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-rose-500/10 text-rose-600 dark:text-rose-400 font-bold rounded-full">累積 ${mistakeCount} 題</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">EMT-1 專屬錯題重測</h3>
            <p class="text-slate-600 dark:text-slate-400 text-xs sm:text-sm leading-relaxed">
              針對 EMT-1 測驗中答錯的題目進行加強特訓，答對自動移出錯題本，直到所有救護考點全部融會貫通。
            </p>
          </div>
          <button class="mt-6 w-full py-2.5 ${mistakeCount > 0 ? 'bg-rose-600 hover:bg-rose-700' : 'bg-slate-400'} text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm" ${mistakeCount === 0 ? 'disabled' : ''}>
            <span>${mistakeCount > 0 ? '重測所有錯題' : '尚無錯題記錄'}</span>
            <i data-lucide="refresh-cw" class="w-4 h-4"></i>
          </button>
        </div>

        <!-- Mode 4: Category Specific -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-amber-500 transition shadow-sm border border-amber-500/20">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400 rounded-xl">
                <i data-lucide="layers" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-amber-500/10 text-amber-600 dark:text-amber-400 font-bold rounded-full">章節專精</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">救護章節專題測驗</h3>
            <p class="text-slate-600 dark:text-slate-400 text-xs">挑選較弱的救護單元進行單元突破：</p>
            <select id="emt-cat-select" class="w-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-2.5 py-1.5 text-xs sm:text-sm text-slate-800 dark:text-slate-200 outline-none focus:border-amber-500">
              <option value="emt_laws">⚖️ 緊急醫療救護法規與倫理 (12題)</option>
              <option value="emt_anatomy">🫀 基礎解剖與八大生命徵象 (14題)</option>
              <option value="emt_airway">🫁 呼吸道處置與氧氣治療 (15題)</option>
              <option value="emt_cpr">⚡ 心肺復甦術與AED (15題)</option>
              <option value="emt_trauma">🩸 創傷評估止血固定搬運 (15題)</option>
              <option value="emt_medical">🏥 急症評估處置與休克 (15題)</option>
              <option value="emt_mci">🚨 大量傷病患START檢傷 (10題)</option>
            </select>
          </div>
          <button onclick="startEmtCategoryQuiz()" class="mt-6 w-full py-2.5 bg-amber-600 hover:bg-amber-700 text-white font-semibold rounded-xl transition flex items-center justify-center gap-2 shadow-sm text-xs sm:text-sm">
            <span>開始章節刷題</span>
            <i data-lucide="play" class="w-4 h-4"></i>
          </button>
        </div>
      </div>

      <!-- Quick Custom Setup Box -->
      <div class="glass-panel p-4 sm:p-5 rounded-2xl flex flex-wrap items-center justify-between gap-4 text-xs sm:text-sm text-slate-600 dark:text-slate-400">
        <div class="flex items-center gap-4 flex-wrap">
          <label class="flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" id="emt-opt-shuffle-q" checked class="rounded text-teal-600 focus:ring-teal-500 w-4 h-4">
            <span class="font-medium">隨機打亂題目順序</span>
          </label>
          <label class="flex items-center gap-2 cursor-pointer select-none">
            <input type="checkbox" id="emt-opt-shuffle-opt" checked class="rounded text-teal-600 focus:ring-teal-500 w-4 h-4">
            <span class="font-medium">隨機打亂選項 (A)(B)(C)(D) 分配</span>
          </label>
        </div>
        <button onclick="resetAllEmtMistakes()" class="text-rose-500 hover:text-rose-600 transition flex items-center gap-1 font-medium text-xs">
          <i data-lucide="trash-2" class="w-3.5 h-3.5"></i> 清空 EMT 錯題記錄
        </button>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function startEmtCategoryQuiz() {
  const cat = document.getElementById('emt-cat-select')?.value || 'emt_laws';
  startEmtQuiz('category', cat);
}

function shuffleEmtQuestionOptions(q) {
  const origAnswer = q.answer;
  const rawOpts = q.options.map((opt, idx) => {
    let cleanText = opt;
    if (cleanText.match(/^\([A-D1-4]\)\s*/)) {
      cleanText = cleanText.replace(/^\([A-D1-4]\)\s*/, '');
    }
    return { text: cleanText, isCorrect: idx === origAnswer };
  });

  const shuffledOpts = [...rawOpts];
  shuffleArray(shuffledOpts);

  const labels = ['(A)', '(B)', '(C)', '(D)'];
  const newOptions = shuffledOpts.map((o, idx) => `${labels[idx]} ${o.text}`);
  const newAnswer = shuffledOpts.findIndex(o => o.isCorrect);

  return {
    ...q,
    options: newOptions,
    answer: newAnswer
  };
}

function startEmtQuiz(mode, category = 'all') {
  const shuffleQ = document.getElementById('emt-opt-shuffle-q')?.checked ?? true;
  const shuffleOpt = document.getElementById('emt-opt-shuffle-opt')?.checked ?? true;

  let pool = [...AppState.emt.questions];
  if (pool.length === 0) {
    alert('EMT 題庫載入中，請稍候重試！');
    return;
  }

  let selected = [];
  let isInstant = (mode === 'practice20' || mode === 'category');
  let timeLimit = 3000; // 50 mins

  if (mode === 'mock50') {
    selected = pickRandom(pool, 50);
    isInstant = false;
  } else if (mode === 'practice20') {
    selected = pickRandom(pool, 20);
    isInstant = true;
  } else if (mode === 'category') {
    selected = pool.filter(q => q.category === category);
    if (shuffleQ) shuffleArray(selected);
    isInstant = true;
  } else if (mode === 'mistakes') {
    selected = pool.filter(q => AppState.emt.mistakes.has(q.id));
    if (shuffleQ) shuffleArray(selected);
    isInstant = true;
  }

  if (selected.length === 0) {
    alert('此分類目前沒有題目可供測驗！');
    return;
  }

  // Shuffle options if requested
  if (shuffleOpt) {
    selected = selected.map(q => shuffleEmtQuestionOptions(q));
  } else if (shuffleQ) {
    shuffleArray(selected);
  }

  AppState.emt.quiz = {
    active: true,
    mode: mode,
    selectedCategory: category,
    questions: selected,
    currentIndex: 0,
    answers: {},
    flags: new Set(),
    instantFeedback: isInstant,
    timer: null,
    timeRemaining: timeLimit,
    totalTime: timeLimit,
    startTime: Date.now(),
    isSubmitted: false,
    shuffleQuestions: shuffleQ,
    shuffleOptions: shuffleOpt
  };

  if (!isInstant) {
    startEmtTimer();
  }

  renderActiveEmtQuiz();
}

function startEmtTimer() {
  if (AppState.emt.quiz.timer) clearInterval(AppState.emt.quiz.timer);
  AppState.emt.quiz.timer = setInterval(() => {
    if (!AppState.emt.quiz.active || AppState.emt.quiz.isSubmitted) {
      clearInterval(AppState.emt.quiz.timer);
      return;
    }
    AppState.emt.quiz.timeRemaining--;
    updateEmtTimerDisplay();
    if (AppState.emt.quiz.timeRemaining <= 0) {
      clearInterval(AppState.emt.quiz.timer);
      alert('⏰ 測驗時間截止！系統將自動交卷計分。');
      submitEmtQuiz();
    }
  }, 1000);
}

function updateEmtTimerDisplay() {
  const timerEl = document.getElementById('emt-quiz-timer');
  if (!timerEl) return;
  const rem = AppState.emt.quiz.timeRemaining;
  const mins = Math.floor(rem / 60);
  const secs = rem % 60;
  timerEl.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  if (rem < 300) {
    timerEl.classList.add('text-rose-500', 'animate-pulse');
  }
}

function renderActiveEmtQuiz() {
  const container = document.getElementById('emt-subtab-container');
  if (!container || !AppState.emt.quiz.active) return;

  const quiz = AppState.emt.quiz;
  const q = quiz.questions[quiz.currentIndex];
  if (!q) return;

  const total = quiz.questions.length;
  const curr = quiz.currentIndex + 1;
  const percent = Math.round((curr / total) * 100);
  const userAns = quiz.answers[quiz.currentIndex];
  const isAnswered = (userAns !== undefined);
  const isFlagged = quiz.flags.has(quiz.currentIndex);

  const mins = Math.floor(quiz.timeRemaining / 60);
  const secs = quiz.timeRemaining % 60;
  const timeFormatted = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Quiz Progress Header -->
      <div class="glass-panel p-4 sm:p-5 rounded-2xl space-y-3 shadow-sm border border-teal-500/20">
        <div class="flex items-center justify-between flex-wrap gap-2 text-xs sm:text-sm font-semibold">
          <div class="flex items-center gap-2">
            <span class="px-2.5 py-1 bg-teal-600 text-white rounded-lg text-xs font-bold">
              第 ${curr} / ${total} 題
            </span>
            <span class="text-slate-500 dark:text-slate-400">
              進度：${percent}%
            </span>
          </div>

          <div class="flex items-center gap-3">
            ${!quiz.instantFeedback ? `
              <div class="flex items-center gap-1.5 px-3 py-1 bg-slate-100 dark:bg-slate-800 rounded-lg text-slate-700 dark:text-slate-300 font-mono font-bold text-xs sm:text-sm">
                <i data-lucide="clock" class="w-4 h-4 text-teal-500"></i>
                <span id="emt-quiz-timer">${timeFormatted}</span>
              </div>
            ` : ''}

            <button onclick="toggleEmtFlag(${quiz.currentIndex})" class="px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition ${isFlagged ? 'bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border-amber-300' : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-transparent'}">
              <i data-lucide="flag" class="w-3.5 h-3.5 ${isFlagged ? 'fill-current text-amber-500' : ''}"></i>
              <span>${isFlagged ? '已標記' : '標記此題'}</span>
            </button>

            <button onclick="confirmExitEmtQuiz()" class="text-rose-500 hover:text-rose-600 text-xs font-semibold flex items-center gap-1">
              <i data-lucide="x-circle" class="w-4 h-4"></i>
              <span>結束測驗</span>
            </button>
          </div>
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
          <div class="bg-gradient-to-r from-teal-500 to-emerald-500 h-full transition-all duration-300" style="width: ${percent}%;"></div>
        </div>
      </div>

      <!-- Question Card -->
      <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-slate-200/80 dark:border-slate-800">
        <div class="space-y-3">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800">
              選擇題
            </span>
            <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
              ${q.category_name || q.category}
            </span>
            <span class="text-[11px] text-slate-400">編號: ${q.id}</span>
          </div>

          <h3 class="text-lg sm:text-xl font-bold text-slate-900 dark:text-white leading-relaxed">
            ${q.question}
          </h3>
        </div>

        <!-- Options Container (A)(B)(C)(D) -->
        <div class="space-y-3 pt-2">
          ${q.options.map((opt, oIdx) => {
            let btnClass = "border-slate-200 dark:border-slate-700 bg-white/70 dark:bg-slate-800/40 text-slate-800 dark:text-slate-200 hover:border-teal-500 hover:bg-teal-50/30";
            let iconHtml = `<span class="w-6 h-6 rounded-full border border-slate-300 dark:border-slate-600 flex items-center justify-center text-xs font-bold shrink-0">${String.fromCharCode(65 + oIdx)}</span>`;

            if (isAnswered) {
              if (quiz.instantFeedback) {
                // Instant Feedback Mode
                if (oIdx === q.answer) {
                  btnClass = "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 font-bold";
                  iconHtml = `<span class="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold shrink-0"><i data-lucide="check" class="w-3.5 h-3.5"></i></span>`;
                } else if (oIdx === userAns) {
                  btnClass = "border-rose-500 bg-rose-50 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200 font-bold";
                  iconHtml = `<span class="w-6 h-6 rounded-full bg-rose-500 text-white flex items-center justify-center text-xs font-bold shrink-0"><i data-lucide="x" class="w-3.5 h-3.5"></i></span>`;
                } else {
                  btnClass = "opacity-50 border-slate-200 dark:border-slate-800 text-slate-400";
                }
              } else {
                // Mock Exam Mode
                if (oIdx === userAns) {
                  btnClass = "border-teal-500 bg-teal-50 dark:bg-teal-950/50 text-teal-900 dark:text-teal-200 font-bold shadow-sm";
                  iconHtml = `<span class="w-6 h-6 rounded-full bg-teal-600 text-white flex items-center justify-center text-xs font-bold shrink-0">${String.fromCharCode(65 + oIdx)}</span>`;
                }
              }
            }

            return `
              <button onclick="selectEmtAnswer(${oIdx})" ${isAnswered && quiz.instantFeedback ? 'disabled' : ''} class="w-full text-left p-4 rounded-2xl border transition flex items-center gap-3 text-sm leading-relaxed ${btnClass}">
                ${iconHtml}
                <span class="flex-1">${opt}</span>
              </button>
            `;
          }).join('')}
        </div>

        <!-- Instant Feedback Explanation Box -->
        ${isAnswered && quiz.instantFeedback ? `
          <div class="mt-6 p-5 rounded-2xl border ${userAns === q.answer ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-300 dark:border-emerald-800/60' : 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-300 dark:border-rose-800/60'} space-y-3">
            <div class="flex items-center gap-2">
              <span class="text-sm font-black ${userAns === q.answer ? 'text-emerald-700 dark:text-emerald-300' : 'text-rose-600 dark:text-rose-400'}">
                ${userAns === q.answer ? '✅ 答對了！' : '❌ 答錯了！'}
              </span>
              <span class="text-xs font-bold text-slate-700 dark:text-slate-300">
                正確答案：<strong class="text-emerald-600 dark:text-emerald-400 font-black">${q.options[q.answer]}</strong>
              </span>
            </div>

            <p class="text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
              <strong>【法規與救護解析】</strong> ${q.explanation}
            </p>

            ${q.source ? `
              <div class="pt-2 border-t border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between text-xs text-slate-500">
                <span>出處依據：<strong>${q.source}</strong></span>
                ${q.source_url ? `
                  <a href="${q.source_url}" target="_blank" class="text-teal-600 dark:text-teal-400 hover:underline flex items-center gap-1 font-semibold">
                    <span>查驗最新條文</span>
                    <i data-lucide="external-link" class="w-3 h-3"></i>
                  </a>
                ` : ''}
              </div>
            ` : ''}
          </div>
        ` : ''}
      </div>

      <!-- Navigation & Action Buttons -->
      <div class="flex items-center justify-between gap-3">
        <button onclick="prevEmtQuestion()" ${quiz.currentIndex === 0 ? 'disabled' : ''} class="px-5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 font-semibold text-xs sm:text-sm hover:bg-slate-100 dark:hover:bg-slate-800 transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2">
          <i data-lucide="chevron-left" class="w-4 h-4"></i>
          <span>上一題</span>
        </button>

        ${curr === total ? `
          <button onclick="submitEmtQuiz()" class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow-lg transition flex items-center gap-2">
            <i data-lucide="send" class="w-4 h-4"></i>
            <span>完成交卷評分</span>
          </button>
        ` : `
          <button onclick="nextEmtQuestion()" class="px-6 py-2.5 bg-teal-600 hover:bg-teal-700 text-white font-bold text-xs sm:text-sm rounded-xl shadow-md transition flex items-center gap-2">
            <span>下一題</span>
            <i data-lucide="chevron-right" class="w-4 h-4"></i>
          </button>
        `}
      </div>

      <!-- Question Jump Grid Drawer / Overview -->
      <div class="glass-panel p-4 sm:p-5 rounded-2xl space-y-3 shadow-sm border border-slate-200/80 dark:border-slate-800">
        <div class="flex items-center justify-between text-xs font-semibold text-slate-600 dark:text-slate-400">
          <span>題目跳轉清單 (已作答 ${Object.keys(quiz.answers).length} / ${total} 題)</span>
          <span class="flex items-center gap-2">
            <span class="inline-block w-2.5 h-2.5 rounded-full bg-teal-600"></span> 已答
            <span class="inline-block w-2.5 h-2.5 rounded-full bg-slate-200 dark:bg-slate-700"></span> 未答
            <span class="inline-block w-2.5 h-2.5 rounded-full bg-amber-400"></span> 標記
          </span>
        </div>
        <div class="grid grid-cols-10 sm:grid-cols-15 md:grid-cols-20 gap-1.5 pt-1">
          ${quiz.questions.map((_, idx) => {
            const answered = (quiz.answers[idx] !== undefined);
            const flagged = quiz.flags.has(idx);
            const isCurrent = (idx === quiz.currentIndex);

            let bgClass = "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300";
            if (isCurrent) {
              bgClass = "ring-2 ring-teal-500 font-black";
            }
            if (flagged) {
              bgClass = "bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-200 border border-amber-400";
            } else if (answered) {
              bgClass = "bg-teal-600 text-white";
            }

            return `
              <button onclick="jumpToEmtQuestion(${idx})" class="w-8 h-8 rounded-lg text-xs font-semibold transition flex items-center justify-center ${bgClass}">
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

function selectEmtAnswer(optIdx) {
  const quiz = AppState.emt.quiz;
  if (!quiz.active || quiz.isSubmitted) return;

  const q = quiz.questions[quiz.currentIndex];
  quiz.answers[quiz.currentIndex] = optIdx;

  if (quiz.instantFeedback) {
    if (optIdx !== q.answer) {
      AppState.emt.mistakes.add(q.id);
    } else {
      if (AppState.emt.mistakes.has(q.id)) {
        AppState.emt.mistakes.delete(q.id);
      }
    }
    localStorage.setItem('sms_emt_mistakes', JSON.stringify(Array.from(AppState.emt.mistakes)));
  }

  renderActiveEmtQuiz();
}

function nextEmtQuestion() {
  const quiz = AppState.emt.quiz;
  if (quiz.currentIndex < quiz.questions.length - 1) {
    quiz.currentIndex++;
    renderActiveEmtQuiz();
  }
}

function prevEmtQuestion() {
  const quiz = AppState.emt.quiz;
  if (quiz.currentIndex > 0) {
    quiz.currentIndex--;
    renderActiveEmtQuiz();
  }
}

function jumpToEmtQuestion(idx) {
  const quiz = AppState.emt.quiz;
  if (idx >= 0 && idx < quiz.questions.length) {
    quiz.currentIndex = idx;
    renderActiveEmtQuiz();
  }
}

function toggleEmtFlag(idx) {
  const quiz = AppState.emt.quiz;
  if (quiz.flags.has(idx)) {
    quiz.flags.delete(idx);
  } else {
    quiz.flags.add(idx);
  }
  renderActiveEmtQuiz();
}

function confirmExitEmtQuiz() {
  if (confirm('確定要提前結束本次 EMT-1 測驗嗎？未儲存的答題進度將會遺失。')) {
    if (AppState.emt.quiz.timer) clearInterval(AppState.emt.quiz.timer);
    AppState.emt.quiz.active = false;
    renderEmtQuizSetup();
  }
}

function submitEmtQuiz() {
  const quiz = AppState.emt.quiz;
  if (!quiz.active) return;

  if (quiz.timer) clearInterval(quiz.timer);

  let correctCount = 0;
  quiz.questions.forEach((q, idx) => {
    const userAns = quiz.answers[idx];
    if (userAns === q.answer) {
      correctCount++;
      if (AppState.emt.mistakes.has(q.id)) {
        AppState.emt.mistakes.delete(q.id);
      }
    } else {
      AppState.emt.mistakes.add(q.id);
    }
  });

  localStorage.setItem('sms_emt_mistakes', JSON.stringify(Array.from(AppState.emt.mistakes)));

  quiz.isSubmitted = true;
  quiz.score = Math.round((correctCount / quiz.questions.length) * 100);
  renderEmtQuizResults();
}

function renderEmtQuizResults() {
  const container = document.getElementById('emt-subtab-container');
  if (!container || !AppState.emt.quiz.active) return;

  const quiz = AppState.emt.quiz;
  const total = quiz.questions.length;
  let correctCount = 0;
  quiz.questions.forEach((q, idx) => {
    if (quiz.answers[idx] === q.answer) correctCount++;
  });

  const score = quiz.score;
  const isPassed = (score >= 70);

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Score Hero Box -->
      <div class="glass-panel p-6 sm:p-8 rounded-3xl text-center space-y-4 shadow-lg border ${isPassed ? 'border-emerald-500/40 bg-emerald-50/20 dark:bg-emerald-950/20' : 'border-rose-500/40 bg-rose-50/20 dark:bg-rose-950/20'}">
        <div class="w-16 h-16 rounded-full mx-auto flex items-center justify-center text-white shadow-lg ${isPassed ? 'bg-emerald-500' : 'bg-rose-500'}">
          <i data-lucide="${isPassed ? 'check-circle' : 'alert-triangle'}" class="w-8 h-8"></i>
        </div>

        <h3 class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white">
          ${isPassed ? '🎉 測驗合格！恭喜通過 EMT-1 學科門檻' : '⚠️ 測驗未及格，請加強複習再戰！'}
        </h3>
        <p class="text-sm text-slate-600 dark:text-slate-400">
          成功嶺初級救護技術員 (EMT-1) 期末學科測驗及格標準為 <strong>70 分</strong>
        </p>

        <div class="text-5xl sm:text-6xl font-black tracking-tight ${isPassed ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">
          ${score} <span class="text-xl sm:text-2xl font-bold text-slate-500">分</span>
        </div>

        <div class="flex items-center justify-center gap-6 text-xs sm:text-sm text-slate-600 dark:text-slate-300 font-medium pt-2">
          <span>總題數：<strong>${total}</strong> 題</span>
          <span>答對：<strong class="text-emerald-600">${correctCount}</strong> 題</span>
          <span>答錯：<strong class="text-rose-600">${total - correctCount}</strong> 題</span>
          <span>正確率：<strong>${Math.round((correctCount / total) * 100)}%</strong></span>
        </div>

        <div class="flex items-center justify-center gap-3 pt-4 flex-wrap">
          <button onclick="startEmtQuiz('${quiz.mode}', '${quiz.selectedCategory}')" class="px-5 py-2.5 bg-teal-600 hover:bg-teal-700 text-white rounded-xl font-bold text-xs sm:text-sm shadow-md transition flex items-center gap-2">
            <i data-lucide="refresh-cw" class="w-4 h-4"></i>
            <span>再次重測</span>
          </button>
          ${AppState.emt.mistakes.size > 0 ? `
            <button onclick="startEmtQuiz('mistakes')" class="px-5 py-2.5 bg-rose-600 hover:bg-rose-700 text-white rounded-xl font-bold text-xs sm:text-sm shadow-md transition flex items-center gap-2">
              <i data-lucide="alert-circle" class="w-4 h-4"></i>
              <span>複習所有錯題 (${AppState.emt.mistakes.size})</span>
            </button>
          ` : ''}
          <button onclick="AppState.emt.quiz.active = false; renderEmtQuizSetup();" class="px-5 py-2.5 bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 rounded-xl font-bold text-xs sm:text-sm hover:bg-slate-300 transition flex items-center gap-2">
            <i data-lucide="arrow-left" class="w-4 h-4"></i>
            <span>返回測驗選單</span>
          </button>
        </div>
      </div>

      <!-- Detailed Question Review Section -->
      <div class="space-y-4">
        <h4 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
          <i data-lucide="clipboard-list" class="w-5 h-5 text-teal-500"></i> 本次測驗試題完整解析與檢討
        </h4>

        <div class="space-y-4">
          ${quiz.questions.map((q, idx) => {
            const userAns = quiz.answers[idx];
            const isCorrect = (userAns === q.answer);

            return `
              <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-3 shadow-sm border ${isCorrect ? 'border-slate-200 dark:border-slate-800' : 'border-rose-300 dark:border-rose-900/60 bg-rose-50/20 dark:bg-rose-950/10'}">
                <div class="flex items-center justify-between gap-2 flex-wrap text-xs">
                  <div class="flex items-center gap-2">
                    <span class="w-6 h-6 rounded-full flex items-center justify-center font-bold text-white ${isCorrect ? 'bg-emerald-500' : 'bg-rose-500'}">
                      ${idx + 1}
                    </span>
                    <span class="font-bold ${isCorrect ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'}">
                      ${isCorrect ? '答對' : '答錯'}
                    </span>
                    <span class="text-slate-500">${q.category_name}</span>
                  </div>
                  <span class="text-slate-400">題號: ${q.id}</span>
                </div>

                <h5 class="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-relaxed">
                  ${q.question}
                </h5>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm pt-1">
                  ${q.options.map((opt, oIdx) => {
                    let optStyle = "p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300";
                    if (oIdx === q.answer) {
                      optStyle = "p-2.5 rounded-xl border-2 border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 font-bold";
                    } else if (oIdx === userAns && !isCorrect) {
                      optStyle = "p-2.5 rounded-xl border-2 border-rose-500 bg-rose-50 dark:bg-rose-950/40 text-rose-900 dark:text-rose-200 font-bold";
                    }
                    return `<div class="${optStyle}">${opt}</div>`;
                  }).join('')}
                </div>

                <div class="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl space-y-1.5 text-xs text-slate-700 dark:text-slate-300 leading-relaxed border border-slate-200/60 dark:border-slate-700/60">
                  <div class="font-bold text-emerald-600 dark:text-emerald-400">
                    <strong>【正確答案】</strong> ${q.options[q.answer]}
                  </div>
                  <div>
                    <strong>【詳解依據】</strong> ${q.explanation}
                  </div>
                  ${q.source ? `
                    <div class="pt-1 flex items-center justify-between text-slate-500">
                      <span>來源：${q.source}</span>
                      ${q.source_url ? `
                        <a href="${q.source_url}" target="_blank" class="text-teal-600 hover:underline flex items-center gap-1 font-semibold">
                          <span>查看官方條文</span>
                          <i data-lucide="external-link" class="w-3 h-3"></i>
                        </a>
                      ` : ''}
                    </div>
                  ` : ''}
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

function resetAllEmtMistakes() {
  if (AppState.emt.mistakes.size === 0) {
    alert('目前沒有 EMT 錯題記錄！');
    return;
  }
  if (confirm('確定要清空所有的 EMT-1 錯題記錄嗎？')) {
    AppState.emt.mistakes.clear();
    localStorage.removeItem('sms_emt_mistakes');
    renderEmtQuizSetup();
  }
}

/* ==========================================================================
   EMT-1 QUESTION BANK BROWSER (題庫速查與背題模式)
   ========================================================================== */

function renderEmtBank() {
  const container = document.getElementById('emt-subtab-container');
  if (!container) return;

  const bank = AppState.emt.bank;
  let filtered = [...AppState.emt.questions];

  // Category filter
  if (bank.categoryFilter !== 'all') {
    filtered = filtered.filter(q => q.category === bank.categoryFilter);
  }

  // Keyword search
  if (bank.searchTerm) {
    const term = bank.searchTerm.toLowerCase();
    filtered = filtered.filter(q => {
      const qText = q.question.toLowerCase();
      const explText = (q.explanation || '').toLowerCase();
      const optsText = (q.options || []).join(' ').toLowerCase();
      const srcText = (q.source || '').toLowerCase();
      return qText.includes(term) || explText.includes(term) || optsText.includes(term) || srcText.includes(term);
    });
  }

  const totalFiltered = filtered.length;
  const pageSize = bank.pageSize || 15;
  const totalPages = Math.ceil(totalFiltered / pageSize) || 1;
  if (bank.currentPage > totalPages) bank.currentPage = totalPages;
  if (bank.currentPage < 1) bank.currentPage = 1;

  const startIndex = (bank.currentPage - 1) * pageSize;
  const pageQuestions = filtered.slice(startIndex, startIndex + pageSize);

  container.innerHTML = `
    <div class="space-y-6">
      <!-- Search & Filters Header Card -->
      <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-4 shadow-sm border border-teal-500/20">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="search" class="w-5 h-5 text-teal-500"></i> EMT-1 全真題庫速查與背題模式
            </h3>
            <p class="text-xs text-slate-500 dark:text-slate-400">
              即時搜尋題目關鍵字、按 7 大急救章節精準篩選，支援遮蔽答案背題翻牌模式。
            </p>
          </div>
          <div class="flex items-center gap-2 flex-wrap">
            <a href="pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf" download class="flex items-center gap-1.5 bg-teal-600 hover:bg-teal-700 text-white px-3.5 py-2 rounded-xl text-xs font-semibold shadow transition" title="下載 EMT-1 題庫 PDF">
              <i data-lucide="file-down" class="w-4 h-4"></i>
              <span>下載 EMT-1 題庫 PDF</span>
            </a>
            <label class="flex items-center gap-2 cursor-pointer select-none bg-teal-50 dark:bg-teal-950/50 px-3.5 py-2 rounded-xl border border-teal-200 dark:border-teal-800 text-xs font-semibold text-teal-800 dark:text-teal-300">
              <input type="checkbox" id="emt-bank-hide-answers" ${bank.hideAnswers ? 'checked' : ''} onchange="toggleEmtHideAnswers(this.checked)" class="rounded text-teal-600 focus:ring-teal-500 w-4 h-4">
              <span class="flex items-center gap-1"><i data-lucide="eye-off" class="w-3.5 h-3.5"></i> 遮蔽答案 (背題翻牌)</span>
            </label>
          </div>
        </div>

        <!-- Filter Controls -->
        <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 pt-1">
          <!-- Keyword Input -->
          <div class="sm:col-span-7 relative">
            <i data-lucide="search" class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"></i>
            <input type="text" id="emt-bank-search" value="${bank.searchTerm}" oninput="handleEmtSearch(this.value)" placeholder="搜尋題目、解析關鍵字（如：GCS、抽吸時間、止血帶、VF、START、管理辦法...）" class="w-full pl-9 pr-4 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-800 dark:text-slate-200 outline-none focus:border-teal-500 transition">
          </div>

          <!-- Chapter Select -->
          <div class="sm:col-span-5">
            <select id="emt-bank-cat" onchange="handleEmtCatFilter(this.value)" class="w-full px-3 py-2 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs sm:text-sm text-slate-800 dark:text-slate-200 outline-none focus:border-teal-500">
              <option value="all" ${bank.categoryFilter === 'all' ? 'selected' : ''}>分類：全部分類 (${AppState.emt.questions.length}題)</option>
              <option value="emt_laws" ${bank.categoryFilter === 'emt_laws' ? 'selected' : ''}>⚖️ 緊急醫療救護法規與倫理 (12題)</option>
              <option value="emt_anatomy" ${bank.categoryFilter === 'emt_anatomy' ? 'selected' : ''}>🫀 基礎解剖與八大生命徵象 (14題)</option>
              <option value="emt_airway" ${bank.categoryFilter === 'emt_airway' ? 'selected' : ''}>🫁 呼吸道處置與氧氣治療 (15題)</option>
              <option value="emt_cpr" ${bank.categoryFilter === 'emt_cpr' ? 'selected' : ''}>⚡ 心肺復甦術與AED (15題)</option>
              <option value="emt_trauma" ${bank.categoryFilter === 'emt_trauma' ? 'selected' : ''}>🩸 創傷評估止血固定搬運 (15題)</option>
              <option value="emt_medical" ${bank.categoryFilter === 'emt_medical' ? 'selected' : ''}>🏥 急症評估處置與休克 (15題)</option>
              <option value="emt_mci" ${bank.categoryFilter === 'emt_mci' ? 'selected' : ''}>🚨 大量傷病患START檢傷 (10題)</option>
            </select>
          </div>
        </div>

        <!-- Filtered Count Bar -->
        <div class="flex items-center justify-between text-xs text-slate-500 pt-1 border-t border-slate-100 dark:border-slate-800">
          <span>共篩選出 <strong class="text-teal-600 dark:text-teal-400 font-bold">${totalFiltered}</strong> 題 ｜ 目前第 ${bank.currentPage} / ${totalPages} 頁</span>
          <span class="text-[11px] text-slate-400">點擊卡片星號可收藏題目</span>
        </div>
      </div>

      <!-- Question Cards List -->
      <div class="space-y-4">
        ${pageQuestions.map((q, idx) => {
          const isBookmarked = AppState.emt.bookmarks.has(q.id);
          const qIndexGlobal = startIndex + idx + 1;

          return `
            <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-4 shadow-sm border border-slate-200/80 dark:border-slate-800 hover:border-teal-500/40 transition">
              <div class="flex items-start justify-between gap-3">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="px-2.5 py-0.5 rounded-lg text-xs font-bold bg-teal-600 text-white">
                    #${qIndexGlobal}
                  </span>
                  <span class="px-2 py-0.5 rounded-md text-[11px] font-bold bg-teal-50 dark:bg-teal-950 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800">
                    選擇題
                  </span>
                  <span class="px-2 py-0.5 rounded-md text-[11px] font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                    ${q.category_name}
                  </span>
                  <span class="text-[11px] text-slate-400">${q.id}</span>
                </div>

                <button onclick="toggleEmtBookmark('${q.id}')" class="text-slate-400 hover:text-amber-500 transition p-1" title="收藏題目">
                  <i data-lucide="star" class="w-4 h-4 ${isBookmarked ? 'fill-amber-400 text-amber-500' : ''}"></i>
                </button>
              </div>

              <!-- Question Text -->
              <h4 class="text-sm sm:text-base font-bold text-slate-900 dark:text-white leading-relaxed">
                ${q.question}
              </h4>

              <!-- Options List (A)(B)(C)(D) -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs sm:text-sm pt-1">
                ${q.options.map((opt, oIdx) => {
                  const isAnswer = (oIdx === q.answer);
                  let optClass = "p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 bg-slate-50/50 dark:bg-slate-800/30";
                  if (!bank.hideAnswers && isAnswer) {
                    optClass = "p-2.5 rounded-xl border-2 border-emerald-500 bg-emerald-50 dark:bg-emerald-950/40 text-emerald-900 dark:text-emerald-200 font-bold shadow-sm";
                  }
                  return `
                    <div class="${optClass}">
                      ${opt}
                    </div>
                  `;
                }).join('')}
              </div>

              <!-- Answer & Explanation -->
              ${bank.hideAnswers ? `
                <div class="pt-2">
                  <button onclick="this.nextElementSibling.classList.toggle('hidden');" class="text-xs font-semibold text-teal-600 dark:text-teal-400 flex items-center gap-1 hover:underline">
                    <i data-lucide="eye" class="w-3.5 h-3.5"></i>
                    <span>點擊查看答案與解析</span>
                  </button>
                  <div class="hidden mt-3 p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl space-y-2 text-xs text-slate-700 dark:text-slate-300 leading-relaxed border border-slate-200/80 dark:border-slate-700">
                    <div class="font-bold text-emerald-600 dark:text-emerald-400">
                      <strong>【參考答案】</strong> ${q.options[q.answer]}
                    </div>
                    <div>
                      <strong>【解析依據】</strong> ${q.explanation}
                    </div>
                    ${q.source ? `
                      <div class="pt-2 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between text-slate-500">
                        <span>出處：${q.source}</span>
                        ${q.source_url ? `
                          <a href="${q.source_url}" target="_blank" class="text-teal-600 hover:underline flex items-center gap-1 font-semibold">
                            <span>官方法規直連</span>
                            <i data-lucide="external-link" class="w-3 h-3"></i>
                          </a>
                        ` : ''}
                      </div>
                    ` : ''}
                  </div>
                </div>
              ` : `
                <div class="p-4 bg-slate-50 dark:bg-slate-800/60 rounded-xl space-y-2 text-xs text-slate-700 dark:text-slate-300 leading-relaxed border border-slate-200/80 dark:border-slate-700">
                  <div class="font-bold text-emerald-600 dark:text-emerald-400">
                    <strong>【參考答案】</strong> ${q.options[q.answer]}
                  </div>
                  <div>
                    <strong>【解析依據】</strong> ${q.explanation}
                  </div>
                  ${q.source ? `
                    <div class="pt-2 border-t border-slate-200/60 dark:border-slate-700/60 flex items-center justify-between text-slate-500">
                      <span>出處：<strong>${q.source}</strong></span>
                      ${q.source_url ? `
                        <a href="${q.source_url}" target="_blank" class="text-teal-600 hover:underline flex items-center gap-1 font-semibold">
                          <span>官方法規直連</span>
                          <i data-lucide="external-link" class="w-3 h-3"></i>
                        </a>
                      ` : ''}
                    </div>
                  ` : ''}
                </div>
              `}
            </div>
          `;
        }).join('')}
      </div>

      <!-- Pagination Controls -->
      ${totalPages > 1 ? `
        <div class="glass-panel p-4 rounded-2xl flex items-center justify-between text-xs font-semibold">
          <button onclick="changeEmtBankPage(${bank.currentPage - 1})" ${bank.currentPage <= 1 ? 'disabled' : ''} class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-100 transition">
            上一頁
          </button>
          <span>第 ${bank.currentPage} / ${totalPages} 頁</span>
          <button onclick="changeEmtBankPage(${bank.currentPage + 1})" ${bank.currentPage >= totalPages ? 'disabled' : ''} class="px-3 py-1.5 rounded-lg border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 disabled:opacity-30 disabled:cursor-not-allowed hover:bg-slate-100 transition">
            下一頁
          </button>
        </div>
      ` : ''}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function handleEmtSearch(val) {
  AppState.emt.bank.searchTerm = val.trim();
  AppState.emt.bank.currentPage = 1;
  renderEmtBank();
}

function handleEmtCatFilter(val) {
  AppState.emt.bank.categoryFilter = val;
  AppState.emt.bank.currentPage = 1;
  renderEmtBank();
}

function toggleEmtHideAnswers(checked) {
  AppState.emt.bank.hideAnswers = checked;
  renderEmtBank();
}

function changeEmtBankPage(page) {
  AppState.emt.bank.currentPage = page;
  renderEmtBank();
  window.scrollTo({ top: 300, behavior: 'smooth' });
}

function toggleEmtBookmark(qId) {
  if (AppState.emt.bookmarks.has(qId)) {
    AppState.emt.bookmarks.delete(qId);
  } else {
    AppState.emt.bookmarks.add(qId);
  }
  localStorage.setItem('sms_emt_bookmarks', JSON.stringify(Array.from(AppState.emt.bookmarks)));
  renderEmtBank();
}

/* ==========================================================================
   EMT-1 CORE STUDY GUIDE & PROTOCOLS (法規與急救精華講義)
   ========================================================================== */

function renderEmtStudy() {
  const container = document.getElementById('emt-subtab-container');
  if (!container) return;

  const data = AppState.emt.studyData;
  if (!data) {
    container.innerHTML = `<div class="p-8 text-center text-slate-400">講義載入中...</div>`;
    return;
  }

  container.innerHTML = `
    <div class="space-y-8">
      <!-- 0. 最新法規修正依據與主管機關異動速覽 (對齊新訓法規標準) -->
      ${data.law_meta ? `
        <div class="glass-panel p-6 rounded-2xl space-y-4 shadow-sm border border-teal-500/30">
          <div class="flex items-center justify-between flex-wrap gap-2">
            <h4 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <i data-lucide="sparkles" class="w-5 h-5 text-teal-500"></i> EMT-1 核心法規修正依據與主管機關體系速覽 (最新公告標準)
            </h4>
            <span class="text-xs text-teal-600 dark:text-teal-400 bg-teal-50 dark:bg-teal-950 px-2.5 py-1 rounded-full font-bold border border-teal-200 dark:border-teal-800">
              全國法規資料庫官方對齊
            </span>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            ${data.law_meta.map(item => `
              <div class="p-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 space-y-2">
                <div class="flex items-center justify-between gap-2">
                  <span class="text-sm font-bold text-slate-900 dark:text-white">${item.title}</span>
                  <span class="text-[11px] px-2 py-0.5 rounded bg-teal-100 text-teal-800 dark:bg-teal-950 dark:text-teal-300 font-semibold shrink-0">${item.badge}</span>
                </div>
                <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">${item.text}</p>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- 1. 核心法規逐條詳細對照 (對齊新訓條文規格，提供完整法定內文與出處連結) -->
      ${data.statutory_articles ? `
        <div class="space-y-4">
          <div class="flex items-center gap-2 border-l-4 border-teal-500 pl-3">
            <h3 class="text-lg font-black text-slate-900 dark:text-white">一、核心法規逐條對照與鑑測考點詳解 (母法與行政命令全條文)</h3>
          </div>

          <div class="space-y-3">
            ${data.statutory_articles.map((art, idx) => `
              <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-3 shadow-sm border border-slate-200 dark:border-slate-800">
                <div class="flex items-center justify-between flex-wrap gap-2">
                  <div class="flex items-center gap-2">
                    <span class="px-2.5 py-1 rounded-lg bg-teal-600 text-white font-bold text-xs">${art.law}</span>
                    <span class="text-sm font-black text-slate-900 dark:text-white">${art.article} · ${art.title}</span>
                  </div>
                  <a href="${art.url}" target="_blank" rel="noopener noreferrer" class="text-teal-600 dark:text-teal-400 hover:underline text-xs flex items-center gap-1 font-semibold" title="在全國法規資料庫中檢視官方條文">
                    <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
                    <span>全國法規資料庫</span>
                  </a>
                </div>

                <div class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed font-mono whitespace-pre-line">
                  ${art.official_text}
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-12 gap-3 text-xs pt-1">
                  <div class="sm:col-span-8 p-3 rounded-lg bg-teal-50/50 dark:bg-teal-950/20 border border-teal-100 dark:border-teal-900/40 space-y-1">
                    <span class="font-bold text-teal-800 dark:text-teal-300 block">💡 鑑測必考核心重點解析：</span>
                    <p class="text-slate-700 dark:text-slate-300">${art.key_point}</p>
                  </div>
                  <div class="sm:col-span-4 p-3 rounded-lg bg-rose-50/50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/40 space-y-1">
                    <span class="font-bold text-rose-800 dark:text-rose-300 block">⚖️ 法律效力與罰則：</span>
                    <p class="text-slate-700 dark:text-slate-300">${art.penalty}</p>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}

      <!-- 2. 救護技術員管理辦法重點卡片 -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-teal-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">二、救護技術員管理辦法與緊急醫療救護法 重點歸納</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          ${data.laws_summary.map(law => `
            <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-3 shadow-sm border border-teal-500/20">
              <div class="flex items-center justify-between">
                <h4 class="text-base font-bold text-teal-700 dark:text-teal-300">${law.title}</h4>
                <span class="px-2 py-0.5 bg-teal-100 dark:bg-teal-950 text-teal-800 dark:text-teal-300 text-xs font-bold rounded">
                  ${law.article}
                </span>
              </div>
              <ul class="space-y-1.5 text-xs sm:text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                ${law.points.map(pt => `
                  <li class="flex items-start gap-1.5">
                    <span class="text-teal-500 font-bold shrink-0">•</span>
                    <span>${pt}</span>
                  </li>
                `).join('')}
              </ul>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- 3. 八大生命徵象正常值與危急標準表 -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-emerald-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">三、八大生命徵象 (Vital Signs) 正常範圍與危急數值</h3>
        </div>

        <div class="glass-panel p-4 sm:p-6 rounded-2xl shadow-sm border border-emerald-500/20 overflow-x-auto">
          <table class="w-full text-left text-xs sm:text-sm border-collapse">
            <thead>
              <tr class="border-b border-slate-200 dark:border-slate-700 text-slate-900 dark:text-white font-bold bg-emerald-50/50 dark:bg-emerald-950/30">
                <th class="p-3">評估項目</th>
                <th class="p-3">成人正常值</th>
                <th class="p-3">小兒 / 嬰兒</th>
                <th class="p-3 text-rose-600 dark:text-rose-400">危急標準與異常指標</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              ${data.vital_signs.table.map(row => `
                <tr class="hover:bg-slate-50/50 dark:hover:bg-slate-800/20">
                  <td class="p-3 font-bold text-slate-900 dark:text-white">${row.item}</td>
                  <td class="p-3 text-slate-700 dark:text-slate-300">${row.adult}</td>
                  <td class="p-3 text-slate-600 dark:text-slate-400">${row.child || row.infant}</td>
                  <td class="p-3 font-semibold text-rose-600 dark:text-rose-400">${row.critical}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </div>

      <!-- 4. GCS 昏迷指數速查表 -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-amber-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">四、格拉斯哥昏迷指數 (Glasgow Coma Scale, GCS) 評分表</h3>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          ${data.gcs_table.categories.map(cat => `
            <div class="glass-panel p-5 rounded-2xl space-y-3 shadow-sm border border-amber-500/20">
              <h4 class="font-bold text-sm text-amber-700 dark:text-amber-300 border-b border-slate-200 dark:border-slate-800 pb-2">
                ${cat.category}
              </h4>
              <div class="space-y-2 text-xs">
                ${cat.items.map(it => `
                  <div class="flex items-center justify-between p-2 rounded-lg bg-slate-50 dark:bg-slate-800/40">
                    <span class="text-slate-700 dark:text-slate-300">${it.desc}</span>
                    <span class="px-2 py-0.5 rounded bg-amber-500 text-white font-bold">${it.score}分</span>
                  </div>
                `).join('')}
              </div>
            </div>
          `).join('')}
        </div>

        <!-- GCS Severity Levels -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          ${data.gcs_table.clinical_meaning.map(lvl => `
            <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-800/40 text-xs space-y-1">
              <span class="font-bold text-teal-600 dark:text-teal-400">${lvl.range}</span>
              <div class="font-bold text-slate-900 dark:text-white">${lvl.severity}</div>
              <p class="text-slate-500 text-[11px]">${lvl.desc}</p>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- 5. 成人生存之鏈與高品質 CPR+AED 五大黃金指標 -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-rose-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">五、成人生存之鏈與高品質 CPR+AED 五大黃金指標</h3>
        </div>

        <div class="glass-panel p-5 sm:p-6 rounded-2xl space-y-4 shadow-sm border border-rose-500/20">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
            ${data.cpr_aed_guide.indicators.map(ind => `
              <div class="p-4 rounded-xl border border-rose-100 dark:border-rose-900/60 bg-rose-50/30 dark:bg-rose-950/20 space-y-1.5">
                <span class="font-bold text-rose-700 dark:text-rose-400 text-xs sm:text-sm block">${ind.rule}</span>
                <p class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed">${ind.detail}</p>
              </div>
            `).join('')}
          </div>

          <div class="pt-3 border-t border-slate-200 dark:border-slate-800">
            <h4 class="font-bold text-xs sm:text-sm text-slate-900 dark:text-white mb-2">【AED 標準五大步驟流程】</h4>
            <div class="grid grid-cols-1 sm:grid-cols-5 gap-2 text-xs">
              ${data.cpr_aed_guide.aed_protocol.map((stp, idx) => `
                <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 space-y-1">
                  <span class="font-bold text-teal-600 block">${stp.step}</span>
                  <p class="text-[11px] text-slate-600 dark:text-slate-400">${stp.desc}</p>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      </div>

      <!-- 6. 常用氧氣治療設備規格與鋼瓶可用時間計算公式 -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-cyan-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">六、常用氧氣治療設備與鋼瓶計算公式</h3>
        </div>

        <div class="glass-panel p-5 rounded-2xl shadow-sm border border-cyan-500/20 space-y-4">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            ${data.oxygen_therapy.table.map(ox => `
              <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 space-y-1.5">
                <div class="font-bold text-cyan-700 dark:text-cyan-300 text-xs sm:text-sm">${ox.device}</div>
                <div class="text-xs font-semibold text-teal-600">流量: ${ox.flow} ｜ 濃度: ${ox.fio2}</div>
                <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">${ox.desc}</p>
              </div>
            `).join('')}
          </div>

          <!-- Formula Box -->
          <div class="p-4 rounded-xl bg-cyan-50/60 dark:bg-cyan-950/30 border border-cyan-200 dark:border-cyan-800 space-y-2 text-xs sm:text-sm">
            <div class="font-bold text-cyan-900 dark:text-cyan-200 flex items-center gap-2">
              <i data-lucide="calculator" class="w-4 h-4 text-cyan-600"></i> ${data.oxygen_therapy.formula.title}
            </div>
            <div class="p-2.5 bg-white dark:bg-slate-900 rounded-lg font-mono font-bold text-center text-cyan-700 dark:text-cyan-300 border border-cyan-300 dark:border-cyan-700">
              ${data.oxygen_therapy.formula.equation}
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs pt-1">
              ${data.oxygen_therapy.formula.constants.map(c => `
                <div class="p-2 bg-white/70 dark:bg-slate-800 rounded border border-cyan-200/60 dark:border-cyan-800">
                  <strong>${c.cylinder}</strong>：常數 <strong>${c.constant}</strong> (安全存量 ${c.safety})
                </div>
              `).join('')}
            </div>
            <p class="text-xs text-slate-600 dark:text-slate-300 italic">
              <strong>${data.oxygen_therapy.formula.example}</strong>
            </p>
          </div>
        </div>
      </div>

      <!-- 7. 創傷評估處置 XABCDE -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-indigo-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">七、創傷評估 XABCDE 處置要領</h3>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          ${data.trauma_care.steps.map(s => `
            <div class="glass-panel p-4 rounded-xl space-y-2 shadow-sm border border-indigo-500/20">
              <span class="px-2 py-0.5 bg-indigo-600 text-white rounded text-xs font-bold inline-block">${s.step}</span>
              <h4 class="font-bold text-sm text-slate-900 dark:text-white">${s.name}</h4>
              <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">${s.action}</p>
            </div>
          `).join('')}
        </div>
      </div>

      <!-- 8. START 大量傷病患檢傷分類 -->
      <div class="space-y-4">
        <div class="flex items-center gap-2 border-l-4 border-emerald-500 pl-3">
          <h3 class="text-lg font-black text-slate-900 dark:text-white">八、大量傷病患 START 檢傷分類決策流程 (RPM 法)</h3>
        </div>

        <div class="glass-panel p-5 rounded-2xl shadow-sm border border-emerald-500/20 space-y-3">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            ${data.start_triage.flowchart.map(st => `
              <div class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700 space-y-2">
                <span class="font-bold text-xs text-teal-600">${st.stage}</span>
                <div class="font-bold text-sm text-slate-900 dark:text-white">${st.condition}</div>
                <div class="px-2.5 py-1 rounded bg-slate-200 dark:bg-slate-700 font-bold text-xs inline-block">${st.result}</div>
                <p class="text-xs text-slate-600 dark:text-slate-400">${st.action}</p>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

/* ==========================================================================
   EMT-1 TEN+ LEARNING RESOURCES (十大學習資源清單與直連)
   ========================================================================== */

function renderEmtResources() {
  const container = document.getElementById('emt-subtab-container');
  if (!container) return;

  const data = AppState.emt.studyData;
  const list = data ? data.resources : [];

  container.innerHTML = `
    <div class="space-y-6">
      <div class="glass-panel p-6 rounded-2xl space-y-2 border border-teal-500/20 shadow-sm">
        <h3 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
          <i data-lucide="book-marked" class="w-5 h-5 text-teal-500"></i> EMT-1 十大學習資源清單與官方直連彙整
        </h3>
        <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400">
          全網蒐集消防署官方電子書教材、全國法規資料庫官方條文、歷屆替代役學長 Google Drive 神手冊、Dcard 真題分享與阿摩線上題庫，一鍵點擊直連。
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        ${list.map(res => `
          <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between space-y-3 shadow-sm border border-slate-200 dark:border-slate-800 hover:border-teal-500 transition">
            <div class="space-y-2">
              <div class="flex items-center justify-between gap-2 flex-wrap">
                <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-teal-100 dark:bg-teal-950 text-teal-800 dark:text-teal-300">
                  ${res.category}
                </span>
                <span class="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                  ${res.type}
                </span>
              </div>
              <h4 class="text-base font-bold text-slate-900 dark:text-white">
                ${res.name}
              </h4>
              <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                ${res.desc}
              </p>
            </div>

            <div class="pt-2">
              <a href="${res.url}" target="_blank" class="w-full py-2.5 px-4 bg-teal-600 hover:bg-teal-700 text-white rounded-xl text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm">
                <span>前往資源連結</span>
                <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
              </a>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

