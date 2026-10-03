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

category_tags = {
    'emt_laws': '法規',
    'emt_anatomy': '解剖',
    'emt_airway': '呼吸',
    'emt_cpr': 'CPR/AED',
    'emt_trauma': '創傷',
    'emt_medical': '急症',
    'emt_mci': '檢傷'
}

# Build table rows (4 columns: 題號, 題目內容, 選項與解析, 連結出處)
rows_html = []
labels = ['(A)', '(B)', '(C)', '(D)']

for idx, q in enumerate(questions):
    q_num = idx + 1
    cat_str = category_tags.get(q['category'], '急救')
    type_badge = f'<span class="badge badge-mc">【{cat_str}】</span>'
    
    # Options (A)(B)(C)(D) with bolded answer
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
            opts.append(f'<div class="opt-item opt-correct"><strong>{lbl} {opt_text}</strong></div>')
        else:
            opts.append(f'<div class="opt-item">{lbl} {opt_text}</div>')
    
    opt_ans_html = '<div class="opt-list">' + ''.join(opts) + '</div>'
    
    if q.get('explanation'):
        opt_ans_html += f'<div class="expl-box"><strong>【解析】</strong>{q["explanation"]}</div>'

    # Source link
    source_name = q.get('source', '消防署初級救護技術員教材')
    source_url = q.get('source_url', 'http://ebook.nfa.gov.tw/1080503/')
    source_html = f'<a href="{source_url}" target="_blank" class="source-link">{source_name}</a>'

    row = f"""
    <tr>
      <td class="col-num text-center"><strong>{q_num}</strong></td>
      <td class="col-q">{type_badge} {q['question']}</td>
      <td class="col-ans-opt">{opt_ans_html}</td>
      <td class="col-src">{source_html}</td>
    </tr>
    """
    rows_html.append(row)

# Complete HTML document
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>成功嶺替代役 EMT-1 初級救護技術員 全真題庫全集彙編</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 8mm 8mm 10mm 8mm;
    @bottom-right {{
      content: "第 " counter(page) " 頁，共 " counter(pages) " 頁";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 8pt;
      color: #555;
    }}
    @bottom-left {{
      content: "成功嶺替代役 EMT-1 全真題庫全集彙編 ｜ 衛福部與消防署教材最新修訂";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 8pt;
      color: #555;
    }}
  }}

  body {{
    font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", "Times New Roman", serif;
    font-size: 8.5pt;
    line-height: 1.32;
    color: #111;
    margin: 0;
    padding: 0;
  }}

  /* Document Header */
  .doc-header {{
    text-align: center;
    border-bottom: 2px solid #047857;
    padding-bottom: 4px;
    margin-bottom: 6px;
  }}
  .doc-title {{
    font-size: 15pt;
    font-weight: bold;
    color: #065f46;
    letter-spacing: 1px;
    margin: 0 0 2px 0;
  }}
  .doc-subtitle {{
    font-size: 9.5pt;
    font-weight: bold;
    color: #0f766e;
    margin: 0 0 2px 0;
  }}
  .doc-meta {{
    font-size: 8pt;
    color: #444;
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
    padding: 4px 4px;
    font-size: 8.2pt;
    font-weight: bold;
    text-align: center;
  }}
  td {{
    border: 1px solid #94a3b8;
    padding: 2.5px 4.5px;
    vertical-align: top;
    font-size: 8.2pt;
    word-break: break-word;
  }}
  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* Column Widths (4 columns) */
  .col-num {{ width: 3.5%; }}
  .col-q {{ width: 48.5%; }}
  .col-ans-opt {{ width: 33%; }}
  .col-src {{ width: 15%; }}

  .text-center {{ text-align: center; }}

  /* Badges & Tags */
  .badge {{
    display: inline-block;
    padding: 0 3px;
    border-radius: 2px;
    font-size: 7.2pt;
    font-weight: bold;
    margin-right: 2px;
    vertical-align: baseline;
    line-height: 1.25;
  }}
  .badge-mc {{ background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}

  /* Merged Options & Answer & Explanation */
  .opt-list {{ font-size: 8pt; line-height: 1.3; margin-bottom: 1px; }}
  .opt-item {{ margin-bottom: 0.5px; color: #1e293b; }}
  .opt-correct strong {{
    color: #047857;
    background-color: #d1fae5;
    padding: 0 2px;
    border-radius: 2px;
    border: 1px solid #6ee7b7;
  }}

  .expl-box {{
    font-size: 7.4pt;
    color: #475569;
    line-height: 1.24;
    border-top: 1px dashed #cbd5e1;
    padding-top: 2px;
    margin-top: 1px;
  }}

  .source-link {{
    color: #0d9488;
    text-decoration: underline;
    font-size: 7.4pt;
    word-break: break-all;
    line-height: 1.2;
    display: inline-block;
  }}
</style>
</head>
<body>

  <div class="doc-header">
    <div class="doc-title">成功嶺替代役 EMT-1 初級救護技術員 全真題庫全集彙編</div>
    <div class="doc-subtitle">衛生福利部與內政部消防署 40 小時訓練教材 · 替代役 EMT-1 鑑測真題全集 ｜ 總題數：{len(questions)} 題</div>
    <div class="doc-meta">
      適用梯次：2024–2026 最新各梯次役男 ｜ 及格標準：學科測驗 70 分 ｜ 編修日期：2026 年 10 月
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th class="col-num">題號</th>
        <th class="col-q">題目內容</th>
        <th class="col-ans-opt">選項、參考答案與法規解析</th>
        <th class="col-src">連結來源 / 出處</th>
      </tr>
    </thead>
    <tbody>
      {''.join(rows_html)}
    </tbody>
  </table>

</body>
</html>
"""

# Save HTML file
os.makedirs('pdf', exist_ok=True)
html_file_path = 'pdf/emt_questions_biaukai.html'
output_pdf = 'pdf/替代役EMT1初級救護技術員_全真題庫_標楷體版.pdf'

with open(html_file_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Saved HTML template to {html_file_path}, size: {len(html_content)} bytes")

# Generate PDF with Playwright
print("Generating PDF via Playwright Chromium...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('file:///' + os.path.abspath(html_file_path).replace('\\', '/'))
    page.wait_for_timeout(2000)
    page.pdf(
        path=output_pdf,
        format='A4',
        print_background=True,
        margin={
            'top': '8mm',
            'bottom': '10mm',
            'left': '8mm',
            'right': '8mm'
        }
    )
    browser.close()

# Optimize with PyMuPDF
try:
    import fitz
    doc = fitz.open(output_pdf)
    tmp_opt = output_pdf + '.opt'
    doc.save(tmp_opt, garbage=4, deflate=True, clean=True)
    doc.close()
    os.replace(tmp_opt, output_pdf)
    print(f"Optimized with PyMuPDF to {os.path.getsize(output_pdf)/1024:.1f} KB")
except Exception as e:
    print("PyMuPDF optimization skipped:", e)

pdf_size = os.path.getsize(output_pdf)
print(f"Successfully generated PDF: {output_pdf} (Size: {pdf_size/1024:.1f} KB)")
