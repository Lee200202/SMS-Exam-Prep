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
            if not 3 <= len(options) <= 4 or len(set(options)) != len(options):
                errors.append("%s %s 選項數量或內容異常" % (name, qid))
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
    study = load("study_data.json")
    emt_study = load("emt_study_data.json")

    check_bank("新訓", recruit, {"regulations", "rights", "management", "volunteer", "shooting"}, law_names)
    check_bank("EMT", emt, None, law_names)

    stats = recruit["stats"]
    actual = {
        "total": len(recruit["questions"]),
        "true_false": sum(q["type"] == "true_false" for q in recruit["questions"]),
        "multiple_choice": sum(q["type"] == "multiple_choice" for q in recruit["questions"]),
    }
    for key, value in actual.items():
        if stats.get(key) != value:
            errors.append("questions.json stats.%s=%s 與實際 %s 不符" % (key, stats.get(key), value))

    for name, data in (("questions", recruit), ("emt_questions", emt), ("study_data", study), ("emt_study_data", emt_study)):
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
    for var, data in (("APP_QUESTIONS", recruit), ("APP_STUDY_DATA", study), ("APP_EMT_QUESTIONS", emt), ("APP_EMT_STUDY_DATA", emt_study)):
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
        for q in recruit["questions"] + emt["questions"]:
            row = rows.get(q["id"])
            answer = q["answer"] if q["type"] == "true_false" else q["options"][q["answer"]]
            if not row:
                errors.append("逐題審核表缺少 %s" % q["id"])
            elif row["核定答案"] != str(answer) or row["題幹"] != q["question"]:
                errors.append("逐題審核表的 %s 與題庫不一致，請重跑 apply_review" % q["id"])
        if len(rows) != len(recruit["questions"]) + len(emt["questions"]):
            errors.append("逐題審核表列數 %d 與題數不符" % len(rows))

    # 模擬考只抽已核實的題目：確認數量足夠，且沒有舊法題或待補證題混入
    allowed = {"law", "partial", "unverified", "experience", "outdated", "textbook"}
    for name, data, pool, need in (("新訓", recruit, {"law"}, 50), ("EMT", emt, {"law", "textbook"}, 50)):
        for q in data["questions"]:
            if q.get("review") not in allowed:
                errors.append("%s %s 的查核狀態不明：%s" % (name, q["id"], q.get("review")))
            if (q.get("status") == "outdated") != (q.get("review") == "outdated"):
                errors.append("%s %s 的舊法標記不一致" % (name, q["id"]))
        count = sum(q.get("review") in pool for q in data["questions"])
        if count < need:
            errors.append("%s 可列入模擬考的題目只有 %d 題，不足 %d 題" % (name, count, need))

    # PDF 必須在資料最後一次修改之後重新產生（scripts/build_all.py 會寫入 pdf/manifest.json）
    manifest_path = os.path.join(ROOT, "pdf", "manifest.json")
    digest = lambda name: hashlib.sha1(open(os.path.join(ROOT, "data", name), "rb").read().replace(b"\r\n", b"\n")).hexdigest()
    if not os.path.exists(manifest_path):
        errors.append("找不到 pdf/manifest.json，請執行 scripts/build_all.py")
    else:
        manifest = json.load(open(manifest_path, encoding="utf-8"))
        for name in ("questions.json", "emt_questions.json", "study_data.json"):
            if manifest.get("sources", {}).get(name) != digest(name):
                errors.append("PDF 不是用目前的 %s 產生的，請執行 scripts/build_all.py" % name)
    for html_name, data in (("questions_biaukai.html", recruit), ("emt_questions_biaukai.html", emt)):
        page = open(os.path.join(ROOT, "pdf", html_name), encoding="utf-8").read()
        missing = [q["id"] for q in data["questions"] if q["question"] not in page]
        if missing:
            errors.append("%s 缺少或未更新的題目：%s" % (html_name, missing[:5]))

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
