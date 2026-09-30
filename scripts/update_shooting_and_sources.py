import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Load questions.json
with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions_file = json.load(f)

questions = questions_file.get('questions', [])

# 1. Update source links for all existing questions based on their category
source_map = {
    'regulations': {
        'url': 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0040018',
        'name': '全國法規資料庫 - 替代役實施條例'
    },
    'volunteer': {
        'url': 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0050131',
        'name': '全國法規資料庫 - 志願服務法'
    },
    'rights': {
        'url': 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0040018',
        'name': '替代役實施條例第20~24條(役男權益/保險/撫卹)'
    },
    'management': {
        'url': 'https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0040020',
        'name': '替代役役男訓練服勤管理辦法與獎懲規定'
    },
    'shooting': {
        'url': 'https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r',
        'name': 'Google文件打靶筆記原文與247T、257T鑑測真題'
    }
}

for q in questions:
    cat = q.get('category', 'regulations')
    mapping = source_map.get(cat, source_map['regulations'])
    if not q.get('source'):
        q['source'] = mapping['name']
    if not q.get('source_url'):
        q['source_url'] = mapping['url']

# 2. Add complete shooting questions directly from the original chunk:
# "成功嶺打靶射擊訓練全攻略與 257T 最新試題 (完整原文) 完整還原 Google 文件打靶筆記原文與 247T、257T 鑑測真題"
# Existing shooting questions already has TF-257-01~04 and MC-257-01~02. Let's make sure all items in the chunk have both True/False and Multiple Choice variants, faithfully matching the original chunk text!

existing_ids = {q['id'] for q in questions}

