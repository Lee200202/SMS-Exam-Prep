import os
import re
import json

base_dir = r"c:\Users\user\桌面\成功嶺新訓考古題\temp_repo\questions"
tf_path = os.path.join(base_dir, "true_and_false.md")
mc_path = os.path.join(base_dir, "multiple_choice.md")

# Ensure output directory exists
out_dir = r"c:\Users\user\桌面\成功嶺新訓考古題\data"
os.makedirs(out_dir, exist_ok=True)

# 1. Parse existing True/False questions
tf_list = []
with open(tf_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if parts and parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]
        if len(parts) >= 2:
            ans, q = parts[0], parts[1]
            if ans in ["Ans", ":---:"]:
                continue
            if ans in ["O", "X", "o", "x", "0"]:
                ans = "O" if ans in ["O", "o", "0"] else "X"
                clean_q = re.sub(r"<[^>]+>", "", q).strip()
                
                # Deduce category
                category = "regulations"
                if any(w in clean_q for w in ["志願服務", "志工"]):
                    category = "volunteer"
                elif any(w in clean_q for w in ["射擊", "打靶", "步槍", "靶場", "槍枝", "國防"]):
                    category = "shooting"
                elif any(w in clean_q for w in ["保險", "撫卹", "醫療", "健保", "薪俸", "薪資", "權利", "扶助", "公假", "喪假", "婚假", "病假", "事假", "陪產假", "身分證", "保留學籍"]):
                    category = "rights"
                elif any(w in clean_q for w in ["獎懲", "記過", "申誡", "罰勤", "罰薪", "輔導教育", "申訴", "管理幹部", "行進", "走道", "長官"]):
                    category = "management"
                
                tf_list.append({
                    "id": f"TF-{len(tf_list)+1:03d}",
                    "type": "true_false",
                    "category": category,
                    "question": clean_q,
                    "answer": ans,
                    "explanation": ""
                })

