"""Print four compact question books; answers are only in the final section."""
import html
import json
import os
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PDF = ROOT / "pdf"
CONFIGS = [
    ("recruit", "data/questions.json", "新訓歷屆來源題", "新訓_歷屆來源題_無解析版.pdf", "questions_plain.html"),
    ("recruit_authored", "data/questions.json", "新訓自編概念練習", "新訓_自編概念練習_無解析版.pdf", "questions_authored_plain.html"),
    ("emt", "data/emt_questions.json", "EMT-1 來源題", "EMT1_來源題_無解析版.pdf", "emt_questions_plain.html"),
    ("emt_authored", "data/emt_practice_questions.json", "EMT-1 自編教材概念練習", "EMT1_自編概念練習_無解析版.pdf", "emt_practice_plain.html"),
]
ABC = "ABCDE"
OPTION_PREFIX = re.compile(r"^\s*[（(][A-Ea-e][）)]\s*")


def e(value):
    return html.escape(str(value), quote=True)


def option_text(value):
    return OPTION_PREFIX.sub("", str(value)).strip()


def booklet(title, questions):
    tf = [q for q in questions if q["type"] == "true_false"]
    mc = [q for q in questions if q["type"] != "true_false"]
    ordered = tf + mc
    sections, answers = [], []
    for heading, group, start in (("是非題", tf, 1), ("選擇題", mc, len(tf) + 1)):
        if not group:
            continue
        cards = []
        for number, q in enumerate(group, start):
            old = q.get("status") == "outdated" or q.get("review", "").endswith("_conflict")
            badges = ""
            if old:
                badges = '<span class="tag warning">不計分</span>'
            if q["type"] == "true_false":
                opts = '<div class="choices">□ 正確（O）　　□ 錯誤（X）</div>'
                answer = q["answer"]
            else:
                short = all(len(option_text(o)) <= 19 for o in q["options"])
                opts = '<div class="choices ' + ('short' if short else '') + '">' + "".join(
                    f'<div>（{ABC[i] if i < len(ABC) else i + 1}）{e(option_text(opt))}</div>'
                    for i, opt in enumerate(q["options"])
                ) + '</div>'
                answer = ABC[q["answer"]]
            cards.append(
                f'<article class="question" data-qid="{e(q["id"])}">'
                f'<div class="stem"><b>{number:03d}.</b>'
                f'<span>{e(q["question"])}{badges}</span></div>'
                f'{opts}</article>'
            )
            uncertain = q.get("review") not in ("law", "textbook114") and not old
            key = "—" if old else answer + ("†" if uncertain else "")
            answers.append(f'<div class="key-item"><span>{number:03d}</span><b>{e(key)}</b></div>')
        sections.append(f'<section><h2>{heading} <small>{len(group)} 題</small></h2>{"".join(cards)}</section>')
    css = """
@page { size: A4; margin: 10mm 10mm 13mm;
  @bottom-center { content: "第 " counter(page) " 頁"; font: 9pt "DFKai-SB","標楷體",serif; color:#59606b; } }
* { box-sizing: border-box; }
body { margin:0; color:#171c26; font:10pt/1.38 "DFKai-SB","標楷體","BiauKai","KaiTi",serif; }
h1,h2,p { margin:0; }
h1 { font-size:19pt; letter-spacing:1px; line-height:1.35; }
h2 { font-size:12pt; color:#203f60; border-bottom:1px solid #c3cfda; padding-bottom:2mm; margin:5mm 0 3mm; break-after:avoid; }
h2 small { font-size:9pt; font-weight:normal; color:#64748b; }
.cover { border-bottom:2px solid #284869; padding-bottom:4mm; margin-bottom:4mm; }
.subtitle { color:#365876; font-size:11pt; margin-top:2mm; }
.meta { color:#59606b; font-size:9pt; margin-top:2mm; }
.question { border:1px solid #d5dde5; border-radius:1.5mm; padding:1.7mm 2.3mm; margin-bottom:1.5mm; break-inside:avoid; }
.stem { display:grid; grid-template-columns:max-content minmax(0,1fr); font-size:10.3pt; margin-bottom:.5mm; }
.stem b { color:#17466b; }
.stem span { min-width:0; overflow-wrap:anywhere; }
.tag { font-size:8pt; color:#385d77; border:1px solid #bccbd5; border-radius:2mm; padding:0 .9mm; margin-left:2mm; }
.tag.warning { color:#874327; border-color:#c9a58f; }
.choices { margin-left:6mm; }
.choices.short { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); column-gap:3mm; }
.choices div { min-width:0; overflow-wrap:anywhere; }
.key { break-before:page; }
.key h2 { font-size:16pt; }
.key p { color:#4f5f70; font-size:9pt; margin-bottom:5mm; }
.key-grid { display:grid; grid-template-columns:repeat(10,1fr); gap:.8mm 1mm; }
.key-item { display:flex; justify-content:space-between; border-bottom:1px solid #dce3e9; padding:.5mm .4mm; font-size:8.5pt; }
"""
    return (
        '<!doctype html><html lang="zh-TW"><head><meta charset="utf-8">'
        f'<title>{e(title)}｜無解析版</title><style>{css}</style></head><body>'
        '<header class="cover">'
        f'<h1>{e(title)}</h1><p class="subtitle">無解析版 · 答案在末頁</p>'
        f'<p class="meta">共 {len(ordered)} 題 · 是非 {len(tf)} 題 · 選擇 {len(mc)} 題</p>'
        '</header>'
        f'<main id="questions">{"".join(sections)}</main>'
        '<section class="key"><h2>答案速查</h2>'
        '<p>「—」表示舊制或條件衝突，不作現行計分；'
        '「†」表示答案尚待完整核實，請以當梯授課與現行法規為準。</p>'
        f'<div class="key-grid">{"".join(answers)}</div></section></body></html>'
    )


def main():
    PDF.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for bank, data_file, title, pdf_name, html_name in CONFIGS:
            data = json.loads((ROOT / data_file).read_text(encoding="utf-8"))
            questions = data["questions"]
            if bank.startswith("recruit"):
                authored = bank.endswith("authored")
                questions = [q for q in questions if
                             (q.get("provenance", {}).get("class") == "site_authored") == authored]
            else:
                questions = [q for q in questions if q.get("status") != "outdated"]
            markup = booklet(title, questions)
            html_path, pdf_path = PDF / html_name, PDF / pdf_name
            html_path.write_text(markup, encoding="utf-8", newline="\n")
            page = browser.new_page()
            page.goto(html_path.as_uri())
            page.pdf(path=str(pdf_path), format="A4", print_background=True, prefer_css_page_size=True)
            page.close()
            try:
                import fitz
                doc = fitz.open(pdf_path)
                optimized = pdf_path.with_suffix(".pdf.opt")
                doc.save(optimized, garbage=4, deflate=True, clean=True)
                doc.close()
                os.replace(optimized, pdf_path)
            except ImportError:
                pass
            print(f"{pdf_path.name}: {len(questions)} 題，{pdf_path.stat().st_size // 1024} KB")
        browser.close()


if __name__ == "__main__":
    main()
