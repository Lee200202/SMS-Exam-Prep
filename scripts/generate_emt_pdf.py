import os
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

# 1. Load EMT questions
with open('data/emt_questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

questions = data['questions']
stats = data.get('stats', {})

category_names = {
    'emt_laws': '緊急醫療救護法規與倫理',
    'emt_anatomy': '基礎解剖與生命徵象',
    'emt_airway': '呼吸道處置與氧氣治療',
    'emt_cpr': '心肺復甦術與AED',
    'emt_trauma': '創傷評估止血固定',
    'emt_medical': '急症評估處置與休克',
    'emt_mci': '大量傷病患檢傷搬運'
}

# Build table rows
rows_html = []
labels = ['(A)', '(B)', '(C)', '(D)']

for idx, q in enumerate(questions):
    q_num = idx + 1
    q_type_str = "選擇題"
    q_type_badge = '<span class="badge badge-mc">選擇題</span>'
    cat_str = category_names.get(q['category'], q['category'])
    
    # Options (A)(B)(C)(D)
    opts = []
    for o_idx, opt in enumerate(q.get('options', [])):
        # Normalize prefix if already has (A)
        clean_opt = opt
        if clean_opt.startswith('(') and len(clean_opt) >= 4 and clean_opt[2] == ')':
            lbl = clean_opt[:3]
            opt_text = clean_opt[3:].strip()
        else:
            lbl = labels[o_idx] if o_idx < len(labels) else f'({o_idx+1})'
            opt_text = clean_opt
            
        is_ans = (o_idx == q['answer'])
        if is_ans:
            opts.append(f'<span class="correct-opt"><strong>{lbl} {opt_text}</strong></span>')
        else:
            opts.append(f'{lbl} {opt_text}')
    options_html = '<div class="opt">' + '<br>'.join(opts) + '</div>'
    
    ans_idx = q['answer']
    ans_lbl = labels[ans_idx] if ans_idx < len(labels) else f'({ans_idx+1})'
    ans_opt_content = q['options'][ans_idx] if ans_idx < len(q['options']) else ''
    if ans_opt_content.startswith('(') and len(ans_opt_content) >= 4:
        ans_opt_content = ans_opt_content[3:].strip()
    ans_text = f'{ans_lbl} {ans_opt_content}'

    # Answer in bold + explanation
    ans_html = f'<div class="ans-box"><strong>【 {ans_text} 】</strong></div>'
    if q.get('explanation'):
        ans_html += f'<div class="expl"><strong>【解析】</strong>{q["explanation"]}</div>'

    # Source link
    source_name = q.get('source', '消防署初級救護技術員教材')
    source_url = q.get('source_url', 'http://ebook.nfa.gov.tw/1080503/')
    source_html = f'<a href="{source_url}" target="_blank" class="source-link">{source_name}</a>'

    row = f"""
    <tr>
      <td class="col-num text-center"><strong>{q_num}</strong></td>
      <td class="col-type text-center">{q_type_badge}<br><span class="cat-tag">{cat_str}</span></td>
      <td class="col-q">{q['question']}</td>
      <td class="col-opt">{options_html}</td>
      <td class="col-ans">{ans_html}</td>
      <td class="col-src">{source_html}</td>
    </tr>
    """
    rows_html.append(row)

# Complete HTML document
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>成功嶺替代役 EMT-1 初級救護技術員 全真題庫全集彙編 (標楷體版)</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 12mm 10mm 15mm 10mm;
    @bottom-right {{
      content: "第 " counter(page) " 頁，共 " counter(pages) " 頁";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 9pt;
      color: #555;
    }}
    @bottom-left {{
      content: "成功嶺替代役 EMT-1 全真題庫全集彙編 ｜ 衛福部與消防署教材最新修訂";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 9pt;
      color: #555;
    }}
  }}

  body {{
    font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", "Times New Roman", serif;
    font-size: 9pt;
    line-height: 1.42;
    color: #111;
    margin: 0;
    padding: 0;
  }}

  /* Document Header */
  .doc-header {{
    text-align: center;
    border-bottom: 2px solid #047857;
    padding-bottom: 8px;
    margin-bottom: 12px;
  }}
  .doc-title {{
    font-size: 16pt;
    font-weight: bold;
    color: #065f46;
    letter-spacing: 1.5px;
    margin: 0 0 4px 0;
  }}
  .doc-subtitle {{
    font-size: 10.5pt;
    font-weight: bold;
    color: #0f766e;
    margin: 0 0 4px 0;
  }}
  .doc-meta {{
    font-size: 8.5pt;
    color: #444;
  }}

  /* Stat Summary Box */
  .stat-box {{
    border: 1px solid #10b981;
    background-color: #f0fdf4;
    padding: 6px 12px;
    margin-bottom: 12px;
    font-size: 8.5pt;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-radius: 4px;
  }}

  /* Table Style */
  table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    page-break-inside: auto;
  }}
  thead {{
    display: table-header-group;
  }}
  tr {{
    page-break-inside: avoid;
    page-break-after: auto;
  }}
  th {{
    background-color: #ecfdf5;
    color: #064e3b;
    border: 1px solid #059669;
    padding: 6px 4px;
    font-size: 8.5pt;
    font-weight: bold;
    text-align: center;
  }}
  td {{
    border: 1px solid #94a3b8;
    padding: 5px 6px;
    vertical-align: top;
    font-size: 8.5pt;
    word-break: break-word;
  }}
  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* Column Widths */
  .col-num {{ width: 5%; }}
  .col-type {{ width: 14%; }}
  .col-q {{ width: 31%; }}
  .col-opt {{ width: 23%; }}
  .col-ans {{ width: 17%; }}
  .col-src {{ width: 10%; }}

  .text-center {{ text-align: center; }}

  /* Badges & Tags */
  .badge {{
    display: inline-block;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: bold;
  }}
  .badge-mc {{ background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}
  .cat-tag {{ font-size: 7.5pt; color: #334155; display: block; margin-top: 2px; line-height: 1.2; font-weight: bold; }}

  .opt {{
    font-size: 8pt;
    line-height: 1.35;
    color: #1e293b;
  }}
  .correct-opt {{
    color: #047857;
    background-color: #d1fae5;
    padding: 0 2px;
    border-radius: 2px;
  }}

  .ans-box {{
    color: #047857;
    font-size: 8.5pt;
    margin-bottom: 3px;
  }}
  .expl {{
    font-size: 7.8pt;
    color: #475569;
    line-height: 1.3;
    border-top: 1px dashed #cbd5e1;
    padding-top: 3px;
    margin-top: 2px;
  }}

  .source-link {{
    color: #0d9488;
    text-decoration: underline;
    font-size: 7.5pt;
    word-break: break-all;
    line-height: 1.2;
    display: inline-block;
  }}
</style>
</head>
<body>

  <div class="doc-header">
    <div class="doc-title">成功嶺替代役 EMT-1 初級救護技術員 全真題庫全集彙編</div>
    <div class="doc-subtitle">衛生福利部與內政部消防署 40 小時訓練教材 · 替代役鑑測真題標準標楷體版</div>
    <div class="doc-meta">
      適用梯次：2024-2026 最新各梯次役男 ｜ 及格標準：學科測驗 70 分 ｜ 編修日期：2026 年 10 月
    </div>
  </div>

  <div class="stat-box">
    <div>
      <strong>【題庫總覽】</strong>
      總題數：<strong>{len(questions)}</strong> 題 ｜ 題型：<strong>單選選擇題 100%</strong>
    </div>
    <div>
      <strong>【章節分佈】</strong>
      法規倫理：12題 ｜ 生命徵象：14題 ｜ 呼吸道氧療：15題 ｜ CPR/AED：15題 ｜ 創傷止血：15題 ｜ 急症休克：15題 ｜ START檢傷：10題
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th class="col-num">題號</th>
        <th class="col-type">題型 / 類別<br>(章節出處)</th>
        <th class="col-q">題目內容</th>
        <th class="col-opt">選項條列<br>(A)(B)(C)(D)</th>
        <th class="col-ans">參考答案與詳解<br>(粗體高亮)</th>
        <th class="col-src">官方來源 / 法規<br>(點擊可直連)</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>

</body>
</html>
"""

# Save temp html
tmp_html = 'pdf_emt_temp.html'
with open(tmp_html, 'w', encoding='utf-8') as f:
    f.write(html_content)

output_pdf = 'pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf'
os.makedirs('pdf', exist_ok=True)

print(f"Generating PDF using Playwright to {output_pdf}...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('file:///' + os.path.abspath(tmp_html).replace('\\', '/'))
    page.wait_for_timeout(1000)
    page.pdf(
        path=output_pdf,
        format='A4',
        print_background=True,
        margin={
            'top': '12mm',
            'bottom': '15mm',
            'left': '10mm',
            'right': '10mm'
        }
    )
    browser.close()

if os.path.exists(tmp_html):
    os.remove(tmp_html)

print(f"Successfully generated: {output_pdf} ({os.path.getsize(output_pdf)} bytes)")
