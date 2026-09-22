import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

new_render_code = r'''
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

  const fullText = data.full_text ? data.full_text.items : [];

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

      <!-- Google Doc Shooting Full Text & 257T Questions -->
      ${fullText.length > 0 ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-emerald-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="file-text" class="w-5 h-5 text-emerald-500"></i> ${data.full_text.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">完整還原 Google 文件打靶筆記原文與 247T、257T 鑑測真題</p>
            </div>
          </div>

          <div class="space-y-3">
            ${fullText.map(line => `
              <div class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-800/40 text-xs sm:text-sm leading-relaxed text-slate-800 dark:text-slate-200">
                ${line.replace(/\*\*(.*?)\*\*/g, '<strong class="text-emerald-600 dark:text-emerald-400 font-bold">$1</strong>')}
              </div>
            `).join('')}
          </div>
        </div>
      ` : ''}
    </div>
  `;

  if (window.lucide) window.lucide.createIcons();
}

function renderChecklist() {
  const data = AppState.studyData.packing_list;
  const container = document.getElementById('checklist-content-body');
  if (!container || !data) return;

  const fullText = data.full_text ? data.full_text.items : [];

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
            <button onclick="window.print()" class="px-3 py-2 bg-emerald-500 hover:bg-emerald-600 text-white rounded-xl text-xs font-semibold transition flex items-center gap-1 shadow">
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

      <!-- Google Doc Raw Checklist Full Text & Notes -->
      ${fullText.length > 0 ? `
        <div class="glass-panel p-6 sm:p-8 rounded-3xl space-y-6 shadow-sm border border-emerald-500/20">
          <div class="flex items-center justify-between flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-3">
            <div>
              <h4 class="text-lg font-black text-slate-900 dark:text-white flex items-center gap-2">
                <i data-lucide="file-text" class="w-5 h-5 text-emerald-500"></i> ${data.full_text.title}
              </h4>
              <p class="text-xs text-slate-500 dark:text-slate-400">完整列出 Google 雲端文件檢核表原文（含數量、避坑防雷沒用物品、防蚊液法定成分詳細說明）</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
            ${fullText.map(line => {
              const isDanger = line.includes('[X]') || line.includes('違禁品') || line.includes('沒用的東西');
              const isWarning = line.includes('防蚊液') || line.includes('重要');
              return `
                <div class="p-3 rounded-xl border ${isDanger ? 'border-rose-200 bg-rose-50/40 dark:bg-rose-950/20 text-rose-800 dark:text-rose-300' : isWarning ? 'border-amber-200 bg-amber-50/40 dark:bg-amber-950/20 text-amber-800 dark:text-amber-300' : 'border-slate-200 dark:border-slate-800 bg-white/60 dark:bg-slate-800/40 text-slate-800 dark:text-slate-200'} text-xs sm:text-sm leading-relaxed">
                  ${line}
                </div>
              `;
            }).join('')}
          </div>
        </div>
      ` : ''}
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
'''

# Read current app.js
with open('js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# Replace from /* ========================================================================== STUDY GUIDES
pattern = re.compile(r'/\* ==========================================================================\s+STUDY GUIDES.*?(?=function toggleChecklistItem)', re.DOTALL)
if pattern.search(app_js):
    app_js = pattern.sub(lambda m: new_render_code.strip() + '\n\n', app_js)
    with open('js/app.js', 'w', encoding='utf-8') as f:
        f.write(app_js)
    print("Successfully updated app.js with complete text rendering!")
else:
    print("Could not find pattern in app.js!")
