# -*- coding: utf-8 -*-
"""
Update js/app.js to implement:
1. 4-tab top-level navigation: Home, Recruit, EMT-1, Checklist
2. Unified recruit sub-navigation architecture mirroring EMT-1
3. Detailed Homepage & Project Origin guide in renderHomeSection()
4. In-depth EMT-1 legal articles in renderEmtStudy()
"""

with open("js/app.js", "r", encoding="utf-8") as f:
    content = f.read()

# 1. New Top Section
new_top_section = '''/**
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

        <!-- Module Card 4: 標楷體題庫 PDF -->
        <div class="glass-panel p-5 sm:p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500 transition shadow-sm group border border-cyan-500/20">
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="p-2.5 bg-cyan-100 dark:bg-cyan-950 text-cyan-600 dark:text-cyan-400 rounded-xl group-hover:scale-110 transition">
                <i data-lucide="file-down" class="w-6 h-6"></i>
              </span>
              <span class="text-xs px-2.5 py-1 bg-cyan-500/10 text-cyan-600 dark:text-cyan-400 font-bold rounded-full">離線紙本</span>
            </div>
            <h3 class="text-lg font-bold text-slate-900 dark:text-white">📄 標楷體題庫 PDF</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              雙欄 A4 公文標楷體排版，答案粗體高亮、法條解析與超連結完備。新訓題庫 (30頁) + EMT-1 題庫 (23頁)，可直接下載帶入成功嶺自修。
            </p>
          </div>
          <div class="mt-5 grid grid-cols-2 gap-2">
            <a href="pdf/替代役新訓題庫_全集彙編_標楷體版.pdf" download class="py-2 px-2 bg-emerald-600 hover:bg-emerald-700 text-white text-[11px] font-bold rounded-xl transition text-center shadow-sm">
              新訓 PDF
            </a>
            <a href="pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf" download class="py-2 px-2 bg-teal-600 hover:bg-teal-700 text-white text-[11px] font-bold rounded-xl transition text-center shadow-sm">
              EMT-1 PDF
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
'''

# Find the start of QUIZ ENGINE
quiz_engine_marker = "/* ==========================================================================\n   QUIZ ENGINE"
pos_quiz_engine = content.find(quiz_engine_marker)
if pos_quiz_engine == -1:
    raise Exception("Could not find QUIZ ENGINE marker")

# Replace lines 1 to QUIZ ENGINE
remaining_content = content[pos_quiz_engine:]

# 2. Enhanced renderEmtStudy() implementation
enhanced_render_emt_study = '''function renderEmtStudy() {
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
}'''

# Find the start and end of existing renderEmtStudy in remaining_content
start_emt_study = remaining_content.find("function renderEmtStudy() {")
end_emt_study = remaining_content.find("/* ==========================================================================\n   EMT-1 TEN+ LEARNING RESOURCES")

if start_emt_study == -1 or end_emt_study == -1:
    raise Exception(f"Could not find renderEmtStudy boundaries ({start_emt_study}, {end_emt_study})")

updated_remaining = remaining_content[:start_emt_study] + enhanced_render_emt_study + "\n\n" + remaining_content[end_emt_study:]

final_content = new_top_section + "\n" + updated_remaining

with open("js/app.js", "w", encoding="utf-8") as f:
    f.write(final_content)

print("Successfully updated js/app.js with 4-tab architecture and enhanced EMT-1 study!")
