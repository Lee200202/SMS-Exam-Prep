# -*- coding: utf-8 -*-
"""
2026-10 逐題查核結果的套用腳本（可重複執行）。

查核方式：以 data/laws.json（全國法規資料庫現行條文）逐題比對，人工判定後把結論寫在本檔的表格裡。
- LAW_BASIS：確認有條文依據的題目 → 來源改為該條文、解析改為條文原文。
- FIXES：與現行條文牴觸而改寫的題目。
- OUTDATED：現行法規已無對應規定的舊法題，保留在題庫供對照，不列入測驗。
- 其餘題目：收錄的法規中查無明文（多為營區規定、行政作業或歷屆經驗），保留歷屆答案並標示「未能以法規查核」。

執行後會更新 questions.json、emt_questions.json、study_data.json、emt_study_data.json，
並產生 docs/資料查核紀錄.md。之後請跑 validate_data.py 與 generate_bundle.py。
"""
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEWED_AT = "2026-10-04"


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def save(name, data):
    with open(os.path.join(ROOT, "data", name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


LAWS = {l["pcode"]: l for l in load("laws.json")["laws"]}


def article(pcode, no):
    for chapter in LAWS[pcode]["chapters"]:
        for art in chapter["articles"]:
            if art["no"] == str(no):
                return art
    raise KeyError("%s 第 %s 條不存在" % (pcode, no))


def single_url(pcode, no):
    return "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=%s&flno=%s" % (pcode, no)


def quote(pcode, no, keyword=""):
    """回傳條文中含關鍵字的那一行（找不到關鍵字就用第一行）；若該行是列舉的開頭，補上整條。"""
    art = article(pcode, no)
    lines = [text for _, text in art["lines"]]
    picked = next((t for t in lines if keyword and keyword in t), lines[0])
    if keyword and keyword not in picked:
        raise ValueError("%s 第 %s 條找不到「%s」" % (pcode, no, keyword))
    if picked.endswith("：") and len("".join(lines)) < 260:
        picked = "".join(lines)
    elif re.match(r"^[（(]?[一二三四五六七八九十]+[）)、]", picked) and lines[0].endswith("："):
        picked = lines[0] + picked  # 列舉項目前面補上該條的開頭
    return picked


def basis(q, pcode, no, keyword=""):
    law = LAWS[pcode]["name"]
    q["source_kind"] = "law"
    q["source"] = "%s 第%s條" % (law, no)
    q["source_url"] = single_url(pcode, no)
    q["review"] = "law"
    q["explanation"] = "《%s》第%s條：%s" % (law, no, quote(pcode, no, keyword)) + SUFFIX.get(q["id"], "")


A, B = "D0040017", "D0040018"          # 替代役實施條例、施行細則
APPLY, MANAGE, LEAVE = "D0040016", "D0040020", "D0040021"
REWARD, COUNSEL, RIGHTS = "D0040028", "D0040019", "D0040024"
INSURE, PENSION, PAY = "D0040027", "D0040025", "D0040029"
ROSTER, EARLY, FAMILY, RECALL = "D0040022", "D0040026", "D0040032", "D0040033"
VOLUNTEER, EMS, EMT, TRAFFIC = "D0050131", "L0020045", "L0020141", "K0040013"

# 題號 -> (法規, 條號, 用來定位該行的關鍵字)
LAW_BASIS = {
    # ---- 替代役實施條例與子法
    "TF-001": (A, 2, ""), "MC-257-03": (A, 2, ""),
    "TF-002": (A, 3, ""), "TF-052": (A, 3, ""),
    "TF-003": (A, 4, "替代役之類別"), "TF-004": (A, 4, "替代役之類別"),
    "TF-046": (A, 4, "替代役之類別"), "TF-047": (A, 4, "替代役之類別"),
    "TF-005": (B, 3, "消防役"), "TF-008": (B, 3, "教育服務役"), "TF-009": (B, 3, "醫療役"),
    "TF-110": (B, 3, "環保役"), "MC-DOC2-09": (B, 3, "社會役"),
    "TF-006": (B, 2, ""), "TF-007": (B, 2, ""),
    "TF-010": (A, 5, "年滿十八歲"), "TF-090": (A, 5, "年滿十八歲"), "MC-044": (A, 5, "年滿十八歲"),
    "TF-049": (A, 5, "優先甄試"), "TF-104": (A, 5, "因犯罪"),
    "TF-105": (A, 6, ""),
    "TF-012": (A, 7, "與常備兵役同"), "TF-088": (A, 7, "與常備兵役同"), "TF-087": (A, 7, "與常備兵役同"),
    "TF-014": (A, 10, "足以危害團體健康"), "MC-043": (A, 10, "足以危害團體健康"),
    "MC-003": (A, 10, "傷病經鑑定不堪服役"), "MC-052": (A, 10, "經通緝、羈押"),
    "TF-015": (A, 10, "停役期間"), "MC-077": (A, 10, "停役期間"),
    "TF-058": (A, 11, "免予回役"), "TF-077": (A, 11, "免予回役"), "TF-DOC2-05": (A, 11, "免予回役"),
    "TF-016": (A, 12, "家庭發生重大變故"), "TF-017": (A, 12, "家庭發生重大變故"),
    "MC-DOC2-03": (A, 12, "家庭發生重大變故"),
    "TF-018": (A, 13, "訓練區分"), "MC-019": (A, 13, "由需用機關辦理"), "MC-055": (A, 13, "宗教因素"),
    "MC-062": (A, 18, ""),
    "TF-020": (A, 20, "學生保留學籍"), "TF-119": (A, 21, "轉任公職"),
    "TF-022": (A, 24, "兼職"), "TF-056": (A, 24, "兼職"), "MC-079": (A, 24, "替代役役男應履行下列義務"),
    "TF-055": (A, 25, ""),
    "TF-083": (A, 28, "平均領受"), "MC-049": (A, 30, ""), "MC-035": (A, 31, ""),
    "MC-028": (A, 32, "大學畢業"), "MC-085": (A, 32, "大學畢業"), "MC-036": (A, 32, "給與終身"),
    "MC-038": (A, 34, "一等給與終身"), "MC-095": (A, 34, "一等給與終身"),
    "TF-065": (A, 37, ""), "MC-037": (A, 38, ""),
    "TF-023": (A, 40, ""), "TF-034": (A, 43, "事故發生月份"),
    "TF-024": (A, 50, ""), "TF-071": (A, 50, ""), "MC-033": (A, 50, ""), "TF-DOC2-03": (A, 50, ""),
    "TF-043": (A, 52, ""), "TF-044": (A, 52, ""), "MC-046": (A, 52, ""), "MC-096": (A, 52, ""),
    "TF-025": (A, 53, ""), "MC-006": (A, 53, ""),
    "TF-026": (A, 55, "視情節輕重"), "TF-057": (A, 55, "視情節輕重"),
    "TF-027": (A, 55, "罰勤，平日"), "MC-011": (A, 55, "罰勤，平日"), "MC-097": (A, 55, "罰勤，平日"),
    "MC-257-04": (A, 55, "罰勤，平日"),
    "TF-028": (A, 55, "罰薪，扣除"), "MC-048": (A, 55, "罰薪，扣除"), "MC-098": (A, 55, "罰薪，扣除"),
    "TF-054": (A, 55, "報請需用機關核定"), "MC-073": (A, 55, "報請需用機關核定"),
    "MC-082": (A, 55, "報請需用機關核定"),
    "TF-076": (A, "55-1", "意圖避免"),
    "TF-030": (A, 58, ""), "TF-074": (A, 59, ""),
    "MC-025": (B, 12, "十分之一"), "MC-061": (B, 12, "十分之一"), "MC-DOC2-04": (B, 12, "管理幹部之甄選"),
    # ---- 役男申請服替代役辦法
    "TF-107": (APPLY, 11, "六十五歲以上"), "TF-111": (APPLY, 11, "役男育有子女"),
    "TF-123": (APPLY, 11, "役男育有子女"), "TF-101": (APPLY, 20, "抽籤"), "MC-016": (APPLY, 21, ""),
    # ---- 一般替代役役男訓練服勤管理辦法
    "TF-041": (MANAGE, 3, ""), "TF-072": (MANAGE, 7, ""), "MC-059": (MANAGE, 8, "勤務之編組"),
    "MC-DOC2-07": (MANAGE, 13, "集中或個別住宿"), "TF-DOC2-04": (MANAGE, 15, "得"),
    "TF-031": (MANAGE, 20, ""), "MC-068": (MANAGE, 20, ""), "MC-083": (MANAGE, 20, ""),
    # ---- 請假規則
    "MC-078": (LEAVE, 2, "出席作證"), "MC-069": (LEAVE, 2, "與其職務有關之各項會議或活動"),
    "TF-122": (LEAVE, 3, ""), "MC-018": (LEAVE, 3, ""), "MC-074": (LEAVE, 3, ""),
    "TF-066": (LEAVE, 4, ""), "TF-086": (LEAVE, 4, ""), "TF-138": (LEAVE, 4, ""),
    "MC-007": (LEAVE, 4, ""), "MC-076": (LEAVE, 4, ""),
    "TF-040": (LEAVE, 5, "可分次申請"), "TF-139": (LEAVE, 5, "可分次申請"), "MC-040": (LEAVE, 5, "婚假十四日"),
    "MC-029": (LEAVE, 6, "給假十五日"), "MC-031": (LEAVE, 6, "給假十五日"), "MC-094": (LEAVE, 6, "給假十五日"),
    "MC-030": (LEAVE, 6, "給假十日"), "MC-032": (LEAVE, 6, "給假十日"), "TF-095": (LEAVE, 6, "核給喪假"),
    "TF-039": (LEAVE, 7, ""), "TF-038": (LEAVE, 10, ""),
    # ---- 獎懲、輔導教育
    "TF-067": (REWARD, 3, ""), "TF-114": (REWARD, 10, "遺失識別證"),
    "TF-051": (REWARD, 11, "四小時以上"), "TF-100": (REWARD, 11, "四小時以上"),
    "MC-080": (REWARD, 12, "得予罰薪"), "TF-070": (REWARD, 13, "利用職權欺凌屬員"),
    "MC-081": (REWARD, 13, "累計三日以上"),
    "MC-054": (REWARD, 19, "應召開會議審議"), "MC-020": (REWARD, 19, "懲處處分書"),
    "TF-120": (REWARD, 20, "三十日內"), "TF-141": (REWARD, 20, "三十日內"), "MC-071": (REWARD, 20, "三十日內"),
    "MC-084": (REWARD, 21, ""), "MC-001": (REWARD, 22, "得不予處理"),
    "MC-027": (COUNSEL, 4, ""), "TF-073": (COUNSEL, 8, ""), "MC-063": (COUNSEL, 8, ""),
    # ---- 權利、保險醫療、撫卹、薪俸、役籍、提前退役、家屬扶助、召集
    "TF-021": (RIGHTS, 2, "給予公假"), "TF-096": (RIGHTS, 2, "家屬不能維持生活"),
    "TF-061": (RIGHTS, 4, ""), "MC-075": (RIGHTS, 4, ""), "TF-032": (RIGHTS, 6, ""), "TF-048": (RIGHTS, 10, ""),
    "TF-092": (INSURE, 2, ""), "TF-102": (INSURE, 3, "身心障礙給付"), "MC-021": (INSURE, 3, "身心障礙給付"),
    "MC-022": (INSURE, 3, "身心障礙給付"), "TF-103": (INSURE, 3, "平均分配"),
    "TF-097": (INSURE, 3, "親自指定"), "MC-009": (INSURE, 3, "親自指定"),
    "TF-099": (INSURE, 4, "親自填具"), "MC-067": (INSURE, 4, "親自填具"),
    "MC-034": (INSURE, 7, ""), "TF-042": (INSURE, 9, "退役後鑑定"),
    "MC-DOC2-10": (INSURE, "11-1", "替代役役男傷病赴國軍醫療院所就醫"),
    "TF-063": (INSURE, 12, "替代役役男傷病赴國軍醫療院所以外"), "MC-065": (INSURE, 12, "替代役役男傷病赴國軍醫療院所以外"),
    "TF-140": (INSURE, 12, "替代役役男傷病赴國軍醫療院所以外"), "MC-057": (INSURE, 12, "替代役役男傷病赴國軍醫療院所以外"),
    "TF-118": (INSURE, 12, "替代役役男傷病赴國軍醫療院所以外"), "TF-117": (INSURE, 12, "每半年一次預撥"),
    "MC-008": (PENSION, 16, "三個月"), "TF-121": (PAY, 3, "管理幹部"),
    "MC-015": (ROSTER, 4, "備役期間之役籍資料"),
    "TF-091": (EARLY, 2, "未滿十二歲"), "TF-108": (EARLY, 3, ""), "TF-112": (EARLY, 3, ""),
    "TF-069": (FAMILY, 10, "一次安家費"), "TF-068": (FAMILY, 10, "最高以六口為限"), "MC-004": (FAMILY, 10, "最高以六口為限"),
    "TF-106": (RECALL, 3, "演訓召集"), "MC-DOC2-06": (RECALL, 3, "演訓召集"),
    # ---- 2026-10-04 自彙編補回的題目
    "TF-144": (A, 50, ""), "TF-145": (B, 12, "管理幹部之甄選"), "TF-146": (B, 12, "管理幹部之甄選"),
    "TF-148": (B, 3, "社會役"), "MC-099": (A, 32, "得繼續給卹至成年"), "MC-100": (A, 7, "與常備兵役同"),
    "MC-101": (A, 55, "視情節輕重"),
    # ---- 志願服務法
    "TF-124": (VOLUNTEER, 3, "志願服務"), "MC-086": (VOLUNTEER, 4, "衛生福利部"),
    "TF-127": (VOLUNTEER, 16, ""), "TF-128": (VOLUNTEER, 16, ""),
    "TF-125": (VOLUNTEER, 20, "三百小時"), "MC-087": (VOLUNTEER, 20, "三百小時"), "MC-088": (VOLUNTEER, 20, "得以免費"),
}

FIXES = {
    "TF-002": {"question": "所謂替代役，係指役齡男子於需用機關擔任輔助性工作，履行政府公共事務或其他社會服務。"},
    "TF-117": {
        "answer": "O",
        "revised": "歷屆考古題答案為「錯」；依現行《替代役役男保險及醫療實施辦法》第12條，應自行負擔之醫療費用由主管機關負擔並預撥健保署，故改為「對」。",
    },
    "MC-013": {
        "question": "替代役役男一般保險之保險受益人，自通知保險給付之日起，逾幾年不行使即喪失其領受保險給付權利？",
        "options": ["2年", "3年", "5年", "10年"], "answer": 3,
        "revised": "原考古題答案為 5 年（修正前條文），已依現行第47條改為 10 年。",
    },
    "MC-040": {
        "question": "替代役役男結婚，依《替代役役男請假規則》得核給婚假幾日？（婚假可分次申請，但應於結婚之日起三個月內請畢）",
        "options": ["10日", "12日", "14日", "15日"], "answer": 2,
        "revised": "原考古題題幹為「應於一個月內請畢」（舊規定），已依現行第5條改為三個月。",
    },
    "TF-106": {
        "question": "依《替代役役男服役期滿後召集服勤實施辦法》，演訓召集於平時訓練或演習時實施，由內政部按年度計畫於退役後八年內實施，同一年度以一次為限，每次五日以內。",
        "answer": "O",
        "revised": "原考古題為「每次1日以內，必要時得延長為3日至5日」（舊規定），已依現行第3條改寫。",
    },
    # ---- 2026-10-04 第二輪：題幹的限制詞必須出現在所引條文裡
    "TF-018": {
        "question": "替代役訓練區分為基礎訓練及專業訓練。",
        "revised": "原題幹為「軍事基礎訓練」；現行第13條的用語是「基礎訓練」，已依條文更新。",
    },
    "TF-038": {
        "question": "替代役役男基礎訓練期間請假，由訓練單位依相關准假權責核處。",
        "revised": "原題幹為「軍事基礎訓練期間請假由訓練單位逕行核處」，已依現行第10條文字更新。",
    },
    "TF-041": {
        "question": "一般替代役役男受基礎訓練期間，因未達替代役體位應予驗退者，由主管機關辦理。",
        "revised": "原題幹為「軍事基礎訓練」；現行第3條的用語是「基礎訓練」，已依條文更新。",
    },
    "TF-072": {
        "question": "依《一般替代役役男訓練服勤管理辦法》第7條規定：需用機關辦理一般替代役役男服勤單位分發，應將基礎訓練成績列入分發成績；其所占比率不得低於分發成績計算基準之百分之四十。",
        "revised": "原題幹為「軍事基礎訓練成績」；現行第7條的用語是「基礎訓練成績」，已依條文更新。",
    },
    "TF-054": {
        "question": "罰站、罰勤、禁足、申誡及記過，由服勤、訓練單位核處；罰薪、輔導教育，由服勤單位提出，報請需用機關核定，並於一週內送請主管機關備查。",
        "revised": "原題幹漏字，讀起來變成「罰站、罰勤、禁足、申誡及記過由服勤單位提出，報請需用機關核定」，與第55條不符；已依條文補全。",
    },
    "TF-111": {
        "question": "役男育有子女或配偶懷孕，符合因家庭因素申請服替代役之情形。",
        "revised": "原題幹為「育有12歲以下子女或配偶懷孕六個月以上」（舊規定）；現行第11條已無年齡與月數限制，已依條文改寫。",
    },
    "MC-095": {
        "options": ["一等給與終身", "二等給與20年", "三等給與15年", "重度機能障礙給與20年"], "answer": 0,
        "revised": "原選項「二等殘給與10年」「三等殘給與5年」依第34條也是正確敘述，不是唯一正解；已改寫干擾選項。",
    },
    "TF-097": {
        "question": "替代役役男入營後應親自填寫替代役役男一般保險及團體保險意外保險受益人指定書。",
        "revised": "站方先前把題幹縮寫成「應親自填寫保險受益指定書」，已還原為彙編原文。",
    },
    "MC-DOC2-03": {
        "options": ["直轄市、縣（市）政府", "鄉鎮市區公所", "主管機關（內政部）", "服勤單位"], "answer": 2,
        "revised": "原選項寫「內政部（役政署）」；役政署已改制，條文用語為主管機關。",
    },
}
BASIS_OVERRIDE = {"MC-013": (A, 47, "逾十年")}

# 所引條文只支持題幹的一部分，或選項不是唯一正解：保留歷屆答案、標示「條文只支持一部分」，不列入模擬考
PARTIAL = {
    "TF-114": "第10條第5款只規定遺失識別證得予罰勤、禁足或申誡；題幹後段「如毀損尚能辨識，且據以繳交換新證者，免予懲處」不在條文內。",
    "TF-119": "第21條只規定服替代役之年資「依相關法令規定辦理」，沒有寫明於退休時併計。",
    "TF-DOC2-03": "第50條只規定國民年金保險費由主管機關編列預算支付；題幹關於《國民年金法》加保範圍的敘述，不在本站收錄的法規內。",
    "MC-071": "第20條規定向需用機關提出申訴（原懲處機關為需用機關者向主管機關提出）。選項中的「需用機關」也符合條文文字，本題選項有歧義。",
}

# 判定為核實、但信心為「中」的題目（條文用語與題幹不完全相同，或需要推論）
MEDIUM = {
    "TF-003", "TF-004", "TF-010", "TF-012", "TF-026", "TF-046", "TF-055", "TF-063", "TF-087", "TF-097", "TF-099",
    "TF-101", "TF-141", "TF-144", "TF-146", "TF-148", "MC-009", "MC-016", "MC-019", "MC-065", "MC-067", "MC-069", "MC-088", "MC-096",
}

# 條文原文之外需要補一句說明的題目
SUFFIX = {
    "TF-003": "現行條文已不再區分「社會治安類」「社會服務類」。",
    "TF-004": "現行條文沒有「文化服務役」，也不再區分「社會服務類」。",
    "TF-087": "條文沒有「長1個月」的規定，實際役期由行政院核定。",
    "MC-069": "與職務無關的活動不符合公假要件，依第7條只能請事假並擇日補勤。",
    "TF-095": "舅舅不在第6條所列親屬之內。",
    "TF-111": "現行條文為「役男育有子女或配偶懷孕」，已無子女年齡與懷孕月數的限制。",
    "TF-117": "題目中的「健保局」現為衛生福利部中央健康保險署。",
    "TF-099": "條文只就一般保險規定，團體意外保險不在本條範圍。",
    "MC-009": "條文只就一般保險規定，團體意外保險不在本條範圍。",
    "MC-067": "條文只就一般保險規定，團體意外保險不在本條範圍。",
    "TF-026": "題幹只列出部分懲處種類。",
    "TF-046": "題幹只列出部分役別。",
    "TF-010": "條文用語是「一般替代役」。",
    "TF-097": "條文只就一般保險規定，團體意外保險不在本條範圍。",
    "TF-144": "條文用語是「由主管機關編列預算支付」，主管機關為內政部。",
    "TF-145": "甄選與核定是需用機關的權責，不是服勤單位。",
    "TF-148": "照顧老人屬社會役的勤務內容。",
    "TF-141": "受理申訴機關應自收受申訴書之日起三十日內以書面答覆，必要時得延長十日（第21條）。",
    "TF-073": "例外是喪假與病假，不是婚假與陪產假。",
}

OUTDATED = {
    "TF-029": "現行《替代役實施條例》第56條已改為「得邀請民間團體代表、學者及專家」辦理審查，條文中已無「替代役審議委員會」。",
    "TF-060": "現行《替代役役男獎懲辦法》第20條規定向「需用機關」提出申訴（原懲處機關為需用機關者，向主管機關提出），與題目所稱向原懲處機關申訴不同。",
    "TF-079": "現行《替代役役男提前退役辦法》第2條所列得申請提前退役的情形，不包含低收入戶或中低收入戶。",
    "TF-093": "現行《替代役役男請假規則》第7條已無「事假累計八小時折算一日」的規定。",
    "TF-113": "現行《役男申請服替代役辦法》第11條所列家庭因素，已無「父、母或配偶患有重大傷病，或家屬二人以上患有輕度身心障礙」這一項。",
    "MC-053": "現行《替代役役男請假規則》第7條已無「事假累計八小時折算一日」的規定。",
    "MC-058": "現行《替代役役男請假規則》第7條已無「事假累計八小時折算一日」的規定。",
    "MC-012": "彙編編者已把這題的答案改註為「35%」，但四個選項（45%、40%、22.5%、42.5%）都沒有這個答案；配分由訓練單位公告，各梯次可能不同。",
    "TF-123": "現行《役男申請服替代役辦法》第11條為「役男育有子女或配偶懷孕」，已無「懷孕6個月以上」的限制；同一考點已由 TF-111 依現行條文改寫。",
}
OUTDATED_SOURCE = {
    "TF-029": (A, 56), "TF-060": (REWARD, 20), "TF-079": (EARLY, 2), "TF-093": (LEAVE, 7),
    "TF-113": (APPLY, 11), "MC-053": (LEAVE, 7), "MC-058": (LEAVE, 7), "TF-123": (APPLY, 11),
    "MC-012": (MANAGE, 7),
}

# 條文只有部分依據、或題目涉及未收錄的規定：保留歷屆答案並附上說明
NOTES = {
    "TF-142": "體能測驗的替代項目屬訓練單位規定，收錄的法規中查無明文。彙編標註 205T 考過，答案照彙編。",
    "TF-143": "年終工作獎金發放日屬行政作業規定，收錄的法規中查無明文。彙編標註 205T 考過，答案照彙編。",
    "TF-147": "《志願服務法》條文中查無「滿一年、一百五十小時」的文字，這項規定出自子法，本站未收錄。彙編標註 257T 考過，答案照彙編。",
    "TF-149": "長照政策不在收錄的法規內。彙編列為 257T 考點，答案欄空白，依彙編敘述收錄為「正確」。",
    "TF-150": "長照政策不在收錄的法規內。彙編列為 257T 考點，答案欄空白，依彙編敘述收錄為「正確」。",
    "TF-151": "長照政策不在收錄的法規內。彙編列為 257T 考點，答案欄空白，依彙編敘述收錄為「正確」。",
    "TF-152": "彙編註記「正確為 4-7 月」。演習時間每年由主管機關公告，可能變動。",
    "TF-153": "定義出自性別平等相關法規，本站未收錄。彙編答案欄空白，依彙編敘述收錄為「正確」。",
    "TF-011": "《替代役實施條例》第7條只規定常備役體位申請服一般替代役的役期「較常備兵役長六個月以內」，實際月數由行政院核定，條文沒有寫明。",
    "TF-013": "《替代役實施條例》第7條未就宗教因素另定役期，實際役期由行政院核定。",
    "TF-089": "《替代役實施條例》第7條只規定「較常備兵役長六個月以內」，實際役期由行政院核定。",
    "MC-047": "《替代役實施條例》第7條未就宗教因素另定役期，實際役期由行政院核定。",
    "MC-DOC2-05": "《替代役實施條例》第7條只規定「較常備兵役長六個月以內」，實際役期由行政院核定。",
    "TF-019": "收錄的現行法規中沒有「不具現役軍人身分」的明文，本題為歷屆答案。",
    "TF-078": "收錄的現行法規中沒有「不具現役軍人身分」的明文，本題為歷屆答案。",
    "TF-098": "《一般替代役役男訓練服勤管理辦法》第4條規定宗教因素役男由主管機關指定專列梯次徵集至需用機關實施基礎訓練及專業訓練，但條文沒有寫訓練週數。",
    "TF-126": "《志願服務法》第20條沒有規定榮譽卡的使用期限，期限與換發規定在子法，本站未收錄。",
    "TF-129": "一人一冊的規定出自《志願服務證及服務紀錄冊管理辦法》，本站未收錄該辦法全文。",
    "TF-130": "紀錄冊核發條件出自《志願服務證及服務紀錄冊管理辦法》，本站未收錄該辦法全文。",
    "TF-131": "《志願服務法》條文中沒有志工年齡上下限的規定。",
    "MC-002": "《替代役役男獎懲辦法》第19條規定記過、罰薪或輔導教育之懲處處分書應備理由；《替代役實施條例》第55條另規定申誡、記過以書面為之。本題選項有爭議，保留歷屆答案。",
    "MC-010": "內政部役政署已於民國 112 年改制，替代役訓練業務現由內政部替代役訓練及管理中心辦理。本題保留歷屆答案。",
    "MC-041": "內政部役政署已於民國 112 年改制，替代役訓練業務現由內政部替代役訓練及管理中心辦理。本題保留歷屆答案。",
    "MC-051": "內政部役政署已於民國 112 年改制，替代役訓練業務現由內政部替代役訓練及管理中心辦理。本題保留歷屆答案。",
    "TF-081": "內政部役政署已於民國 112 年改制，替代役訓練業務現由內政部替代役訓練及管理中心辦理。本題保留歷屆答案。",
    "MC-026": "中央健康保險局已改制為衛生福利部中央健康保險署。本題保留歷屆答案。",
    "MC-012": "成績配分屬訓練單位規定，各梯次可能不同，本題為歷屆答案。",
    "MC-005": "成績配分屬訓練單位規定，各梯次可能不同，本題為歷屆答案。",
    "MC-039": "成績配分屬訓練單位規定，各梯次可能不同，本題為歷屆答案。",
    "TF-094": "成績配分屬訓練單位規定，各梯次可能不同，本題為歷屆答案。",
}
UNVERIFIED_NOTE = "收錄的現行法規中查無對應條文，這題的答案來自歷屆考古題，請以當梯次教材為準。"


# 彙編（增補至 257T）裡有、但網站先前漏收的題目。題幹與選項照彙編原文，梯次標記也照彙編。
# 彙編「選擇題」區後段混有是非敘述；答案欄空白的幾則是 257T 考點紀錄，彙編把它們列為正確敘述。
def _new(qid, kind, category, question, answer, tag, options=None):
    q = {"id": qid, "type": kind, "category": category, "question": question}
    if options:
        q["options"] = options
    q.update({"answer": answer, "explanation": "", "exam_tag": tag, "source": "", "source_url": ""})
    return q


NEW_QUESTIONS = [
    _new("TF-142", "true_false", "rights", "基礎訓練體能測驗以3,000公尺徒手跑步測驗為原則，若患有痼疾無法受測3,000公尺徒手跑步者，經檢附相關醫療證明或體檢資料驗證確認後，得依役男意願自主選擇「仰臥起坐」「伏地挺身」或「單槓引體向上」其中1個測驗項目替代。", "O", "【205T考】"),
    _new("TF-143", "true_false", "rights", "一般替代役役男退役發給年終工作獎金，於退役當月15日逕入役男帳戶。", "O", "【205T考】"),
    _new("TF-144", "true_false", "rights", "替代役役男之全民健康保險、一般保險及團體意外保險統一由內政部支付。", "O", "【219T考】【227T考】"),
    _new("TF-145", "true_false", "management", "替代役管理幹部由服勤單位甄選核定。", "X", "【219T考】【227T考】【247T考】【257T考選擇】"),
    _new("TF-146", "true_false", "management", "管理幹部經需用機關在職訓練後始可擔任。", "O", "【219T考】【227T考】"),
    _new("TF-147", "true_false", "volunteer", "志工服務年資滿1年，服務時數達150小時以上者，得向志願服務運用單位申請認證服務績效及發給志願服務績效證明書。", "O", "【257T考選擇】"),
    _new("TF-148", "true_false", "regulations", "在老人中心服役為社會役。", "O", ""),
    _new("TF-149", "true_false", "rights", "目前台灣長照為長照2.0。", "O", "【257T考】"),
    _new("TF-150", "true_false", "rights", "目前長照專線為1966。", "O", "【257T考是非】"),
    _new("TF-151", "true_false", "rights", "長照服務對象為65歲以上老人、55歲以上原住民、50歲以上失智症者、失能身心障礙者。", "O", "【257T考】【257T考選擇】"),
    _new("TF-152", "true_false", "management", "民安演習時間為9-10月。", "X", ""),
    _new("TF-153", "true_false", "rights", "性霸凌：指透過語言、肢體或其他暴力，對於他人之性別特徵、性別特質、性傾向或性別認同進行貶抑、攻擊或威脅之行為。", "O", ""),
    _new("MC-099", "multiple_choice", "rights", "替代役役男發生死亡，依法給予之年撫卹金年限雖然屆滿，而子女尚未成年者，得繼續給卹至", 2, "【203T考】【205T考】",
         ["大學畢業", "研究所畢業", "成年", "高中畢業"]),
    _new("MC-100", "multiple_choice", "regulations", "常備役體位因家庭因素服替代役者役期為", 2, "【205T考】",
         ["較常備兵役長2個月", "較常備兵役長4個月", "與常備兵役同", "較常備兵役長15日"]),
    _new("MC-101", "multiple_choice", "management", "替代役役男懲處種類包含哪些？", 3, "【219T考】【227T考】",
         ["罰勤、禁足、罰站", "申誡、記過", "罰薪、輔導教育", "以上皆是"]),
]


def review_recruit():
    data = load("questions.json")
    have = {q["id"] for q in data["questions"]}
    data["questions"] += [dict(q) for q in NEW_QUESTIONS if q["id"] not in have]
    summary = {"law": 0, "partial": 0, "unverified": 0, "experience": 0, "outdated": 0}
    for q in data["questions"]:
        qid = q["id"]
        if qid in FIXES:
            q.update(FIXES[qid])
        q.pop("status", None)
        q.pop("status_note", None)
        q["reviewed_at"] = REVIEWED_AT
        q["confidence"] = "中" if qid in MEDIUM else "高"
        if qid in OUTDATED:
            pcode, no = OUTDATED_SOURCE[qid]
            q.update({
                "status": "outdated", "status_note": OUTDATED[qid] + ("本題不列入測驗。" if qid == "MC-012" else "本題依舊規定出題，不列入測驗。"),
                "explanation": "", "review": "outdated", "source_kind": "law",
                "source": "%s 第%s條" % (LAWS[pcode]["name"], no), "source_url": single_url(pcode, no),
            })
        elif qid in LAW_BASIS or qid in BASIS_OVERRIDE:
            basis(q, *BASIS_OVERRIDE.get(qid, LAW_BASIS.get(qid)))
            if qid in PARTIAL:
                q["review"] = "partial"
                q["confidence"] = "低"
                q["explanation"] += "\n" + PARTIAL[qid] + "本題保留歷屆答案，不列入模擬考。"
        elif q["category"] == "shooting":
            q["review"] = "experience"
            q["source_kind"] = "experience"
            q["confidence"] = "低"
        else:
            q["review"] = "unverified"
            q["confidence"] = "低"
            q["explanation"] = NOTES.get(qid, UNVERIFIED_NOTE)
            if qid not in NOTES or "條" not in q["source"]:
                q["source_kind"] = "past"
                q["source"] = "歷屆考古題（未能以法規查核）"
                q["source_url"] = ""
        summary[q["review"]] += 1
    active = [q for q in data["questions"] if q.get("status") != "outdated"]
    data["updatedAt"] = REVIEWED_AT
    data["stats"] = {
        "total": len(data["questions"]), "active": len(active),
        "true_false": sum(q["type"] == "true_false" for q in data["questions"]),
        "multiple_choice": sum(q["type"] == "multiple_choice" for q in data["questions"]),
        "with_explanation": sum(bool(q.get("explanation")) for q in data["questions"]),
        "review": summary,
    }
    save("questions.json", data)
    return data, summary


# ---------------------------------------------------------------- EMT-1
EMT_FIXES = {
    "EMT-LAW-01": {
        "question": "依現行《救護技術員管理辦法》（民國 114 年 1 月 1 日施行）附表一，初級救護技術員（EMT-1）訓練課程的總時數為幾小時？",
        "options": ["(A) 24 小時", "(B) 40 小時", "(C) 56 小時", "(D) 80 小時"], "answer": 2,
        "explanation": "《救護技術員管理辦法》第3條：各級救護技術員之訓練課程模組別、科目別、內容及時數如附表一至附表三。附表一「初級救護技術員訓練課程基準」共七個模組，總時數 56 小時。修正前為 40 小時，舊教材與歷屆考古題多以 40 小時作答。",
        "basis": (EMT, 3), "revised": "原考古題答案為 40 小時（修正前規定），已依現行附表一改為 56 小時。",
    },
    "EMT-LAW-02": {
        "explanation": "《救護技術員管理辦法》第9條：各級救護技術員證書有效期間為三年。",
        "basis": (EMT, 9),
    },
    "EMT-LAW-03": {
        "question": "依現行《救護技術員管理辦法》，初級救護技術員（EMT-1）於證書效期三年內應完成多少繼續教育課程，才得申請展延？",
        "options": [
            "(A) 16 小時以上，其中 8 小時以上為指定模組之科目",
            "(B) 24 小時以上，其中 12 小時以上為模組二、四及六之科目",
            "(C) 32 小時以上，其中 16 小時以上為指定模組之科目",
            "(D) 40 小時以上，不限科目",
        ], "answer": 1,
        "explanation": "《救護技術員管理辦法》第10條：初級救護技術員完成附表一所列科目達二十四小時以上，且其中十二小時以上為模組二、四及六之科目，得申請證書效期之展延；展延之有效期間每次為三年。",
        "basis": (EMT, 10), "revised": "原考古題為「每年至少 8 小時」（修正前規定），已依現行第10條改寫。",
    },
    "EMT-LAW-04": {
        "question": "依《救護技術員管理辦法》第13條規定，下列何者「屬於」初級救護技術員（EMT-1）得施行之救護項目？",
        "explanation": "《救護技術員管理辦法》第13條列出初級救護技術員得施行的 20 項救護項目，第14款為「使用自動體外心臟電擊去顫器」。周邊輸液與注射用輸液屬中級項目（第14條）；依預立醫療流程給藥、氣管插管屬高級項目（第15條）。",
        "basis": (EMT, 13), "revised": "原題引用第3條（修正前條號），已改為現行第13條。",
    },
    "EMT-LAW-05": {
        "question": "救護人員施行救護所填具的「救護紀錄表」，依《緊急醫療救護法》第34條規定，應由救護車設置機關（構）及應診之醫療機構保存至少多久？",
        "explanation": "《緊急醫療救護法》第34條：救護人員施行救護，應填具救護紀錄表，分別交由該救護車設置機關（構）及應診之醫療機構保存至少七年。",
        "basis": (EMS, 34), "revised": "原題引用第23條，實際條文在第34條。",
    },
    "EMT-LAW-06": {
        "question": "依《緊急醫療救護法》第14-2條，救護人員以外之人為免除他人生命之急迫危險，使用緊急救護設備或施予急救措施者，法律上如何處理其責任？",
        "explanation": "《緊急醫療救護法》第14-2條：救護人員以外之人，為免除他人生命之急迫危險，使用緊急救護設備或施予急救措施者，適用民法、刑法緊急避難免責之規定。救護人員於非值勤期間，前項規定亦適用之。",
        "basis": (EMS, "14-2"),
    },
    "EMT-LAW-07": {
        "question": "救護技術員因業務而知悉或持有他人之秘密，無故洩漏者，依《緊急醫療救護法》第35條及第45條之罰則為何？",
        "answer": 1,
        "explanation": "《緊急醫療救護法》第35條：救護技術員及其他參與緊急醫療救護業務之機關（構）所屬人員，因業務而知悉或持有他人之秘密，不得無故洩漏。違反者依第45條第3款處新臺幣一萬元以上五萬元以下罰鍰。",
        "basis": (EMS, 35), "revised": "原考古題答案為二萬元以上十萬元以下，且引用第37、44條；依現行第35、45條應為一萬元以上五萬元以下。",
    },
    "EMT-LAW-08": {
        "question": "依《緊急醫療救護法》第29條，救護人員應將緊急傷病患送達何處？",
        "explanation": "《緊急醫療救護法》第29條：救護人員應依救災救護指揮中心指示前往現場急救，並將緊急傷病患送達就近適當醫療機構。",
        "basis": (EMS, 29),
    },
    "EMT-LAW-09": {
        "question": "依《緊急醫療救護法》第18條規定，救護車於救護傷病患及運送病人時，出勤人員的最低要求為何？",
        "options": [
            "(A) 一名救護技術員獨自出勤即可",
            "(B) 應有救護人員二名以上出勤",
            "(C) 至少三名高級救護技術員",
            "(D) 必須有一名急診專科醫師隨車",
        ], "answer": 1,
        "explanation": "《緊急醫療救護法》第18條：救護車於救護傷病患及運送病人時，應有救護人員二名以上出勤；加護救護車出勤之救護人員，至少應有一名為醫師、護理人員或中級以上救護技術員。",
        "basis": (EMS, 18), "revised": "原題引用第17條，且選項含「一名救護人員搭配一名駕駛」，現行第18條並無此規定。",
    },
    "EMT-LAW-12": {
        "question": "依現行《救護技術員管理辦法》，「協助使用吸入型支氣管擴張劑、自備腎上腺素注射筆或硝化甘油舌下含片」最低須為哪一級救護技術員才得施行？",
        "options": ["(A) 初級救護技術員", "(B) 中級救護技術員", "(C) 高級救護技術員", "(D) 各級救護技術員均不得施行"],
        "answer": 1,
        "explanation": "《救護技術員管理辦法》第14條第5款把「協助使用吸入型支氣管擴張劑、自備腎上腺素注射筆或硝化甘油舌下含片」列為中級救護技術員得施行之項目；第13條所列初級救護技術員的 20 項救護項目不包含這一項。",
        "basis": (EMT, 14), "revised": "原考古題認為 EMT-1 可協助病患服用自備藥物；依現行第13、14條，此項屬中級救護技術員之救護項目。",
    },
    "EMT-MCI-10": {
        "question": "依《緊急醫療救護法》第32條，直轄市、縣（市）政府遇大量傷病患或野外緊急救護時，應依災害規模及種類建立什麼，以施行救護有關工作？",
        "options": ["(A) 臨時福利社", "(B) 現場指揮協調系統", "(C) 臨時法庭", "(D) 民宿接待處"], "answer": 1,
        "explanation": "《緊急醫療救護法》第32條：直轄市、縣（市）政府遇大量傷病患或野外緊急救護，應依災害規模及種類，建立現場指揮協調系統，施行救護有關工作。第33條並規定參與現場急救的救護人員及救護運輸工具設置機關（構），均應依現場指揮協調系統之指揮施行救護。",
        "basis": (EMS, 32), "revised": "原題引用第26至28條，實際條文在第32、33條。",
    },
    "EMT-LAW-11": {
        "explanation": "《道路交通安全規則》第93條第2項：消防車、救護車、警備車、工程救險車及毒性化學物質災害事故應變車執行任務時，得不受前項行車速度之限制，且於開啟警示燈及警鳴器執行緊急任務時，得不受標誌、標線及號誌指示之限制。\n條文只免除速限與標誌、標線、號誌的限制，沒有免除肇事責任的規定，所以「完全免除刑事與民事責任」的敘述沒有依據。選項 (D) 所說的注意義務不在這一條的文字裡，本題保留歷屆答案，不列入模擬考。",
        "basis": (TRAFFIC, 93), "partial": True,
        "revised": "原解析引用「法院判例」但沒有可查的出處，已刪除，改為只引用第93條條文。",
    },
}

# 教材題中，作法與較新的急救指引不完全一致的題目：保留教材答案並加註
EMT_CAUTION = {
    "EMT-CPR-11": "各指引對清醒成人嚴重哽塞的第一步作法不同：歐洲復甦委員會（ERC）建議先拍背 5 下，無效再做腹部推擠。考試以訓練單位教材為準。",
    "EMT-AIR-15": "2020 年版美國心臟協會（AHA）指引對有脈搏、呼吸不足的成人，建議每 6 秒給一口氣（每分鐘約 10 次）。考試以訓練單位教材為準。",
    "EMT-MED-08": "抬高下肢對休克的效果證據有限，部分急救指引只建議讓傷患平躺。考試以訓練單位教材為準。",
}


def recalled_questions():
    """把 scripts/emt_recalled.py 的考點題轉成題庫格式。"""
    import emt_recalled as src
    out = []
    for qid, item, category, stem, options, answer, options_by, note, law, retired in src.RECALLED:
        round_label = "270T" if qid.startswith("EMT-270") else "梯次不明（講師提供的舊考古題）"
        q = {
            "id": qid, "type": "multiple_choice", "category": category, "category_name": src.CATEGORY_NAME[category],
            "question": stem, "options": options, "answer": answer, "exam_tag": "【270T考】" if qid.startswith("EMT-270") else "",
            "reviewed_at": REVIEWED_AT,
            "provenance": {
                "class": "recalled", "label": "考生回憶的考點", "source_id": src.SOURCE_ID, "source_item": item,
                "round": round_label, "options_by": options_by,
            },
        }
        tail = "選項是站方依考點自編的。" if options_by == "site" else "選項依回憶者所記。"
        if law:
            pcode, no, keyword = law
            basis(q, pcode, no, keyword)
            q["explanation"] += (chr(10) + note if note else "")
            q["confidence"] = "高"
        else:
            q.update({
                "review": "recalled", "source_kind": "recalled", "confidence": "中",
                "source": ("270T 作者當梯回憶" if qid.startswith("EMT-270") else "Dcard 文章舊考點（梯次不明）") + "，%s" % item, "source_url": src.SOURCE_URL,
                "explanation": (note + chr(10) if note else "") + "答案照回憶者所記，沒有逐題對照現行教材原文。" + tail,
            })
        if retired:
            q.update({"status": "outdated", "status_note": retired + "本題不列入測驗。", "review": "outdated", "confidence": "低"})
        if qid == "EMT-P1-25":
            q.update({"review": "recalled_conflict", "confidence": "低", "caution": "來源回憶與 114 年消防署教材第 125 頁的脈搏條件矛盾；本站題幹改為有脈搏，不列入模擬考。"})
        out.append(q)
    return out


def review_emt():
    data = load("emt_questions.json")
    recalled = recalled_questions()
    # 自編 96 題另存於 data/emt_practice_questions.json，使用者須明確選擇才進入練習。
    data["questions"] = recalled
    summary = {"law": 0, "partial": 0, "textbook": 0, "recalled": 0, "recalled_conflict": 0, "outdated": 0}
    for q in data["questions"]:
        if q.get("provenance", {}).get("class") == "recalled":
            summary[q["review"]] += 1
            continue
        q["reviewed_at"] = REVIEWED_AT
        q["confidence"] = "高"
        q.pop("caution", None)
        fix = EMT_FIXES.get(q["id"])
        if fix:
            fix = dict(fix)
            pcode, no = fix.pop("basis")
            partial = fix.pop("partial", False)
            q.update(fix)
            q["source"] = "%s 第%s條" % (LAWS[pcode]["name"], no)
            q["source_url"] = single_url(pcode, no)
            q["source_kind"] = "law"
            q["review"] = "partial" if partial else "law"
            if partial:
                q["confidence"] = "低"
        else:
            q["confidence"] = "中"
            if q["id"] in EMT_CAUTION:
                q["caution"] = EMT_CAUTION[q["id"]]
                q["confidence"] = "低"
            q["review"] = "textbook"
            q["source_kind"] = "law" if "law.moj.gov.tw" in q["source_url"] else "textbook"
            q["source"] = q["source"].replace("全國法規資料庫 - ", "")
        summary[q["review"]] += 1
    data["updatedAt"] = REVIEWED_AT
    data["subtitle"] = "依 270T 考生回憶的考點重寫；不是逐字原題"
    data["stats"]["review"] = summary
    data["stats"]["total"] = data["total"] = len(data["questions"])
    data["stats"].pop("multiple_choice_count", None)
    data["stats"].pop("categories", None)
    save("emt_questions.json", data)
    return data, summary


EMT_ARTICLES = [
    (EMS, "14-1", "公共場所設置 AED", "中央衛生主管機關公告的公共場所，應置有自動體外心臟電擊去顫器或其他必要之緊急救護設備。"),
    (EMS, "14-2", "急救免責", "救護人員以外之人為免除他人生命之急迫危險而施救，適用民法、刑法緊急避難免責之規定；救護人員於非值勤期間也適用。"),
    (EMS, "18", "救護車出勤人數", "救護傷病患及運送病人時，應有救護人員二名以上出勤。"),
    (EMS, "24", "救護技術員分級", "救護技術員分為初級、中級及高級三類，訓練、繼續教育與得施行之救護項目另以辦法定之。"),
    (EMS, "26", "施行緊急救護的地點", "限於現場、送醫或轉診途中，以及抵達醫療機構而醫護人員尚未處置前。"),
    (EMS, "27", "依救護作業程序施行救護", "救護技術員應依緊急傷病患救護作業程序施行救護；作業程序由直轄市、縣（市）衛生主管機關定之。"),
    (EMS, "29", "送醫原則", "依救災救護指揮中心指示前往現場急救，並將緊急傷病患送達就近適當醫療機構。"),
    (EMS, "32", "大量傷病患的現場指揮", "直轄市、縣（市）政府應依災害規模及種類，建立現場指揮協調系統。"),
    (EMS, "34", "救護紀錄表", "救護紀錄表由救護車設置機關（構）及應診之醫療機構保存至少七年。"),
    (EMS, "35", "保密義務", "因業務知悉或持有他人之秘密，不得無故洩漏；違反者依第45條處新臺幣一萬元以上五萬元以下罰鍰。"),
    (EMT, "3", "訓練課程與時數", "附表一「初級救護技術員訓練課程基準」總時數 56 小時（修正前為 40 小時）。附表內容請看全國法規資料庫。"),
    (EMT, "9", "證書效期", "各級救護技術員證書有效期間為三年。"),
    (EMT, "10", "繼續教育與展延", "初級：三年內完成 24 小時以上，其中 12 小時以上為模組二、四及六之科目；展延每次三年。"),
    (EMT, "13", "初級救護技術員得施行之救護項目", "共 20 項，包含基本心肺復甦術、給予氧氣、使用自動體外心臟電擊去顫器、血糖監測及給予口服葡萄糖等。"),
    (EMT, "14", "中級救護技術員得施行之救護項目", "周邊輸液、聲門上呼吸道、協助使用自備硝化甘油舌下含片等屬中級項目，初級不得施行。"),
    (EMT, "16", "佩帶證書", "救護技術員施行救護時，應佩帶救護技術員證書。"),
]


def review_emt_study():
    study = load("emt_study_data.json")
    study["description"] = "依《緊急醫療救護法》、《救護技術員管理辦法》與消防署初級救護技術員教材整理的重點。醫學內容以訓練單位教材與教官教學為準。"
    study["statutory_articles"] = [{
        "law": LAWS[pcode]["name"], "article": "第 %s 條" % no, "title": title,
        "official_text": "\n".join(text for _, text in article(pcode, no)["lines"]),
        "key_point": point, "url": single_url(pcode, no),
    } for pcode, no, title, point in EMT_ARTICLES]
    study.pop("laws_summary", None)
    study.pop("law_meta", None)
    for res in study["resources"]:
        res.pop("badge", None)
        if "消防署" in res["name"] and "教材" in res["name"]:
            res["desc"] = "內政部消防署編印的初級救護技術員教材電子書（108 年版），依修正前的 40 小時課程編寫，內容包含生命徵象、呼吸道處置、CPR 與 AED、創傷與急症處理。"
        elif "緊急醫療救護法" in res["name"]:
            res["desc"] = "緊急醫療救護的母法。常見考點：急救免責（第14-2條）、救護車出勤人數（第18條）、救護紀錄表保存七年（第34條）、保密義務（第35條）。"
        elif "救護技術員管理辦法" in res["name"]:
            res["desc"] = "規定救護技術員的訓練、證書效期與得施行的救護項目。現行條文自民國 114 年 1 月 1 日施行，初級訓練課程 56 小時，證書效期三年。"
    study["reviewed_at"] = REVIEWED_AT
    save("emt_study_data.json", study)


# ---------------------------------------------------------------- 新訓講義
def review_study():
    study = load("study_data.json")
    reg = study["regulations"]
    reg.pop("law_meta", None)
    for section in reg["sections"]:
        if section["title"].startswith("二、"):
            section["title"] = "二、役期對照（歷屆整理，實際以行政院核定與徵集令為準）"
        elif section["title"].startswith("三、"):
            section["title"] = "三、常考的數字與期限"
            for row in section["table"]["rows"]:
                if row[0] == "驗退期限":
                    row[2] = "歷屆考古題答案；收錄的現行法規中查無 30 天的明文"
                elif row[0] == "罰勤上限":
                    row[2] = "《替代役實施條例》第55條：罰勤，平日以二小時為限，例假日以八小時為限"
                elif row[0] == "申訴期限與答覆":
                    row[2] = "《替代役役男獎懲辦法》第20、21條：懲處處分書送達之次日起30日內向需用機關提出；受理機關應於30日內以書面答覆，必要時得延長10日"
                elif row[0] == "撫卹金請求權時效":
                    row[2] = "《替代役實施條例》第38條：自請卹或請領事由發生之次月起，經過十年不行使而消滅"
                elif row[0] == "一般保險給付時效":
                    row[2] = "《替代役實施條例》第47條：自通知保險給付之日起，逾十年不行使即喪失領受權利"
                elif row[0] == "輔導教育最長期限":
                    row[2] = "《替代役役男輔導教育辦法》第4、8條：最長八星期，得延長一次並不得逾八星期；期間一律停止放假及請假，但喪假、病假不在此限"
        elif section["title"].startswith("四、"):
            section["title"] = "四、替代役役男請假規則（民國 111 年 5 月 30 日修正）"
            section["table"] = {
                "headers": ["假別", "天數", "規定（條號）"],
                "rows": [
                    ["公假", "依實際需要", "參加政府召集之集會或考試、依法主辦之投票、與職務有關之會議或活動、基於法定義務出席作證答辯、奉派參加訓練等，經提出證件者（第2條）"],
                    ["病假", "一次不得超過 30 日", "因疾病必須治療或休養，經檢具醫療機構診斷證明書者（第3條）"],
                    ["陪產檢及陪產假", "7 日，得分次申請", "陪產檢於配偶妊娠期間請假；陪產應於配偶分娩之當日及其前後合計 15 日期間內為之（第4條）"],
                    ["婚假", "14 日，可分次申請", "應於結婚之日起 3 個月內請畢（第5條）"],
                    ["喪假（父母、養父母、配偶）", "15 日", "可分次申請，應於死亡之日起百日內請畢（第6條）"],
                    ["喪假（繼父母、配偶之父母、配偶之養父母、子女）", "10 日", "同上（第6條）"],
                    ["喪假（曾祖父母、祖父母、配偶之祖父母、配偶之繼父母、兄弟姊妹）", "5 日", "同上（第6條）"],
                    ["事假", "視需要時數核給", "因特殊事故必須本人親自處理者，並應擇日施以補勤（第7條）"],
                ],
            }
        elif section["title"].startswith("五、"):
            section["title"] = "五、因家庭因素申請服替代役的情形（役男申請服替代役辦法第11條）"
    reg["key_points_full"]["title"] = "歷屆役男重點筆記（未逐條核對，可能含舊法內容）"

    vol = study["volunteer"]
    vol["sections"][0]["content"][1] = "**中央主管機關**：**衛生福利部**；在直轄市為直轄市政府，在縣（市）為縣（市）政府（志願服務法第4條）。"
    vol["sections"][0]["content"][3] = "**志工基礎教育訓練**：歷屆整理為 **6 小時**。時數由主管機關另行規定，不在《志願服務法》條文中。"
    for item in vol["sections"][1]["items"]:
        if "榮譽卡" in item["title"]:
            item["desc"] = "志工服務年資滿 **3 年**，服務時數達 **300 小時** 以上者，得向地方主管機關申請核發。憑卡進入收費之公立風景區、未編定座次之康樂場所及文教設施得以**免費**（志願服務法第20條）。使用期限與換發規定在子法，本站未收錄。"
        elif "紀錄冊" in item["title"]:
            item["desc"] = "志願服務運用單位對其志工應發給志願服務證及服務紀錄冊（志願服務法第12條）。歷屆考點「一人一本、完成基礎與特殊訓練後核發」出自《志願服務證及服務紀錄冊管理辦法》，本站未收錄該辦法全文。"
        elif "投保" in item["title"]:
            item["desc"] = "志願服務運用單位**應**為志工辦理意外事故保險，必要時並得補助交通、誤餐及特殊保險等經費（志願服務法第16條）。"
        elif "年齡" in item["title"]:
            item["desc"] = "《志願服務法》條文沒有志工年齡的上下限。志工從事的是輔助性服務。"
        item["badge"] = item.get("badge", "").replace("必考", "常考")

    rights = study["rights_and_management"]
    rights["rights"] = [
        "**就醫費用**：傷病赴健保醫事服務機構就醫，依健保法規應自行負擔之醫療費用由主管機關負擔；掛號費在國軍醫療院所由主管機關負擔，在其他醫事服務機構僅因公傷病由主管機關負擔（保險及醫療實施辦法第11-1、12條）。",
        "**保留學籍與底缺年資**：經保留學籍者應於退役後一年內申請復學；經保留職工底缺年資者應於退役後三個月內申請復職（權利實施辦法第4、6條）。",
        "**年資**：服役期滿後轉任公職時，服替代役之年資依相關法令規定辦理（條例第21條）。",
        "**減費優待**：乘坐公營交通運輸工具或進入公營歌劇影院等公共娛樂場所，得予減費優待（條例第20條）。",
        "**申訴**：對記過、罰薪或輔導教育之懲處不服，得於懲處處分書送達之次日起 30 日內，以書面或言詞向需用機關提出申訴；原懲處機關為需用機關者，向主管機關提出（獎懲辦法第20條）。",
    ]
    rights["punishments"] = [
        "**罰站**：每次以 2 小時為限，實施 50 分鐘、休息 10 分鐘；僅限訓練及輔導教育期間實施。",
        "**罰勤**：平日以 2 小時為限，例假日以 8 小時為限。",
        "**禁足**：於例假日實施，每次以 2 日為限。",
        "**申誡、記過**：以書面為之。累計申誡三次以記過一次論；累計記過三次得予罰薪，並得施以輔導教育。",
        "**罰薪**：扣除薪給 10% 至 30%，以 3 個月為限。",
        "**輔導教育**：最長八星期，期滿未考核合格者得延長一次，並不得逾八星期（輔導教育辦法第4條）。",
        "以上除輔導教育期限外，均出自《替代役實施條例》第55條。",
    ]
    rights["rights_points_full"]["title"] = "役男權益重點筆記（未逐條核對，可能含舊法內容）"
    rights["management_points_full"]["title"] = "訓練與服勤管理重點筆記（未逐條核對，可能含舊法內容）"
    study["footnotes"]["title"] = "歷屆考題註解（役男筆記，可能含舊法內容）"
    study["reviewed_at"] = REVIEWED_AT
    save("study_data.json", study)


# ---------------------------------------------------------------- 查核紀錄與逐題審核表
REVIEWER = "Claude（AI）；尚無人工複核"
STATUS = {
    "recalled": "考生回憶的答案（未對照現行教材原文）",
    "recalled_conflict": "回憶題幹與 114 年教材條件矛盾（不列入模擬考）",
    "law": "核實", "partial": "待補證（條文只支持一部分）", "unverified": "待補證（查無條文）",
    "experience": "待補證（經驗題）", "outdated": "舊法停用", "textbook": "待補證（教材題，未對照現行教材原文）",
}
METHOD = {
    "recalled": "題幹由站方依考生回憶的考點重寫；答案照回憶者所記，另以急救常識檢查有無明顯矛盾",
    "recalled_conflict": "核對消防署 114 年教材第 125 頁；回憶題幹的脈搏條件與教材表格不符，先排除模擬考",
    "law": "題幹、選項與所引條文逐字比對，列出不見於條文的片段後逐題裁定",
    "partial": "題幹、選項與所引條文逐字比對；條文只支持一部分",
    "unverified": "在收錄的 20 部法規中檢索，查無對應條文",
    "experience": "出自役男筆記，無官方來源可對照",
    "outdated": "與現行條文比對，確認現行法規已無對應規定",
    "textbook": "檢查題目、答案與解析是否一致；未取得現行教材原文，未逐題對照",
}
SUPPORT = {
    "recalled": "未對照教材原文",
    "recalled_conflict": "回憶條件與教材矛盾",
    "law": "是", "partial": "部分", "unverified": "無條文可對照", "experience": "無條文可對照",
    "outdated": "否（舊法）", "textbook": "未對照教材原文",
}
AMBIGUOUS = {"MC-071", "MC-002"}


def original_answers():
    """改版前（提交 84f23d3）的題目與答案，用來記錄每一題是否被更動。"""
    import subprocess
    out = {}
    for name in ("questions.json", "emt_questions.json"):
        raw = subprocess.run(["git", "-C", ROOT, "show", "84f23d3:data/" + name], capture_output=True).stdout
        for q in json.loads(raw.decode("utf-8"))["questions"]:
            out[q["id"]] = q
    return out


def answer_text(q):
    return q["answer"] if q["type"] == "true_false" else q["options"][q["answer"]]


def law_date(q):
    m = re.search(r"pcode=([A-Z]\d+)", q.get("source_url", ""))
    if m and m.group(1) in LAWS:
        law = LAWS[m.group(1)]
        return "%s %s" % (law["date_label"], law["date"])
    return "108 年版教材" if "ebook.nfa.gov.tw" in q.get("source_url", "") else ""


def write_csv(recruit, emt):
    import csv
    before = original_answers()
    # 模擬考題池：新訓＝彙編收錄且已對照現行條文；EMT＝考生回憶的考點題（含其中的法規題）
    def in_exam(bank, q):
        cls = q.get("provenance", {}).get("class", "")
        if q.get("status") == "outdated":
            return False
        if bank == "recruit":
            return cls.startswith("compiled") and q["review"] == "law"
        return cls == "recalled" and q.get("review") != "recalled_conflict"
    rows = []
    practice = load("emt_practice_questions.json")
    for bank, data in (("recruit", recruit), ("emt", emt), ("emt-practice", practice)):
        for q in data["questions"]:
            old = before.get(q["id"])
            old_answer = answer_text(old) if old else ""
            changed = bool(old) and (old_answer != answer_text(q) or old["question"] != q["question"]
                                     or old.get("options") != q.get("options"))
            review = q["review"]
            if q["id"] in AMBIGUOUS:
                status, unique = "有歧義", "否（有歧義）"
            else:
                status = STATUS[review]
                unique = "是" if review == "law" else "未裁定" if review != "outdated" else "不適用"
            rows.append({
                "題號": q["id"], "題庫": "新訓" if bank == "recruit" else "EMT-1 自編練習" if bank == "emt-practice" else "EMT-1 回憶考點",
                "題型": "是非" if q["type"] == "true_false" else "選擇", "分類": q["category"],
                "出題梯次": q.get("exam_tag", ""), "題幹": q["question"],
                "選項": " ／ ".join(q.get("options", [])),
                "舊版網站答案（不是歷史考卷答案）": old_answer, "核定答案": answer_text(q),
                "題目或答案是否更動": "是" if changed else "否",
                "來源": q["source"], "來源連結": q.get("source_url", ""), "來源日期": law_date(q),
                "所引來源是否支持題幹的關鍵限制詞": SUPPORT[review], "是否唯一正解": unique,
                "處理狀態": status,
                "來源等級": q.get("provenance", {}).get("label", ""),
                "列入模擬考": "是" if in_exam(bank, q) else "否",
                "信心": q.get("confidence", ""), "解析": q.get("explanation", "") or q.get("status_note", ""),
                "改動原因或備註": " ".join(x for x in (q.get("revised", ""), q.get("caution", "")) if x),
                "審核者": REVIEWER, "審核日期": q["reviewed_at"], "審核方式": METHOD[review],
            })
    path = os.path.join(ROOT, "docs", "逐題審核_%s.csv" % REVIEWED_AT)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return rows


def write_report(recruit, emt, r_sum, e_sum, rows):
    laws = load("laws.json")
    articles = sum(l["article_count"] for l in laws["laws"])
    files = [(l, a) for l in laws["laws"] for a in l.get("attachments", [])]
    out = ["# 資料查核紀錄", "", "最後更新：%s" % REVIEWED_AT, "",
           "本檔由 `scripts/apply_review_2026_10.py` 產生。逐題明細在 `docs/逐題審核_%s.csv`（%d 列，每題一列）。" % (REVIEWED_AT, len(rows)), "",
           "審核者是 AI，目前沒有人工複核。「核實」的意思是：題幹與選項已和所引的現行條文逐字比對，條文支持題幹的每個限制詞，而且只有一個正解。", "",
           "## 一、法規版本（%d 部、%d 條、附件 %d 件）" % (len(laws["laws"]), articles, len(files)), "",
           "條文於 %s 取自全國法規資料庫。`python scripts/fetch_laws.py --check` 會重新下載並逐條比對，列出差異與受影響題號。" % laws["fetched_at"], "",
           "| 法規 | 代碼 | 官方頁面標示 | 條數 | 附件 |", "| --- | --- | --- | --- | --- |"]
    for law in laws["laws"]:
        out.append("| [%s](%s) | %s | %s %s | %d | %d |" % (
            law["name"], law["url"], law["pcode"], law["date_label"], law["date"], law["article_count"], len(law.get("attachments", []))))
    out += ["", "### 附件清單", "",
            "附件由官方以檔案提供。站內顯示的是從 PDF 擷取的文字，表格與圖片的排版以官方原件為準；沒有文字的附件只提供官方連結。", "",
            "| 法規 | 附件 | 格式 | 取得 | 頁數 | 站內文字 |", "| --- | --- | --- | --- | --- | --- |"]
    for law, a in files:
        out.append("| %s | [%s](%s) | %s | %s | %s | %s |" % (
            law["name"], a["name"], a["url"], a["format"], "成功" if a["fetched"] else "失敗",
            a.get("pages", "") or "", "有" if a.get("text") else "無（看官方原件）"))
    out += ["", "## 二、新訓題庫（%d 題）" % len(recruit["questions"]), "",
            "| 處理狀態 | 題數 | 列入模擬考 | 說明 |", "| --- | --- | --- | --- |",
            "| 核實 | %d | 是 | 來源為對應條文，解析為條文原文 |" % r_sum["law"],
            "| 待補證（條文只支持一部分）或有歧義 | %d | 否 | 所引條文不支持題幹全部內容，或選項不是唯一正解 |" % r_sum["partial"],
            "| 待補證（查無條文） | %d | 否 | 營區規定、行政作業、成績配分等，收錄的法規中查無明文；保留歷屆答案 |" % r_sum["unverified"],
            "| 待補證（經驗題） | %d | 否 | 射擊類，出自役男筆記 |" % r_sum["experience"],
            "| 舊法停用 | %d | 否 | 現行法規已無對應規定，保留題號與原因供追溯 |" % r_sum["outdated"], "",
            "### 改寫或更正答案的題目", "", "| 題號 | 處理 |", "| --- | --- |"]
    out += ["| %s | %s |" % (q["id"], q["revised"]) for q in recruit["questions"] if q.get("revised")]
    out += ["", "### 舊法題", "", "| 題號 | 原因 |", "| --- | --- |"]
    out += ["| %s | %s |" % (q["id"], q["status_note"]) for q in recruit["questions"] if q.get("status") == "outdated"]
    out += ["", "### 條文只支持一部分或有歧義", "", "| 題號 | 說明 |", "| --- | --- |"]
    out += ["| %s | %s |" % (qid, text) for qid, text in PARTIAL.items()]
    out += ["| MC-002 | %s |" % NOTES["MC-002"]]
    out += ["", "## 三、EMT-1 題庫（%d 題）" % len(emt["questions"]), "",
            "- 法規題 %d 題已對照現行《緊急醫療救護法》與《救護技術員管理辦法》（含附表一）；另有 %d 題條文只支持一部分。" % (e_sum["law"], e_sum["partial"]),
            "- 回憶考點中 %d 題答案仍未逐題對照消防署 114 年教材；另有 %d 題回憶條件與教材矛盾，已排除模擬考。這些內容不適合作為現場醫療決策的依據。" % (e_sum["recalled"], e_sum["recalled_conflict"]),
            "- 96 題 AI 自編概念練習另存資料與 PDF，預設不出題，且永不納入模擬考；尚未逐題核對 114 年教材。", "",
            "### 更正的題目", "", "| 題號 | 處理 |", "| --- | --- |"]
    out += ["| %s | %s |" % (q["id"], q["revised"]) for q in emt["questions"] if q.get("revised")]
    out += ["", "### 與較新急救指引不完全一致、已加註的教材題", "", "| 題號 | 加註 |", "| --- | --- |"]
    out += ["| %s | %s |" % (qid, text) for qid, text in EMT_CAUTION.items()]
    out += ["", "## 四、尚未查核的內容", "",
            "- 新訓 %d 題待補證題、%d 題射擊經驗題：需要當梯次教材或主管機關文件才能核定。" % (r_sum["unverified"] + r_sum["partial"], r_sum["experience"]),
            "- EMT-1 %d 題回憶考點和 96 題自編概念練習：需要現行教材原文逐題對照。" % e_sum["recalled"],
            "- 役期月數、薪給金額、成績配分：由行政院或訓練單位核定，不在收錄的法規條文中，頁面已標示為歷屆整理。",
            "- 「歷屆役男重點筆記」「歷屆考題註解」約 200 則筆記沒有逐條核對，頁面標題已註明可能含舊法內容。",
            "- 用品清單為 2024 年梯次役男分享，非官方清單。", ""]
    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "資料查核紀錄.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))


if __name__ == "__main__":
    recruit, r_sum = review_recruit()
    emt, e_sum = review_emt()
    review_emt_study()
    review_study()
    rows = write_csv(recruit, emt)
    write_report(recruit, emt, r_sum, e_sum, rows)
    print("新訓：", r_sum)
    print("EMT：", e_sum)
    print("逐題審核表：%d 列" % len(rows))
