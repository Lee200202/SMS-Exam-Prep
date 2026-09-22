import json
import re
import os

doc2_path = r"C:\Users\user\.gemini\antigravity\brain\878a1b48-4d39-4b52-998b-42ffd65dd18f\.system_generated\steps\171\content.md"

with open("data/questions.json", "r", encoding="utf-8") as f:
    q_data = json.load(f)

existing_questions = q_data["questions"]

# Footnotes dictionary extracted from doc2
footnotes = {
    "[1]": "社會治安類僅包括警察役與消防役；社會役屬於社會服務類。",
    "[2]": "替代役實施條例所稱需用機關，係指一般替代役役男服勤單位之中央各該主管機關；服勤單位指役男擔任輔助勤務處所之管理單位。",
    "[3]": "替代役實施條例所稱服勤單位，係指役男擔任輔助勤務處所之管理單位，中央各該主管機關為需用機關。",
    "[4]": "家庭發生重大變故須負擔主要責任者，辦理「提前退役」而非停役。",
    "[18]": "最新規定：83年次以後常備役體位申請宗教因素替代役役期為6個月（常備兵為4個月）；82年次以前則為1年。",
    "[19]": "83年次以後，常備役體位因家庭因素服替代役之役期為4個月，與常備役相同。",
    "[20]": "未經准假擅離服勤或指定住宿場所累計3日以上，得施予輔導教育；破壞公物、酗酒為記過或罰薪。",
    "[21]": "需用機關對罰薪或輔導教育案件應於7日內核定，並於一週內送主管機關備查。",
    "[22]": "罰薪、輔導教育應於一週內（7日內）送請主管機關備查。",
    "[23]": "經診斷確定足以危害團體健康安全或不堪服役停役者，依免予回役作業規定「免予回役」。",
    "[24]": "替代役管理幹部由需用機關甄選，並實施在職訓練後擔任。",
    "[25]": "83年次以後一般替代役役期為6個月，較常備兵軍事訓練役（4個月）長2個月。",
    "[26]": "一般替代役役男退役年終獎金採隨退隨發，於退役當月15日逕入役男郵局帳戶。",
    "[27]": "法規條文為「得」遴選，非「應」遴選。",
    "[28]": "至國軍醫療院所就醫，掛號費由主管機關內政部全額負擔；國軍醫院以外之健保特約機構，掛號費由役男自付（因公傷病除外）。"
}

