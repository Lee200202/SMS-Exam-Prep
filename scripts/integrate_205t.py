"""Record the 205T A-paper recollection without duplicating existing practice items.

The original author supplied questions but no answer key. The mappings and
proposed answers below are manual editorial decisions; the output keeps that
distinction explicit. Pass the original DOCX path when running this script.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

from audit_205t_docx import paragraphs


ROOT = Path(__file__).resolve().parent.parent
PTT = "https://www.ptt.cc/bbs/SMSlife/M.1570117334.A.953.html"
LAW = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode={}\u0026flno={}"

# Paper order -> one existing site item. Two items missing from the site receive
# stable IDs below. A different question type means the concept is already
# present, not that the site's wording reproduces the paper.
TF_IDS = [
    "TF-032", "TF-077", "TF-081", "TF-057", "TF-DOC2-03",
    "TF-097", "TF-044", "TF-143", "TF-DOC2-01", "TF-075",
    "MC-045", "TF-036", "TF-102", "TF-092", "TF-142",
    "TF-080", "TF-144", "TF-084", "TF-DOC2-02", "TF-154",
    "TF-103", "TF-095", "TF-062", "TF-059", "TF-117",
]
MC_IDS = [
    "MC-062", "MC-061", "MC-DOC2-03", "MC-040", "MC-044",
    "MC-257-03", "MC-DOC2-06", "MC-102", "MC-023", "MC-069",
    "MC-011", "MC-059", "MC-042", "TF-017", "MC-063",
    "MC-006", "MC-082", "MC-DOC2-07", "MC-068", "MC-DOC2-05",
    "MC-100", "MC-027", "MC-019", "TF-006", "MC-084",
]

# Answers refer to the 205T paper's order, NOT the order of a site item. Blank
# means a current-scoring answer is unsafe or lacks adequate current evidence.
TF_ANSWERS = [
    "X", "X", "", "O", "O", "O", "O", "O", "", "",
    "O", "O", "O", "O", "", "X", "O", "", "O", "O",
    "O", "X", "O", "O", "O",
]
MC_ANSWERS = [
    "1", "1", "3", "2", "2", "1", "4", "4", "2", "1",
    "4", "3", "2", "2", "2", "2", "4", "3", "3", "",
    "3", "4", "3", "2", "3",
]

HISTORICAL = {
    ("是非", 3): "題幹寫已改制的役政署／訓練班；不可把 2019 年機關名稱當現行答案。",
    ("是非", 9): "入營逾 30 日的歷史分界；現行基礎訓練約 26 日，須另查當梯制度。",
    ("是非", 15): "體能測驗替代項目屬當梯訓練規定，未找到現行全國一致依據。",
    ("是非", 18): "缺考以 0／40 分核算屬當梯評分規則，未找到現行公告支持。",
    ("選擇", 20): "原題只寫 83 年次以後，現行役期因 83–93 與 94 年次以後而不同，選項不能有唯一答案。",
}

OFFICIAL = {
    ("是非", 5): ("https://dca.moi.gov.tw/chaspx/Faq_Detail.aspx?id=6692&web=85", "官方國民年金說明；原文有『為／未』轉寫錯字"),
    ("是非", 6): ("https://dca.moi.gov.tw/userfiles/Files/morefile1_50_5549_67.pdf", "官方受益人指定書附表"),
    ("是非", 8): ("https://dca.moi.gov.tw/chaspx/Faq_Detail.aspx?id=6562&web=85", "官方年終獎金問答"),
    ("是非", 11): ("https://dca.moi.gov.tw/chaspx/Faq_Detail.aspx?id=6671&web=85", "官方入營健保轉出問答"),
    ("是非", 12): ("https://www.nhi.gov.tw/ch/cp-5057-4907a-2673-1.html", "健保署現行郵局代收補卡說明"),
    ("是非", 16): ("https://dca.moi.gov.tw/chaspx/Faq_Detail.aspx?id=271&web=88", "服勤單位受理，主管機關核定；原題說服勤單位核定，故為錯"),
    ("是非", 17): ("https://dca.moi.gov.tw/userfiles/Files/morefile1_17_6341_38.pdf", "官方健保須知；一般保費與補充保費分開"),
    ("是非", 19): ("https://dca.moi.gov.tw/userfiles/files/j1cpujw.pdf", "內政部服勤管理要點；個別役別實施範圍仍須留意"),
    ("是非", 23): ("https://dca.moi.gov.tw/chaspx/Faq_Detail.aspx?id=271&web=88", "官方傷病停役申請流程；向服勤單位提出"),
    ("是非", 25): ("https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0040027&flno=12", "醫療自付費規定；原題舊稱健保局"),
    ("選擇", 9): ("https://dca.moi.gov.tw/CHASPX/Faq_Detail.aspx?id=6723&web=85", "官方服役中家庭因素申請問答"),
    ("選擇", 13): ("https://dca.moi.gov.tw/training/web/static/QA.html", "官方驗退體位判定問答"),
}

PENDING = {
    ("是非", 10): "驗退與傷病停役的檢定程序不同；原題『均須』尚未證成。",
    ("是非", 24): "制服要求見特定服勤管理資料，尚未證成對所有役別一律適用。",
}

NEW_ITEMS = {
    "TF-154": {
        "id": "TF-154", "type": "true_false", "category": "rights",
        "question": "替代役役男因公死亡，遺族年撫卹金給與十五年；年限屆滿而子女尚未成年者，得繼續給卹至成年。",
        "answer": "O", "exam_tag": "【205T A卷回憶】", "explanation": "",
        "source": "替代役實施條例 第32條",
        "source_url": LAW.format("D0040017", 32), "source_kind": "law", "review": "law",
    },
    "MC-102": {
        "id": "MC-102", "type": "multiple_choice", "category": "management",
        "question": "需用機關對服勤單位提出的罰薪或輔導教育懲處案件，應於幾日內核定？",
        "options": ["三日", "五日", "七日", "十日"], "answer": 3,
        "exam_tag": "【205T A卷回憶】", "explanation": "",
        "source": "替代役役男獎懲辦法 第19條",
        "source_url": LAW.format("D0040028", 19), "source_kind": "law", "review": "law",
    },
}


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/integrate_205t.py C:/path/to/205Texam.docx")
    source = Path(sys.argv[1])
    lines = paragraphs(source)
    if len(lines) != 53 or len(TF_IDS) != 25 or len(MC_IDS) != 25:
        raise ValueError("205T A 卷不是預期的 25 題是非加 25 題選擇")
    bank_path = ROOT / "data/questions.json"
    bank = json.loads(bank_path.read_text(encoding="utf-8"))
    by_id = {q["id"]: q for q in bank["questions"]}
    for qid, item in NEW_ITEMS.items():
        if qid not in by_id:
            q = dict(item)
            bank["questions"].append(q)
            by_id[qid] = q

    rows = []
    for kind, ids, answers, offset in (
        ("是非", TF_IDS, TF_ANSWERS, 2),
        ("選擇", MC_IDS, MC_ANSWERS, 28),
    ):
        for number, (qid, answer) in enumerate(zip(ids, answers, strict=True), 1):
            q = by_id[qid]
            original = lines[offset + number - 1]
            locator = f"{kind} {number}"
            relation = "原題校字" if qid in NEW_ITEMS else "題型不同、同考點" if (kind == "是非") != (q["type"] == "true_false") else "站內已有同題或改寫"
            entry = {"source_id": "P10", "source_item": locator, "relationship": relation}
            evidence = [e for e in q.get("exam_evidence", []) if e.get("source_id") != "P10"]
            q["exam_evidence"] = evidence + [entry]
            key = (kind, number)
            if key in HISTORICAL:
                verdict, answer, note, url = "歷史題；不按現行計分", "", HISTORICAL[key], ""
            elif key in PENDING:
                verdict, answer, note, url = "待補官方依據；不計分", "", PENDING[key], ""
            elif key in OFFICIAL:
                url, note = OFFICIAL[key]
                verdict = "官方說明支持；非原作者答案"
            elif q.get("review") == "law" and q.get("source_url", "").startswith("https://law.moj.gov.tw/"):
                url, note, verdict = q["source_url"], "對照現行條文；原作者未附答案", "現行法條支持；非原作者答案"
            else:
                url, note, verdict = "", "原作者沒有答案；現行官方依據仍不足", "待補官方依據；不計分"
                answer = ""
            rows.append({
                "205T題型": kind, "卷內題號": number,
                "來源文字SHA256前12碼": hashlib.sha256(original.encode("utf-8")).hexdigest()[:12],
                "原文前12字定位": original[:12], "網站對應ID": qid,
                "對應關係": relation, "原作者答案": "未附", "現行查核答案": answer,
                "裁定": verdict, "查核連結": url, "差異或限制": note,
            })
    out = ROOT / "docs/205T_A卷逐題裁定_2026-10-04.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    bank_path.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"205T A 卷：50 題已逐項定位；現行可判 {sum(bool(r['現行查核答案']) for r in rows)} 題；新增 2 題。")


if __name__ == "__main__":
    main()