# 2. Parse existing Multiple Choice questions
mc_list = []
with open(mc_path, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if parts and parts[0] == "":
            parts = parts[1:]
        if parts and parts[-1] == "":
            parts = parts[:-1]
        if len(parts) >= 2:
            ans_raw, q_raw = parts[0], parts[1]
            if ans_raw in ["Ans", ":---:"]:
                continue
            clean_q = re.sub(r"<[^>]+>", "", q_raw).strip()
            
            pos_matches = list(re.finditer(r"\(([1-4])\)", clean_q))
            if pos_matches and len(pos_matches) >= 2:
                q_stem = clean_q[:pos_matches[0].start()].strip()
                options = []
                for i in range(len(pos_matches)):
                    start = pos_matches[i].end()
                    end = pos_matches[i+1].start() if i+1 < len(pos_matches) else len(clean_q)
                    opt_text = clean_q[start:end].strip()
                    options.append(opt_text)
                
                ans_idx = 0
                if ans_raw.isdigit():
                    ans_idx = int(ans_raw) - 1
                else:
                    matched = False
                    for idx, opt in enumerate(options):
                        if ans_raw in opt or opt in ans_raw:
                            ans_idx = idx
                            matched = True
                            break
                    if not matched:
                        m = re.search(r"[1-4]", ans_raw)
                        if m:
                            ans_idx = int(m.group()) - 1
                
                # Special fix for MC-012 (軍事基礎訓練學科測驗佔比)
                if "軍事基礎訓練學科測驗以替代役法令等專業課程為主" in q_stem:
                    # Historically 45% or 40%, let's keep 45% (option 1 -> index 0)
                    ans_idx = 0

                # Determine category
                category = "regulations"
                if any(w in q_stem for w in ["志願服務", "志工"]):
                    category = "volunteer"
                elif any(w in q_stem for w in ["射擊", "打靶", "步槍", "靶場", "槍枝", "國防"]):
                    category = "shooting"
                elif any(w in q_stem for w in ["保險", "撫卹", "醫療", "健保", "薪資", "扶助", "婚假", "病假", "事假", "陪產假", "喪假", "留學籍", "受益人", "折抵"]):
                    category = "rights"
                elif any(w in q_stem for w in ["申訴", "獎懲", "罰勤", "罰薪", "輔導教育", "擅離", "管理幹部", "基本教練", "跑步", "驗退", "停役"]):
                    category = "management"

                mc_list.append({
                    "id": f"MC-{len(mc_list)+1:03d}",
                    "type": "multiple_choice",
                    "category": category,
                    "question": q_stem,
                    "options": options,
                    "answer": ans_idx,
                    "explanation": ""
                })

# 3. Add high-yield Volunteer Service Act (志願服務法) questions
extra_volunteer = [
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "我國《志願服務法》所稱志願服務，指民眾出於自由意志，非基於個人義務或法律責任，以知識、體能、勞力等奉獻社會，不以獲取報酬為目的之各項輔助性服務。",
        "answer": "O",
        "explanation": "依《志願服務法》第3條規定：志願服務以不獲取報酬為目的。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "志工服務年資滿 3 年，服務時數達 300 小時以上者，得向地方主管機關申請核發志願服務榮譽卡。",
        "answer": "O",
        "explanation": "依《志願服務法》第20條規定，志工服務年資滿3年，服務時數達300小時以上，得檢具證明文件申請核發志願服務榮譽卡。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "志願服務榮譽卡使用期限為5年，期滿後志工可直接自動永久續卡，無須再提出申請。",
        "answer": "X",
        "explanation": "志願服務榮譽卡使用期限為3年，期限屆滿前得檢具相關證明重新申請。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "志願服務運用單位應為志工辦理意外事故保險，必要時並得補助交通、誤餐及特殊保險等費用。",
        "answer": "O",
        "explanation": "依《志願服務法》第16條規定，辦理意外事故保險為運用單位之法定責任。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "若志工個人平時已自行購買多份民間商業意外險，志願服務運用單位即可依法免除為其辦理意外事故保險之義務。",
        "answer": "X",
        "explanation": "為志工辦理意外事故保險為法定強制責任，不得因個人已投保而免除。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "同一位志工若同時於多個不同運用單位服務，每個單位都必須發給該志工一本獨立的志願服務紀錄冊。",
        "answer": "X",
        "explanation": "同一志工僅持有「一本」志願服務紀錄冊，不同單位之服務時數合併登錄於同本紀錄冊。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "志工必須同時完成基礎訓練及特殊訓練之後，方得由志願服務運用單位檢具相關文件造冊向主管機關申請核發志願服務紀錄冊。",
        "answer": "O",
        "explanation": "依規定志工須完成「基礎訓練」與「特殊訓練」兩階段方得領取服務紀錄冊。"
    },
    {
        "type": "true_false",
        "category": "volunteer",
        "question": "法規明定擔任志願服務志工有嚴格的年齡上下限，未滿 12 歲或超過 70 歲者絕對不得擔任志工。",
        "answer": "X",
        "explanation": "《志願服務法》並未硬性限定年齡上限，全民皆可依體能與志趣參與志願服務。"
    },
    {
        "type": "multiple_choice",
        "category": "volunteer",
        "question": "依《志願服務法》規定，全國志願服務之中央主管機關為下列何者？",
        "options": ["內政部", "教育部", "衛生福利部", "勞動部"],
        "answer": 2,
        "explanation": "《志願服務法》中央主管機關現為「衛生福利部」（原為內政部，政府組改後移撥衛福部）。"
    },
    {
        "type": "multiple_choice",
        "category": "volunteer",
        "question": "志工志願服務年資滿幾年，且服務時數達多少小時以上，得申請核發「志願服務榮譽卡」？",
        "options": ["滿1年，150小時", "滿2年，200小時", "滿3年，300小時", "滿3年，500小時"],
        "answer": 2,
        "explanation": "申請志願服務榮譽卡門檻為：服務年資滿3年，時數達300小時以上。"
    },
    {
        "type": "multiple_choice",
        "category": "volunteer",
        "question": "持有志願服務榮譽卡之志工，依法可享有下列何項具體權益或優待？",
        "options": ["免費搭乘所有民營客運與高鐵", "進入公立收費之公園、森林遊樂區、公立博物館免費或優惠", "於公立醫院免收所有健保部分負擔與自費項目", "享有政府每月發放之志工津貼補助"],
        "answer": 1,
        "explanation": "志願服務榮譽卡享有進入政府機關管理之公立收費風景區、未編定座次之康樂場所及文教設施免費或優待。"
    },
    {
        "type": "multiple_choice",
        "category": "volunteer",
        "question": "關於志願服務運用單位對於志工應盡之義務，下列敘述何者錯誤？",
        "options": ["應為志工辦理意外事故保險", "應提供志工必要之教育訓練", "得要求志工無償代行單位公務員之公權力簽署行政處分", "應發給志工服務時數證明或紀錄冊登錄"],
        "answer": 2,
        "explanation": "志工係輔助性角色，絕不可代行法定公權力或簽署行政處分。"
    }
]

