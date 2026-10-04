# -*- coding: utf-8 -*-
"""
從全國法規資料庫 (law.moj.gov.tw) 下載本站引用法規的現行全文與附件，輸出 data/laws.json。

用法：
  python scripts/fetch_laws.py            下載並覆寫 data/laws.json
  python scripts/fetch_laws.py --cached   只重新解析已下載的頁面，不連線
  python scripts/fetch_laws.py --check    下載後與 data/laws.json 逐條比對，列出差異與受影響題號；
                                          有差異時以非 0 結束，不覆寫資料

- 以 curl 下載（Python 內建 urllib 在部分環境會被憑證驗證擋下）。
- 只解析官方頁面上的法規名稱、修正日期、章節與條文，不做任何改寫。
- 附件（附表）逐件下載；PDF 會擷取文字供站內搜尋，表格排版以官方原件為準。
- 下載完成後請執行 scripts/generate_bundle.py 重新產生前端資料包。
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
BASE = "https://law.moj.gov.tw/LawClass/"
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
    ("D0040033", "recruit"),  # 替代役役男服役期滿後召集服勤實施辦法
    ("D0040038", "recruit"),  # 替代役役男出境管理辦法
    ("D0050131", "recruit"),  # 志願服務法
    ("L0020045", "emt"),      # 緊急醫療救護法
    ("L0020047", "emt"),      # 緊急醫療救護法施行細則（大量傷病患定義）
    ("L0020141", "emt"),      # 救護技術員管理辦法
    ("K0040013", "emt"),      # 道路交通安全規則（EMT-LAW-11 引用第93條）
]

TOKEN = re.compile(
    r'<div class="h3 char-(\d)">(.*?)</div>'                       # 章節標題
    r'|<div class="col-no">((?:(?!</div>).)*?)<a[^>]*name="([^"]+)"[^>]*>(.*?)</a>'  # 條號（有附件的條文前面多一個圖示）
    r'|<div class="line-(\d{4})[^"]*">(.*?)</div>'                  # 條文行
    r'|<pre[^>]*>(.*?)</pre>',                                      # 附表或公式
    re.S,
)
ATTACHMENT = re.compile(r'LawGetFile\.ashx\?FileId=(\d+)[^"]*"[^>]*>([^<]+)</a>')


def clean(text):
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).replace("　", " ").strip()


def curl(url, path, min_size):
    for attempt in range(6):
        result = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "90", "-A", UA, "-o", path, url],
            capture_output=True,
        )
        if result.returncode == 0 and os.path.exists(path) and os.path.getsize(path) > min_size:
            return True
        time.sleep(5 * (attempt + 1))  # 官方網站會暫時擋下連續請求，逐次拉長等待
    return False


def download(pcode, use_cache):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, pcode + ".html")
    url = BASE + "LawAll.aspx?pcode=" + pcode
    if not (use_cache and os.path.exists(path)):
        if not curl(url, path, 5000):
            raise RuntimeError("下載失敗：" + pcode)
        time.sleep(2)
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read(), url


def pdf_text(path):
    """擷取 PDF 文字。沒有安裝 pymupdf 或擷取失敗時回傳空字串（附件仍會列出並連到官方原件）。"""
    try:
        import pymupdf
    except ImportError:
        return 0, ""
    try:
        doc = pymupdf.open(path)
        text = "\n".join(page.get_text() for page in doc)
        return len(doc), re.sub(r"[ \t]+\n", "\n", text).strip()
    except Exception:
        return 0, ""


def fetch_attachments(page):
    """逐件下載官方頁列出的附件。回傳的每一筆都標示是否取得成功，取得失敗不會被當成完整。"""
    items = []
    for file_id, raw_name in ATTACHMENT.findall(page):
        name = re.sub(r"\s+", " ", html.unescape(raw_name).replace("　", " ")).strip()
        fmt = name.rsplit(".", 1)[-1].upper() if "." in name else ""
        url = BASE + "LawGetFile.ashx?FileId=%s&lan=C" % file_id
        path = os.path.join(CACHE, "att_%s.%s" % (file_id, fmt.lower() or "bin"))
        ok = os.path.exists(path) and os.path.getsize(path) > 500
        if not ok:
            ok = curl(url, path, 500)
            time.sleep(1)
        item = {"file_id": file_id, "name": name, "format": fmt, "url": url, "fetched": bool(ok),
                "bytes": os.path.getsize(path) if ok else 0}
        if ok and fmt == "PDF":
            item["pages"], item["text"] = pdf_text(path)
        items.append(item)
    return items


def parse(page, pcode, url, group):
    name = re.search(r"<title>\s*(.*?)-全國法規資料庫", page, re.S)
    date = re.search(r"<th>(修正日期|發布日期|公布日期)：</th>\s*<td[^>]*>\s*(.*?)\s*</td>", page, re.S)
    if not name or not date:
        raise RuntimeError("找不到法規名稱或日期：" + pcode)
    header = clean(page[page.find("<table"): page.find("law-reg-content")])
    if "廢止" in header or "停止適用" in header:
        raise RuntimeError("法規已廢止或停止適用，請重新檢視引用它的題目：" + pcode)

    body = page[page.find('class="law-reg-content"'):]
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
        elif m.group(4) is not None:
            article = {"no": m.group(4), "label": re.sub(r"\s+", " ", clean(m.group(5))), "lines": []}
            if "附件" in m.group(3):
                article["attachment"] = True
            current["articles"].append(article)
        elif m.group(6) is not None and article is not None:
            text = clean(m.group(7))
            if text:
                article["lines"].append([int(m.group(6)) // 2, text])
        elif m.group(8) is not None and article is not None:
            text = clean(m.group(8))
            if text:
                article["lines"].append([0, text])
    if current["articles"] or current["title"]:
        chapters.append(current)

    count = sum(len(c["articles"]) for c in chapters)
    expected = len(re.findall(r"第 [\d\-]+ 條</a>", body))
    if count == 0 or count != expected:
        raise RuntimeError("%s 解析出 %d 條，但頁面上有 %d 條" % (pcode, count, expected))
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


def fetch_all(use_cache):
    laws = []
    for pcode, group in LAWS:
        page, url = download(pcode, use_cache)
        law = parse(page, pcode, url, group)
        law["attachments"] = fetch_attachments(page)
        laws.append(law)
        missing = [a["name"] for a in law["attachments"] if not a["fetched"]]
        print("%s %s｜%s %s｜%d 條｜附件 %d 件%s" % (
            pcode, law["name"], law["date_label"], law["date"], law["article_count"],
            len(law["attachments"]), "（%d 件取得失敗）" % len(missing) if missing else ""))
    return {
        "source": "全國法規資料庫 https://law.moj.gov.tw/",
        "fetched_at": datetime.date.today().isoformat(),
        "laws": laws,
    }


def flatten(law):
    """{條號: 條文各行} —— 逐條比對用。"""
    out = {}
    for chapter in law["chapters"]:
        for art in chapter["articles"]:
            out[art["no"]] = [chapter["title"]] + [text for _, text in art["lines"]]
    return out


def affected_questions(pcode, article_no=None):
    hits = []
    for name in ("questions.json", "emt_questions.json"):
        with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
            for q in json.load(f)["questions"]:
                url = q.get("source_url", "")
                if "pcode=" + pcode in url and (article_no is None or url.endswith("flno=" + article_no)):
                    hits.append(q["id"])
    return hits


def check(fresh):
    """與現有 data/laws.json 逐條比較。回傳差異筆數。"""
    with open(OUT, encoding="utf-8") as f:
        old = {l["pcode"]: l for l in json.load(f)["laws"]}
    diffs = 0
    for law in fresh["laws"]:
        before = old.get(law["pcode"])
        if not before:
            print("新增法規：%s %s" % (law["pcode"], law["name"]))
            diffs += 1
            continue
        for key in ("name", "date", "article_count"):
            if before[key] != law[key]:
                print("%s %s：%s 由「%s」變為「%s」；引用題號 %s" % (
                    law["pcode"], law["name"], key, before[key], law[key], affected_questions(law["pcode"])))
                diffs += 1
        a, b = flatten(before), flatten(law)
        for no in sorted(set(a) | set(b), key=lambda x: [int(n) for n in x.split("-")]):
            if a.get(no) != b.get(no):
                state = "新增" if no not in a else "刪除" if no not in b else "修改"
                print("%s 第 %s 條 %s；受影響題號 %s" % (law["name"], no, state, affected_questions(law["pcode"], no) or "無"))
                diffs += 1
        names_old = sorted(x["name"] for x in before.get("attachments", []))
        names_new = sorted(x["name"] for x in law["attachments"])
        if names_old != names_new:
            print("%s 附件清單有變動" % law["name"])
            diffs += 1
    for pcode in set(old) - {l["pcode"] for l in fresh["laws"]}:
        print("站內有、但清單已移除的法規：", pcode)
        diffs += 1
    total = sum(l["article_count"] for l in fresh["laws"])
    print("比對完成：%d 部、%d 條，差異 %d 筆" % (len(fresh["laws"]), total, diffs))
    return diffs


def main():
    fresh = fetch_all("--cached" in sys.argv)
    if "--check" in sys.argv:
        sys.exit(1 if check(fresh) else 0)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(fresh, f, ensure_ascii=False, indent=1)
    print("已寫入", OUT)


if __name__ == "__main__":
    main()
