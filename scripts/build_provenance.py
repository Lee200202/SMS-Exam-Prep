# -*- coding: utf-8 -*-
"""
逐題溯源：把題庫每一題對回它的歷史來源，分開記錄「有沒有來源」與「今天的答案對不對」。

新訓：對照 data/gdoc1_full.txt（「成功嶺新訓考古題」彙編，增補至 257T，2024/8/3 版；
      本站最初就是由這份文件整理而來。檔案是他人著作，沒有放進版本庫，要重跑需自行放回 data/）。
EMT ：目前沒有取得可逐字比對的成功嶺 EMT-1 考卷，全部標為站方自編的教材練習題。

輸出：
  docs/question_provenance.csv   368 題各一列
  data/questions.json、data/emt_questions.json 的 provenance 欄位

來源等級（provenance.class）：
  compiled_verbatim  彙編逐字收錄（只正規化空白、標點與全半形）
  compiled_minor     彙編收錄，本站只有錯字或用字微調
  compiled_adapted   彙編收錄，本站依現行法規改寫了題幹、選項或答案
  site_authored      彙編裡找不到，是站方（先前的 AI）自行編寫，沒有考過的證據

用法：python scripts/build_provenance.py
"""
import csv
import difflib
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_FILE = os.path.join(ROOT, "data", "gdoc1_full.txt")
SOURCE_ID = "R01"
SOURCE_NAME = "成功嶺新訓考古題彙編（增補至 257T，2024/8/3 版）"
REVIEW_DATE = "2026-10-04"
TAG = re.compile(r"[【［\[][^】］\]]*考[^】］\]]*[】］\]]")


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(ROOT, "data", name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def norm(text):
    text = TAG.sub("", text)
    text = text.translate(str.maketrans("（）：；，？！", "():;,?!"))
    return re.sub(r"[\s。.、,;:?!「」『』()\[\]【】\"'　]", "", text).lower()


def parse_source():
    """回傳彙編裡的是非題與選擇題：[{kind, no, stem, options, answer, tags, note}]

    彙編的版面是兩欄表格：答案欄在前、題目欄在後，匯出成文字後變成「答案幾行、題目幾行」。
    答案欄多半是 O／X 或選項編號，也可能帶括號（【3】、（4））；編者依新法更正過的題目
    會直接寫答案文字（十年、15日、35%）。題目欄除了題幹，常附同考點的另一種問法或附註。
    """
    lines = [l.strip() for l in open(SOURCE_FILE, encoding="utf-8-sig").read().split("\n")]
    start_tf = max(i for i, l in enumerate(lines) if l == "是非題")
    start_mc = max(i for i, l in enumerate(lines) if l == "選擇題")
    end_mc = next(i for i, l in enumerate(lines) if i > start_mc and l == "替代役實施條例")
    items = []
    for kind, lo, hi in (("TF", start_tf, start_mc), ("MC", start_mc, end_mc)):
        between, current = [], None
        for line in lines[lo + 1:hi]:
            if not line or line in ("Ans", "Question"):
                continue
            m = re.match(r"^(\d+)\.\s*(.+)$", line)
            expected = (current["no"] + 1) if current else 1
            if m and int(m.group(1)) == expected:
                # 兩題之間的短行是這一題的答案欄，長行是上一題題目欄的後續文字
                short = [x for x in between if len(x) <= 6]
                if current is not None:
                    current["extra"] = " ".join(x for x in between if len(x) > 6)
                current = {"kind": kind, "no": expected, "first": m.group(2), "extra": "", "cell": short}
                items.append(current)
                between = []
            else:
                between.append(line)
    for it in items:
        first, extra, cell = it.pop("first"), it.pop("extra"), it.pop("cell")
        it["tags"] = "".join(TAG.findall(first + extra))
        tokens = [re.sub(r"[【】（）()\[\]\s]", "", x) for x in cell]
        body = first
        if it["kind"] == "MC":
            head = TAG.split(first)
            body = next((part for part in head if re.search(r"[(（]1[)）]", part)), TAG.sub("", first))
        notes = re.findall(r"[(（](?:按：|\d{8}修正)[^)）]*[)）]|\[\d+\]|☞.*$", body)
        for note in notes:
            body = body.replace(note, "")
        parts = re.split(r"\s*[(（]([1-4])[)）]\s*", TAG.sub("", body))
        it["stem"] = parts[0].strip()
        it["options"] = [parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)]
        it["note"] = " ".join(notes)
        if it["options"]:
            # 選擇題：答案是選項編號，或編者改寫的答案文字
            it["answer"] = next((x for x in tokens if re.fullmatch(r"[1-4]", x)), None) or next(
                (x for x in tokens if x not in ("O", "X", "選擇", "是非")), "")
        else:
            it["answer"] = next((x for x in tokens if x in ("O", "X")), "")
    return items


