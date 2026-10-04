import os
import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

# 1. The recalled bank and the authored practice bank are printed separately.
practice = '--practice' in sys.argv
with open('data/emt_practice_questions.json' if practice else 'data/emt_questions.json', 'r', encoding='utf-8') as f:
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

# Build table rows (4 columns: 題號, 題目內容, 選項與解析, 答案)
rows_html = []
labels = ['(A)', '(B)', '(C)', '(D)']
option_prefix = re.compile(r'^\s*[（(][A-Ea-e][）)]\s*')

for idx, q in enumerate(questions):
    q_num = idx + 1
    
    # Source link (compact sub-part under explanation)
    source_name = q.get('source', '消防署初級救護技術員教材')
    source_url = q.get('source_url', 'http://ebook.nfa.gov.tw/1080503/')
    source_link_html = f'<a href="{source_url}" target="_blank" class="source-link">參考：{source_name}</a>'
    if q.get('status') == 'outdated':
        continue  # 回憶者註明已過時的題目不印

    # Options (A)(B)(C)(D) with identical text colors (NO green spoiler)
    opts = []
    for o_idx, opt in enumerate(q.get('options', [])):
        # Normalize prefix if already has (A)
        lbl = labels[o_idx] if o_idx < len(labels) else f'({o_idx+1})'
        opt_text = option_prefix.sub('', opt).strip()
            
        opts.append(f'<div class="opt-item">{lbl} {opt_text}</div>')
    
    opt_ans_html = '<div class="opt-list">' + ''.join(opts) + '</div>'
    
    if q.get('explanation'):
        opt_ans_html += f'<div class="expl-box"><strong>【解析】</strong>{q["explanation"]}<div class="source-sub">{source_link_html}</div></div>'
    else:
        opt_ans_html += f'<div class="source-sub">{source_link_html}</div>'

    # Answer cell in rightmost column (for cover-and-test)
    ans_idx = q['answer']
    ans_lbl = labels[ans_idx] if ans_idx < len(labels) else f'({ans_idx+1})'
    ans_html = f'<div class="ans-cell"><strong>{ans_lbl}</strong></div>'

    row = f"""
    <tr data-qid="{q['id']}">
      <td class="col-q"><div class="qprompt"><span class="qnum">{q_num:03d}.</span><span class="qtext">{q['question']}</span></div></td>
      <td class="col-opt">{opt_ans_html}</td>
      <td class="col-ans text-center">{ans_html}</td>
    </tr>
    """
    rows_html.append(row)

# Complete HTML document
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>{'EMT-1 教材概念自編練習（非考古題）' if practice else 'EMT-1 考生回憶考點（非逐字原題）'}</title>
<style>
  /* 標楷體沒有粗體字重，合成粗體會被輸出成 Type3 字型而讓 PDF 膨脹 */
  strong, b, th {{ font-weight: normal; }}
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
      content: "{'EMT-1 自編練習 ｜ 非考古題，教材內容待複核' if practice else 'EMT-1 回憶考點 ｜ 非正式原卷，以主管機關公告為準'}";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 8pt;
      color: #555;
    }}
  }}

  body {{
    font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", "Times New Roman", serif;
    font-size: 9.3pt;
    line-height: 1.34;
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
    font-weight: normal;
    color: #065f46;
    letter-spacing: 1px;
    margin: 0 0 2px 0;
  }}
  .doc-subtitle {{
    font-size: 9.5pt;
    font-weight: normal;
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
    padding: 3px 4px;
    font-size: 8.8pt;
    font-weight: normal;
    text-align: center;
  }}
  td {{
    border: 1px solid #94a3b8;
    padding: 3px 4px;
    vertical-align: top;
    font-size: 9pt;
    word-break: break-word;
  }}
  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* 題號與題幹共用一欄；解析獲得較多橫向空間，減少換行。 */
  .col-q {{ width: 42%; }}
  .col-opt {{ width: 50%; }}
  .col-ans {{ width: 8%; }}
  .qprompt {{ display: grid; grid-template-columns: max-content minmax(0,1fr); }}
  .qnum {{ color: #065f46; white-space: nowrap; }}
  .qtext {{ min-width: 0; overflow-wrap: anywhere; }}

  .text-center {{ text-align: center; }}

  /* Badges & Tags */
  .badge {{
    display: inline-block;
    padding: 0 3px;
    border-radius: 2px;
    font-size: 7.8pt;
    font-weight: normal;
    margin-right: 2px;
    vertical-align: baseline;
    line-height: 1.25;
  }}
  .badge-mc {{ background-color: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0; }}

  /* Options list (clean neutral text color, NO green spoilers) */
  .opt-list {{ font-size: 8.8pt; line-height: 1.34; margin-bottom: 1px; }}
  .opt-item {{ margin-bottom: 1px; color: #1e293b; }}

  /* Legal explanation & compact source citation */
  .expl-box {{
    font-size: 8.2pt;
    color: #475569;
    line-height: 1.38;
    border-top: 1px dashed #cbd5e1;
    padding-top: 2px;
    margin-top: 2px;
  }}
  .source-sub {{
    font-size: 7.8pt;
    margin-top: 2px;
    color: #0d9488;
  }}
  .source-link {{
    color: #0d9488;
    text-decoration: underline;
    font-size: 7.8pt;
    word-break: break-all;
    line-height: 1.2;
    display: inline-block;
  }}

  /* Rightmost Answer Column (easy to cover with a bookmark/ruler) */
  .ans-cell {{
    font-size: 9pt;
    font-weight: normal;
    color: #0f172a;
    padding-top: 2px;
  }}
</style>
</head>
<body>

  <div class="doc-header">
    <div class="doc-title">{'EMT-1 教材概念自編練習（非考古題）' if practice else 'EMT-1 考生回憶考點（非逐字原題）'}</div>
    <div class="doc-subtitle">有解析版 ｜ 共 {len(questions)} 題</div>
  </div>

  <table>
    <thead>
      <tr>
        <th class="col-q">題目</th>
        <th class="col-opt">選項與法規解析</th>
        <th class="col-ans">答案</th>
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
html_file_path = 'pdf/emt_practice_biaukai.html' if practice else 'pdf/emt_questions_biaukai.html'
output_pdf = 'pdf/EMT1_自編教材概念練習_非考古題.pdf' if practice else 'pdf/EMT1_考生回憶考點_非原卷.pdf'

with open(html_file_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(line.rstrip() for line in html_content.splitlines()) + '\n')

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
