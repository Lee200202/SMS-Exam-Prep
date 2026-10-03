# -*- coding: utf-8 -*-
"""
2026-10 改版的一次性資料整理（可重複執行，已整理過的部分會略過）。

- 題庫：修正法規來源名稱與連結、改寫與現行法規牴觸的題目、移除無佐證的強斷言。
- 講義：移除「最新／必考」等斷言、刪除已由 data/laws.json 取代的手抄條文。
- 用品清單：把「要準備的物品」「管制說明」「不用帶」「經驗提醒」分成不同型別並合併重複項。

執行後請跑 scripts/validate_data.py 與 scripts/generate_bundle.py。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEWED_AT = "2026-10-03"
LAW = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode="


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(ROOT, "data", name), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def soften(text):
    """移除沒有逐項佐證的強斷言用語。"""
    for old, new in (
        ("最新現行", "現行"),
        ("現行法規最新標準", "現行法規"),
        ("全員必考", "常考"),
        ("高頻必考", "常考"),
        ("必考", "常考"),
        ("最新", ""),
    ):
        text = text.replace(old, new)
    return text


def walk(node, fn):
    if isinstance(node, dict):
        return {k: walk(v, fn) for k, v in node.items()}
    if isinstance(node, list):
        return [walk(v, fn) for v in node]
    if isinstance(node, str):
        return fn(node)
    return node


# ---------------------------------------------------------------- 新訓題庫
RECRUIT_SOURCES = {
    "regulations": ("law", "替代役實施條例", LAW + "D0040017"),
    "rights": ("law", "替代役實施條例（權利義務、撫卹、保險）", LAW + "D0040017"),
    "management": ("law", "一般替代役役男訓練服勤管理辦法", LAW + "D0040020"),
    "volunteer": ("law", "志願服務法", LAW + "D0050131"),
}

QUESTION_FIXES = {
    "MC-037": {
        "question": "撫卹金領受權利之時效，自請卹或請領事由發生之次月起，經過幾年不行使而消滅？",
        "options": ["3年", "5年", "7年", "10年"],
        "answer": 3,
        "explanation": "《替代役實施條例》第38條：請卹及請領各期撫卹金權利之時效，自請卹或請領事由發生之次月起，經過十年不行使而消滅。歷屆考古題的選項與答案（5年）是依修正前條文，本題已依現行條文改寫。",
        "source": "替代役實施條例 第38條",
        "source_url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0040017&flno=38",
        "revised": "原考古題答案為 5 年（修正前條文），已依現行第38條改為 10 年。",
    },
    "MC-007": {
        "question": "替代役役男因配偶妊娠產檢或分娩，核給陪產檢及陪產假七日，得分次申請。陪產之請假應於配偶分娩之當日及其前後合計幾日期間內為之？",
        "options": ["5日", "7日", "10日", "15日"],
        "answer": 3,
        "explanation": "《替代役役男請假規則》第4條：核給陪產檢及陪產假七日，得分次申請；除陪產檢於配偶妊娠期間請假外，陪產之請假應於配偶分娩之當日及其前後合計十五日期間內為之。",
        "source": "替代役役男請假規則 第4條",
        "source_url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0040021&flno=4",
        "revised": "原考古題依舊規定（陪產假三日、前後五日內請畢），已依現行第4條改寫。",
    },
    "MC-076": {
        "question": "依現行《替代役役男請假規則》，替代役役男因配偶妊娠產檢或分娩，得核給陪產檢及陪產假幾日？",
        "options": ["3日", "5日", "7日", "10日"],
        "answer": 2,
        "explanation": "《替代役役男請假規則》第4條：替代役役男因配偶妊娠產檢或分娩，核給陪產檢及陪產假七日，得分次申請。",
        "source": "替代役役男請假規則 第4條",
        "source_url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0040021&flno=4",
        "revised": "原考古題答案為 5 日（舊規定），已依現行第4條改為 7 日。",
    },
    "TF-107": {
        "question": "役男家屬均屬65歲以上、未滿15歲、患有身心障礙或重大傷病者，符合因家庭因素申請服替代役之情形。",
        "answer": "O",
        "explanation": "《役男申請服替代役辦法》第11條第1項第1款：役男家屬均屬六十五歲以上、未滿十五歲、患有身心障礙、重大傷病或十五歲以上未滿十八歲經立案學校證明就學中。",
        "source": "役男申請服替代役辦法 第11條",
        "source_url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0040016&flno=11",
        "revised": "原考古題為「60歲以上、未滿18歲」（舊規定），已依現行第11條改寫。",
    },
}

# 現行請假規則第7條已無「事假按時數累計八小時折算一日」，舊題不再出題，只留在題庫供對照。
OUTDATED = {
    "MC-053": "現行《替代役役男請假規則》第7條已刪除「事假累計八小時折算一日」的規定，本題為舊法題，不列入測驗。",
    "MC-058": "現行《替代役役男請假規則》第7條已刪除「事假累計八小時折算一日」的規定，本題為舊法題，不列入測驗。",
}


def migrate_questions():
    data = load("questions.json")
    questions = data["questions"]
    for q in questions:
        cat = q["category"]
        if cat in RECRUIT_SOURCES and "source_kind" not in q:
            kind, name, url = RECRUIT_SOURCES[cat]
            q["source_kind"], q["source"], q["source_url"] = kind, name, url
        elif "source_kind" not in q:
            q["source_kind"] = "experience"
            q["source"] = "役男筆記與歷屆鑑測題整理（非官方）"
        q["explanation"] = soften(q.get("explanation", ""))
        if q["id"] in QUESTION_FIXES:
            q.update(QUESTION_FIXES[q["id"]])
        if q["id"] in OUTDATED:
            q["status"] = "outdated"
            q["status_note"] = OUTDATED[q["id"]]
            q["explanation"] = ""
            q["source"] = "替代役役男請假規則 第7條"
            q["source_url"] = "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0040021&flno=7"
    active = [q for q in questions if q.get("status") != "outdated"]
    data["version"] = "2026.10"
    data["updatedAt"] = REVIEWED_AT
    data["stats"] = {
        "total": len(questions),
        "active": len(active),
        "true_false": sum(q["type"] == "true_false" for q in questions),
        "multiple_choice": sum(q["type"] == "multiple_choice" for q in questions),
        "with_explanation": sum(bool(q.get("explanation")) for q in questions),
    }
    save("questions.json", data)
    print("questions.json", data["stats"])


# ---------------------------------------------------------------- EMT 題庫
def fix_emt_url(text):
    # L0020048 是已廢止的《救護車裝備標準》；《救護技術員管理辦法》的代碼是 L0020141
    return text.replace("pcode=L0020048", "pcode=L0020141")


def migrate_emt():
    data = walk(load("emt_questions.json"), lambda s: fix_emt_url(soften(s)))
    data["title"] = "EMT-1 初級救護技術員學科題庫"
    data["subtitle"] = "依消防署初級救護技術員教材與歷屆役男分享整理，非官方題庫"
    data["updatedAt"] = REVIEWED_AT
    data["total"] = len(data["questions"])
    save("emt_questions.json", data)

    study = walk(load("emt_study_data.json"), lambda s: fix_emt_url(soften(s)))
    study["title"] = "EMT-1 初級救護技術員重點整理"
    study["updated_at"] = REVIEWED_AT
    save("emt_study_data.json", study)
    print("emt_questions.json", data["total"])


# ---------------------------------------------------------------- 用品清單
SYMBOLS = re.compile(r"^[\s🔒💊🚬👟🧥🧼🛏️✏️🩲🧴🪥👕🧦🩴😷📿👓🩹🧻🍬🎨📜🎒💡❌🚫️]+")
TAG = re.compile(r"【(Dcard|記事本|群組)[^】]*】\s*")
DROP = {
    # 與其他項目重複，內容已併入保留的那一筆
    "auth_stable_toothbrush", "auth_plain_undershirt", "auth_plain_socks", "auth_plain_slippers",
    "auth_medical_masks", "auth_optical_glasses", "auth_thick_pocket_tissues",
    "auth_sealed_throat_drops", "auth_blank_paper_pens", "auth_certificates_all",
}
RENAME = {
    "prickly_heat_powder": "涼感爽身粉",
    "deodorant": "止汗劑 (滾珠式)",
    "throat_drops_pink": "喉糖 (未拆封鐵盒)",
    "slippers_blue": "藍白拖鞋 (營站購買，鞋側做記號)",
    "auth_first_aid_med": "簡易外傷用品 (透氣膠布、碘酒消毒棉片、綠油精)",
    "auth_luggage_guide": "入營包：雙肩後背包或運動提袋",
    "auth_religion_jewelry": "宗教信仰飾品 (木質或編織，不可為金屬)",
}
RETIP = {
    "doc_specialty": "專長證照、外語檢定、駕照、獎狀、作品集等影本，選服勤單位時可作為佐證。",
    "throat_drops_pink": "入營檢查前不要拆封，拆封會被視為散裝食物。歷屆分享多買枇杷潤喉口味。",
    "auth_luggage_guide": "內務空間小，硬殼行李箱放不進黑色大行李袋，請用一般後背包或運動圓筒包。",
    "ban_rule_note": "違禁品在入營安檢時會集中保管，結訓離營時發還。實際認定以當梯次幹部公告為準。",
    "tip_sick_call": "身體不適請立刻向幹部反映並依營區程序就醫，不要因為課程或成績而拖延。",
    "tip_mess_crew": "打飯班每餐要打菜、清洗餐桶，工作量大，建議排頭盡早安排輪替。",
    "tip_barber_avoid": "入營前已自行理髮的人，歷屆分享不需再理也不需在理髮名冊簽名，實際作法依當梯次幹部指示。",
}
RENAME_TIPS = {
    "ban_rule_note": "違禁品會集中保管，結訓時發還",
    "tip_sick_call": "生病請立即反映並就醫",
    "tip_mess_crew": "打飯班盡早安排輪替",
    "tip_barber_avoid": "入營前先理好頭髮",
}
MOVE = {  # 物品 id -> 新分類 id
    "spare_clothes": "identities",
    "auth_luggage_guide": "identities",
    "auth_first_aid_med": "toiletries_med",
    "auth_religion_jewelry": "control_levels",
    "shoe_size_sport": "tips",
    "shoe_size_leather": "tips",
    "canteen_caution": "tips",
}
CATEGORIES = [
    ("documents", "pack", "文件與證明", "用 L 夾裝好，報到時會查驗。"),
    ("identities", "pack", "證件、現金與隨身物品", ""),
    ("god_tier_items", "pack", "用餐、收納與寢室用品", ""),
    ("toiletries_med", "pack", "盥洗、藥品與清潔用品", ""),
    ("stationery_drill", "pack", "文具與內務小工具", ""),
    ("commissary_buy", "pack", "入營後可在營站加購", "公發數量不夠替換時再買，不必事先準備。"),
    ("control_levels", "info", "物品管制等級說明", "這一區是管制方式的說明，不是待辦項目。"),
    ("avoid", "info", "不用帶，或會被集中保管的物品", "請不要把這些物品當成要準備的東西。"),
    ("tips", "info", "入營後的經驗提醒", "歷屆役男分享，各梯次作法可能不同。"),
]


def clean_item(item, category_id):
    name = SYMBOLS.sub("", item["name"]).strip()
    tip = item.get("tip", "")
    source = ""
    found = TAG.search(tip) or TAG.search(name)
    if found:
        source = "Dcard 役男分享" if found.group(1) == "Dcard" else "役男群組記事本"
    tip = TAG.sub("", tip).strip()
    name = TAG.sub("", name).strip()
    out = {"id": item["id"]}
    level = re.match(r"^【(重度管制|中度管制|輕度管制)】\s*(.*)$", name)
    if level:
        out["level"], name = level.group(1), level.group(2)
    lead = re.match(r"^【(.+?)】[：:]?\s*(.*)$", name)
    if lead:
        name = lead.group(1) + ("：" + lead.group(2) if lead.group(2) else "")
    out["name"] = RENAME_TIPS.get(item["id"], RENAME.get(item["id"], name))
    if category_id not in ("control_levels", "avoid", "tips"):
        out["must"] = bool(item.get("must"))
    out["tip"] = RETIP.get(item["id"], tip)
    if source and item["id"] not in RETIP:
        out["source"] = source
    return out


def migrate_packing(study):
    packing = study["packing_list"]
    if packing.get("schema") == 2:
        return
    buckets = {cid: [] for cid, *_ in CATEGORIES}
    seen = set()
    for category in packing["categories"]:
        for item in category["items"]:
            iid = item["id"]
            if iid in DROP or iid in seen:
                continue
            seen.add(iid)
            if iid in MOVE:
                target = MOVE[iid]
            elif category["id"] == "contraband":
                target = "tips" if iid.startswith("tip_") else "avoid"
            elif category["id"] == "authorized_custom":
                target = "god_tier_items"
            else:
                target = category["id"]
            buckets[target].append(clean_item(item, target))
    study["packing_list"] = {
        "schema": 2,
        "title": "新訓用品清單",
        "description": "依 2024 年梯次（257T、277T 等）役男分享整理，不是官方清單。實際可攜帶物品與管制方式，以徵集令及當梯次營區通知為準。",
        "reviewed_at": REVIEWED_AT,
        "categories": [
            {"id": cid, "kind": kind, "name": name, "note": note, "items": buckets[cid]}
            for cid, kind, name, note in CATEGORIES
        ],
    }


def migrate_study():
    study = load("study_data.json")
    migrate_packing(study)
    packing = study.pop("packing_list")
    study = walk(study, soften)
    study["packing_list"] = packing

    # 手抄條文改由 data/laws.json（官方全文）提供
    study["regulations"].pop("full_act", None)
    study["volunteer"].pop("full_act", None)
    study["regulations"]["title"] = "替代役實施條例重點"
    study["regulations"]["description"] = "依《替代役實施條例》及相關子法整理的考試重點。條文原文請看「法規全文」。"
    study["regulations"]["key_points_full"]["title"] = "歷屆役男重點筆記"
    study["volunteer"]["title"] = "志願服務法重點"
    study["volunteer"]["description"] = "依《志願服務法》（民國 109 年 1 月 15 日修正）整理。"
    rights = study["rights_and_management"]
    rights["title"] = "役男權益與服勤管理"
    rights["description"] = "權益保障、獎懲、薪給與新訓成績配分整理。"
    rights["grade_breakdown"]["title"] = "基礎訓練成績配分（歷屆經驗）"
    rights["grade_breakdown"]["desc"] = "以下比例來自歷屆（247T）役男分享，並非官方公告；實際配分依當梯次公告為準。"
    rights["salary_structure"]["title"] = "薪給待遇（歷屆整理，金額以內政部公告為準）"
    rights["rights_points_full"]["title"] = "役男權益重點筆記"
    rights["management_points_full"]["title"] = "訓練與服勤管理重點筆記"
    study["shooting"]["title"] = "步槍射擊重點"
    study["shooting"]["description"] = "射擊安全守則、口訣與歷屆鑑測常見內容，依役男筆記整理。"
    study["footnotes"]["title"] = "歷屆考題註解"
    study["footnotes"]["notes"] = [n for n in study["footnotes"]["notes"] if n.get("num")]
    study["reviewed_at"] = REVIEWED_AT
    save("study_data.json", study)
    packing_counts = {c["id"]: len(c["items"]) for c in packing["categories"]}
    print("study_data.json packing", packing_counts)


if __name__ == "__main__":
    migrate_questions()
    migrate_emt()
    migrate_study()