def previous_site():
    """改版前（提交 84f23d3）的網站題目，用來分辨「彙編原文」與「本站後來的改寫」。"""
    out = {}
    for name in ("questions.json", "emt_questions.json"):
        raw = subprocess.run(["git", "-C", ROOT, "show", "84f23d3:data/" + name], capture_output=True).stdout
        for q in json.loads(raw.decode("utf-8"))["questions"]:
            out[q["id"]] = q
    return out


def full_text(stem, options):
    return norm(stem) + "|" + "|".join(norm(o) for o in options)


def answer_text(q):
    if q["type"] == "true_false":
        return q["answer"]
    return q["options"][q["answer"]]


def match(q, old, items):
    """用改版前的題文找彙編裡最像的一題。"""
    has_options = q["type"] != "true_false"
    base = old or q
    target = full_text(base["question"], base.get("options", []))
    best, score = None, 0.0
    for it in items:
        if bool(it["options"]) != has_options:
            continue
        cand = full_text(it["stem"], it["options"])
        if abs(len(cand) - len(target)) > max(len(target), len(cand)) * 0.6:
            continue
        ratio = difflib.SequenceMatcher(None, target, cand, autojunk=False).ratio()
        if ratio > score:
            best, score = it, ratio
    return best, score


def source_answer_text(item):
    """彙編標的答案：是非題為 O／X；選擇題為選項文字。答案欄若是編者依新法改寫的文字，原樣回傳。"""
    answer = item["answer"]
    if item["options"] and re.fullmatch(r"[1-4]", answer) and len(item["options"]) >= int(answer):
        return item["options"][int(answer) - 1]
    return answer


# 站方把彙編題大幅改寫過，文字相似度不足以自動對上的題目：人工指定對應的彙編題
MANUAL = {
    "MC-DOC2-01": ("MC", 86), "MC-DOC2-02": ("MC", 87), "MC-DOC2-03": ("MC", 88), "MC-DOC2-06": ("MC", 93),
    "MC-DOC2-07": ("MC", 94), "MC-DOC2-10": ("MC", 101), "TF-DOC2-05": ("TF", 59),
    "TF-097": ("TF", 99), "TF-142": ("TF", 96), "TF-143": ("MC", 91), "TF-144": ("MC", 95), "TF-145": ("MC", 97),
    "TF-146": ("MC", 98), "TF-147": ("MC", 105), "TF-148": ("MC", 107), "TF-149": ("MC", 102), "TF-150": ("MC", 103),
    "TF-151": ("MC", 104), "TF-152": ("MC", 108), "TF-153": ("MC", 112),
    "MC-099": ("MC", 29), "MC-100": ("MC", 49), "MC-101": ("MC", 99),
}
# 相似度夠高但其實是站方另寫的題目
NOT_FROM_SOURCE = {"MC-094", "MC-257-05"}
# 彙編答案欄空白（只記錄「257T 考過這個考點」）的題目
BLANK_ANSWER = {"TF-147", "TF-148", "TF-149", "TF-150", "TF-151", "TF-153"}


def classify(q, old, item, score):
    if item is None or (score < 0.72 and q["id"] not in MANUAL) or q["id"] in NOT_FROM_SOURCE:
        return "site_authored"
    if q["id"] in BLANK_ANSWER and norm(item["stem"]) == norm(q["question"]):
        return "compiled_verbatim"
    if q["id"] in ("TF-152",):
        return "compiled_minor"
    source = full_text(item["stem"], item["options"])
    now = full_text(q["question"], q.get("options", []))
    source_answer = source_answer_text(item)
    same_answer = norm(str(source_answer)) == norm(str(answer_text(q)))
    if now == source and same_answer:
        return "compiled_verbatim"
    if q.get("revised") or not same_answer:
        return "compiled_adapted"
    ratio = difflib.SequenceMatcher(None, now, source, autojunk=False).ratio()
    return "compiled_minor" if ratio >= 0.9 else "compiled_adapted"


LABEL = {
    "recalled": "考生回憶的考點",
    "compiled_verbatim": "彙編逐字收錄", "compiled_minor": "彙編收錄（用字微調）",
    "compiled_adapted": "彙編收錄，依現行法規改寫", "site_authored": "站方自編，無考古題來源",
}


