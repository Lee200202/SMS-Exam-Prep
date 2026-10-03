/**
 * 成功嶺新訓備考：單頁應用主程式（無外部相依）
 *
 * 結構：資料載入 → 路由 → 各頁面的 view* 函式回傳 HTML 字串 → 事件以 data-action 委派。
 * 新訓與 EMT-1 共用同一套測驗與題庫程式，差異只在 BANKS 的設定。
 */
(function () {
  'use strict';

  /* ------------------------------------------------------------ 工具 */
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ESC[c]);
  // 講義文字只允許 **粗體** 與換行，其餘一律跳脫
  const rich = (s) => esc(s)
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/&lt;br\s*\/?&gt;|\n/g, '<br>');
  const safeUrl = (u) => (/^https?:\/\//i.test(u || '') ? u : '');
  const ext = (url, label) => (safeUrl(url)
    ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(label)}<span class="sr-only">（另開新視窗）</span></a>`
    : esc(label));
  const reEsc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const hl = (text, kw) => {
    const safe = esc(text);
    return kw ? safe.replace(new RegExp(reEsc(esc(kw)), 'gi'), '<mark>$&</mark>') : safe;
  };
  const shuffle = (arr) => {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };
  const clock = (ms) => {
    const total = Math.max(0, Math.round(ms / 1000));
    return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
  };

  const store = {
    get(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw == null ? fallback : JSON.parse(raw);
      } catch (e) {
        return fallback; // 壞資料或無法讀取時退回預設值
      }
    },
    set(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch (e) {
        toast('瀏覽器無法儲存紀錄（可能是無痕模式或空間已滿）。');
      }
    },
    del(key) {
      try { localStorage.removeItem(key); } catch (e) { /* 無法存取時略過 */ }
    },
  };
  const loadSet = (key) => {
    const v = store.get(key, []);
    return new Set(Array.isArray(v) ? v.filter((x) => typeof x === 'string') : []);
  };
  const saveSet = (key, set) => store.set(key, Array.from(set));

  let toastTimer = null;
  function toast(message) {
    const el = $('#toast');
    if (!el) return;
    el.textContent = message;
    el.classList.add('is-show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('is-show'), 3200);
  }

  /** 自訂確認對話框。actions 的第一個是安全選項（按 Esc 等同選它）。 */
  function ask({ title, body, actions }) {
    return new Promise((resolve) => {
      const dlg = $('#dialog');
      if (!dlg || typeof dlg.showModal !== 'function') {
        resolve(window.confirm(`${title}\n\n${body}`) ? actions[actions.length - 1].value : actions[0].value);
        return;
      }
      $('#dialog-title').textContent = title;
      $('#dialog-body').innerHTML = `<p>${esc(body)}</p>`;
      $('#dialog-actions').innerHTML = actions.map((a, i) =>
        `<button type="button" class="btn ${a.kind ? 'btn-' + a.kind : ''}" data-dialog="${i}">${esc(a.label)}</button>`).join('');
      const done = (value) => {
        dlg.removeEventListener('cancel', onCancel);
        dlg.removeEventListener('click', onClick);
        if (dlg.open) dlg.close();
        resolve(value);
      };
      const onCancel = (e) => { e.preventDefault(); done(actions[0].value); };
      const onClick = (e) => {
        const btn = e.target.closest('[data-dialog]');
        if (btn) done(actions[Number(btn.dataset.dialog)].value);
      };
      dlg.addEventListener('cancel', onCancel);
      dlg.addEventListener('click', onClick);
      dlg.showModal();
      $('[data-dialog]', dlg).focus();
    });
  }

  /* ------------------------------------------------------------ 設定與狀態 */
  const PDFS = {
    recruit: ['pdf/替代役新訓題庫_全集彙編_標楷體版.pdf', '新訓學科題庫 PDF'],
    emt: ['pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf', 'EMT-1 題庫 PDF'],
    checklist: ['pdf/成功嶺替代役新訓_必備用品建議檢核表_標楷體版.pdf', '用品清單 PDF'],
  };
  const pdfLink = (key, cls = 'btn') =>
    `<a class="${cls}" href="${encodeURI(PDFS[key][0])}" download>下載${PDFS[key][1]}</a>`;

  const BANKS = {
    recruit: {
      id: 'recruit', label: '新訓學科', pass: 60, mockCount: 50, mockMinutes: 40, quickCount: 20,
      mistakesKey: 'sms_mistakes', bookmarksKey: 'sms_bookmarks', sessionKey: 'sms_session_v2_recruit',
      quizRoute: 'quiz', bankRoute: 'bank',
      cats: {
        regulations: '替代役實施條例', rights: '權益、撫卹與保險', management: '訓練服勤與獎懲',
        volunteer: '志願服務法', shooting: '射擊與國防',
      },
    },
    emt: {
      id: 'emt', label: 'EMT-1', pass: 70, mockCount: 50, mockMinutes: 50, quickCount: 20,
      mistakesKey: 'sms_emt_mistakes', bookmarksKey: 'sms_emt_bookmarks', sessionKey: 'sms_session_v2_emt',
      quizRoute: 'emt', bankRoute: 'emt-bank',
      cats: {},
    },
  };

  const ROUTES = {
    home: ['home'],
    quiz: ['recruit', 'quiz'], bank: ['recruit', 'bank'], regulations: ['recruit', 'regulations'],
    volunteer: ['recruit', 'volunteer'], rights: ['recruit', 'rights'], shooting: ['recruit', 'shooting'],
    laws: ['recruit', 'laws'],
    emt: ['emt', 'quiz'], 'emt-bank': ['emt', 'bank'], 'emt-study': ['emt', 'study'],
    'emt-laws': ['emt', 'laws'], 'emt-resources': ['emt', 'resources'],
    checklist: ['checklist'],
  };
  const ALIASES = { '': 'home', recruit: 'quiz', 'emt-quiz': 'emt' };
  const SUBNAV = {
    recruit: [['quiz', '測驗'], ['bank', '題庫'], ['regulations', '條例重點'], ['volunteer', '志願服務'],
      ['rights', '權益服勤'], ['shooting', '射擊'], ['laws', '法規全文']],
    emt: [['emt', '測驗'], ['emt-bank', '題庫'], ['emt-study', '重點整理'], ['emt-laws', '法規全文'],
      ['emt-resources', '學習資源']],
  };
  const SECTION_HEAD = {
    recruit: ['新訓學科', '替代役基礎訓練學科測驗的題庫、重點整理與法規全文。'],
    emt: ['EMT-1 初級救護技術員', '學科題庫、重點整理與相關法規。及格標準為 70 分。'],
  };

  const state = {
    route: 'home',
    study: {},
    emtStudy: {},
    meta: {},
    laws: null,
    banks: {},
    checked: new Set(),
    checklistOnlyTodo: false,
    paletteOpen: false,
    focusAfterRender: null,
  };

  function normalize(q) {
    const isTF = q.type === 'true_false';
    return {
      id: q.id,
      type: isTF ? 'tf' : 'mc',
      cat: q.category,
      text: q.question,
      options: isTF ? ['正確', '錯誤'] : q.options.map((o) => String(o).replace(/^\s*[(（][A-D][)）]\s*/, '').replace(/。\s*$/, '')),
      answer: isTF ? (q.answer === 'O' ? 0 : 1) : q.answer,
      explanation: q.explanation || '',
      tag: q.exam_tag || '',
      source: q.source || '',
      sourceUrl: q.source_url || '',
      sourceKind: q.source_kind || (/law\.moj\.gov\.tw/.test(q.source_url || '') ? 'law' : 'other'),
      outdated: q.status === 'outdated',
      statusNote: q.status_note || '',
      revised: q.revised || '',
    };
  }

  function setupBank(id, raw) {
    const cfg = BANKS[id];
    const questions = (raw.questions || []).map(normalize);
    if (id === 'emt') {
      (raw.questions || []).forEach((q) => { cfg.cats[q.category] = q.category_name || q.category; });
    }
    const byId = new Map(questions.map((q) => [q.id, q]));
    const keep = (set) => new Set(Array.from(set).filter((qid) => byId.has(qid)));
    const bank = {
      cfg, questions, byId,
      pool: questions.filter((q) => !q.outdated),
      mistakes: keep(loadSet(cfg.mistakesKey)),
      bookmarks: keep(loadSet(cfg.bookmarksKey)),
      session: null,
      filter: { q: '', type: 'all', cat: 'all', scope: 'all', hide: false, limit: 20 },
      revealed: new Set(),
      resultFilter: 'all',
    };
    bank.session = restoreSession(bank);
    state.banks[id] = bank;
  }

  async function loadData() {
    if (!(window.APP_QUESTIONS && window.APP_STUDY_DATA && window.APP_EMT_QUESTIONS && window.APP_EMT_STUDY_DATA)) {
      // 資料包不存在時改抓個別 JSON（需以 http 伺服器開啟）
      const names = ['questions', 'study_data', 'emt_questions', 'emt_study_data'];
      const [q, s, eq, es] = await Promise.all(names.map((n) => fetch(`data/${n}.json`).then((r) => {
        if (!r.ok) throw new Error(`${n}.json ${r.status}`);
        return r.json();
      })));
      window.APP_QUESTIONS = q; window.APP_STUDY_DATA = s; window.APP_EMT_QUESTIONS = eq; window.APP_EMT_STUDY_DATA = es;
    }
    state.study = window.APP_STUDY_DATA;
    state.emtStudy = window.APP_EMT_STUDY_DATA;
    state.meta = { updatedAt: window.APP_QUESTIONS.updatedAt || '' };
    setupBank('recruit', window.APP_QUESTIONS);
    setupBank('emt', window.APP_EMT_QUESTIONS);
    state.checked = loadSet('sms_checklist');
  }

  let lawsPromise = null;
  function loadLaws() {
    if (state.laws) return Promise.resolve(state.laws);
    if (!lawsPromise) {
      lawsPromise = new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = 'data/laws_bundle.js?v=20261003';
        script.onload = () => (window.APP_LAWS ? resolve(window.APP_LAWS) : reject(new Error('laws bundle empty')));
        script.onerror = () => reject(new Error('laws bundle failed'));
        document.head.appendChild(script);
      }).then((laws) => { state.laws = laws; return laws; })
        .catch((err) => { lawsPromise = null; throw err; });
    }
    return lawsPromise;
  }

  /* ------------------------------------------------------------ 測驗狀態機 */
  // session.status：active（作答中）→ paused（暫停，可恢復）→ done（已交卷，顯示結果）
  const NO_SHUFFLE = /以上|上述|前述|皆是|皆非|皆可|皆對|皆錯|[(（]?[A-DＡ-Ｄ][)）]|[1-4１-４]\s*[、及與和]\s*[1-4１-４]/;

  function restoreSession(bank) {
    const s = store.get(bank.cfg.sessionKey, null);
    const valid = s && s.v === 2 && Array.isArray(s.items) && s.items.length > 0 &&
      s.items.every((it) => bank.byId.has(it.id) && Array.isArray(it.order) &&
        it.order.length === bank.byId.get(it.id).options.length) &&
      s.answers && typeof s.answers === 'object' && ['active', 'paused', 'done'].includes(s.status);
    if (!valid) {
      if (s) store.del(bank.cfg.sessionKey);
      return null;
    }
    if (s.status === 'active') {
      // 上次關閉或重新整理時仍在作答：以最後一次記錄的時間點視為暫停
      s.elapsedMs += Math.max(0, (s.lastSeen || s.resumedAt) - s.resumedAt);
      s.status = 'paused';
    }
    s.current = Math.min(Math.max(0, s.current | 0), s.items.length - 1);
    return s;
  }

  function saveSession(bank) {
    if (bank.session) store.set(bank.cfg.sessionKey, bank.session);
    else store.del(bank.cfg.sessionKey);
  }

  const elapsed = (s) => s.elapsedMs + (s.status === 'active' ? Date.now() - s.resumedAt : 0);
  const timeLeft = (s) => (s.totalMs ? s.totalMs - elapsed(s) : Infinity);

  function createSession(bank, mode, ids, opts) {
    const items = ids.map((id) => {
      const q = bank.byId.get(id);
      const base = q.options.map((_, i) => i);
      const canShuffle = opts.shuffleOptions && q.type === 'mc' && !q.options.some((o) => NO_SHUFFLE.test(o));
      return { id, order: canShuffle ? shuffle(base) : base };
    });
    bank.session = {
      v: 2, bank: bank.cfg.id, mode, label: opts.label, items, answers: {}, flags: [], current: 0,
      instant: !!opts.instant, totalMs: opts.minutes ? opts.minutes * 60000 : 0,
      elapsedMs: 0, resumedAt: Date.now(), lastSeen: Date.now(), status: 'active', result: null,
    };
    bank.resultFilter = 'all';
    saveSession(bank);
  }

  async function startQuiz(bank, mode, extra = {}) {
    const cfg = bank.cfg;
    const shuffleOptions = !($('#opt-shuffle') && !$('#opt-shuffle').checked);
    let ids = [];
    let opts = { shuffleOptions };
    if (mode === 'mock') {
      ids = shuffle(bank.pool).slice(0, cfg.mockCount).map((q) => q.id);
      opts = { ...opts, label: '模擬考', minutes: cfg.mockMinutes, instant: false };
    } else if (mode === 'quick') {
      ids = shuffle(bank.pool).slice(0, cfg.quickCount).map((q) => q.id);
      opts = { ...opts, label: '快速練習', instant: true };
    } else if (mode === 'category') {
      const cat = $('#opt-cat') ? $('#opt-cat').value : Object.keys(cfg.cats)[0];
      const count = Number($('#opt-count') ? $('#opt-count').value : 20) || Infinity;
      ids = shuffle(bank.pool.filter((q) => q.cat === cat)).slice(0, count).map((q) => q.id);
      opts = { ...opts, label: `章節練習：${cfg.cats[cat]}`, instant: true };
    } else if (mode === 'mistakes') {
      ids = shuffle(bank.pool.filter((q) => bank.mistakes.has(q.id))).slice(0, 50).map((q) => q.id);
      opts = { ...opts, label: '錯題重測', instant: true };
    } else if (mode === 'retry') {
      ids = shuffle(extra.ids || []);
      opts = { ...opts, label: '本次錯題重測', instant: true };
    }
    if (!ids.length) {
      toast(mode === 'mistakes' ? '錯題本目前是空的。' : '沒有可以出題的題目。');
      return;
    }
    if (bank.session && bank.session.status === 'paused') {
      const ok = await ask({
        title: '放棄未完成的測驗？',
        body: `你有一份暫停中的「${bank.session.label}」。開始新的測驗會放棄它的作答紀錄。`,
        actions: [{ label: '取消', value: false }, { label: '放棄並開始新的', value: true, kind: 'danger' }],
      });
      if (!ok) return;
    }
    createSession(bank, mode === 'retry' ? 'mistakes' : mode, ids, opts);
    state.focusAfterRender = '#question-text';
    render();
    window.scrollTo(0, 0);
  }

  function pauseSession(bank, silent) {
    const s = bank.session;
    if (!s || s.status !== 'active') return;
    s.elapsedMs = elapsed(s);
    s.status = 'paused';
    saveSession(bank);
    if (!silent) toast('測驗已暫停，回到測驗頁可以繼續。');
  }

  function resumeSession(bank) {
    const s = bank.session;
    if (!s || s.status !== 'paused') return;
    s.status = 'active';
    s.resumedAt = Date.now();
    s.lastSeen = Date.now();
    saveSession(bank);
    if (timeLeft(s) <= 0) { finishSession(bank, 'timeout'); return; }
    state.focusAfterRender = '#question-text';
    render();
  }

  function answerQuestion(bank, optIndex) {
    const s = bank.session;
    if (!s || s.status !== 'active') return;
    const i = s.current;
    const q = bank.byId.get(s.items[i].id);
    if (!(optIndex >= 0 && optIndex < q.options.length)) return;
    if (s.instant && s.answers[i] !== undefined) return; // 即時回饋模式作答後鎖定
    s.answers[i] = optIndex;
    if (s.instant) {
      // 這題的答案已確定，立刻更新錯題本
      if (optIndex === q.answer) {
        if (s.mode === 'mistakes') bank.mistakes.delete(q.id);
      } else {
        bank.mistakes.add(q.id);
      }
      saveSet(bank.cfg.mistakesKey, bank.mistakes);
      state.focusAfterRender = '#feedback';
    } else {
      state.focusAfterRender = `.option[data-opt="${optIndex}"]`;
    }
    saveSession(bank);
    render();
  }

  function finishSession(bank, reason) {
    const s = bank.session;
    if (!s || s.status === 'done') return;
    const usedMs = Math.min(elapsed(s), s.totalMs || Infinity);
    const byCat = {};
    let correct = 0, wrong = 0, blank = 0;
    s.items.forEach((it, i) => {
      const q = bank.byId.get(it.id);
      const chosen = s.answers[i];
      const cat = byCat[q.cat] || (byCat[q.cat] = { correct: 0, total: 0 });
      cat.total++;
      if (chosen === undefined) {
        blank++; // 未作答：不計分，也不寫入錯題本
      } else if (chosen === q.answer) {
        correct++; cat.correct++;
        if (s.mode === 'mistakes') bank.mistakes.delete(q.id);
      } else {
        wrong++;
        bank.mistakes.add(q.id);
      }
    });
    saveSet(bank.cfg.mistakesKey, bank.mistakes);
    const score = Math.round((correct / s.items.length) * 100);
    s.result = { correct, wrong, blank, score, passed: score >= bank.cfg.pass, usedMs, reason, byCat };
    s.status = 'done';
    s.elapsedMs = usedMs;
    bank.resultFilter = wrong ? 'bad' : 'all';
    saveSession(bank);
    state.focusAfterRender = '#result-title';
    render();
    window.scrollTo(0, 0);
    if (reason === 'timeout') toast('時間到，已自動交卷。');
  }

  function activeBank() {
    const [section, view] = ROUTES[state.route];
    return view === 'quiz' ? state.banks[section] : null;
  }

  function tick() {
    const bank = activeBank();
    const s = bank && bank.session;
    if (!s || s.status !== 'active') return;
    s.lastSeen = Date.now();
    if (!s.totalMs) return;
    const left = timeLeft(s);
    if (left <= 0) { finishSession(bank, 'timeout'); return; }
    const el = $('#quiz-timer');
    if (el) {
      el.textContent = clock(left);
      el.classList.toggle('is-low', left < 5 * 60000);
    }
  }

  /* ------------------------------------------------------------ 共用片段 */
  const typeLabel = (q) => (q.type === 'tf' ? '是非' : '選擇');
  const starIcon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1 5.8L12 16.9l-5.2 2.7 1-5.8L3.5 9.7l5.9-.8z"/></svg>';

  function starButton(bank, q) {
    const on = bank.bookmarks.has(q.id);
    return `<button type="button" class="star-btn star" data-action="bookmark" data-bank="${bank.cfg.id}" data-id="${esc(q.id)}" aria-pressed="${on}" aria-label="${on ? '取消收藏' : '收藏這一題'}">${starIcon}</button>`;
  }

  function sourceLine(q) {
    if (!q.source && !q.sourceUrl) return '';
    const label = q.sourceKind === 'law' ? '參考法規' : q.sourceKind === 'experience' ? '經驗來源' : '參考資料';
    return `<p class="small muted">${label}：${ext(q.sourceUrl, q.source || q.sourceUrl)}</p>`;
  }

  function explainBlock(q) {
    const parts = [];
    if (q.explanation) parts.push(`<p>${rich(q.explanation)}</p>`);
    else parts.push('<p class="muted">這一題目前沒有解析。</p>');
    if (q.revised) parts.push(`<p class="small"><span class="chip chip-amber">已依現行法規改寫</span> ${esc(q.revised)}</p>`);
    parts.push(sourceLine(q));
    return parts.join('');
  }

  /** 列出所有選項並標示正解；chosen 為使用者選的原始索引（可省略）。 */
  function answerList(q, order, chosen, kw) {
    return `<ul class="answers">${order.map((orig, pos) => {
      const key = q.type === 'tf' ? (orig === 0 ? '○' : '✕') : 'ABCD'[pos];
      const isAnswer = orig === q.answer;
      const marks = [];
      if (isAnswer) marks.push('正確答案');
      if (chosen === orig) marks.push('你的答案');
      return `<li class="${isAnswer ? 'is-answer' : ''}"><span aria-hidden="true">${key}</span><span>${hl(q.options[orig], kw)}</span>${marks.length ? `<span class="tick">${marks.join('・')}</span>` : ''}</li>`;
    }).join('')}</ul>`;
  }

  const tagText = (q) => {
    const tags = (q.tag.match(/【(.+?)】/g) || []).map((t) => t.slice(1, -1).replace(/考$/, ''));
    return tags.length ? `<span class="small muted">出現梯次：${esc(tags.join('、'))}</span>` : '';
  };

  /* ------------------------------------------------------------ 首頁 */
  function resumeBanner(bank) {
    const s = bank.session;
    if (!s || s.status !== 'paused') return '';
    const answered = Object.keys(s.answers).length;
    const time = s.totalMs ? `，剩餘 ${clock(timeLeft(s))}` : '';
    return `<div class="notice notice-warn" data-resume="${bank.cfg.id}">
      <p><strong>${esc(bank.cfg.label)}有一份未完成的「${esc(s.label)}」</strong>：已作答 ${answered} / ${s.items.length} 題${time}。</p>
      <div class="row">
        <button type="button" class="btn btn-primary" data-action="quiz-resume" data-bank="${bank.cfg.id}">繼續作答</button>
        <button type="button" class="btn btn-danger" data-action="quiz-discard" data-bank="${bank.cfg.id}">放棄這份測驗</button>
      </div>
    </div>`;
  }

  function viewHome() {
    const r = state.banks.recruit, e = state.banks.emt;
    const tf = r.questions.filter((q) => q.type === 'tf').length;
    return `
    <section class="hero stack-sm">
      <h1>替代役新訓學科與 EMT-1 題庫練習</h1>
      <p>歷屆役男整理的考古題，可以模擬考、快速練習、查題與複習錯題，並附官方法規全文。這不是官方網站。</p>
      <div class="row">
        <a class="btn btn-primary btn-lg" href="#quiz">開始新訓學科測驗</a>
        <a class="btn btn-primary btn-lg" href="#emt">開始 EMT-1 測驗</a>
      </div>
      <p class="small muted" id="home-stats">新訓學科 ${r.questions.length} 題（是非 ${tf}、選擇 ${r.questions.length - tf}）・EMT-1 ${e.questions.length} 題・資料整理日 ${esc(state.meta.updatedAt)}</p>
    </section>
    <div class="stack">
      ${resumeBanner(r)}${resumeBanner(e)}
      <section aria-labelledby="home-tasks">
        <h2 id="home-tasks">你想做什麼？</h2>
        <ul class="task-list">
          <li><a href="#bank"><b>查新訓題庫</b><span>用關鍵字、題型、章節找題目</span></a></li>
          <li><a href="#emt-bank"><b>查 EMT-1 題庫</b><span>依章節瀏覽，附解析</span></a></li>
          <li><a href="#regulations"><b>看重點整理</b><span>條例、志願服務、權益、射擊</span></a></li>
          <li><a href="#laws"><b>讀法規全文</b><span>全國法規資料庫的現行條文</span></a></li>
          <li><a href="#emt-study"><b>看 EMT-1 重點</b><span>生命徵象、CPR、檢傷分類</span></a></li>
          <li><a href="#checklist"><b>整理入營用品</b><span>可勾選的清單與管制提醒</span></a></li>
        </ul>
      </section>
      <section class="card" aria-labelledby="home-progress">
        <h2 id="home-progress">你的紀錄</h2>
        <div class="stat-row">
          <div class="stat"><b>${r.mistakes.size}</b><span>新訓錯題</span></div>
          <div class="stat"><b>${r.bookmarks.size}</b><span>新訓收藏</span></div>
          <div class="stat"><b>${e.mistakes.size}</b><span>EMT-1 錯題</span></div>
          <div class="stat"><b>${e.bookmarks.size}</b><span>EMT-1 收藏</span></div>
        </div>
        <p class="small muted" style="margin-top:16px">紀錄只存在這台裝置的瀏覽器裡，不會上傳。</p>
        <button type="button" class="btn btn-danger" data-action="clear-all">清除這台裝置上的所有紀錄</button>
      </section>
      <section class="card" aria-labelledby="home-pdf">
        <h2 id="home-pdf">下載 PDF</h2>
        <p class="muted">入營後手機會被管制，可以先印出來。</p>
        <div class="row">${pdfLink('recruit')}${pdfLink('emt')}${pdfLink('checklist')}</div>
      </section>
      <details>
        <summary>資料來源與使用限制</summary>
        <div class="details-body read">
          <p>題目來自歷屆役男公開分享的考古題與筆記，不是主管機關公布的題庫。法規條文直接取自全國法規資料庫，取得日期標示在「法規全文」頁。</p>
          <p>考古題可能依當時的舊法出題。與現行法規不一致的題目，已依現行條文改寫並在題目上標示；尚未逐題核對條號的題目，來源只會標示參考的法規名稱。</p>
          <p>用品清單、成績配分與薪給等內容屬於歷屆經驗，實際以徵集令、當梯次營區通知與主管機關公告為準。</p>
        </div>
      </details>
    </div>`;
  }

  /* ------------------------------------------------------------ 測驗畫面 */
  function viewQuizSetup(bank) {
    const cfg = bank.cfg;
    const catOptions = Object.entries(cfg.cats).map(([id, name]) =>
      `<option value="${esc(id)}">${esc(name)}（${bank.pool.filter((q) => q.cat === id).length} 題）</option>`).join('');
    return `
    <div class="stack">
      ${resumeBanner(bank)}
      <div class="mode-list">
        <section class="card mode">
          <h2>模擬考</h2>
          <p>隨機 ${cfg.mockCount} 題，限時 ${cfg.mockMinutes} 分鐘，${cfg.pass} 分及格。交卷後才看答案。</p>
          <button type="button" class="btn btn-primary" data-action="quiz-start" data-mode="mock">開始模擬考</button>
        </section>
        <section class="card mode">
          <h2>快速練習</h2>
          <p>隨機 ${cfg.quickCount} 題，不計時。每答一題立刻看對錯與解析。</p>
          <button type="button" class="btn btn-primary" data-action="quiz-start" data-mode="quick">開始快速練習</button>
        </section>
        <section class="card mode">
          <h2>章節練習</h2>
          <div class="field"><label for="opt-cat">章節</label><select id="opt-cat">${catOptions}</select></div>
          <div class="field"><label for="opt-count">題數</label>
            <select id="opt-count"><option value="10">10 題</option><option value="20" selected>20 題</option><option value="0">全部</option></select></div>
          <button type="button" class="btn btn-primary" data-action="quiz-start" data-mode="category">開始章節練習</button>
        </section>
        <section class="card mode">
          <h2>錯題重測</h2>
          <p>錯題本目前有 <strong id="mistake-count">${bank.mistakes.size}</strong> 題。重測答對的題目會從錯題本移除。</p>
          <div class="row">
            <button type="button" class="btn btn-primary" data-action="quiz-start" data-mode="mistakes" ${bank.mistakes.size ? '' : 'disabled'}>重測錯題</button>
            <a class="btn" href="#${cfg.bankRoute}" data-action="show-mistakes">在題庫查看</a>
            ${bank.mistakes.size ? '<button type="button" class="btn btn-danger" data-action="clear-mistakes">清空錯題本</button>' : ''}
          </div>
        </section>
      </div>
      <div class="card stack-sm">
        <label class="check"><input type="checkbox" id="opt-shuffle" checked> 選擇題的選項隨機排列</label>
        <p class="small muted">含「以上皆是」這類選項的題目不會打亂。未作答的題目不計分，也不會加入錯題本。模擬考計時以實際時間計算，切到其他 App 時不會停；離開測驗頁或重新整理會自動暫停，可以回來繼續。</p>
        <div class="row">${pdfLink(cfg.id)}</div>
      </div>
    </div>`;
  }

  function viewQuizActive(bank) {
    const s = bank.session;
    const n = s.items.length, i = s.current;
    const item = s.items[i];
    const q = bank.byId.get(item.id);
    const chosen = s.answers[i];
    const locked = s.instant && chosen !== undefined;
    const answered = Object.keys(s.answers).length;
    const flagged = s.flags.includes(i);

    const options = item.order.map((orig, pos) => {
      const key = q.type === 'tf' ? (orig === 0 ? '○' : '✕') : 'ABCD'[pos];
      let cls = '', mark = '';
      if (locked) {
        if (orig === q.answer) { cls = ' is-correct'; mark = chosen === orig ? '✓ 你答對了' : '✓ 正確答案'; }
        else if (orig === chosen) { cls = ' is-wrong'; mark = '✕ 你的答案'; }
      }
      return `<li><button type="button" class="option${cls}" role="radio" aria-checked="${chosen === orig}" data-action="quiz-answer" data-opt="${orig}" ${locked ? 'disabled' : ''}>
        <span class="key" aria-hidden="true">${key}</span><span>${esc(q.options[orig])}</span>${mark ? `<span class="mark">${mark}</span>` : ''}</button></li>`;
    }).join('');

    let feedback = '';
    if (locked) {
      const ok = chosen === q.answer;
      const pos = item.order.indexOf(q.answer);
      const answerText = q.type === 'tf' ? q.options[q.answer] : `${'ABCD'[pos]}．${q.options[q.answer]}`;
      feedback = `<section class="feedback ${ok ? 'is-ok' : 'is-bad'}" id="feedback" tabindex="-1">
        <h3>${ok ? '✓ 答對了' : `✕ 答錯了，正確答案是「${esc(answerText)}」`}</h3>
        ${explainBlock(q)}
      </section>`;
    }

    const palette = s.items.map((it, idx) => {
      const a = s.answers[idx];
      let cls = '', label = '未作答';
      if (a !== undefined) {
        if (s.instant) {
          const ok = a === bank.byId.get(it.id).answer;
          cls = ok ? 'is-ok' : 'is-bad'; label = ok ? '答對' : '答錯';
        } else { cls = 'is-answered'; label = '已作答'; }
      }
      const flag = s.flags.includes(idx);
      return `<button type="button" class="${cls}${flag ? ' is-flag' : ''}" data-action="quiz-goto" data-index="${idx}" ${idx === i ? 'aria-current="true"' : ''} aria-label="第 ${idx + 1} 題，${label}${flag ? '，已標記' : ''}">${idx + 1}</button>`;
    }).join('');

    const last = i === n - 1;
    return `
    <div class="quiz" data-bank="${bank.cfg.id}">
      <div class="quiz-bar">
        <div><strong>${esc(bank.cfg.label)}・${esc(s.label)}</strong><br><span class="small muted" id="quiz-progress">第 ${i + 1} / ${n} 題・已作答 ${answered} 題</span></div>
        <div class="row">
          ${s.totalMs ? `<span class="timer" id="quiz-timer" role="timer" aria-label="剩餘時間">${clock(timeLeft(s))}</span>` : ''}
          <button type="button" class="btn" data-action="quiz-pause">暫停</button>
          <button type="button" class="btn btn-primary" data-action="quiz-submit">交卷</button>
        </div>
      </div>
      <progress max="${n}" value="${answered}" aria-label="作答進度"></progress>
      <article class="card question">
        <div class="question-meta">
          <span class="chip chip-primary">${typeLabel(q)}</span>
          <span class="chip">${esc(bank.cfg.cats[q.cat] || q.cat)}</span>
          ${flagged ? '<span class="chip chip-amber">已標記</span>' : ''}
        </div>
        <h1 class="question-text" id="question-text" tabindex="-1">${esc(q.text)}</h1>
        <ul class="options" role="radiogroup" aria-labelledby="question-text">${options}</ul>
        ${feedback}
      </article>
      <div class="quiz-nav">
        <button type="button" class="btn" data-action="quiz-prev" ${i === 0 ? 'disabled' : ''}>上一題</button>
        <button type="button" class="btn" data-action="quiz-flag" aria-pressed="${flagged}">${flagged ? '取消標記' : '標記這題'}</button>
        ${last
          ? '<button type="button" class="btn btn-primary" data-action="quiz-submit">交卷</button>'
          : `<button type="button" class="btn ${locked || (!s.instant && chosen !== undefined) ? 'btn-primary' : ''}" data-action="quiz-next">下一題</button>`}
      </div>
      <details id="palette" style="margin-top:24px" ${state.paletteOpen ? 'open' : ''}>
        <summary>答題卡（共 ${n} 題，未作答 ${n - answered} 題）</summary>
        <div class="details-body">
          <div class="palette">${palette}</div>
          <p class="legend">${s.instant ? '綠色＝答對　紅色＝答錯' : '青色＝已作答'}　白色＝未作答　橘點＝已標記</p>
        </div>
      </details>
      <p class="small muted" style="margin-top:16px">鍵盤操作：數字 1–4 選答，← → 換題。</p>
    </div>`;
  }

  function viewQuizResult(bank) {
    const s = bank.session, r = s.result, cfg = bank.cfg;
    const n = s.items.length;
    const rows = s.items.map((it, i) => {
      const q = bank.byId.get(it.id);
      const chosen = s.answers[i];
      return { q, it, i, chosen, kind: chosen === undefined ? 'blank' : chosen === q.answer ? 'ok' : 'bad' };
    });
    const f = bank.resultFilter;
    const shown = rows.filter((row) => f === 'all' || row.kind === f);
    const KIND = { ok: ['答對', 'chip-ok'], bad: ['答錯', 'chip-red'], blank: ['未作答', 'chip-amber'] };
    const filterBtn = (id, label, count) =>
      `<button type="button" class="btn ${f === id ? 'btn-primary' : ''}" data-action="result-filter" data-filter="${id}" aria-pressed="${f === id}">${label}（${count}）</button>`;
    const cats = Object.entries(r.byCat).map(([cat, v]) => ({ name: cfg.cats[cat] || cat, ...v, rate: Math.round((v.correct / v.total) * 100) }))
      .sort((a, b) => a.rate - b.rate);
    const wrongIds = rows.filter((row) => row.kind === 'bad').map((row) => row.q.id);

    return `
    <div class="stack">
      <section class="card stack-sm">
        <h1 id="result-title" tabindex="-1">${esc(cfg.label)}・${esc(s.label)}結果</h1>
        ${r.reason === 'timeout' ? '<p class="notice notice-warn">時間到，系統已自動交卷。</p>' : ''}
        <div class="score">
          <b>${r.score}</b><span>分（滿分 100）</span>
          <span class="chip ${r.passed ? 'chip-ok' : 'chip-red'}">${r.passed ? '✓ 達到及格標準' : '✕ 未達及格標準'}（${cfg.pass} 分）</span>
        </div>
        <div class="stat-row">
          <div class="stat"><b id="result-correct">${r.correct}</b><span>答對</span></div>
          <div class="stat"><b id="result-wrong">${r.wrong}</b><span>答錯</span></div>
          <div class="stat"><b id="result-blank">${r.blank}</b><span>未作答</span></div>
          <div class="stat"><b>${clock(r.usedMs)}</b><span>作答時間</span></div>
        </div>
        <p class="small muted">分數＝答對題數 ÷ 總題數（${n} 題）。答錯的 ${r.wrong} 題已加入錯題本；未作答的題目不會加入。</p>
        <div class="row">
          ${wrongIds.length ? '<button type="button" class="btn btn-primary" data-action="result-retry">重測這次答錯的題目</button>' : ''}
          <button type="button" class="btn" data-action="result-again">再測一次</button>
          <button type="button" class="btn" data-action="result-close">回測驗選單</button>
        </div>
      </section>
      <section aria-labelledby="result-cats">
        <h2 id="result-cats">各章節答對率</h2>
        <div class="table-wrap"><table>
          <thead><tr><th>章節</th><th>答對 / 題數</th><th>答對率</th></tr></thead>
          <tbody>${cats.map((c) => `<tr><th scope="row">${esc(c.name)}${c.rate < cfg.pass ? ' <span class="chip chip-amber">需加強</span>' : ''}</th><td>${c.correct} / ${c.total}</td>
            <td><div class="row" style="gap:8px;flex-wrap:nowrap"><span style="min-width:3em">${c.rate}%</span><div class="bar ${c.rate < cfg.pass ? 'is-weak' : ''}" style="flex:1"><i style="width:${c.rate}%"></i></div></div></td></tr>`).join('')}</tbody>
        </table></div>
      </section>
      <section aria-labelledby="result-review">
        <h2 id="result-review">逐題檢討</h2>
        <div class="row" style="margin-bottom:16px">
          ${filterBtn('all', '全部', n)}${filterBtn('bad', '答錯', r.wrong)}${filterBtn('blank', '未作答', r.blank)}${filterBtn('ok', '答對', r.correct)}
        </div>
        <div id="review-list">
        ${shown.length ? shown.map((row) => `
          <details ${row.kind === 'bad' ? 'open' : ''}>
            <summary><span class="chip ${KIND[row.kind][1]}">${KIND[row.kind][0]}</span><span>第 ${row.i + 1} 題　${esc(row.q.text)}</span></summary>
            <div class="details-body">
              <div class="row row-between"><span class="small muted">${esc(row.q.id)}・${typeLabel(row.q)}・${esc(cfg.cats[row.q.cat] || row.q.cat)}</span>${starButton(bank, row.q)}</div>
              ${answerList(row.q, row.it.order, row.chosen)}
              <div class="explain">${explainBlock(row.q)}</div>
            </div>
          </details>`).join('') : '<p class="empty">這個分類沒有題目。</p>'}
        </div>
      </section>
    </div>`;
  }

  /* ------------------------------------------------------------ 題庫 */
  function viewBank(bank) {
    const cfg = bank.cfg, f = bank.filter;
    const hasTypes = bank.questions.some((q) => q.type === 'tf');
    const sel = (value, current) => (value === current ? 'selected' : '');
    return `
    <div class="card">
      <div class="toolbar">
        <div class="field field-search ${hasTypes ? '' : 'field-wide'}">
          <label for="bank-search">搜尋題目、選項或解析</label>
          <input type="search" id="bank-search" data-bank="${cfg.id}" value="${esc(f.q)}" placeholder="例如：${cfg.id === 'emt' ? 'GCS、止血帶' : '陪產假、撫卹'}" autocomplete="off" enterkeyhint="search">
        </div>
        ${hasTypes ? `<div class="field field-select"><label for="bank-type">題型</label>
          <select id="bank-type" data-filter="type"><option value="all" ${sel('all', f.type)}>全部題型</option><option value="tf" ${sel('tf', f.type)}>是非題</option><option value="mc" ${sel('mc', f.type)}>選擇題</option></select></div>` : ''}
        <div class="field field-select">
          <label for="bank-cat">章節</label>
          <select id="bank-cat" data-filter="cat"><option value="all">全部章節</option>${Object.entries(cfg.cats).map(([id, name]) => `<option value="${esc(id)}" ${sel(id, f.cat)}>${esc(name)}</option>`).join('')}</select>
        </div>
        <div class="field field-select">
          <label for="bank-scope">範圍</label>
          <select id="bank-scope" data-filter="scope"><option value="all" ${sel('all', f.scope)}>全部題目</option><option value="bookmarks" ${sel('bookmarks', f.scope)}>我的收藏</option><option value="mistakes" ${sel('mistakes', f.scope)}>錯題本</option></select>
        </div>
        <div class="toolbar-checks">
          <label class="check"><input type="checkbox" id="bank-hide" ${f.hide ? 'checked' : ''}> 背題模式（先隱藏答案）</label>
          <button type="button" class="btn-link" data-action="bank-reset">清除篩選</button>
        </div>
      </div>
    </div>
    <p id="bank-count" class="muted" role="status" aria-live="polite" style="margin:16px 0"></p>
    <div id="bank-list"></div>
    <div id="bank-more" style="margin-top:24px;text-align:center"></div>`;
  }

  function bankMatches(bank) {
    const f = bank.filter;
    const kw = f.q.trim().toLowerCase();
    return bank.questions.filter((q) => {
      if (f.type !== 'all' && q.type !== f.type) return false;
      if (f.cat !== 'all' && q.cat !== f.cat) return false;
      if (f.scope === 'bookmarks' && !bank.bookmarks.has(q.id)) return false;
      if (f.scope === 'mistakes' && !bank.mistakes.has(q.id)) return false;
      if (!kw) return true;
      return [q.id, q.text, q.explanation, ...q.options].join('\n').toLowerCase().includes(kw);
    });
  }

  function bankCard(bank, q) {
    const kw = bank.filter.q.trim();
    const hidden = bank.filter.hide && !bank.revealed.has(q.id);
    const order = q.options.map((_, i) => i);
    const body = hidden
      ? `<ul class="answers">${order.map((orig, pos) => `<li><span aria-hidden="true">${q.type === 'tf' ? (orig === 0 ? '○' : '✕') : 'ABCD'[pos]}</span><span>${hl(q.options[orig], kw)}</span></li>`).join('')}</ul>
         <button type="button" class="btn" data-action="bank-reveal" data-id="${esc(q.id)}">顯示答案與解析</button>`
      : `${answerList(q, order, undefined, kw)}
         <div class="explain">${q.explanation ? `<p>${hl(q.explanation, kw).replace(/\n/g, '<br>')}</p>` : '<p class="muted">這一題目前沒有解析。</p>'}
           ${q.revised ? `<p class="small"><span class="chip chip-amber">已依現行法規改寫</span> ${esc(q.revised)}</p>` : ''}
           ${sourceLine(q)}</div>`;
    return `<article class="card qcard" id="q-${esc(q.id)}" data-id="${esc(q.id)}">
      <div class="qcard-head">
        <span class="id">${esc(q.id)}</span><span class="chip chip-primary">${typeLabel(q)}</span><span class="chip">${esc(bank.cfg.cats[q.cat] || q.cat)}</span>
        ${bank.mistakes.has(q.id) ? '<span class="chip chip-red">錯題</span>' : ''}
        ${starButton(bank, q)}
      </div>
      <h3>${hl(q.text, kw)}</h3>
      ${q.outdated ? `<p class="notice notice-warn small"><strong>舊法題，不列入測驗。</strong>${esc(q.statusNote)}</p>` : ''}
      ${q.outdated ? sourceLine(q) : body}
      <div class="row row-between" style="margin-top:8px">${tagText(q)}
        ${bank.mistakes.has(q.id) ? `<button type="button" class="btn-link" data-action="mistake-remove" data-id="${esc(q.id)}">移出錯題本</button>` : ''}</div>
    </article>`;
  }

  function updateBank(bank) {
    const list = $('#bank-list');
    if (!list) return;
    const matches = bankMatches(bank);
    const shown = matches.slice(0, bank.filter.limit);
    $('#bank-count').textContent = `找到 ${matches.length} 題${matches.length > shown.length ? `，目前顯示前 ${shown.length} 題` : ''}`;
    if (!matches.length) {
      const scope = bank.filter.scope;
      const why = scope === 'bookmarks' && !bank.bookmarks.size ? '你還沒有收藏任何題目。按題目右上角的星號可以收藏。'
        : scope === 'mistakes' && !bank.mistakes.size ? '錯題本目前是空的。測驗答錯的題目會出現在這裡。'
        : '沒有符合條件的題目，試試其他關鍵字或清除篩選。';
      list.innerHTML = `<div class="card empty"><p>${why}</p><button type="button" class="btn" data-action="bank-reset">清除篩選</button></div>`;
    } else {
      list.innerHTML = shown.map((q) => bankCard(bank, q)).join('');
    }
    $('#bank-more').innerHTML = matches.length > shown.length
      ? `<button type="button" class="btn" data-action="bank-more">再顯示 20 題（還有 ${matches.length - shown.length} 題）</button>` : '';
  }

  /* ------------------------------------------------------------ 講義共用 */
  const listBlock = (items) => `<ul>${items.map((t) => `<li>${rich(String(t).replace(/^\s*[*＊•]\s*/, ''))}</li>`).join('')}</ul>`;
  const tableBlock = (headers, rows) => `<div class="table-wrap"><table class="responsive">
    <thead><tr>${headers.map((h) => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead>
    <tbody>${rows.map((row) => `<tr>${row.map((cell, i) => (i === 0 ? `<th scope="row">${rich(cell)}</th>` : `<td data-label="${esc(headers[i])}">${rich(cell)}</td>`)).join('')}</tr>`).join('')}</tbody>
  </table></div>`;
  const fold = (title, inner, open) => `<details ${open ? 'open' : ''}><summary>${esc(title)}</summary><div class="details-body">${inner}</div></details>`;
  const lawsHint = (route) => `<p class="notice small">這一頁是重點整理，可能經過簡化。條文原文請看 <a href="#${route}">法規全文</a>，內容以原文為準。</p>`;

  function sectionsBlock(sections) {
    return sections.map((sec) => {
      let inner = '';
      if (sec.content) inner = listBlock(sec.content);
      else if (sec.table) inner = tableBlock(sec.table.headers, sec.table.rows);
      else if (sec.items) inner = `<div class="grid grid-2">${sec.items.map((it) => `<div class="card"><h4>${esc(it.title)}</h4><p>${rich(it.desc)}</p></div>`).join('')}</div>`;
      return `<h3>${esc(sec.title)}</h3>${inner}`;
    }).join('');
  }

  function viewRegulations() {
    const d = state.study.regulations;
    return `<div class="prose stack-sm"><h2>${esc(d.title)}</h2><p class="muted read">${esc(d.description)}</p>${lawsHint('laws')}
      ${sectionsBlock(d.sections)}
      <h3>補充筆記</h3>${fold(`${d.key_points_full.title}（${d.key_points_full.items.length} 則）`, listBlock(d.key_points_full.items))}</div>`;
  }

  function viewVolunteer() {
    const d = state.study.volunteer;
    return `<div class="prose stack-sm"><h2>${esc(d.title)}</h2><p class="muted read">${esc(d.description)}</p>${lawsHint('laws')}${sectionsBlock(d.sections)}</div>`;
  }

  function viewRights() {
    const d = state.study.rights_and_management;
    const g = d.grade_breakdown, notes = state.study.footnotes;
    return `<div class="prose stack-sm"><h2>${esc(d.title)}</h2><p class="muted read">${esc(d.description)}</p>${lawsHint('laws')}
      <h3>${esc(g.title)}</h3><p class="notice notice-warn small">${esc(g.desc)}</p>
      ${tableBlock(['項目', '比例', '說明'], g.components.map((c) => [c.name, c.ratio, c.desc]))}
      <div class="card" id="calc"><h4>成績試算</h4>
        <div class="grid grid-2">${g.components.map((c, i) => `<div class="field"><label for="calc-${i}">${esc(c.name)}（${esc(c.ratio)}）</label><input type="number" id="calc-${i}" data-calc="${parseFloat(c.ratio) || 0}" min="0" max="100" inputmode="decimal" placeholder="0–100"></div>`).join('')}</div>
        <p style="margin-top:16px">加權總分：<strong id="calc-total">—</strong></p></div>
      <h3>役男權益</h3>${listBlock(d.rights)}
      <h3>懲處種類與上限</h3>${listBlock(d.punishments)}
      <h3>${esc(d.salary_structure.title)}</h3>${tableBlock(['對象', '金額', '說明'], d.salary_structure.data.map((x) => [x.tier, x.amount, x.detail]))}
      <h3>補充筆記</h3>
      ${fold(`${d.rights_points_full.title}（${d.rights_points_full.items.length} 則）`, listBlock(d.rights_points_full.items))}
      ${fold(`${d.management_points_full.title}（${d.management_points_full.items.length} 則）`, listBlock(d.management_points_full.items))}
      ${fold(`${notes.title}（${notes.notes.length} 則）`, `<ol>${notes.notes.map((x) => `<li value="${Number(x.num) || 0}">${rich(String(x.text).replace(/^☞/, ''))}</li>`).join('')}</ol>`)}</div>`;
  }

  function viewShooting() {
    const d = state.study.shooting;
    const steps = (rows) => `<ol class="steps">${rows.map(([head, body]) => `<li><b>${esc(head)}</b><span>${rich(body)}</span></li>`).join('')}</ol>`;
    return `<div class="prose stack-sm"><h2>${esc(d.title)}</h2><p class="muted read">${esc(d.description)}</p>
      <p class="notice small">依歷屆役男筆記整理，非官方教材。靶場上一律聽從射擊指揮官與幹部的口令。</p>
      <h3>靶場安全守則</h3>${listBlock(d.rules)}
      <h3>射擊八步驟</h3>${steps(d.eight_steps.map((x) => [`${x.step}　${x.action}`, x.desc]))}
      <h3>故障排除口訣</h3>${steps(d.malfunction.map((x) => [x.step, x.desc]))}
      <h3>靶場口令</h3>${steps(d.commands.map((x) => [x.cmd, x.desc]))}
      <h3>${esc(d.t65k2_specs.title)}</h3>${listBlock(d.t65k2_specs.facts)}</div>`;
  }

  function viewEmtStudy() {
    const d = state.emtStudy;
    const v = d.vital_signs, g = d.gcs_table, c = d.cpr_aed_guide, o = d.oxygen_therapy, t = d.trauma_care, s = d.start_triage;
    return `<div class="prose stack-sm"><h2>${esc(d.title)}</h2><p class="muted read">${esc(d.description)}</p>${lawsHint('emt-laws')}
      <h3>法規條文與考點</h3>
      ${d.statutory_articles.map((a) => fold(`${a.law} ${a.article}　${a.title}`, `
        <p><strong>條文：</strong>${rich(a.official_text)}</p><p><strong>重點：</strong>${rich(a.key_point)}</p>
        <p><strong>罰則：</strong>${rich(a.penalty)}</p><p class="small">${ext(a.url, '在全國法規資料庫查看')}</p>`)).join('')}
      <h3>法規重點歸納</h3>
      ${d.laws_summary.map((l) => fold(`${l.title}（${l.article}）`, listBlock(l.points))).join('')}
      <h3>${esc(v.title)}</h3><p class="muted">${esc(v.description)}</p>
      ${tableBlock(['項目', '成人', '兒童', '嬰兒', '危急數值'], v.table.map((x) => [x.item, x.adult, x.child, x.infant, x.critical]))}
      <h3>${esc(g.title)}</h3><p class="muted">${esc(g.description)}</p>
      <div class="grid grid-3">${g.categories.map((cat) => `<div class="card"><h4>${esc(cat.category)}</h4><ul>${cat.items.map((x) => `<li><strong>${esc(x.score)}</strong>　${rich(x.desc)}</li>`).join('')}</ul></div>`).join('')}</div>
      ${tableBlock(['分數範圍', '嚴重度', '說明'], g.clinical_meaning.map((x) => [x.range, x.severity, x.desc]))}
      <h3>${esc(c.title)}</h3><p class="muted">${esc(c.description)}</p>
      ${tableBlock(['指標', '內容'], c.indicators.map((x) => [x.rule, x.detail]))}
      <h4 style="margin-top:16px">AED 操作步驟</h4><ol>${c.aed_protocol.map((x) => `<li>${rich(x.desc)}</li>`).join('')}</ol>
      <p class="notice small">${rich(c.shockable_rhythms)}</p>
      <h3>${esc(o.title)}</h3>
      ${tableBlock(['設備', '流量', '氧氣濃度', '說明'], o.table.map((x) => [x.device, x.flow, x.fio2, x.desc]))}
      <div class="card"><h4>${esc(o.formula.title)}</h4><p>${rich(o.formula.equation)}</p>
        ${tableBlock(['鋼瓶', '常數', '安全存量'], o.formula.constants.map((x) => [x.cylinder, x.constant, x.safety]))}
        <p style="margin-top:16px">${rich(o.formula.example)}</p></div>
      <h3>${esc(t.title)}</h3><p class="muted">${esc(t.description)}</p>
      ${tableBlock(['步驟', '名稱', '處置'], t.steps.map((x) => [x.step, x.name, x.action]))}
      <h3>${esc(s.title)}</h3><p class="muted">${esc(s.description)}</p>
      ${tableBlock(['階段', '條件', '結果', '處置'], s.flowchart.map((x) => [x.stage, x.condition, x.result, x.action]))}</div>`;
  }

  function viewEmtResources() {
    const d = state.emtStudy;
    return `<div class="stack-sm"><h2>學習資源</h2><p class="muted read">以下是外部網站，內容由各單位維護。</p>
      <div class="grid grid-2">${d.resources.map((r) => `<article class="card"><div class="row" style="margin-bottom:8px"><span class="chip chip-primary">${esc(r.category)}</span><span class="chip">${esc(r.type)}</span></div>
        <h3>${ext(r.url, r.name)}</h3><p class="muted">${rich(r.desc)}</p></article>`).join('')}</div></div>`;
  }

  /* ------------------------------------------------------------ 法規全文 */
  function lawArticle(a, kw) {
    return `<div class="law-article"><h4>${esc(a.label)}</h4>${a.lines.map(([indent, text]) =>
      `<p class="in-${Math.min(indent, 3)}">${hl(text, kw).replace(/\n/g, '<br>')}</p>`).join('')}</div>`;
  }

  function lawBody(law) {
    return `<p class="small muted">${esc(law.date_label)}：${esc(law.date)}　${ext(law.url, '全國法規資料庫原文')}</p>
      ${law.chapters.map((ch) => `${ch.title ? `<h3 class="law-chapter">${esc(ch.title)}</h3>` : ''}${ch.articles.map((a) => lawArticle(a)).join('')}`).join('')}`;
  }

  function viewLaws(group) {
    return `<div class="stack-sm"><h2>法規全文</h2>
      <p class="muted read" id="law-meta">法規載入中…</p>
      <div class="card"><div class="field"><label for="law-search">搜尋條文</label>
        <input type="search" id="law-search" data-group="${group}" placeholder="輸入關鍵字，例如：${group === 'emt' ? '救護紀錄表' : '撫卹、請假'}" autocomplete="off"></div></div>
      <p id="law-count" class="muted" role="status" aria-live="polite"></p>
      <div id="law-list"></div></div>`;
  }

  function updateLaws(group) {
    const list = $('#law-list');
    if (!list || !state.laws) return;
    const laws = state.laws.laws.filter((l) => l.group === group);
    const kw = ($('#law-search').value || '').trim();
    $('#law-meta').innerHTML = `共 ${laws.length} 部法規，條文於 ${esc(state.laws.fetched_at)} 取自${ext('https://law.moj.gov.tw/', '全國法規資料庫')}，未經改寫。之後如有修正，請以官方網站為準。`;
    if (!kw) {
      $('#law-count').textContent = '';
      list.innerHTML = laws.map((l) => `<details data-law="${esc(l.pcode)}"><summary><span>${esc(l.name)}<br><span class="small muted">${esc(l.date_label)} ${esc(l.date)}・${l.article_count} 條</span></span></summary><div class="details-body"></div></details>`).join('');
      return;
    }
    const lower = kw.toLowerCase();
    let total = 0;
    const html = laws.map((l) => {
      const hits = [];
      l.chapters.forEach((ch) => ch.articles.forEach((a) => {
        if (a.lines.some(([, text]) => text.toLowerCase().includes(lower))) hits.push(a);
      }));
      total += hits.length;
      return hits.length ? `<section class="card"><h3>${esc(l.name)}（${hits.length} 條）</h3>${hits.map((a) => lawArticle(a, kw)).join('')}</section>` : '';
    }).join('');
    $('#law-count').textContent = `找到 ${total} 條條文`;
    list.innerHTML = total ? `<div class="stack-sm">${html}</div>` : '<div class="card empty"><p>沒有符合的條文，試試其他關鍵字。</p></div>';
  }

  function initLaws(group) {
    loadLaws().then(() => updateLaws(group)).catch(() => {
      const meta = $('#law-meta');
      if (meta) meta.innerHTML = `法規資料載入失敗。請重新整理，或直接到${ext('https://law.moj.gov.tw/', '全國法規資料庫')}查詢。`;
    });
  }

  /* ------------------------------------------------------------ 用品清單 */
  const packItems = () => state.study.packing_list.categories.filter((c) => c.kind === 'pack').flatMap((c) => c.items);

  function viewChecklist() {
    const d = state.study.packing_list;
    const cats = d.categories.map((cat) => {
      if (cat.kind === 'pack') {
        const items = cat.items.filter((it) => !state.checklistOnlyTodo || !state.checked.has(it.id));
        const done = cat.items.filter((it) => state.checked.has(it.id)).length;
        return `<section class="card" aria-labelledby="cat-${esc(cat.id)}">
          <div class="row row-between"><h2 id="cat-${esc(cat.id)}">${esc(cat.name)}</h2><span class="chip" data-cat-count="${esc(cat.id)}">${done} / ${cat.items.length}</span></div>
          ${cat.note ? `<p class="muted small">${esc(cat.note)}</p>` : ''}
          ${items.length ? `<ul class="items">${items.map((it) => `<li><label class="item">
            <input type="checkbox" data-check="${esc(it.id)}" ${state.checked.has(it.id) ? 'checked' : ''}>
            <span class="name">${esc(it.name)}${it.must ? ' <span class="chip chip-primary">必帶</span>' : ''}</span>
            <span class="tip">${rich(it.tip)}${it.source ? `（${esc(it.source)}）` : ''}</span></label></li>`).join('')}</ul>` : '<p class="muted">這一類都準備好了。</p>'}
        </section>`;
      }
      return `<section class="card" aria-labelledby="cat-${esc(cat.id)}">
        <h2 id="cat-${esc(cat.id)}">${esc(cat.name)}</h2>
        ${cat.note ? `<p class="notice small">${esc(cat.note)}</p>` : ''}
        <ul class="info-list">${cat.items.map((it) => `<li>${it.level ? `<span class="chip chip-amber">${esc(it.level)}</span> ` : ''}<strong>${esc(it.name)}</strong>
          <p class="tip">${rich(it.tip)}${it.source ? `（${esc(it.source)}）` : ''}</p></li>`).join('')}</ul>
      </section>`;
    }).join('');
    return `
    <div class="page-head"><h1>${esc(d.title)}</h1><p>${esc(d.description)}</p></div>
    <div class="stack">
      <section class="card stack-sm no-print" aria-label="準備進度">
        <div class="stat-row">
          <div class="stat"><b id="check-must">0 / 0</b><span>必帶物品</span></div>
          <div class="stat"><b id="check-all">0 / 0</b><span>全部物品</span></div>
        </div>
        <progress id="check-progress" max="1" value="0" aria-label="必帶物品準備進度"></progress>
        <div class="row">
          <label class="check"><input type="checkbox" id="check-only-todo" ${state.checklistOnlyTodo ? 'checked' : ''}> 只看還沒準備的</label>
          <button type="button" class="btn" data-action="print">列印清單</button>
          ${pdfLink('checklist')}
          <button type="button" class="btn btn-danger" data-action="check-reset">清除所有勾選</button>
        </div>
        <p class="small muted">勾選紀錄存在這台裝置。資料整理日 ${esc(d.reviewed_at || '')}。</p>
      </section>
      ${cats}
    </div>`;
  }

  function updateChecklistProgress() {
    if (!$('#check-must')) return;
    const items = packItems();
    const must = items.filter((it) => it.must);
    const done = (arr) => arr.filter((it) => state.checked.has(it.id)).length;
    $('#check-must').textContent = `${done(must)} / ${must.length}`;
    $('#check-all').textContent = `${done(items)} / ${items.length}`;
    const bar = $('#check-progress');
    bar.max = must.length; bar.value = done(must);
    state.study.packing_list.categories.filter((c) => c.kind === 'pack').forEach((c) => {
      const el = $(`[data-cat-count="${c.id}"]`);
      if (el) el.textContent = `${done(c.items)} / ${c.items.length}`;
    });
  }

  /* ------------------------------------------------------------ 路由與繪製 */
  function render() {
    const app = $('#app');
    const [section, view] = ROUTES[state.route];
    $$('.main-nav a').forEach((a) => {
      if (a.dataset.nav === section) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    let html = '';
    if (section === 'home') html = viewHome();
    else if (section === 'checklist') html = viewChecklist();
    else {
      const bank = state.banks[section];
      const s = bank.session;
      if (view === 'quiz' && s && s.status === 'active') {
        html = viewQuizActive(bank); // 作答中只顯示題目，不顯示其他導覽
      } else {
        const [title, desc] = SECTION_HEAD[section];
        const nav = `<nav aria-label="${esc(title)}子選單"><ul class="sub-nav">${SUBNAV[section].map(([route, label]) =>
          `<li><a href="#${route}" ${route === state.route ? 'aria-current="page"' : ''}>${label}</a></li>`).join('')}</ul></nav>`;
        let body = '';
        if (view === 'quiz') body = s && s.status === 'done' ? viewQuizResult(bank) : viewQuizSetup(bank);
        else if (view === 'bank') body = viewBank(bank);
        else if (view === 'laws') body = viewLaws(section);
        else if (view === 'regulations') body = viewRegulations();
        else if (view === 'volunteer') body = viewVolunteer();
        else if (view === 'rights') body = viewRights();
        else if (view === 'shooting') body = viewShooting();
        else if (view === 'study') body = viewEmtStudy();
        else if (view === 'resources') body = viewEmtResources();
        const head = view === 'quiz' && s && s.status === 'done' ? '' : `<div class="page-head"><h1>${esc(title)}</h1><p>${esc(desc)}</p></div>`;
        html = `${head}${nav}<div id="view">${body}</div>`;
      }
    }
    app.innerHTML = html;
    if (view === 'bank') updateBank(state.banks[section]);
    if (view === 'laws') initLaws(section);
    if (section === 'checklist') updateChecklistProgress();
    document.title = `${section === 'home' ? '首頁' : section === 'checklist' ? '用品清單' : SECTION_HEAD[section][0]}｜成功嶺新訓備考`;
    if (state.focusAfterRender) {
      const el = $(state.focusAfterRender);
      state.focusAfterRender = null;
      if (el) el.focus({ preventScroll: false });
    }
  }

  function onRoute(first) {
    const raw = decodeURIComponent(location.hash.replace(/^#/, ''));
    const route = ROUTES[raw] ? raw : (ALIASES[raw] || (raw.startsWith('q-') ? state.route : 'home'));
    const leaving = activeBank();
    if (leaving && route !== state.route) pauseSession(leaving);
    const changed = route !== state.route;
    state.route = route;
    render();
    if (!first && changed) {
      window.scrollTo(0, 0);
      $('#main').focus({ preventScroll: true });
    }
  }

  /* ------------------------------------------------------------ 事件 */
  const currentBank = () => {
    const [section] = ROUTES[state.route];
    return state.banks[section] || null;
  };

  const actions = {
    'toggle-theme'() {
      const dark = document.documentElement.dataset.theme !== 'dark';
      document.documentElement.dataset.theme = dark ? 'dark' : 'light';
      try { localStorage.setItem('sms_theme', dark ? 'dark' : 'light'); } catch (e) { /* 略過 */ }
    },
    'quiz-start'(el) { startQuiz(currentBank(), el.dataset.mode); },
    'quiz-resume'(el) {
      const bank = state.banks[el.dataset.bank];
      if (state.route !== bank.cfg.quizRoute) { state.route = bank.cfg.quizRoute; history.replaceState(null, '', `#${bank.cfg.quizRoute}`); }
      resumeSession(bank);
    },
    async 'quiz-discard'(el) {
      const bank = state.banks[el.dataset.bank];
      const ok = await ask({ title: '放棄這份測驗？', body: '作答紀錄會被刪除，無法復原。已寫入錯題本的題目不受影響。',
        actions: [{ label: '保留', value: false }, { label: '放棄', value: true, kind: 'danger' }] });
      if (!ok) return;
      bank.session = null; saveSession(bank); render();
    },
    'quiz-answer'(el) { answerQuestion(currentBank(), Number(el.dataset.opt)); },
    'quiz-prev'() { gotoQuestion(currentBank().session.current - 1); },
    'quiz-next'() { gotoQuestion(currentBank().session.current + 1); },
    'quiz-goto'(el) { gotoQuestion(Number(el.dataset.index)); },
    'quiz-flag'() {
      const bank = currentBank(), s = bank.session;
      const at = s.flags.indexOf(s.current);
      if (at >= 0) s.flags.splice(at, 1); else s.flags.push(s.current);
      saveSession(bank);
      state.focusAfterRender = '[data-action="quiz-flag"]';
      render();
    },
    'quiz-pause'() {
      const bank = currentBank();
      pauseSession(bank, true);
      render();
      window.scrollTo(0, 0);
      toast('已暫停並儲存進度。');
    },
    async 'quiz-submit'() {
      const bank = currentBank(), s = bank.session;
      const blank = s.items.length - Object.keys(s.answers).length;
      const ok = await ask({
        title: '確定交卷？',
        body: blank ? `還有 ${blank} 題沒有作答。未作答的題目不計分，也不會加入錯題本。` : '所有題目都已作答。交卷後會顯示成績與解析。',
        actions: [{ label: '繼續作答', value: false }, { label: '交卷', value: true, kind: 'primary' }],
      });
      if (ok && bank.session && bank.session.status === 'active') finishSession(bank, 'submit');
    },
    'result-filter'(el) {
      currentBank().resultFilter = el.dataset.filter;
      state.focusAfterRender = `[data-action="result-filter"][data-filter="${el.dataset.filter}"]`;
      render();
    },
    'result-retry'() {
      const bank = currentBank(), s = bank.session;
      const ids = s.items.filter((it, i) => s.answers[i] !== undefined && s.answers[i] !== bank.byId.get(it.id).answer).map((it) => it.id);
      startQuiz(bank, 'retry', { ids });
    },
    'result-again'() {
      const bank = currentBank(), mode = bank.session.mode;
      bank.session = null; saveSession(bank);
      if (mode === 'category') { render(); return; }
      startQuiz(bank, mode);
    },
    'result-close'() {
      const bank = currentBank();
      bank.session = null; saveSession(bank); render(); window.scrollTo(0, 0);
    },
    async 'clear-mistakes'() {
      const bank = currentBank();
      const ok = await ask({ title: '清空錯題本？', body: `會移除 ${bank.mistakes.size} 題錯題紀錄，無法復原。`,
        actions: [{ label: '取消', value: false }, { label: '清空', value: true, kind: 'danger' }] });
      if (!ok) return;
      bank.mistakes.clear(); saveSet(bank.cfg.mistakesKey, bank.mistakes); render();
    },
    'show-mistakes'() {
      const bank = currentBank();
      Object.assign(bank.filter, { q: '', type: 'all', cat: 'all', scope: 'mistakes', limit: 20 });
    },
    bookmark(el) {
      const bank = state.banks[el.dataset.bank], id = el.dataset.id;
      if (bank.bookmarks.has(id)) bank.bookmarks.delete(id); else bank.bookmarks.add(id);
      saveSet(bank.cfg.bookmarksKey, bank.bookmarks);
      const on = bank.bookmarks.has(id);
      el.setAttribute('aria-pressed', String(on));
      el.setAttribute('aria-label', on ? '取消收藏' : '收藏這一題');
      toast(on ? '已收藏' : '已取消收藏');
    },
    'bank-reveal'(el) {
      const bank = currentBank();
      bank.revealed.add(el.dataset.id);
      const card = el.closest('.qcard');
      card.outerHTML = bankCard(bank, bank.byId.get(el.dataset.id));
    },
    'bank-more'() {
      const bank = currentBank();
      bank.filter.limit += 20;
      updateBank(bank);
    },
    'bank-reset'() {
      const bank = currentBank();
      Object.assign(bank.filter, { q: '', type: 'all', cat: 'all', scope: 'all', limit: 20 });
      bank.revealed.clear();
      state.focusAfterRender = '#bank-search';
      render();
    },
    'mistake-remove'(el) {
      const bank = currentBank();
      bank.mistakes.delete(el.dataset.id);
      saveSet(bank.cfg.mistakesKey, bank.mistakes);
      updateBank(bank);
      toast('已移出錯題本');
    },
    print() { window.print(); },
    async 'check-reset'() {
      const ok = await ask({ title: '清除所有勾選？', body: '用品清單的勾選紀錄會全部清除。',
        actions: [{ label: '取消', value: false }, { label: '清除', value: true, kind: 'danger' }] });
      if (!ok) return;
      state.checked.clear(); saveSet('sms_checklist', state.checked); render();
    },
    async 'clear-all'() {
      const ok = await ask({ title: '清除所有紀錄？', body: '錯題本、收藏、未完成的測驗與用品清單勾選都會刪除，無法復原。',
        actions: [{ label: '取消', value: false }, { label: '全部清除', value: true, kind: 'danger' }] });
      if (!ok) return;
      Object.values(state.banks).forEach((bank) => {
        bank.mistakes.clear(); bank.bookmarks.clear(); bank.session = null;
        store.del(bank.cfg.mistakesKey); store.del(bank.cfg.bookmarksKey); store.del(bank.cfg.sessionKey);
      });
      state.checked.clear(); store.del('sms_checklist');
      render();
      toast('已清除這台裝置上的紀錄。');
    },
  };

  function gotoQuestion(index) {
    const bank = currentBank(), s = bank && bank.session;
    if (!s || s.status !== 'active' || index < 0 || index >= s.items.length) return;
    s.current = index;
    saveSession(bank);
    state.focusAfterRender = '#question-text';
    render();
    const bar = $('.quiz-bar');
    if (bar) window.scrollTo(0, 0);
  }

  let composing = false;
  let searchTimer = null;
  function onSearchInput(el) {
    if (composing) return; // 中文輸入法選字中，等 compositionend 再搜尋
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      if (el.id === 'bank-search') {
        const bank = state.banks[el.dataset.bank];
        bank.filter.q = el.value;
        bank.filter.limit = 20;
        updateBank(bank); // 只更新結果區，輸入框不重繪，焦點與游標不會跑掉
      } else if (el.id === 'law-search') {
        updateLaws(el.dataset.group);
      }
    }, 120);
  }

  function bindEvents() {
    document.addEventListener('click', (e) => {
      const el = e.target.closest('[data-action]');
      if (!el || el.disabled) return;
      const fn = actions[el.dataset.action];
      if (fn) fn(el, e);
    });

    document.addEventListener('compositionstart', () => { composing = true; });
    document.addEventListener('compositionend', (e) => {
      composing = false;
      if (e.target.matches('#bank-search, #law-search')) onSearchInput(e.target);
    });
    document.addEventListener('input', (e) => {
      const el = e.target;
      if (el.matches('#bank-search, #law-search')) onSearchInput(el);
      else if (el.matches('[data-calc]')) {
        const inputs = $$('[data-calc]');
        const filled = inputs.filter((x) => x.value !== '');
        const total = inputs.reduce((sum, x) => sum + (Math.min(100, Math.max(0, Number(x.value) || 0)) * Number(x.dataset.calc)) / 100, 0);
        $('#calc-total').textContent = filled.length ? `${total.toFixed(1)} 分${filled.length < inputs.length ? '（尚有項目未填，以 0 分計）' : ''}` : '—';
      }
    });
    document.addEventListener('change', (e) => {
      const el = e.target;
      const bank = currentBank();
      if (el.matches('[data-filter]') && bank) {
        bank.filter[el.dataset.filter] = el.value;
        bank.filter.limit = 20;
        updateBank(bank);
      } else if (el.id === 'bank-hide' && bank) {
        bank.filter.hide = el.checked;
        bank.revealed.clear();
        updateBank(bank);
      } else if (el.matches('[data-check]')) {
        if (el.checked) state.checked.add(el.dataset.check); else state.checked.delete(el.dataset.check);
        saveSet('sms_checklist', state.checked);
        updateChecklistProgress();
      } else if (el.id === 'check-only-todo') {
        state.checklistOnlyTodo = el.checked;
        state.focusAfterRender = '#check-only-todo';
        render();
      }
    });
    // details 的 toggle 事件不會冒泡，用捕獲階段監聽
    document.addEventListener('toggle', (e) => {
      const el = e.target;
      if (el.id === 'palette') state.paletteOpen = el.open;
      if (el.dataset && el.dataset.law && el.open && state.laws) {
        const body = $('.details-body', el);
        if (!body.childElementCount) body.innerHTML = lawBody(state.laws.laws.find((l) => l.pcode === el.dataset.law));
      }
    }, true);

    document.addEventListener('keydown', (e) => {
      const bank = activeBank(), s = bank && bank.session;
      if (!s || s.status !== 'active' || $('#dialog').open) return;
      if (e.ctrlKey || e.metaKey || e.altKey || e.target.matches('input, select, textarea')) return;
      if (e.key === 'ArrowRight') gotoQuestion(s.current + 1);
      else if (e.key === 'ArrowLeft') gotoQuestion(s.current - 1);
      else if (/^[1-4]$/.test(e.key)) {
        const orig = s.items[s.current].order[Number(e.key) - 1];
        if (orig !== undefined) answerQuestion(bank, orig);
      }
    });

    window.addEventListener('hashchange', () => onRoute(false));
    setInterval(tick, 500);
    const stamp = () => {
      const bank = activeBank(), s = bank && bank.session;
      if (s && s.status === 'active') { s.lastSeen = Date.now(); saveSession(bank); }
    };
    window.addEventListener('pagehide', stamp);
    document.addEventListener('visibilitychange', () => { if (document.hidden) stamp(); else tick(); });
  }

  /* ------------------------------------------------------------ 啟動 */
  document.addEventListener('DOMContentLoaded', async () => {
    try {
      await loadData();
    } catch (err) {
      $('#app').innerHTML = '<p class="notice notice-danger">題庫載入失敗，請重新整理頁面。如果是直接開啟檔案，請確認 data/data_bundle.js 存在。</p>';
      console.error(err);
      return;
    }
    bindEvents();
    onRoute(true);
  });
})();
