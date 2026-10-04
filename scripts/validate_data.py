# -*- coding: utf-8 -*-
"""
資料檢查：題庫結構、來源連結、用品清單與資料包是否一致。
有錯誤時以非 0 結束，方便在提交前擋下壞資料。

用法：python scripts/validate_data.py
"""
import difflib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors, warnings = [], []
BANNED = ["最新", "100% 正確", "正確率 100%", "全員必考", "必考"]


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def strings(node):
    if isinstance(node, dict):
        for v in node.values():
            yield from strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from strings(v)
    elif isinstance(node, str):
        yield node


def check_bank(name, data, categories, law_names):
    seen = set()
    for q in data["questions"]:
        qid = q.get("id", "?")
        if qid in seen:
            errors.append("%s 題號重複：%s" % (name, qid))
        seen.add(qid)
        for key in ("id", "type", "category", "question", "answer", "source", "review"):
            if q.get(key) in (None, ""):
                errors.append("%s %s 缺少欄位 %s" % (name, qid, key))
        if categories and q.get("category") not in categories:
            errors.append("%s %s 章節不明：%s" % (name, qid, q.get("category")))
        if q["type"] == "true_false":
            if q["answer"] not in ("O", "X"):
                errors.append("%s %s 是非題答案必須是 O 或 X" % (name, qid))
        elif q["type"] == "multiple_choice":
            options = q.get("options", [])
            if not 3 <= len(options) <= 5 or len(set(options)) != len(options):
                errors.append("%s %s 選項數量或內容異常" % (name, qid))
            if any(re.match(r"^\s*[（(][A-Ea-e][）)]", option) for option in options):
                errors.append("%s %s 選項資料含多餘標號，PDF 會重複顯示" % (name, qid))
            if not (isinstance(q["answer"], int) and 0 <= q["answer"] < len(options)):
                errors.append("%s %s 正解索引超出範圍" % (name, qid))
        else:
            errors.append("%s %s 題型不明：%s" % (name, qid, q["type"]))
        url = q.get("source_url", "")
        if q.get("review") == "law" and "LawSingle.aspx" not in url:
            errors.append("%s %s 標為有條文依據，但連結不是單一條文" % (name, qid))
        if url == "" and q.get("source_kind") == "past":
            pass  # 查無法規依據的歷屆題沒有來源連結
        elif not url.startswith(("https://", "http://")):
            errors.append("%s %s 來源連結格式錯誤" % (name, qid))
        pcode = re.search(r"law\.moj\.gov\.tw.*pcode=([A-Z]\d+)", url, re.I)
        if pcode:
            law = law_names.get(pcode.group(1).upper())
            if not law:
                errors.append("%s %s 連到未收錄的法規代碼 %s" % (name, qid, pcode.group(1)))
            elif law not in q["source"]:
                errors.append("%s %s 來源名稱「%s」與連結的法規「%s」不符" % (name, qid, q["source"], law))
        if q.get("status") == "outdated" and not q.get("status_note"):
            errors.append("%s %s 標為舊法題但沒有說明" % (name, qid))
        if not q.get("explanation") and q.get("status") != "outdated":
            warnings.append("%s %s 沒有解析" % (name, qid))
    return seen


def near_duplicates(questions):
    norm = lambda t: re.sub(r"[\s，。、：；？！「」（）()]", "", t)
    texts = [(q["id"], norm(q["question"])) for q in questions]
    pairs = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i][1], texts[j][1]
            if abs(len(a) - len(b)) < 8 and difflib.SequenceMatcher(None, a, b).ratio() > 0.9:
                pairs.append((texts[i][0], texts[j][0]))
    return pairs