def main():
    items = parse_source()
    print("彙編：是非 %d 題、選擇 %d 題" % (sum(i["kind"] == "TF" for i in items), sum(i["kind"] == "MC" for i in items)))
    old = previous_site()
    rows, counts = [], {}
    recruit = load("questions.json")
    used = {}
    for q in recruit["questions"]:
        item, score = match(q, old.get(q["id"]), items)
        if q["id"] in MANUAL:
            item = next(i for i in items if (i["kind"], i["no"]) == MANUAL[q["id"]])
        cls = classify(q, old.get(q["id"]), item, score)
        prov = {"class": cls, "label": LABEL[cls]}
        if cls != "site_authored":
            key = "%s %d" % ("是非" if item["kind"] == "TF" else "選擇", item["no"])
            prov.update({"source_id": SOURCE_ID, "source_item": key, "tags": item["tags"]})
            used.setdefault(key, []).append(q["id"])
        q["provenance"] = prov
        counts[cls] = counts.get(cls, 0) + 1
        rows.append(row("新訓", q, old.get(q["id"]), item if cls != "site_authored" else None, score, cls))
    recruit["stats"]["provenance"] = counts
    save("questions.json", recruit)
    print("新訓：", counts)
    dup = {k: v for k, v in used.items() if len(v) > 1}
    print("同一彙編題對到多個站內題：", dup)
    missing = [("%s %d" % ("是非" if i["kind"] == "TF" else "選擇", i["no"])) for i in items
               if ("%s %d" % ("是非" if i["kind"] == "TF" else "選擇", i["no"])) not in used]
    print("彙編有、站內沒有對到的題：", missing)

    emt = load("emt_questions.json")
    emt_counts = {}
    for q in emt["questions"]:
        prov = q.get("provenance", {})
        if prov.get("class") != "recalled":
            prov = {"class": "site_authored", "label": LABEL["site_authored"]}
        q["provenance"] = prov
        emt_counts[prov["class"]] = emt_counts.get(prov["class"], 0) + 1
        r = row("EMT-1", q, old.get(q["id"]), None, 0, "site_authored")
        if prov["class"] == "recalled":
            r.update({
                "source_id": prov["source_id"], "source_item": prov["source_item"], "source_exam_round": prov["round"],
                "source_original_stem": "（不轉錄原文，請看來源連結）",
                "source_original_options": "回憶者有記選項" if prov["options_by"] == "source" else "回憶者沒有記選項，本站選項為站方自編",
                "source_original_answer_text": answer_text(q), "match_class": "考生回憶的考點（題文為站方重寫）",
                "answer_diff": "相同", "has_batch_evidence": "是" if prov["round"] == "270T" else "否（梯次不明）",
                "decision": "不列入測驗（回憶者註明已過時）" if q.get("status") == "outdated" else "有考過的證據：列入 EMT-1 模擬考",
            })
        rows.append(r)
    emt["stats"]["provenance"] = emt_counts
    save("emt_questions.json", emt)
    print("EMT：", emt_counts)

    path = os.path.join(ROOT, "docs", "question_provenance.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("已寫入 %s（%d 列）" % (path, len(rows)))


def row(bank, q, old, item, score, cls):
    source_answer = source_answer_text(item) if item else ""
    current = answer_text(q)
    stem_same = bool(item) and norm(item["stem"]) == norm(q["question"])
    opts_same = bool(item) and [norm(o) for o in item["options"]] == [norm(o) for o in q.get("options", [])]
    ans_same = bool(item) and norm(str(source_answer)) == norm(str(current))
    return {
        "bank": bank, "site_id": q["id"], "site_stem": q["question"],
        "site_options_original_order": " ／ ".join(q.get("options", [])),
        "site_answer_text": current, "site_exam_tag": q.get("exam_tag", ""),
        "site_review_status": q.get("review", ""),
        "old_site_answer_text（改版前網站答案，不是歷史考卷答案）": answer_text(old) if old else "",
        "source_id": SOURCE_ID if item else "", "source_item": ("%s %d" % ("是非" if item["kind"] == "TF" else "選擇", item["no"])) if item else "",
        "source_original_stem": item["stem"] if item else "",
        "source_original_options": " ／ ".join(item["options"]) if item else "",
        "source_original_answer": (item["answer"] if item else ""),
        "source_original_answer_text": source_answer,
        "source_exam_round": item["tags"] if item else "",
        "match_class": LABEL[cls], "match_score": ("%.2f" % score) if item else "",
        "stem_diff": "" if not item else ("相同" if stem_same else "不同"),
        "option_diff": "" if not item or not item["options"] else ("相同" if opts_same else "不同"),
        "answer_diff": "" if not item else ("相同" if ans_same else "不同"),
        "has_batch_evidence": "是" if item and item["tags"] else "否",
        "current_basis": q.get("source", ""), "current_basis_url": q.get("source_url", ""),
        "revision_note": q.get("revised", "") or q.get("status_note", ""),
        "decision": decision(cls, q, item),
        "reviewer": "Claude（AI）；尚無人工複核", "review_date": REVIEW_DATE,
    }


def decision(cls, q, item):
    if cls == "site_authored":
        return "站方自編練習題：不得稱為考古題，不列入「考古題模擬考」"
    if q.get("review") == "outdated":
        return "彙編舊法題：保留供對照，不出題"
    if q.get("review") == "law":
        return "彙編題，答案已對照現行條文：列入考古題模擬考"
    return "彙編題，但現行答案待補證：不列入模擬考，可在練習中選用"


if __name__ == "__main__":
    main()
