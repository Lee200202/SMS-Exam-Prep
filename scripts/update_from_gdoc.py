import json
import os
import re

gdoc_txt_path = r"C:\Users\user\.gemini\antigravity\brain\878a1b48-4d39-4b52-998b-42ffd65dd18f\.system_generated\steps\97\content.md"

# Load current questions.json
with open("data/questions.json", "r", encoding="utf-8") as f:
    questions_data = json.load(f)

# Load current study_data.json
with open("data/study_data.json", "r", encoding="utf-8") as f:
    study_data = json.load(f)

# Read Google doc text
with open(gdoc_txt_path, "r", encoding="utf-8") as f:
    gdoc_text = f.read()

# 1. Add 257T Shooting and recent exam questions
extra_257_questions = [
    {
        "id": "TF-257-01",
        "type": "true_false",
        "category": "shooting",
        "exam_tag": "【257T考】",
        "question": "T65K2步槍避火罩具有減音、滅光、減少後座力之功用。",
        "answer": "X",
        "explanation": "依國軍步槍教範，T65K2步槍槍口避火罩主要功用僅為「減光」，並無顯著減音或減少後座力之設計。"
    },
    {
        "id": "TF-257-02",
        "type": "true_false",
        "category": "shooting",
        "exam_tag": "【257T考】",
        "question": "T65K2步槍覘孔可分為前覘孔與後覘孔，前覘孔為射擊0至300公尺目標，後覘孔為射擊300至800公尺目標。",
        "answer": "O",
        "explanation": "正確。0-3覘孔為近距離（0-300公尺不含），3-8覘孔為中遠距離（300-800公尺）瞄準使用。"
    },
    {
        "id": "TF-257-03",
        "type": "true_false",
        "category": "shooting",
        "exam_tag": "【257T考】",
        "question": "為求訓練迅速與方便，T65K2步槍可在草地或砂地上直接實施槍枝分解與結合。",
        "answer": "X",
        "explanation": "嚴禁在草地、砂地上實施槍枝分解與結合，以避免砂石塵土進入機匣磨損零件，並防細小機件遺失。"
    },
    {
        "id": "TF-257-04",
        "type": "true_false",
        "category": "shooting",
        "exam_tag": "【257T考】",
        "question": "靶場非操作與射擊時間，嚴禁個人擅自取槍瞄準，槍枝集中放置處應指派槍前哨負責警戒。",
        "answer": "O",
        "explanation": "靶場安全至上，非射擊時間個人絕不可隨意取槍瞄準把玩，槍枝架放處須有專人哨兵看守。"
    },
    {
        "id": "MC-257-01",
        "type": "multiple_choice",
        "category": "shooting",
        "exam_tag": "【257T考】",
        "question": "實彈射擊實施時，槍械到達靶場後應由何人統一指揮下達驗槍程序？",
        "options": ["分隊長", "區隊長", "中隊長", "實彈射擊役男本人"],
        "answer": 2,
        "explanation": "槍械到達射擊場地由「中隊長」親自統一指揮驗槍，確認無彈無虞後始得展開後續操課。"
    },
    {
        "id": "MC-257-02",
        "type": "multiple_choice",
        "category": "shooting",
        "exam_tag": "【257T考】",
        "question": "步槍「箱上瞄準」訓練測驗之合格標準與要求為？",
        "options": ["3分鐘內畫2個三角形", "5分鐘內畫3個三角形", "10分鐘內畫5個三角形", "無時間限制畫出同心圓即可"],
        "answer": 1,
        "explanation": "箱上瞄準測驗要求：5分鐘內在標靶紙上連續完成3個三角形瞄準點，三點連線構成之三角形越小表示瞄準線越穩定一致。"
    },
    {
        "id": "MC-257-03",
        "type": "multiple_choice",
        "category": "regulations",
        "exam_tag": "【205T/219T/257T考】",
        "question": "依《替代役實施條例》規定，替代役之法定主管機關為下列何者？",
        "options": ["內政部", "國防部", "行政院", "直轄市、縣(市)政府"],
        "answer": 0,
        "explanation": "《替代役實施條例》第2條明定：本條例所稱主管機關為內政部（替代役業務由內政部役政署承辦）。"
    },
    {
        "id": "MC-257-04",
        "type": "multiple_choice",
        "category": "management",
        "exam_tag": "【247T/257T考】",
        "question": "依役男獎懲規定，替代役役男違反生活及勤務規定予以「罰勤」時，例假日每日以幾小時為限？",
        "options": ["2小時", "4小時", "6小時", "8小時"],
        "answer": 3,
        "explanation": "平日罰勤以2小時為限；例假日罰勤以8小時為限。榮譽假1日可抵銷罰勤8小時。"
    },
    {
        "id": "MC-257-05",
        "type": "multiple_choice",
        "category": "regulations",
        "exam_tag": "【247T/257T考】",
        "question": "役男入營後，因體格不適服替代役者，應於入營幾天內辦理驗退？",
        "options": ["15天", "20天", "30天", "45天"],
        "answer": 2,
        "explanation": "《替代役實施條例》第10條及施行細則規定：入營後30天內因體格不適服替代役者辦理驗退。"
    }
]