def main():
    laws = load("laws.json")
    law_names = {l["pcode"]: l["name"] for l in laws["laws"]}
    for law in laws["laws"]:
        if not law["date"] or law["article_count"] < 1:
            errors.append("法規資料不完整：%s" % law["pcode"])
        flagged = sum(1 for c in law["chapters"] for a in c["articles"] if a.get("attachment"))
        if flagged and not law.get("attachments"):
            errors.append("%s 有條文標示附件，但附件清單是空的" % law["name"])
        for att in law.get("attachments", []):
            if not att["fetched"]:
                errors.append("%s 的附件「%s」沒有取得成功" % (law["name"], att["name"]))
        path = os.path.join(ROOT, "data", "laws", law["pcode"] + ".js")
        expected = json.dumps(law, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        if not os.path.exists(path) or expected not in open(path, encoding="utf-8").read():
            errors.append("data/laws/%s.js 與 laws.json 不一致，請重跑 generate_bundle.py" % law["pcode"])

    recruit = load("questions.json")
    emt = load("emt_questions.json")
    practice = load("emt_practice_questions.json")
    study = load("study_data.json")
    emt_study = load("emt_study_data.json")

    check_bank("新訓", recruit, {"regulations", "rights", "management", "volunteer", "shooting"}, law_names)
    check_bank("EMT", emt, None, law_names)
    check_bank("EMT 自編練習", practice, None, law_names)
    if len(practice["questions"]) != 96:
        errors.append("EMT 自編練習應有 96 題")
    if set(q["id"] for q in emt["questions"]) & set(q["id"] for q in practice["questions"]):
        errors.append("EMT 回憶考點與自編練習題號重複")
    if any(q.get("provenance", {}).get("class") != "site_authored" for q in practice["questions"]):
        errors.append("EMT 自編練習有題目被標成非自編題")

    stats = recruit["stats"]
    actual = {
        "total": len(recruit["questions"]),
        "true_false": sum(q["type"] == "true_false" for q in recruit["questions"]),
        "multiple_choice": sum(q["type"] == "multiple_choice" for q in recruit["questions"]),
    }
    for key, value in actual.items():
        if stats.get(key) != value:
            errors.append("questions.json stats.%s=%s 與實際 %s 不符" % (key, stats.get(key), value))

    for name, data in (("questions", recruit), ("emt_questions", emt), ("emt_practice_questions", practice), ("study_data", study), ("emt_study_data", emt_study)):
        for text in strings(data):
            for word in BANNED:
                if word in text:
                    errors.append("%s.json 含未經佐證的斷言「%s」：%s" % (name, word, text[:40]))

    ids = set()
    for cat in study["packing_list"]["categories"]:
        if cat["kind"] not in ("pack", "info"):
            errors.append("用品清單分類型別錯誤：%s" % cat["id"])
        for item in cat["items"]:
            if item["id"] in ids:
                errors.append("用品清單 id 重複：%s" % item["id"])
            ids.add(item["id"])
            if cat["kind"] == "pack" and "must" not in item:
                errors.append("用品清單 %s 缺少 must" % item["id"])
            if re.search(r"[\U0001F000-\U0001FAFF❌]", item["name"]):
                errors.append("用品清單名稱含表情符號：%s" % item["id"])

    bundle_path = os.path.join(ROOT, "data", "data_bundle.js")
    with open(bundle_path, encoding="utf-8") as f:
        bundle = f.read()
    for var, data in (("APP_QUESTIONS", recruit), ("APP_STUDY_DATA", study), ("APP_EMT_QUESTIONS", emt), ("APP_EMT_PRACTICE_QUESTIONS", practice), ("APP_EMT_STUDY_DATA", emt_study)):
        expected = "window.%s = %s;" % (var, json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
        if expected not in bundle:
            errors.append("data_bundle.js 的 %s 與 JSON 不一致，請重跑 generate_bundle.py" % var)

    # 逐題審核表必須涵蓋每一題，而且核定答案與題庫一致
    import csv
    import glob
    import hashlib
    audits = sorted(glob.glob(os.path.join(ROOT, "docs", "逐題審核_*.csv")))
    if not audits:
        errors.append("找不到 docs/逐題審核_*.csv")
    else:
        with open(audits[-1], encoding="utf-8-sig", newline="") as f:
            rows = {row["題號"]: row for row in csv.DictReader(f)}
        for q in recruit["questions"] + emt["questions"] + practice["questions"]:
            row = rows.get(q["id"])
            answer = q["answer"] if q["type"] == "true_false" else q["options"][q["answer"]]
            if not row:
                errors.append("逐題審核表缺少 %s" % q["id"])
            elif row["核定答案"] != str(answer) or row["題幹"] != q["question"]:
                errors.append("逐題審核表的 %s 與題庫不一致，請重跑 apply_review" % q["id"])
        if len(rows) != len(recruit["questions"]) + len(emt["questions"]) + len(practice["questions"]):
            errors.append("逐題審核表列數 %d 與題數不符" % len(rows))

    # 模擬考只抽已核實的題目：確認數量足夠，且沒有舊法題或待補證題混入
    allowed = {"law", "partial", "unverified", "experience", "outdated", "textbook", "textbook114", "recalled", "recalled_conflict", "imported", "imported_conflict"}
    origins = {"compiled_verbatim", "compiled_minor", "compiled_adapted", "paper_verbatim", "paper_adapted", "recalled", "uploaded", "site_authored"}

    def in_exam(name, q):
        cls = q.get("provenance", {}).get("class", "")
        if q.get("status") == "outdated":
            return False
        return (cls.startswith(("compiled", "paper_")) and q.get("review") == "law") if name == "新訓" else cls in ("recalled", "uploaded") and q.get("review") not in ("recalled_conflict", "imported_conflict")

    # 205T A 卷 50 題各對應一筆站內題，不製造重複題；展示標籤不再使用「回憶」。
    p10 = [(q, e["source_item"]) for q in recruit["questions"]
           for e in q.get("exam_evidence", []) if e.get("source_id") == "P10"]
    if len(p10) != 50 or len({item for _, item in p10}) != 50 or len({q["id"] for q, _ in p10}) != 50:
        errors.append("205T A 卷應逐題對應 50 個不同卷內題號及 50 個不同站內題 ID")
    if any("回憶" in q.get("exam_tag", "") or "回憶" in q.get("provenance", {}).get("label", "")
           for q, _ in p10):
        errors.append("205T A 卷題仍顯示回憶標籤")

    for name, data, need in (("新訓", recruit, 50), ("EMT", emt, 40)):
        for q in data["questions"]:
            if q.get("review") not in allowed:
                errors.append("%s %s 的查核狀態不明：%s" % (name, q["id"], q.get("review")))
            if q.get("provenance", {}).get("class") not in origins:
                errors.append("%s %s 沒有來源等級，請重跑 build_provenance.py" % (name, q["id"]))
            if (q.get("status") == "outdated") != (q.get("review") == "outdated"):
                errors.append("%s %s 的舊法標記不一致" % (name, q["id"]))
        pool = [q for q in data["questions"] if in_exam(name, q)]
        if len(pool) < need:
            errors.append("%s 可列入模擬考的題目只有 %d 題，不足 %d 題" % (name, len(pool), need))
        # 模擬考題池裡，正解不應該靠「最長」或「唯一帶英文」就猜得出來
        mc = [q for q in pool if q["type"] == "multiple_choice"]
        longest = sum(1 for q in mc if len(q["options"][q["answer"]]) > max(
            len(o) for i, o in enumerate(q["options"]) if i != q["answer"]))
        english = sum(1 for q in mc if re.search(r"[A-Za-z]{2,}", q["options"][q["answer"]]) and not any(
            re.search(r"[A-Za-z]{2,}", o) for i, o in enumerate(q["options"]) if i != q["answer"]))
        print("%s 模擬考題池 %d 題（選擇題 %d）：正解是最長選項 %d 題、正解是唯一含英文的選項 %d 題" % (
            name, len(pool), len(mc), longest, english))
        if mc and (longest / len(mc) > 0.4 or english / len(mc) > 0.1):
            errors.append("%s 模擬考題池的選項有可猜的規律（最長 %d、唯一英文 %d／%d）" % (name, longest, english, len(mc)))

    # 站方自己寫的選項不能留下盲猜線索：正解不可常是最長、不可是唯一帶英文、題幹選項不夾英文註解，
    # 正解位置也不能集中在同一個選項（PDF 是照存檔順序印的）
    gloss = re.compile(r"[（(][A-Za-z][A-Za-z0-9 ',/.\-]*[a-z]{3}[A-Za-z0-9 ',/.\-]*[）)]")
    word = re.compile(r"[A-Za-z]{2,}")
    for name, pool in (
        ("EMT 自編練習", practice["questions"]),
        ("EMT 回憶考點（站方補寫選項）", [q for q in emt["questions"] if q.get("provenance", {}).get("options_by") == "site"]),
        ("新訓站方自編選擇題", [q for q in recruit["questions"] if q["type"] == "multiple_choice"
                         and q.get("provenance", {}).get("class") == "site_authored"]),
    ):
        longest = english = 0
        position = [0, 0, 0, 0, 0]
        for q in pool:
            options, answer = q["options"], q["answer"]
            others = [o for i, o in enumerate(options) if i != answer]
            longest += len(options[answer]) > max(len(o) for o in others)
            english += bool(word.search(options[answer])) and not any(word.search(o) for o in others)
            position[answer] += 1
            if gloss.search(q["question"]) or any(gloss.search(o) for o in options):
                errors.append("%s 的題幹或選項夾了英文註解，站方撰寫的題目請只用中文名稱" % q["id"])
            if max(len(o) for o in options) - min(len(o) for o in options) > 6:
                errors.append("%s 的選項長短差太多（超過 6 個字），請改寫成相近長度" % q["id"])
        print("%s %d 題：正解是唯一最長 %d 題、唯一含英文 %d 題、正解位置 A/B/C/D = %s" % (
            name, len(pool), longest, english, "/".join(str(n) for n in position[:4])))
        if longest / len(pool) > 0.25 or english:
            errors.append("%s 的正解有可猜的規律（唯一最長 %d、唯一英文 %d／%d）" % (name, longest, english, len(pool)))
        if max(position) / len(pool) > 0.45:
            errors.append("%s 的正解位置過度集中（%s）" % (name, position[:4]))

    # PDF 必須在資料最後一次修改之後重新產生（scripts/build_all.py 會寫入 pdf/manifest.json）
    manifest_path = os.path.join(ROOT, "pdf", "manifest.json")
    digest = lambda name: hashlib.sha1(open(os.path.join(ROOT, "data", name), "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    if not os.path.exists(manifest_path):
        errors.append("找不到 pdf/manifest.json，請執行 scripts/build_all.py")
    else:
        manifest = json.load(open(manifest_path, encoding="utf-8"))
        for name in ("questions.json", "emt_questions.json", "emt_practice_questions.json", "study_data.json"):
            if manifest.get("sources", {}).get(name) != digest(name):
                errors.append("PDF 不是用目前的 %s 產生的，請執行 scripts/build_all.py" % name)
    for html_name, data in (("questions_biaukai.html", recruit), ("questions_authored_biaukai.html", recruit),
                            ("questions_plain.html", recruit), ("questions_authored_plain.html", recruit),
                            ("emt_questions_biaukai.html", emt), ("emt_practice_biaukai.html", practice),
                            ("emt_questions_plain.html", emt), ("emt_practice_plain.html", practice)):
        page = open(os.path.join(ROOT, "pdf", html_name), encoding="utf-8").read()
        # EMT 的 PDF 不印回憶者註明已過時的題目
        skip = lambda q: html_name.startswith("emt") and q.get("status") == "outdated"
        subset = [q for q in data["questions"] if not html_name.startswith("questions_") or ((q.get("provenance", {}).get("class") == "site_authored") == html_name.startswith("questions_authored"))]
        missing = [q["id"] for q in subset if ('data-qid="%s"' % q["id"]) not in page and not skip(q)]
        if missing:
            errors.append("%s 缺少或未更新的題目：%s" % (html_name, missing[:5]))
        unexpected = [q["id"] for q in data["questions"] if q not in subset and ('data-qid="%s"' % q["id"]) in page]
        if unexpected:
            errors.append("%s 混入另一冊的題目：%s" % (html_name, unexpected[:5]))
        if html_name.endswith("_plain.html") and ("【解析】" in page or 'class="key"' not in page):
            errors.append("%s 必須隱藏逐題解析，並把答案集中於末節" % html_name)
        if html_name.endswith("_plain.html") and 'class="key-item"' in page.split('<main id="questions">', 1)[-1].split('</main>', 1)[0]:
            errors.append("%s 題目頁混入答案速查" % html_name)
        if html_name.endswith("_plain.html"):
            expected = sum(not skip(q) for q in subset)
            if page.count('data-qid="') != expected or page.count('class="key-item"') != expected:
                errors.append("%s 題目與末頁答案筆數不一致" % html_name)

    dups = near_duplicates(recruit["questions"])
    print("新訓 %d 題（是非 %d、選擇 %d），EMT %d 題，法規 %d 部" % (
        actual["total"], actual["true_false"], actual["multiple_choice"], len(emt["questions"]), len(laws["laws"])))
    print("沒有解析的題目：%d 題" % sum("沒有解析" in w for w in warnings))
    print("題幹高度相似的題組：%d 組 %s" % (len(dups), dups))
    for message in errors:
        print("錯誤：", message)
    print("結果：%d 個錯誤" % len(errors))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