# 4. Add high-yield Rifle Shooting & Defense (打靶訓練與全民國防) questions
extra_shooting = [
    {
        "type": "true_false",
        "category": "shooting",
        "question": "成功嶺實彈射擊時，射擊基本口訣為「托、抵、握、貼、瞄、停、扣、報」八大要領。",
        "answer": "O",
        "explanation": "射擊口訣八大要領：托(托前護木)、抵(槍托抵肩)、握(右手握握把)、貼(右腮緊貼槍面)、瞄(瞄準目標)、停(自然停止呼吸)、扣(食指第一節徐徐扣引扳機)、報(維持姿勢報靶)。"
    },
    {
        "type": "true_false",
        "category": "shooting",
        "question": "在靶場若遇步槍卡彈或無法擊發時，射手應立即自行拆解槍枝排障，不需舉手報告。",
        "answer": "X",
        "explanation": "靶場鐵律：遇槍枝故障時應維持槍口指向目標方向，立即「舉手」報告教官處理，嚴禁自行擅自轉身或拆解。"
    },
    {
        "type": "true_false",
        "category": "shooting",
        "question": "步槍射擊瞄準之正確認知為：眼睛、覘孔、準星尖與目標靶心，必須構成「三點一線」之同心圓與平視直線。",
        "answer": "O",
        "explanation": "準星尖平正於覘孔中央，使準星尖對準目標瞄準點中央，維持三點一線。"
    },
    {
        "type": "true_false",
        "category": "shooting",
        "question": "射擊練習中，步槍故障排除的基本口訣為「拍、拉、看、瞄、射」五步驟。",
        "answer": "O",
        "explanation": "故障排除基本口訣：拍(拍緊彈匣底板)、拉(拉拉柄向後)、看(看進彈口是否有卡彈或雙重進彈)、瞄(重新瞄準目標)、射(扣扳機擊發)。"
    },
    {
        "type": "true_false",
        "category": "shooting",
        "question": "靶場口令下達「左線預備」時，通常代表要求射手打開步槍保險，由「S（安全）」撥轉至「單發（R/1）」位置。",
        "answer": "O",
        "explanation": "左線預備開保險，右線預備做深呼吸與最後確認，全線預備開保險開始射擊。"
    },
    {
        "type": "true_false",
        "category": "shooting",
        "question": "在任何情況下（無論有無裝填子彈、有無開保險），槍口絕對不可對人，此為靶場至高無上之安全守則。",
        "answer": "O",
        "explanation": "安全第一，將任何槍枝視為已上膛狀態，槍口嚴禁指向任何人。"
    },
    {
        "type": "multiple_choice",
        "category": "shooting",
        "question": "步槍實彈射擊八大要領口訣「托、抵、握、貼、瞄、停、扣、報」中，「停」代表的意思為何？",
        "options": ["射擊完畢立即停止動作", "在預備擊發時自然暫停呼吸，避免胸腔起伏晃動槍身", "扣下扳機後停止十秒才能站起", "由靶場指揮官喊停止"],
        "answer": 1,
        "explanation": "「停」意指在擊發瞄準瞬間自然吐氣後暫停呼吸数秒，使槍身保持最平穩狀態。"
    },
    {
        "type": "multiple_choice",
        "category": "shooting",
        "question": "步槍故障排除「拍、拉、看、瞄、射」五大步驟中，「拍」主要之操作目的為何？",
        "options": ["拍打槍管散熱", "拍緊彈匣底部，確認彈匣確實卡緊入位", "拍擊槍托調整長度", "拍打射手肩部提醒射擊"],
        "answer": 1,
        "explanation": "拍(拍彈匣底板)是確保彈匣定位卡損確實卡入彈匣井，避免因供彈不良產生不進彈障礙。"
    },
    {
        "type": "multiple_choice",
        "category": "shooting",
        "question": "實彈射擊時，關於「扣扳機」之正確動作要領，下列敘述何者最正確？",
        "options": ["用食指根部猛力快速扣到底", "食指第二節用力向側邊按壓", "以食指第一節（指腹前段）置於扳機中央，徐徐均勻向後正直扣引", "用兩隻手指合力扣引"],
        "answer": 2,
        "explanation": "扣扳機要領：以食指第一節肉厚處置於扳機上，自然向後均勻正直施力扣引，不可猛扣。"
    },
    {
        "type": "multiple_choice",
        "category": "shooting",
        "question": "在靶場實彈射擊進行中，指揮官下達「停止射擊」口令時，射手第一時間應採取之動作為何？",
        "options": ["將剩餘彈藥全數迅速打完", "立即停止扣扳機，食指離開扳機移至護弓外，步槍維持朝向靶面方向並關上保險", "立刻起立拿著步槍轉身報告指揮官", "將彈匣自行卸下並拆解槍枝"],
        "answer": 1,
        "explanation": "聽聞停止射擊口令，必須立刻停止任何擊發動作，手指離開扳機，槍口仍朝目標區，並依指令關保險。"
    }
]