# Tag existing questions with exam occurrences if mentioned in gdoc
for q in questions_data["questions"]:
    # Match keywords in gdoc to tag
    stem = q["question"][:15]
    if stem in gdoc_text:
        # Search for pattern like 【205T考】【215T考】【219T考】【247T考】【257T考】
        idx = gdoc_text.find(stem)
        snippet = gdoc_text[max(0, idx-50):min(len(gdoc_text), idx+150)]
        tags = re.findall(r"【[0-9]+T[^】]*】|［[0-9]+T[^］]*］", snippet)
        if tags and not q.get("exam_tag"):
            q["exam_tag"] = "".join(tags[:3])

# Append extra 257T questions
questions_data["questions"].extend(extra_257_questions)
questions_data["stats"]["total"] = len(questions_data["questions"])
questions_data["stats"]["true_false"] = sum(1 for q in questions_data["questions"] if q["type"] == "true_false")
questions_data["stats"]["multiple_choice"] = sum(1 for q in questions_data["questions"] if q["type"] == "multiple_choice")
questions_data["stats"]["shooting"] = sum(1 for q in questions_data["questions"] if q["category"] == "shooting")

# 2. Update study_data.json with 247T official score ratios & 2024 Packing list
study_data["rights_and_management"]["grade_breakdown"] = {
    "title": "成功嶺軍事基礎訓練成績計算公式 (247T最新更新標準)",
    "desc": "基礎訓練成績直接影響撥交時的「選服勤單位（選役別）」志願順位，佔分發總成績不得低於40%！",
    "components": [
        {"name": "學科測驗 (筆試)", "ratio": "35%", "desc": "包含替代役法令、志願服務法等是非題與選擇題"},
        {"name": "術科測驗 (鑑測)", "ratio": "35%", "desc": "體能測驗 15% (3000公尺徒手跑步) + 徒手基本教練 20%"},
        {"name": "EMT-1 初級救護技術員", "ratio": "20%", "desc": "術科操作 12% + 學科筆試 8% (關鍵鑑測科目)"},
        {"name": "平時生活與內務考核", "ratio": "10%", "desc": "日常秩序、幹部公差加分、內務棉被蚊帳整潔程度"}
    ]
}

# Add T65K2 rifle specifications to shooting section
study_data["shooting"]["t65k2_specs"] = {
    "title": "T65K2突擊步槍諸元與鑑測考點",
    "facts": [
        "**產製歷程**：高雄聯勤205廠於1987年開發，參考美製M16A2與AR-18步槍優點，針對T65與T65K1改良，同年4月量產。",
        "**槍枝特性**：重量輕、空氣冷卻、氣體傳動、彈匣給彈，具備半自動、三發點放、全自動射擊模式。",
        "**覘孔射程**：0至3覘孔適用於 0~300公尺（不含）目標射擊；3至8覘孔適用於 300（含）~800公尺目標射擊。",
        "**避火罩功能**：主要功用為「減光」，無減音或減少後座力功能（257T是非題考點！）。",
        "**箱上瞄準**：合格標準為「5分鐘內畫3個三角形」。",
        "**驗槍指揮**：槍械到達場地由「中隊長」統一指揮驗槍（257T選擇題考點！）。",
        "**安全守則**：嚴禁在草地、砂地上實施槍枝分解結合；非操作時間嚴禁取槍瞄準，槍枝集放處派設槍前哨。"
    ]
}