# New questions to add from doc2
new_questions_to_add = [
    {
        "id": "TF-DOC2-01",
        "type": "true_false",
        "category": "management",
        "exam_tag": "【203T/205T/215T/227T考】",
        "question": "替代役役男入營逾30天，因傷病不堪服替代役者，可申辦傷病停役。",
        "answer": "O",
        "explanation": "入營30天內體格不適服者辦理「驗退」；入營逾30天不堪服役者申辦「傷病停役」。"
    },
    {
        "id": "TF-DOC2-02",
        "type": "true_false",
        "category": "rights",
        "exam_tag": "【205T考】",
        "question": "役男服勤時，應隨身攜帶役男身分證；身分證除為證明役男現役身分外，不得轉為其他用途，役男停役、提前退役或服役期滿時應繳回服勤單位。",
        "answer": "O",
        "explanation": "依役男身分證管理規範，役男身分證限現役證明，離役時應繳回服勤單位繳銷。"
    },
    {
        "id": "MC-DOC2-01",
        "type": "multiple_choice",
        "category": "rights",
        "exam_tag": "【179T考】",
        "question": "一般替代役役男當月退役退伍，其年終工作獎金依法應於退役當月之哪一日發放逕入郵局帳戶？",
        "options": ["1日", "5日", "15日", "25日"],
        "answer": 2,
        "explanation": "依役政署規定，一般替代役退役年終工作獎金採隨退隨發方式辦理，且於退役當月15日逕入役男帳戶。"
    },
    {
        "id": "MC-DOC2-02",
        "type": "multiple_choice",
        "category": "management",
        "exam_tag": "【179T考】",
        "question": "役男與同戶籍之兄弟姊妹2人以上同時服役，各人之剩餘役期在多久以上，且均未於戶籍地服役，得申請優先分發或調返戶籍地或附近地區之服勤單位（處所）服役？",
        "options": ["1個月以上", "2個月以上", "4個月以上", "6個月以上"],
        "answer": 1,
        "explanation": "依《一般替代役役男優先分發及特殊困難請調原則》，同戶兄弟姊妹2人以上同時在營且剩餘役期均在「2個月以上」，得申請調返戶籍地。"
    },
    {
        "id": "MC-DOC2-03",
        "type": "multiple_choice",
        "category": "regulations",
        "exam_tag": "【205T考】",
        "question": "現役替代役役男符合提前退役規定時，應經由何機關核定？",
        "options": ["直轄市、縣（市）政府", "鄉鎮市區公所", "主管機關內政部（役政署）", "服勤單位"],
        "answer": 2,
        "explanation": "《替代役實施條例》第10條：因家庭發生重大變故等提前退役，經「內政部」核定後辦理。"
    },
    {
        "id": "MC-DOC2-04",
        "type": "multiple_choice",
        "category": "management",
        "exam_tag": "【203T/215T考】",
        "question": "替代役役男之管理幹部由何機關甄選，並於實施在職訓練合格後，負責擔任領導及考核工作？",
        "options": ["需用機關", "主管機關內政部", "服勤單位", "直轄市、縣(市)政府"],
        "answer": 0,
        "explanation": "依《一般替代役役男訓練服勤管理辦法》，管理幹部由「需用機關」甄選並實施在職訓練合格後核定擔任。"
    },
    {
        "id": "MC-DOC2-05",
        "type": "multiple_choice",
        "category": "regulations",
        "exam_tag": "【203T/205T考】",
        "question": "行政院核定83年次以後出生之常備役體位於國內地區服一般替代役之役期為？",
        "options": ["與常備兵軍事訓練役相同(4個月)", "較常備兵軍事訓練役期長15日", "較常備兵軍事訓練役期長2個月(共6個月)", "較常備兵軍事訓練役期長4個月(共8個月)"],
        "answer": 2,
        "explanation": "83年次以後常備役體位服一般替代役役期為6個月，較常備兵軍事訓練役（4個月）多2個月。"
    },
    {
        "id": "TF-DOC2-03",
        "type": "true_false",
        "category": "rights",
        "exam_tag": "【205T考】",
        "question": "依國民年金法規定，年滿25歲未參加軍、公教、勞、農保者為國民年金加保範圍。替代役男服役期間無現役軍人身分，未參加軍人保險，參加替代役一般保險，因此依法為國民年金保險加保對象，其國保保費由內政部編列預算支付。",
        "answer": "O",
        "explanation": "正確。替代役實施條例第50條明定：替代役男各類保險費、國民年金保險費由主管機關編列預算支付。"
    },
    {
        "id": "MC-DOC2-06",
        "type": "multiple_choice",
        "category": "management",
        "exam_tag": "【205T/215T/219T/227T考】",
        "question": "依《替代役役男服役期滿後召集服勤實施辦法》規定，備役役男於平時演習或訓練時，需接受下列何種召集？",
        "options": ["動員召集", "勤務召集", "教育召集", "演訓召集"],
        "answer": 3,
        "explanation": "備役役男平時演練接受「演訓召集」，每次1日以內，必要時得延長為3至5日。"
    },
    {
        "id": "MC-DOC2-07",
        "type": "multiple_choice",
        "category": "management",
        "exam_tag": "【215T考】",
        "question": "替代役役男除家庭因素經核准返家住宿者外，其平時服勤之住宿方式採？",
        "options": ["一律集中住宿", "一律返家住宿", "集中或個別住宿", "由役男自行租屋個別住宿"],
        "answer": 2,
        "explanation": "《替代役役男服勤管理辦法》規定：住宿採「集中或個別住宿」；符合家庭因素者得申請返家住宿。"
    },
    {
        "id": "TF-DOC2-04",
        "type": "true_false",
        "category": "management",
        "exam_tag": "【219T/227T考】",
        "question": "替代役役男於軍事基礎訓練及專業訓練成績表現優異者，服勤單位「應」一律遴選擔任管理幹部。",
        "answer": "X",
        "explanation": "法規條文為「得」遴選，非「應」遴選。幹部員額以不超過需用機關役男總人數十分之一為限。"
    },
    {
        "id": "MC-DOC2-08",
        "type": "multiple_choice",
        "category": "management",
        "exam_tag": "【219T/227T考】",
        "question": "依《替代役實施條例》規定，替代役役男懲處種類包含下列何者？",
        "options": ["罰站、罰勤、禁足", "申誡、記過", "罰薪、輔導教育", "以上皆是"],
        "answer": 3,
        "explanation": "依條例第55條，懲處包含罰站、罰勤、禁足、申誡、記過、罰薪或輔導教育等，選項以上皆是。"
    },
    {
        "id": "MC-DOC2-09",
        "type": "multiple_choice",
        "category": "regulations",
        "exam_tag": "【235T考】",
        "question": "下列哪一個替代役役別，其主要勤務服務對象為兒童與少年、老人與傷病榮民及身心障礙者？",
        "options": ["社會役", "消防役", "警察役", "環保役"],
        "answer": 0,
        "explanation": "社會役之主要勤務內容為擔任社福機構、兒少老弱、榮民及身心障礙者之生活照顧輔助勤務。"
    },
    {
        "id": "MC-DOC2-10",
        "type": "multiple_choice",
        "category": "rights",
        "exam_tag": "【235T考】",
        "question": "替代役役男非因公傷病前往「國軍醫療院所」就醫時，其門診掛號費依法應由何者負擔？",
        "options": ["替代役役男本人負擔", "主管機關內政部全額負擔", "內政部與役男平均分擔", "役男所屬服勤單位負擔"],
        "answer": 1,
        "explanation": "特別注意常考陷阱題：至「國軍醫院」就醫掛號費由內政部支付；若至「民間健保特約醫療機構」就醫，非因公之掛號費則由役男自付。"
    },
    {
        "id": "TF-DOC2-05",
        "type": "true_false",
        "category": "regulations",
        "exam_tag": "【202T考】",
        "question": "替代役役男經診斷確定罹患危害健康安全之疾病或傷病不堪服役而核定停役者，其傷病於停役期間經治療痊癒後，均應強制回役補服未服完之役期。",
        "answer": "X",
        "explanation": "依《停役替代役役男免予回役作業規定》，罹患足以危害團體健康安全之疾病或不堪服役停役者，經審查均核定「免予回役」。"
    }
]

