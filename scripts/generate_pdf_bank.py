import os
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

# 1. Load questions
with open('data/questions.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

questions = data['questions']
stats = data.get('stats', {})

category_names = {
    'regulations': '替代役條例',
    'volunteer': '志願服務',
    'rights': '役男權益',
    'management': '服勤管理',
    'shooting': '打靶射擊'
}

# Separate questions into True/False and Multiple Choice
tf_questions = [q for q in questions if q['type'] == 'true_false']
mc_questions = [q for q in questions if q['type'] == 'multiple_choice']

labels = ['(A)', '(B)', '(C)', '(D)']

def build_rows(q_list, start_num, is_tf_section=False):
    rows = []
    for idx, q in enumerate(q_list):
        q_num = start_num + idx
        cat_str = category_names.get(q['category'], q['category'])
        cat_badge = f'<span class="badge badge-{"tf" if is_tf_section else "mc"}">{cat_str}</span>'
        exam_badge = f'<span class="badge badge-exam">{q["exam_tag"]}</span>' if q.get('exam_tag') else ''
        
        # Source link (compact sub-part under explanation)
        source_name = q.get('source', '全國法規資料庫')
        source_url = q.get('source_url', 'https://law.moj.gov.tw/')
        if source_url:
            source_link_html = f'<a href="{source_url}" target="_blank" class="source-link">參考：{source_name}</a>'
        else:
            source_link_html = f'<span class="source-link">來源：{source_name}</span>'
        
        # Options & Explanation (neutral text colors, NO green spoiler)
        if is_tf_section:
            opt_ans_html = '<div class="tf-line">⭕ 正確 (O) &nbsp;｜&nbsp; ❌ 錯誤 (X)</div>'
            ans_str = '⭕ (O)' if q['answer'] == 'O' else '❌ (X)'
        else:
            opts = []
            for o_idx, opt in enumerate(q.get('options', [])):
                lbl = labels[o_idx] if o_idx < len(labels) else f'({o_idx+1})'
                opts.append(f'<div class="opt-item">{lbl} {opt}</div>')
            opt_ans_html = '<div class="opt-list">' + ''.join(opts) + '</div>'
            ans_str = labels[q['answer']] if q['answer'] < len(labels) else f'({q["answer"]+1})'

        if q.get('status') == 'outdated':
            # 舊法題不提供答案，只保留說明供對照
            ans_str = '舊法題'
            opt_ans_html += f'<div class="expl-box"><strong>【舊法題】</strong>{q.get("status_note", "")}<div class="source-sub">{source_link_html}</div></div>'
        elif q.get('explanation'):
            revised = f'<br><strong>【改寫說明】</strong>{q["revised"]}' if q.get('revised') else ''
            opt_ans_html += f'<div class="expl-box"><strong>【解析】</strong>{q["explanation"]}{revised}<div class="source-sub">{source_link_html}</div></div>'
        else:
            opt_ans_html += f'<div class="source-sub">{source_link_html}</div>'

        # Answer cell (in right column, ready for cover/slide self-testing)
        ans_html = f'<div class="ans-cell"><strong>{ans_str}</strong></div>'

        row = f"""
        <tr>
          <td class="col-num text-center"><strong>{q_num}</strong></td>
          <td class="col-q">{cat_badge} {exam_badge} {q['question']}</td>
          <td class="col-opt">{opt_ans_html}</td>
          <td class="col-ans text-center">{ans_html}</td>
        </tr>
        """
        rows.append(row)
    return ''.join(rows)

tf_rows_html = build_rows(tf_questions, 1, is_tf_section=True)
mc_rows_html = build_rows(mc_questions, len(tf_questions) + 1, is_tf_section=False)

table_header_html = """
    <thead>
      <tr>
        <th class="col-num">題號</th>
        <th class="col-q">題目內容 (含梯次與章節)</th>
        <th class="col-opt">選項與法規解析</th>
        <th class="col-ans">答案</th>
      </tr>
    </thead>
"""

# Complete HTML document
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>成功嶺替代役新訓題庫全集彙編</title>
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
      content: "成功嶺替代役新訓學科考古題彙編 ｜ 非官方整理，以主管機關公告為準";
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
    border-bottom: 2px solid #222;
    padding-bottom: 4px;
    margin-bottom: 6px;
  }}
  .doc-title {{
    font-size: 15pt;
    font-weight: normal;
    letter-spacing: 1px;
    margin: 0 0 2px 0;
  }}
  .doc-subtitle {{
    font-size: 9.5pt;
    font-weight: normal;
    color: #2b4c7e;
    margin: 0 0 2px 0;
  }}
  .doc-meta {{
    font-size: 8pt;
    color: #444;
  }}

  /* Section Banners */
  .section-banner {{
    font-size: 10pt;
    font-weight: normal;
    padding: 4px 8px;
    margin-top: 8px;
    margin-bottom: 4px;
    border-radius: 3px;
    page-break-after: avoid;
    break-after: avoid;
  }}
  .tf-banner {{
    background-color: #1e40af;
    color: #ffffff;
  }}
  .mc-banner {{
    background-color: #581c87;
    color: #ffffff;
  }}

  /* Table Style */
  table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    page-break-inside: auto;
    margin-bottom: 8px;
  }}
  thead {{
    display: table-header-group;
  }}
  tr {{
    page-break-inside: avoid;
    page-break-after: auto;
  }}
  th {{
    background-color: #e6edf5;
    color: #1a2a3a;
    border: 1px solid #4a6b82;
    padding: 4px 4px;
    font-size: 8.2pt;
    font-weight: normal;
    text-align: center;
  }}
  td {{
    border: 1px solid #888;
    padding: 2.5px 4.5px;
    vertical-align: top;
    font-size: 8.2pt;
    word-break: break-word;
  }}
  tr:nth-child(even) {{
    background-color: #fbfcfd;
  }}

  /* Column Widths (4 columns: 題號, 題目內容, 選項與解析, 答案) */
  .col-num {{ width: 3.5%; }}
  .col-q {{ width: 53.5%; }}
  .col-opt {{ width: 36%; }}
  .col-ans {{ width: 7%; }}

  .text-center {{ text-align: center; }}

  /* Badges & Tags */
  .badge {{
    display: inline-block;
    padding: 0 3px;
    border-radius: 2px;
    font-size: 7.2pt;
    font-weight: normal;
    margin-right: 2px;
    vertical-align: baseline;
    line-height: 1.25;
  }}
  .badge-tf {{ background-color: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }}
  .badge-mc {{ background-color: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }}
  .badge-exam {{
    background-color: #fef3c7;
    color: #92400e;
    border: 1px solid #fcd34d;
    font-size: 7.2pt;
    font-weight: normal;
  }}

  /* Options list (clean neutral text color, NO green spoilers) */
  .opt-list {{ font-size: 8pt; line-height: 1.3; margin-bottom: 1px; }}
  .opt-item {{ margin-bottom: 0.5px; color: #1e293b; }}
  .tf-line {{
    font-size: 8.2pt;
    margin-bottom: 1px;
    color: #1e293b;
  }}

  /* Legal explanation & compact source citation */
  .expl-box {{
    font-size: 7.4pt;
    color: #334155;
    line-height: 1.24;
    border-top: 1px dashed #cbd5e1;
    padding-top: 2px;
    margin-top: 1px;
  }}
  .source-sub {{
    font-size: 7.2pt;
    margin-top: 1.5px;
    color: #2563eb;
  }}
  .source-link {{
    font-size: 7.2pt;
    color: #1d4ed8;
    text-decoration: underline;
    line-height: 1.2;
    word-break: break-all;
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

  <!-- Header -->
  <div class="doc-header">
    <div class="doc-title">成功嶺替代役新訓學科考古題彙編（非官方整理）</div>
    <div class="doc-subtitle">涵蓋：替代役實施條例、志願服務法、役男權益與保險撫卹、訓練服勤管理、射擊</div>
    <div class="doc-meta">
      題目來自歷屆役男分享；與現行法規牴觸者已依全國法規資料庫條文改寫並標示 ｜ 資料整理日：{data.get('updatedAt', '')} ｜ 總題數：{len(questions)} 題 (是非題 {len(tf_questions)} 題 · 選擇題 {len(mc_questions)} 題)
    </div>
  </div>

  <!-- Part 1: True / False -->
  <div class="section-banner tf-banner">第一部分：是非題（共 {len(tf_questions)} 題 ｜ 題號：1 ～ {len(tf_questions)}）</div>
  <table>
    {table_header_html}
    <tbody>
      {tf_rows_html}
    </tbody>
  </table>

  <!-- Part 2: Multiple Choice -->
  <div class="section-banner mc-banner">第二部分：單選選擇題（共 {len(mc_questions)} 題 ｜ 題號：{len(tf_questions) + 1} ～ {len(questions)}）</div>
  <table>
    {table_header_html}
    <tbody>
      {mc_rows_html}
    </tbody>
  </table>

</body>
</html>
"""

# Save HTML file
os.makedirs('pdf', exist_ok=True)
html_file_path = 'pdf/questions_biaukai.html'
pdf_file_path = 'pdf/替代役新訓題庫_全集彙編_標楷體版.pdf'

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
        path=pdf_file_path,
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
    doc = fitz.open(pdf_file_path)
    tmp_opt = pdf_file_path + '.opt'
    doc.save(tmp_opt, garbage=4, deflate=True, clean=True)
    doc.close()
    os.replace(tmp_opt, pdf_file_path)
    print(f"Optimized with PyMuPDF to {os.path.getsize(pdf_file_path)/1024:.1f} KB")
except Exception as e:
    print("PyMuPDF optimization skipped:", e)

pdf_size = os.path.getsize(pdf_file_path)
print(f"Successfully generated PDF: {pdf_file_path} (Size: {pdf_size/1024:.1f} KB)")
