# -*- coding: utf-8 -*-
"""
從全國法規資料庫 (law.moj.gov.tw) 下載本站引用法規的現行全文，輸出 data/laws.json。

用法：python scripts/fetch_laws.py
- 以 curl 逐一下載 LawAll.aspx 頁面（Python 內建 urllib 在部分環境會被憑證驗證擋下）。
- 只解析官方頁面上的法規名稱、修正日期、章節與條文，不做任何改寫。
- 下載完成後請再執行 scripts/generate_bundle.py 重新產生前端資料包。
"""
import datetime
import html
import json
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "data", ".law_cache")
OUT = os.path.join(ROOT, "data", "laws.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

# (pcode, 分組) —— 分組決定顯示在新訓或 EMT-1 的法規全文頁
LAWS = [
    ("D0040017", "recruit"),  # 替代役實施條例
    ("D0040018", "recruit"),  # 替代役實施條例施行細則
    ("D0040016", "recruit"),  # 役男申請服替代役辦法
    ("D0040020", "recruit"),  # 一般替代役役男訓練服勤管理辦法
    ("D0040021", "recruit"),  # 替代役役男請假規則
    ("D0040028", "recruit"),  # 替代役役男獎懲辦法
    ("D0040019", "recruit"),  # 替代役役男輔導教育辦法
    ("D0040024", "recruit"),  # 替代役役男權利實施辦法
    ("D0040027", "recruit"),  # 替代役役男保險及醫療實施辦法
    ("D0040025", "recruit"),  # 替代役役男撫卹實施辦法
    ("D0040029", "recruit"),  # 替代役役男薪俸地域加給及主副食費發放辦法
    ("D0040022", "recruit"),  # 替代役役籍管理辦法
    ("D0040026", "recruit"),  # 替代役役男提前退役辦法
    ("D0040032", "recruit"),  # 服兵役役男家屬生活扶助實施辦法
    ("D0050131", "recruit"),  # 志願服務法
    ("L0020045", "emt"),      # 緊急醫療救護法
    ("L0020141", "emt"),      # 救護技術員管理辦法
]

TOKEN = re.compile(
    r'<div class="h3 char-(\d)">(.*?)</div>'                       # 章節標題
    r'|<div class="col-no">\s*<a[^>]*name="([^"]+)"[^>]*>(.*?)</a>'  # 條號
    r'|<div class="line-(\d{4})[^"]*">(.*?)</div>'                  # 條文行
    r'|<pre[^>]*>(.*?)</pre>',                                      # 附表或公式
    re.S,
)


def clean(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).replace("　", " ").strip()


def download(pcode):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, pcode + ".html")
    url = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=" + pcode
    for attempt in range(3):
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "60", "-A", UA, "-o", path, url],
            capture_output=True,
        )
        if result.returncode == 0 and os.path.getsize(path) > 5000:
            break
        time.sleep(3)
    else:
        raise RuntimeError("下載失敗：" + pcode)
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read(), url


def parse(page, pcode, url, group):
    name = re.search(r"<title>\s*(.*?)-全國法規資料庫", page, re.S)
    date = re.search(r"<th>(修正日期|發布日期|公布日期)：</th>\s*<td[^>]*>\s*(.*?)\s*</td>", page, re.S)
    if not name or not date:
        raise RuntimeError("找不到法規名稱或日期：" + pcode)
    if "廢止" in clean(page[page.find("<table") : page.find("law-reg-content")]):
        raise RuntimeError("法規已廢止，請更換 pcode：" + pcode)

    body = page[page.find('class="law-reg-content"') :]
    end = body.find('<div class="text-right">')
    if end > 0:
        body = body[:end]

    chapters = []
    current = {"title": "", "articles": []}
    article = None
    for m in TOKEN.finditer(body):
        if m.group(1) is not None:
            if current["articles"] or current["title"]:
                chapters.append(current)
            current = {"title": re.sub(r"\s+", " ", clean(m.group(2))), "articles": []}
            article = None
        elif m.group(3) is not None:
            article = {"no": m.group(3), "label": re.sub(r"\s+", " ", clean(m.group(4))), "lines": []}
            current["articles"].append(article)
        elif m.group(5) is not None and article is not None:
            text = clean(m.group(6))
            if text:
                article["lines"].append([int(m.group(5)) // 2, text])
        elif m.group(7) is not None and article is not None:
            text = clean(m.group(7))
            if text:
                article["lines"].append([0, text])
    if current["articles"] or current["title"]:
        chapters.append(current)

    count = sum(len(c["articles"]) for c in chapters)
    if count == 0:
        raise RuntimeError("沒有解析到條文：" + pcode)
    empty = [a["label"] for c in chapters for a in c["articles"] if not a["lines"]]
    if empty:
        raise RuntimeError("%s 有條文沒有內容：%s" % (pcode, empty))
    return {
        "pcode": pcode,
        "group": group,
        "name": name.group(1).strip(),
        "date_label": date.group(1),
        "date": re.sub(r"\s+", " ", clean(date.group(2))),
        "url": url,
        "article_count": count,
        "chapters": chapters,
    }


def main():
    laws = []
    for pcode, group in LAWS:
        page, url = download(pcode)
        law = parse(page, pcode, url, group)
        laws.append(law)
        print("%s %s｜%s %s｜%d 條" % (pcode, law["name"], law["date_label"], law["date"], law["article_count"]))
        time.sleep(1)
    data = {
        "source": "全國法規資料庫 https://law.moj.gov.tw/",
        "fetched_at": datetime.date.today().isoformat(),
        "laws": laws,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print("已寫入", OUT)


if __name__ == "__main__":
    main()