# Update existing questions with tags and footnote explanations if missing
existing_stems = {re.sub(r"\s+", "", q["question"][:15]): q for q in existing_questions}

added_count = 0
for nq in new_questions_to_add:
    stem = re.sub(r"\s+", "", nq["question"][:15])
    if stem not in existing_stems:
        existing_questions.append(nq)
        added_count += 1
    else:
        # update exam tag if not present
        existing_q = existing_stems[stem]
        if not existing_q.get("exam_tag") and nq.get("exam_tag"):
            existing_q["exam_tag"] = nq["exam_tag"]
        if not existing_q.get("explanation") and nq.get("explanation"):
            existing_q["explanation"] = nq["explanation"]

# Check all footnote occurrences in explanations
for q in existing_questions:
    for fn_tag, fn_expl in footnotes.items():
        if fn_tag in q["question"] or fn_tag in q.get("explanation", ""):
            if fn_expl not in q.get("explanation", ""):
                q["explanation"] = (q.get("explanation", "") + " " + fn_expl).strip()
            # clean footnote tag from question text
            q["question"] = q["question"].replace(fn_tag, "").strip()

# Update stats
q_data["stats"]["total"] = len(existing_questions)
q_data["stats"]["true_false"] = sum(1 for q in existing_questions if q["type"] == "true_false")
q_data["stats"]["multiple_choice"] = sum(1 for q in existing_questions if q["type"] == "multiple_choice")
q_data["stats"]["categories"] = {
    "regulations": sum(1 for q in existing_questions if q["category"] == "regulations"),
    "volunteer": sum(1 for q in existing_questions if q["category"] == "volunteer"),
    "rights": sum(1 for q in existing_questions if q["category"] == "rights"),
    "management": sum(1 for q in existing_questions if q["category"] == "management"),
    "shooting": sum(1 for q in existing_questions if q["category"] == "shooting")
}

# Write updated questions.json
with open("data/questions.json", "w", encoding="utf-8") as f:
    json.dump(q_data, f, ensure_ascii=False, indent=2)

# Re-read study_data.json to bundle
with open("data/study_data.json", "r", encoding="utf-8") as f:
    s_data = json.load(f)

# Re-bundle data_bundle.js
bundle_content = f"""// Auto-generated data bundle for offline & GitHub Pages support
window.APP_QUESTIONS = {json.dumps(q_data, ensure_ascii=False)};
window.APP_STUDY_DATA = {json.dumps(s_data, ensure_ascii=False)};
"""

with open("data/data_bundle.js", "w", encoding="utf-8") as f:
    f.write(bundle_content)

print(f"Added {added_count} new questions. Total questions is now: {len(existing_questions)}")
print(f"Categories: {q_data['stats']['categories']}")