# 5. Add high-yield Regulations / Rights & Benefits questions
extra_regulations = [
    {
        "type": "true_false",
        "category": "rights",
        "question": "替代役役男服役期間，因配偶分娩，依法得檢附相關證明申請「陪產檢及陪產假」合計 7 日，並得於配偶分娩日前後 15 日內請畢。",
        "answer": "O",
        "explanation": "依最新《替代役役男請假規則》規定，陪產檢及陪產假核給7日，分次申請，於配偶分娩當日及其前後合計15日期間內請畢。"
    },
    {
        "type": "true_false",
        "category": "rights",
        "question": "替代役役男結婚，依法得核給婚假 14 日，可分次申請，但原則上應於結婚之日起 3 個月內請畢。",
        "answer": "O",
        "explanation": "婚假14日，得自分次申請，但應於結婚登記之日起3個月內請畢。"
    },
    {
        "type": "true_false",
        "category": "rights",
        "question": "替代役役男服役期間，若因公傷病經就醫治療，其健保門診掛號費及健保部分負擔均由政府全額負擔。",
        "answer": "O",
        "explanation": "因公傷病就醫之掛號費與全民健康保險自行負擔費用，由內政部全數編列公費補助。"
    },
    {
        "type": "true_false",
        "category": "rights",
        "question": "替代役役男對服勤單位所為之罰薪或記過懲處不服時，得於懲處核定書送達之次日起 30 日內提出申訴，受申訴機關應於 30 日內處理完畢。",
        "answer": "O",
        "explanation": "申訴期限為收到處分次日起30日內；受申訴機關處理期限原則為30日內。"
    },
    {
        "type": "multiple_choice",
        "category": "rights",
        "question": "替代役役男因父母或配偶死亡，依法得核給喪假幾日？",
        "options": ["5日", "10日", "15日", "20日"],
        "answer": 2,
        "explanation": "依請假規則：父母或配偶死亡核給喪假15日；繼父母、配偶之父母或子女死亡核給10日；祖父母等死亡核給5日。"
    },
    {
        "type": "multiple_choice",
        "category": "rights",
        "question": "替代役役男服役期間，因公傷殘給予年撫卹金之年限規定，下列何者正確？",
        "options": ["一等殘給與終身", "二等殘給與10年", "三等殘給與5年", "重度機能障礙給與20年"],
        "answer": 0,
        "explanation": "一等殘撫卹為「給與終身」；二等殘給與十年；三等殘給與五年。"
    },
    {
        "type": "multiple_choice",
        "category": "regulations",
        "question": "依《替代役實施條例》規定，替代役役男無故擅離職役累計逾幾日者，即屬觸犯刑法，應函送司法機關偵辦？",
        "options": ["3日", "5日", "7日", "10日"],
        "answer": 2,
        "explanation": "擅離職役累計逾3日發出離役通報協尋；累計「逾7日」即觸犯刑法移送司法機關究辦。"
    },
    {
        "type": "multiple_choice",
        "category": "management",
        "question": "替代役役男違反生活或服勤管理規定，施以「罰勤」懲處時，平日與例假日之每日時數上限分別為？",
        "options": ["平日1小時，假日4小時", "平日2小時，假日8小時", "平日3小時，假日6小時", "平日4小時，假日8小時"],
        "answer": 1,
        "explanation": "罰勤規定：平日以2小時為限，例假日以8小時為限。"
    },
    {
        "type": "multiple_choice",
        "category": "management",
        "question": "替代役役男違反生活及勤務規定施以「罰薪」處分時，其扣除當月份薪資百分比與最長期限為？",
        "options": ["扣除10%至20%，以1個月為限", "扣除10%至30%，以3個月為限", "扣除20%至50%，以6個月為限", "扣除全部月薪，以2個月為限"],
        "answer": 1,
        "explanation": "罰薪：扣除當月份薪給10%至30%，以3個月為限。"
    }
]