new_shooting_questions = [
    # 避火罩功能 - 選擇題
    {
        "id": "MC-257-06",
        "category": "shooting",
        "type": "multiple_choice",
        "question": "國軍T65K2步槍槍口「避火罩」之主要功用為何？【257T新增題目 原文】",
        "options": [
            "主要功用為「減光」，無減音或減少後座力之功用",
            "主要功用為「減音」，可做微聲射擊",
            "主要功用為「減少後座力」，增進連發穩定度",
            "同時具備減音、滅光及減少後座力三種功能"
        ],
        "answer": 0,
        "explanation": "【257T新增題目 原文】避火罩功能：T65K2步槍避火罩有減音、滅光、減少後座力之公用→錯誤，正確為「減光」。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 覘孔距離 - 選擇題
    {
        "id": "MC-257-07",
        "category": "shooting",
        "type": "multiple_choice",
        "question": "T65K2步槍之「0至3覘孔」與「3至8覘孔」，其適用之射擊目標距離分別為何？【247T、257T期末考 原文】",
        "options": [
            "0至3覘孔為0至300(不含)公尺；3至8覘孔為300(含)至800公尺",
            "0至3覘孔為0至30公尺；3至8覘孔為30至80公尺",
            "0至3覘孔為300至800公尺；3至8覘孔為0至300公尺",
            "兩者射程相同，僅區分為夜間射擊與日間射擊"
        ],
        "answer": 0,
        "explanation": "【打靶筆記原文】有兩個覘孔作為兩個不同距離射擊瞄準用：0至3覘孔為0至300(不含)公尺目標射擊使用；3至8覘孔為300(含)至800公尺目標射擊使用。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 草地砂地分解結合 - 選擇題
    {
        "id": "MC-257-08",
        "category": "shooting",
        "type": "multiple_choice",
        "question": "關於T65K2步槍實施槍枝分解與結合之場地規定，下列敘述何者正確？【257T新增題目 原文】",
        "options": [
            "可在草地、砂地上實施分解與結合",
            "嚴禁在草地、砂地上實施分解與結合，以防沙土雜物進入槍機",
            "只要鋪上雨衣即可在泥濘砂地上分解結合",
            "役男可自行在走廊或草地上練習拆解槍機"
        ],
        "answer": 1,
        "explanation": "【257T新增題目 原文】T65K2步槍可在草地、砂地上實施分解與結合→錯誤(X)。嚴禁在草地、砂地上分解結合！",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 槍前哨與取槍 - 選擇題
    {
        "id": "MC-257-09",
        "category": "shooting",
        "type": "multiple_choice",
        "question": "依射擊訓練安全規定，非操作時間之槍枝管制規定為何？【257T新增題目 原文】",
        "options": [
            "非操作時間，嚴禁個人取槍瞄準，槍枝集放處應派出槍前哨",
            "非操作時間，役男可自行取槍加強箱上瞄準練習",
            "槍枝集放處無須派哨，由靶場安全軍官一人總管即可",
            "非操作時間役男可互相借槍檢查彼此槍機"
        ],
        "answer": 0,
        "explanation": "【257T新增題目 原文】非操作時間，嚴禁個人取槍瞄準，槍枝集放處應派出槍前哨→正確(O)。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 射擊口訣 - 選擇題（按原文chunk精確呈現）
    {
        "id": "MC-257-10",
        "category": "shooting",
        "type": "multiple_choice",
        "question": "射擊口訣八大要領為何？【257T考選擇 原文】",
        "options": [
            "托抵握貼瞄停扣報",
            "托握貼瞄抵扣報停",
            "抵托握貼瞄停報扣",
            "瞄貼握抵托停扣報"
        ],
        "answer": 0,
        "explanation": "【257T考選擇 原文】* 射擊口訣：托、抵、握、貼、瞄、停、扣、報。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 射擊口訣 - 是非題
    {
        "id": "TF-257-05",
        "category": "shooting",
        "type": "true_false",
        "question": "射擊口訣為「托、抵、握、貼、瞄、停、扣、報」八大要領。【257T考選擇 原文考點】",
        "answer": "O",
        "explanation": "【257T考選擇 原文】正確。射擊口訣：托抵握貼瞄停扣報。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 箱上瞄準 - 是非題
    {
        "id": "TF-257-06",
        "category": "shooting",
        "type": "true_false",
        "question": "步槍「箱上瞄準」鑑測訓練之合格標準為「5分鐘內畫3個三角形」。【257T考選擇 原文考點】",
        "answer": "O",
        "explanation": "【257T考選擇 原文】正確。箱上瞄準合格標準：5分鐘畫3個三角形。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 槍枝諸元與開發 - 選擇題
    {
        "id": "MC-257-11",
        "category": "shooting",
        "type": "multiple_choice",
        "question": "關於成功嶺新訓打靶使用槍枝「T65K2突擊步槍」之開發與設計諸元，下列敘述何者正確？【247、257T 期末考 原文】",
        "options": [
            "由高雄聯勤205廠於1987年開發，參考美製M16A2與AR-18步槍優點並針對T65與T65K1缺失改進，同年4月量產",
            "由聯勤202廠開發，主要仿製蘇聯AK-47步槍機構",
            "為水冷式、重型機槍，只具備單發半自動射擊模式",
            "採用彈鏈給彈，重量達7公斤以上之班用機槍"
        ],
        "answer": 0,
        "explanation": "【打靶筆記原文】由高雄的聯勤205廠於1987年開發的，參考了美製M16A2步槍、AR-18步槍的優點，並針對原T65式步槍、T65K1步槍的缺失進行改進，於該年4月量產。本槍是一種重量輕、空氣冷卻、氣體傳動、彈匣給彈、可做半自動，三發連放、全自動射擊之肩射武器。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 槍枝作動特性 - 是非題
    {
        "id": "TF-257-07",
        "category": "shooting",
        "type": "true_false",
        "question": "T65K2突擊步槍是一種重量輕、空氣冷卻、氣體傳動、彈匣給彈、可做半自動、三發連放、全自動射擊之肩射武器。【247T、257T 原文】",
        "answer": "O",
        "explanation": "【打靶筆記原文】正確。本槍是一種重量輕、空氣冷卻、氣體傳動、彈匣給彈、可做半自動，三發連放、全自動射擊之肩射武器。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    },
    # 驗槍指揮官 - 是非題
    {
        "id": "TF-257-08",
        "category": "shooting",
        "type": "true_false",
        "question": "槍械到達場地由中隊長統一指揮驗槍。【257T新增題目 原文考點】",
        "answer": "O",
        "explanation": "【257T新增題目 原文】槍械到達場地由誰統一指揮驗槍? (1)分隊長 (2)區隊長 (3)中隊長 (4)役男。答案為 (3)中隊長。",
        "source": "Google文件打靶筆記原文與247T、257T鑑測真題",
        "source_url": "https://docs.google.com/document/d/1ZVoioIgaMONwXbe6INEmwd22QzGqVPz7/edit#heading=h.36ei31r"
    }
]

# Add only non-existing ones
added_count = 0
for nq in new_shooting_questions:
    if nq['id'] not in existing_ids:
        questions.append(nq)
        existing_ids.add(nq['id'])
        added_count += 1

print(f"Added {added_count} new shooting questions from chunk!")
print(f"Total questions now: {len(questions)}")

# Update stats
cat_counts = {}
for q in questions:
    cat_counts[q['category']] = cat_counts.get(q['category'], 0) + 1

questions_file['questions'] = questions
questions_file['stats'] = {
    'total': len(questions),
    'categories': cat_counts
}

# Save questions.json
with open('data/questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions_file, f, ensure_ascii=False, indent=2)

print("Saved updated questions.json!")