# Update packing list with 2024/08 Google Doc details
study_data["packing_list"] = {
    "title": "成功嶺新訓必備用品建議檢核表 (2024最新梯次實測整理)",
    "description": "203T~257T學長血淚傳承！區分入營前必備文件、重要證件、生活採買與沒用避坑清單，支援線上打勾與本機進度保存。",
    "categories": [
        {
            "id": "docs_2024",
            "name": "一、各式重要 A4 文件 (L夾裝好，報到必查)",
            "color": "rose",
            "items": [
                {"id": "d24-1", "name": "徵集令正本", "tip": "入營搭車與報到必備身分查驗", "must": True},
                {"id": "d24-2", "name": "役期折抵成績單正本", "tip": "高中、大學教官室蓋章之成績單正本，折抵役期必備", "must": True},
                {"id": "d24-3", "name": "最高學歷證明影本", "tip": "選役別時學歷評比重要依據", "must": True},
                {"id": "d24-4", "name": "郵局存摺正面影本", "tip": "每月役男薪資直接匯款發放用", "must": True},
                {"id": "d24-5", "name": "役別甄選專長佐證資料", "tip": "國家專長證照、英文檢定證明、相關經歷，選役別大利多", "must": False},
                {"id": "d24-6", "name": "印出來的考古題重點", "tip": "大餐課或零碎時間背誦，手機管制時的刷題神器", "must": False}
            ]
        },
        {
            "id": "cards_money",
            "name": "二、重要證件、現金與隨身物品",
            "color": "amber",
            "items": [
                {"id": "cm-1", "name": "國民身分證正本", "tip": "身分驗證必備", "must": True},
                {"id": "cm-2", "name": "健保IC卡", "tip": "轉診、醫務室掛號必備", "must": True},
                {"id": "cm-3", "name": "現金 (建議備 2000~3000 元)", "tip": "257T入營需收800現金（團體照、理髮、洗衣等），多備百元鈔", "must": True},
                {"id": "cm-4", "name": "個人私章 (便宜木頭章)", "tip": "各項簽收與裝備領取蓋章，勿帶貴重印鑑", "must": True},
                {"id": "cm-5", "name": "提款卡、悠遊卡、家裡鑰匙", "tip": "放進貴重物品袋隨身集中保管", "must": True},
                {"id": "cm-6", "name": "手機 + 滿電行動電源 1~2 顆", "tip": "營區插座管制無法使用豆腐頭，放手機時間全靠行動電源", "must": True},
                {"id": "cm-7", "name": "有線耳機 3.5mm/Type-C", "tip": "重點提醒：無線藍牙耳機一律為違禁品會被集中保管！", "must": False},
                {"id": "cm-8", "name": "豆腐頭充電器 (收違禁品袋)", "tip": "專訓階段高機率會開放使用插座充電", "must": False},
                {"id": "cm-9", "name": "休閒讀物 (單張印製，不可整本書)", "tip": "小說、數獨、文章印成一張一張的，整本裝訂雜誌小說易被管", "must": False}
            ]
        },
        {
            "id": "daily_hygiene",
            "name": "三、盥洗用品與個人隨身藥品",
            "color": "emerald",
            "items": [
                {"id": "dh-1", "name": "三合一沐浴乳 (洗髮/洗臉/洗澡)", "tip": "戰鬥洗澡搶時間神器，推薦好起泡且好沖洗款式", "must": True},
                {"id": "dh-2", "name": "牙刷 (要能平躺放水杯) & 牙膏", "tip": "內務檢查要求刷毛朝上能平放水杯", "must": True},
                {"id": "dh-3", "name": "手動刮鬍刀", "tip": "不能使用電動充電款，手動最保險", "must": True},
                {"id": "dh-4", "name": "指甲剪 (務必附集屑盒)", "tip": "定期檢查，無集屑盒容易掉碎屑被扣內務分", "must": True},
                {"id": "dh-5", "name": "有夜光與鬧鐘功能的防水手錶", "tip": "部隊生活時間觀念最重要，夜間看時間必備", "must": True},
                {"id": "dh-6", "name": "袖珍包衛生紙 15~20 包", "tip": "隨身口袋常備，操課擦汗、上廁所必備", "must": True},
                {"id": "dh-7", "name": "喉糖 2~3 盒 (全新未拆封)", "tip": "營區唯一合法甜食小確幸，喊口號喉嚨痛救星", "must": True},
                {"id": "dh-8", "name": "極凍涼感濕紙巾 2~3 包", "tip": "夏日大出操後擦臉頸部瞬間降溫超爽快", "must": False},
                {"id": "dh-9", "name": "防蚊液 (重點：不可用噴霧！)", "tip": "建議派卡瑞丁(Picaridin)乳液或滾珠型，防小黑蚊效果最佳", "must": True},
                {"id": "dh-10", "name": "止癢涼感藥品 / 曼秀雷敦", "tip": "防蚊蟲叮咬與提神", "must": False},
                {"id": "dh-11", "name": "長尾夾 4~6 個 (內務定型神器)", "tip": "折棉被、拉蚊帳線條時偷夾住，內務加分神物", "must": False},
                {"id": "dh-12", "name": "休假衣服一套與便帽", "tip": "結訓休假當天穿著離營", "must": True}
            ]
        },
        {
            "id": "station_buy",
            "name": "四、入營當天營站採買推薦物品",
            "color": "sky",
            "items": [
                {"id": "sb-1", "name": "大塑膠袋 x 3 (裝貴重、違禁、藥品)", "tip": "安檢第一天分類大包裝必備", "must": True},
                {"id": "sb-2", "name": "抽取式衛生紙 x 2~3 包", "tip": "一包檢查用絕不開封維持方正，其餘自用", "must": True},
                {"id": "sb-3", "name": "純白毛巾 (可加買 1 條，公發 2 條)", "tip": "掛床頭檢查用，多一條自用洗臉洗澡", "must": True},
                {"id": "sb-4", "name": "公發藍白拖鞋 (營站購買)", "tip": "營區洗澡與寢室活動必穿", "must": True},
                {"id": "sb-5", "name": "排汗內衣 (加買 1~2 件，公發 3 件)", "tip": "夏天流汗多，多備替換洗滌方便", "must": False},
                {"id": "sb-6", "name": "四角內褲 (加買 1~2 件，公發 2 件)", "tip": "公發材質較粗，自備加買舒適很多", "must": False},
                {"id": "sb-7", "name": "黑色中筒軍襪 (加買 1~2 雙，公發 2 雙)", "tip": "每天穿軍靴吸汗替換", "must": False},
                {"id": "sb-8", "name": "耳塞 & 鋼盔海綿墊", "tip": "打靶防耳鳴、戴鋼盔舒適度大幅提升", "must": False}
            ]
        },
        {
            "id": "pitfalls_contraband",
            "name": "五、學長避坑：沒用物品與違禁品警告",
            "color": "red",
            "items": [
                {"id": "pit-1", "name": "❌ 奇異筆（違禁品，會被沒入）", "tip": "公發會發藍筆紅筆，私帶奇異筆常被列入管制", "must": False, "is_danger": True},
                {"id": "pit-2", "name": "❌ 針線盒（不用買，257T有直接送）", "tip": "營區或兵役局通常會送小針線包", "must": False},
                {"id": "pit-3", "name": "❌ 洗衣袋（不用買，公發直接發 3 個）", "tip": "洗衣袋皆有統一中隊號碼標籤，私帶無法送洗", "must": False},
                {"id": "pit-4", "name": "❌ 防磨腳跟貼（257T已換新款皮鞋不磨腳）", "tip": "新款黑皮鞋改良後柔軟不咬腳，幾乎用不到", "must": False},
                {"id": "pit-5", "name": "🚫 打火機、香菸、電子菸、加熱菸", "tip": "營區全面禁菸，查獲一律沒入並從嚴處分", "must": False, "is_danger": True},
                {"id": "pit-6", "name": "🚫 美工刀、剪刀、水果刀等鋒利器具", "tip": "危險物品，安檢直接保管", "must": False, "is_danger": True},
                {"id": "pit-7", "name": "🚫 零食、含糖飲料、外食（喉糖除外）", "tip": "會招引蟲蟻，嚴重影響寢室內務", "must": False, "is_danger": True}
            ]
        }
    ]
}

# Save updated questions.json
with open("data/questions.json", "w", encoding="utf-8") as f:
    json.dump(questions_data, f, ensure_ascii=False, indent=2)

# Save updated study_data.json
with open("data/study_data.json", "w", encoding="utf-8") as f:
    json.dump(study_data, f, ensure_ascii=False, indent=2)

# Re-bundle data_bundle.js
bundle_content = f"""// Auto-generated data bundle for offline & GitHub Pages support
window.APP_QUESTIONS = {json.dumps(questions_data, ensure_ascii=False)};
window.APP_STUDY_DATA = {json.dumps(study_data, ensure_ascii=False)};
"""

with open("data/data_bundle.js", "w", encoding="utf-8") as f:
    f.write(bundle_content)

print(f"Update complete! Total questions: {len(questions_data['questions'])}")