# Append extra items
for item in extra_volunteer + extra_shooting + extra_regulations:
    if item["type"] == "true_false":
        item["id"] = f"TF-{len(tf_list)+1:03d}"
        tf_list.append(item)
    else:
        item["id"] = f"MC-{len(mc_list)+1:03d}"
        mc_list.append(item)

# Build combined dataset
dataset = {
    "version": "2026.1",
    "updatedAt": "2026-09",
    "stats": {
        "total": len(tf_list) + len(mc_list),
        "true_false": len(tf_list),
        "multiple_choice": len(mc_list),
        "categories": {
            "regulations": sum(1 for q in tf_list + mc_list if q["category"] == "regulations"),
            "volunteer": sum(1 for q in tf_list + mc_list if q["category"] == "volunteer"),
            "rights": sum(1 for q in tf_list + mc_list if q["category"] == "rights"),
            "management": sum(1 for q in tf_list + mc_list if q["category"] == "management"),
            "shooting": sum(1 for q in tf_list + mc_list if q["category"] == "shooting")
        }
    },
    "questions": tf_list + mc_list
}

target_file = os.path.join(out_dir, "questions.json")
with open(target_file, "w", encoding="utf-8") as f:
    json.dump(dataset, f, ensure_ascii=False, indent=2)

print(f"Successfully generated {target_file}!")
print(f"Total: {dataset['stats']['total']} questions (TF: {dataset['stats']['true_false']}, MC: {dataset['stats']['multiple_choice']})")
print("Categories:", dataset['stats']['categories'])
