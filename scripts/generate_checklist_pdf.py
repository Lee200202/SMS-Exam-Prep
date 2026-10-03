import os
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

# 1. Load packing list
with open('data/study_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

packing_list = data['packing_list']
categories = packing_list['categories']

pack_items = [it for c in categories if c['kind'] == 'pack' for it in c['items']]
total_items = len(pack_items)
must_items = sum(1 for it in pack_items if it.get('must'))

# Build HTML sections：pack 類別是要準備的物品（有勾選框）；info 類別是說明，不提供勾選
sections_html = []

for cat in categories:
    is_pack = cat['kind'] == 'pack'
    rows = []
    for item in cat['items']:
        tip = item.get('tip', '')
        if item.get('source'):
            tip += f"（{item['source']}）"
        if is_pack:
            check = '<span class="checkbox-box"></span>'
            if item.get('must'):
                badge, row_class = '<span class="badge badge-must">必帶</span>', 'row-must'
            else:
                badge, row_class = '<span class="badge badge-rec">選帶</span>', 'row-rec'
        else:
            check = '—'
            if item.get('level'):
                badge, row_class = f'<span class="badge badge-control">{item["level"]}</span>', 'row-control'
            elif cat['id'] == 'avoid':
                badge, row_class = '<span class="badge badge-danger">不用帶</span>', 'row-danger'
            else:
                badge, row_class = '<span class="badge badge-rec">提醒</span>', 'row-rec'
        rows.append(f"""
        <tr class="{row_class}">
          <td class="col-check text-center">{check}</td>
          <td class="col-name"><strong>{item['name']}</strong></td>
          <td class="col-attr text-center">{badge}</td>
          <td class="col-tip">{tip}</td>
        </tr>
        """)

    note = f'<div style="font-size:9pt;margin:2px 0 4px">{cat["note"]}</div>' if cat.get('note') else ''
    sections_html.append(f"""
    <div class="cat-section">
      <div class="cat-title">{cat['name']} <span class="cat-count">（共 {len(cat['items'])} 項）</span></div>
      {note}
      <table class="item-table">
        <thead>
          <tr>
            <th class="col-check">{'勾選' if is_pack else ''}</th>
            <th class="col-name">{'物品名稱' if is_pack else '項目'}</th>
            <th class="col-attr">類別</th>
            <th class="col-tip">說明</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """)

# Complete HTML document
html_content = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>成功嶺替代役新訓用品清單</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 12mm 10mm 15mm 10mm;
    @bottom-right {{
      content: "第 " counter(page) " 頁，共 " counter(pages) " 頁";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 8.5pt;
      color: #555;
    }}
    @bottom-left {{
      content: "成功嶺替代役新訓用品清單 ｜ 歷屆役男分享整理，非官方清單";
      font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", serif;
      font-size: 8.5pt;
      color: #555;
    }}
  }}

  body {{
    font-family: "DFKai-SB", "標楷體", "BiauKai", "KaiTi", "Times New Roman", serif;
    font-size: 8.8pt;
    line-height: 1.4;
    color: #111;
    margin: 0;
    padding: 0;
  }}

  /* Document Header */
  .doc-header {{
    text-align: center;
    border-bottom: 2px solid #065f46;
    padding-bottom: 6px;
    margin-bottom: 10px;
  }}
  .doc-title {{
    font-size: 16pt;
    font-weight: normal;
    color: #065f46;
    letter-spacing: 1px;
    margin: 0 0 3px 0;
  }}
  .doc-subtitle {{
    font-size: 10pt;
    font-weight: normal;
    color: #047857;
    margin: 0 0 3px 0;
  }}
  .doc-meta {{
    font-size: 8.2pt;
    color: #444;
  }}

  /* Category Section */
  .cat-section {{
    margin-bottom: 12px;
    page-break-inside: auto;
  }}
  .cat-title {{
    background-color: #065f46;
    color: #ffffff;
    font-size: 9.5pt;
    font-weight: normal;
    padding: 4px 8px;
    border-radius: 3px 3px 0 0;
    margin-top: 8px;
  }}
  .cat-count {{
    font-size: 8pt;
    font-weight: normal;
    color: #d1fae5;
  }}

  /* Table Style */
  table.item-table {{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    margin-bottom: 4px;
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
    font-weight: normal;
    text-align: center;
  }}
  td {{
    border: 1px solid #94a3b8;
    padding: 4px 6px;
    vertical-align: top;
    font-size: 8.2pt;
    word-break: break-word;
  }}
  tr:nth-child(even) {{
    background-color: #f8fafc;
  }}

  /* Row Highlights */
  tr.row-must {{
    background-color: #fffbeb;
  }}
  tr.row-danger {{
    background-color: #fef2f2;
  }}

  /* Column Widths */
  .col-check {{ width: 5%; }}
  .col-name {{ width: 25%; }}
  .col-attr {{ width: 11%; }}
  .col-tip {{ width: 59%; }}

  .text-center {{ text-align: center; }}

  /* Checkbox Box */
  strong, b, th {{ font-weight: normal; }}
  .checkbox-box {{
    display: inline-block;
    width: 11pt;
    height: 11pt;
    border: 1.2pt solid #111;
    border-radius: 1.5pt;
    vertical-align: middle;
  }}

  /* Badges */
  .badge {{
    display: inline-block;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 7.2pt;
    font-weight: normal;
    white-space: nowrap;
  }}
  .badge-must {{
    background-color: #fee2e2;
    color: #b91c1c;
    border: 1px solid #f87171;
  }}
  .badge-rec {{
    background-color: #e0f2fe;
    color: #0369a1;
    border: 1px solid #7dd3fc;
  }}
  .badge-control {{
    background-color: #fef3c7;
    color: #b45309;
    border: 1px solid #fcd34d;
  }}
  .badge-danger {{
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
  }}
</style>
</head>
<body>

  <!-- Header -->
  <div class="doc-header">
    <div class="doc-title">成功嶺替代役新訓用品清單（非官方整理）</div>
    <div class="doc-subtitle">{packing_list['description']}</div>
    <div class="doc-meta">
      要準備的物品：{total_items} 項（必帶 {must_items} 項） ｜ 資料整理日：{packing_list.get('reviewed_at', '')}
    </div>
  </div>

  <!-- Sections -->
  {''.join(sections_html)}

</body>
</html>
"""

# Save HTML file
os.makedirs('pdf', exist_ok=True)
html_file_path = 'pdf/checklist_biaukai.html'
output_pdf = 'pdf/成功嶺替代役新訓_必備用品建議檢核表_標楷體版.pdf'

with open(html_file_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Saved HTML template to {html_file_path}, size: {len(html_content)} bytes")

# Generate PDF with Playwright
print("Generating Checklist PDF via Playwright Chromium...")
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
            'top': '12mm',
            'bottom': '15mm',
            'left': '10mm',
            'right': '10mm'
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
print(f"Successfully generated Checklist PDF: {output_pdf} (Size: {pdf_size/1024:.1f} KB)")
