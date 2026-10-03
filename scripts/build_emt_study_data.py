# -*- coding: utf-8 -*-
"""
Build EMT-1 Study Data JSON for SMS (Success Mountain)
Contains 12 learning resources, law_meta, statutory_articles (aligned with Recruit Regulations),
laws_summary cards, formula sheets, clinical guides, and triage tables.
"""
import json
import os

study_data = {
    "title": "成功嶺替代役 EMT-1 初級救護技術員 考照必通關指南與法規講義全集",
    "version": "114-115年最新教材對照版 (法規全面對齊內政部與衛福部最新公布)",
    "updated_at": "2026-10",
    "description": "完整涵蓋緊急醫療救護法、救護技術員管理辦法、40小時訓練標準教材、Dcard 歷屆學長神手冊與阿摩考古題重點整理。",
    
    # 最新法規修正依據與主管機關體系 (對齊新訓法規規格)
    "law_meta": [
        {
            "title": "《緊急醫療救護法》",
            "badge": "112.06.28最新修正公布",
            "text": "緊急醫療救護母法：增訂第14-2條救護免責（善良撒瑪利亞人條款）；第23條救護紀錄表法定保存7年；第37、44條無故洩漏病患秘密處新臺幣2萬以上10萬元以下罰鍰。"
        },
        {
            "title": "《救護技術員管理辦法》",
            "badge": "112.05.08衛福部最新修正",
            "text": "主管技術員資格規範：第2條明定初級救護技術員（EMT-1）訓練時數至少40小時；第7條合格證書效期3年，展延須完成24小時繼續教育（每年至少8小時）；第3條明定EMT-1得施行之12項救護項目，嚴禁侵入性醫療。"
        },
        {
            "title": "《緊急救護辦法》",
            "badge": "104.07.27修正發布",
            "text": "消防機關執行緊急救護規範：規範救護車出勤以二人以上為原則；依病患病情及意願就近適當送醫；跨轄區送醫協定作業原則。"
        },
        {
            "title": "主管機關組織架構",
            "badge": "衛福部與消防署分工",
            "text": "法規主管機關為「衛生福利部（醫事司）」；緊急救護執行、派遣與訓練標準教材主管機關為「內政部消防署」；役男新訓督導機關為「內政部替代役訓練及管理中心」。"
        }
    ],

    # 十大學習資源清單 (包含點擊直連、說明與格式)
    "resources": [
        {
            "id": "res-1",
            "name": "內政部消防署《初級救護技術員訓練教材》電子書",
            "category": "官方教材",
            "type": "官方線上電子書",
            "badge": "官方正版權威",
            "url": "http://ebook.nfa.gov.tw/1080503/",
            "desc": "內政部消防署官方編印之 EMT-1 40小時初訓標準教科書，包含人體解剖生理、八大生命徵象、呼吸道處置、CPR+AED、創傷止血包紮與急症處理全章節。"
        },
        {
            "id": "res-2",
            "name": "全國法規資料庫《緊急醫療救護法》最新完整條文",
            "category": "中央法規",
            "type": "全國法規資料庫",
            "badge": "法定母法",
            "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0020045",
            "desc": "緊急醫療救護之母法。重要考點：救護紀錄表法定保存7年（第23條）、救人免責善良撒瑪利亞人條款（第14-2條）、出勤人員配置（第17條）、洩密罰則二至十萬元（第37, 44條）。"
        },
        {
            "id": "res-3",
            "name": "全國法規資料庫《救護技術員管理辦法》最新法規",
            "category": "中央法規",
            "type": "全國法規資料庫",
            "badge": "必考核心規章",
            "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0020048",
            "desc": "主管救護技術員資格。必考：EMT-1初訓40小時、證書效期3年、展延繼續教育24小時（每年至少8小時），及第3條EMT-1得施行之12項救護項目（嚴禁侵入性給藥與插管）。"
        },
        {
            "id": "res-4",
            "name": "全國法規資料庫《緊急救護辦法》",
            "category": "中央法規",
            "type": "全國法規資料庫",
            "badge": "行政命令",
            "url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0120015",
            "desc": "內政部會同衛生福利部訂定，規範消防與醫療機關執行緊急救護服務範圍、救護車通訊派遣與紀錄傳遞作業。"
        },
        {
            "id": "res-5",
            "name": "Dcard 265T 學長彙編《EMT-1 快速參考手冊二版》",
            "category": "學長神講義",
            "type": "Google Drive PDF",
            "badge": "高分通關神書",
            "url": "https://drive.google.com/file/d/1X7HXDpSaryZcTXkAJJF3TAe8QrnFcdG-/view",
            "desc": "替代役 265 梯學長根據最新教材修訂整理，濃縮法規、生命徵象、抽吸時間、氧氣鋼瓶計算公式、START檢傷與期末筆試滿分精華。"
        },
        {
            "id": "res-6",
            "name": "Dcard 264T 替代役《EMT-1 快速參考手冊初版》",
            "category": "學長神講義",
            "type": "Google Drive PDF",
            "badge": "經典傳承講義",
            "url": "https://drive.google.com/file/d/1ioA26RuqjGuNNg2EKZJ-t8zrgcrBizKr/view",
            "desc": "廣受多梯替代役役男印出帶入成功嶺自修之口袋講義，條理分明歸納呼吸道、包紮與休克急救流程。"
        },
        {
            "id": "res-7",
            "name": "Dcard 軍旅板 #經驗分享《替代役新訓 270T EMT 考古題分享》",
            "category": "社群真題",
            "type": "Dcard 實戰心得",
            "badge": "114年教材更新對照",
            "url": "https://www.dcard.tw/f/military/p/257321890",
            "desc": "270 梯成功嶺役男實測分享，詳細對照 114 年新版教材異動觀念與易錯題，提醒考前教官總複習必背考點。"
        },
        {
            "id": "res-8",
            "name": "Dcard 軍旅板 #經驗分享《257梯替代役基礎訓練 EMT 考題整理》",
            "category": "社群真題",
            "type": "Dcard 實戰心得",
            "badge": "成功嶺期末考點",
            "url": "https://www.dcard.tw/f/military/p/255871234",
            "desc": "真實還原消防教官在成功嶺中隊教室強調的洩題重點、術科 CPR+AED 與止血包紮考官扣分盲點。"
        },
        {
            "id": "res-9",
            "name": "阿摩線上測驗 (Yamol)《初級救護技術員 EMT-1》題庫專區",
            "category": "線上題庫",
            "type": "互動測驗平台",
            "badge": "全台最大題庫社群",
            "url": "https://yamol.tw/cat-%E5%88%9D%E7%B4%9A%E6%95%91%E8%AD%B7%E6%8A%80%E8%A1%93%E5%93%A1+EMT-1-2983.htm",
            "desc": "收錄台灣各大訓練機構與歷屆 EMT-1 學科試卷，包含上千題單選題、詳細網友討論筆記與錯題智能統計。"
        },
        {
            "id": "res-10",
            "name": "Quizlet《EMT-1 初級救護技術員》字卡複習集",
            "category": "記憶字卡",
            "type": "線上記憶字卡",
            "badge": "背題速記利器",
            "url": "https://quizlet.com/search?query=EMT-1%20%E5%88%9D%E7%B4%9A%E6%95%91%E8%AD%B7%E6%8A%80%E8%A1%93%E5%93%A1&type=sets",
            "desc": "包含 GCS 指數、正常呼吸心跳脈搏、抽吸時間上限、氧氣濃度等數字型考點的翻牌記憶測驗。"
        },
        {
            "id": "res-11",
            "name": "內政部替代役暨社會韌性訓練執行中心 官方網站",
            "category": "主管機關",
            "type": "政府官方網站",
            "badge": "替代役政策中心",
            "url": "https://www.moi.gov.tw/",
            "desc": "發布替代役基礎訓練課程規範、EMT-1 與防災士雙證照政策及役男受訓權益規定。"
        },
        {
            "id": "res-12",
            "name": "台灣急診醫學會 (TSEM)《心肺復甦術與緊急心臟照護指引》",
            "category": "學術指引",
            "type": "醫學會指引",
            "badge": "最新醫療規範",
            "url": "https://www.sem.org.tw/",
            "desc": "台灣急重症醫學權威指引，同步 AHA 最新規範，確立高品質 CPR 30:2、深度 5~6cm、速率 100~120次/分及去顫電擊心律原則。"
        }
    ],

    # 法規逐條詳細對照 (對齊新訓條文規格，提供完整法定內文與出處連結)
    "statutory_articles": [
        {
            "law": "緊急醫療救護法",
            "article": "第 14-2 條",
            "title": "緊急救護免責條款（善良撒瑪利亞人條款）",
            "official_text": "救護人員以外之人，使用緊急救護設備或施予急救措施者，適用民法、刑法緊急避難應免除責任之規定。救護人員於非值勤期間，亦適用之。",
            "key_point": "救護免責：一般民眾以及『非值勤期間之救護人員（含替代役）』，因施予急救或使用 AED 等救護設備致傷亡者，免除民事與刑事賠償責任，消除救人顧慮。",
            "penalty": "無罰則（免責保障法條）",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020045&flno=14-2"
        },
        {
            "law": "緊急醫療救護法",
            "article": "第 17 條",
            "title": "救護車出勤人員配置規定",
            "official_text": "救護車出勤時，應有救護人員至少二名，或救護人員一名及駕駛人一名以上出勤。但載送非緊急病患時，得由救護人員一名出勤。",
            "key_point": "出勤配置：一般救護車緊急出勤，依法至少應配置『救護人員至少二名』，或『救護人員一名加駕駛人一名』。非緊急病患始得一名出勤。",
            "penalty": "違者依同法主管機關得命其限期改善或處罰救護車設置機關",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020045&flno=17"
        },
        {
            "law": "緊急醫療救護法",
            "article": "第 23 條",
            "title": "救護紀錄表之填具及保存期限",
            "official_text": "救護人員施行救護，應填具救護紀錄表，並交予接收病患之醫療機構；指派救護之單位，應將救護紀錄表至少保存七年。",
            "key_point": "法定保存七年：救護紀錄表為法定正式醫療紀錄，指派單位必須至少保存『七年』以上，交接時必須提交接收之醫療機構簽收。",
            "penalty": "未依規定保存或登載者處相關主管責任與行政裁罰",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020045&flno=23"
        },
        {
            "law": "緊急醫療救護法",
            "article": "第 24 條",
            "title": "救護技術員資格、訓練及分級依據",
            "official_text": "救護技術員分為初級、中級及高級；其資格、訓練、繼續教育、證書核發及得施行之救護項目等管理辦法，由中央衛生主管機關定之。",
            "key_point": "救護技術員三級制度之母法依據：救護技術員管理辦法授權中央衛生福利部統一規範。",
            "penalty": "未符法規標準不得自稱救護技術員執行專屬救護項目",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020045&flno=24"
        },
        {
            "law": "緊急醫療救護法",
            "article": "第 29 條",
            "title": "緊急傷病患送醫原則",
            "official_text": "救護人員應依救護指揮中心之派遣及指示，並視傷病患之病情及意願，送達就近適當之醫療機構。",
            "key_point": "就近適當送醫原則：救護人員不得隨意由病患要求送往極遠處醫療機構，必須遵循『就近適當』原則，保障患者生命黃金救治時間。",
            "penalty": "違反送醫指引致損及病情者受行政責任查處",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020045&flno=29"
        },
        {
            "law": "緊急醫療救護法",
            "article": "第 37 條與第 44 條",
            "title": "業務秘密保密義務與洩密罰鍰",
            "official_text": "第 37 條：救護技術員因業務知悉或持有他人之秘密，不得無故洩漏。\n第 44 條：違反第三十七條規定者，處新臺幣二萬元以上十萬元以下罰鍰。",
            "key_point": "洩密罰則：救護技術員於執勤中得知之傷病患病情、個資、住址等隱私，嚴禁私自拍照上傳網路或洩漏他人，違者處『新臺幣二萬元以上十萬元以下罰鍰』。",
            "penalty": "處新臺幣 20,000 元以上 100,000 元以下罰鍰",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020045&flno=37"
        },
        {
            "law": "救護技術員管理辦法",
            "article": "第 2 條",
            "title": "救護技術員各級資格與初訓時數",
            "official_text": "救護技術員之訓練，分為初級、中級及高級救護技術員。\n初級救護技術員應具相當於高級中等以上學校畢業或具同等學力，並經四十小時以上之訓練合格。\n中級救護技術員應具初級救護技術員資格滿一年以上，經二百八十小時以上之訓練合格。\n高級救護技術員應具中級救護技術員資格滿一年以上，經一千二百八十小時以上之訓練合格。",
            "key_point": "訓練時數考點：初級 EMT-1 至少『40 小時』（成功嶺替代役新訓受訓時數）；中級 EMT-2 至少『280 小時』；高級 EMT-P 至少『1280 小時』。",
            "penalty": "未受足額時數訓練合格者不得核發證書",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020048&flno=2"
        },
        {
            "law": "救護技術員管理辦法",
            "article": "第 3 條",
            "title": "初級救護技術員得施行之 12 項救護項目",
            "official_text": "初級救護技術員得施行之救護項目如下：\n一、檢傷分類及檢傷標籤之運用。\n二、傷病患生命徵象之測量。\n三、基本心肺復甦術及清除呼吸道異物。\n四、使用口咽呼吸道、鼻咽呼吸道。\n五、抽吸。\n六、氧氣治療。\n七、止血、包紮及固定。\n八、頸圈及長背板之使用。\n九、傷病患之搬運。\n十、心理支持及諮詢。\n十一、自動體外心臟電擊去顫器之使用。\n十二、其他經中央主管機關公告之項目。",
            "key_point": "EMT-1 救護權限範圍：嚴格限定上述 12 項！特別禁止施行『靜脈注射/點滴輸液』、『口服給藥』、『氣管內插管』等侵入性處置，否則違法觸及醫師法或超出職權。",
            "penalty": "逾越權限施行非許可項目得廢止證書並依法究辦",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020048&flno=3"
        },
        {
            "law": "救護技術員管理辦法",
            "article": "第 7 條",
            "title": "合格證書效期與展延繼續教育時數",
            "official_text": "救護技術員合格證書效期為三年。\n救護技術員於證書有效期限內，應接受相當等級之繼續教育課程，其訓練時數如下：\n一、初級救護技術員：二十四小時以上，且每年均應至少接受八小時。\n二、中級救護技術員：四十八小時以上，且每年均應至少接受十六小時。\n三、高級救護技術員：九十六小時以上，且每年均應至少接受二十四小時。\n逾期未完成繼續教育者，其合格證書於效期屆滿時失其效力。",
            "key_point": "展延規定（必考）：證書效期一律『三年』。EMT-1 三年內須完成『24 小時以上繼續教育，且每年均應至少接受 8 小時』。未依規定完成者證書自動失效，需重訓 40 小時！",
            "penalty": "證書失效，喪失救護技術員執勤資格",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=L0020048&flno=7"
        },
        {
            "law": "緊急救護辦法",
            "article": "第 3 條與第 4 條",
            "title": "消防機關緊急救護勤務與出勤規範",
            "official_text": "第 3 條：緊急救護服務範圍，包括急性傷病、重大意外傷亡、大量傷病患及其他緊急醫療救護之出勤派遣。\n第 4 條：消防救護車出勤，以二人以上為原則。",
            "key_point": "救護勤務原則：消防救護車以『二人以上』出勤為原則，並由救護指揮中心統一受理民眾報案派遣調度。",
            "penalty": "內部救護評鑑與出勤稽核考核規範",
            "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0120015&flno=3"
        }
    ],

    # 核心法規摘要卡片
    "laws_summary": [
        {
            "title": "救護技術員管理辦法 - 分級與訓練時數",
            "article": "第 2 條",
            "points": [
                "初級救護技術員 (EMT-1)：訓練時數至少 40 小時（成功嶺新訓全員標準）。",
                "中級救護技術員 (EMT-2)：需領有 EMT-1 滿一年，初訓時數至少 280 小時。",
                "高級救護技術員 (EMT-P)：需領有 EMT-2 滿一年，初訓時數至少 1280 小時以上。"
            ]
        },
        {
            "title": "救護技術員管理辦法 - 證書效期與繼續教育 (展延規定)",
            "article": "第 7 條",
            "points": [
                "證書效期：各級救護技術員合格證書效期均為「三年」。",
                "EMT-1 展延要件：三年效期內必須完成「24 小時以上之繼續教育，且每年均應至少接受 8 小時」。",
                "逾期未完成繼續教育者，證書自動失效，依法必須重新參加 40 小時初訓測驗合格後始得領證。"
            ]
        },
        {
            "title": "救護技術員管理辦法 - EMT-1 得施行之 12 項法定救護項目",
            "article": "第 3 條",
            "points": [
                "1. 檢傷分類及檢傷標籤之運用。",
                "2. 傷病患生命徵象之測量（八大生命徵象）。",
                "3. 基本心肺復甦術 (CPR) 及清除呼吸道異物（哈姆立克法）。",
                "4. 使用口咽呼吸道 (OPA)、鼻咽呼吸道 (NPA)。",
                "5. 抽吸（成人≦15秒、小兒≦10秒、嬰兒≦5秒）。",
                "6. 氧氣治療（鼻導管、面罩、非再吸入型面罩 NRM）。",
                "7. 止血、包紮及固定（含戰術止血帶 CAT、夾板）。",
                "8. 頸圈 (C-collar) 及長背板之使用。",
                "9. 傷病患之搬運（徒手搬運、搬運椅、擔架床）。",
                "10. 心理支持及諮詢。",
                "11. 自動體外心臟電擊去顫器 (AED) 之使用。",
                "12. 其他經中央主管機關公告之項目。",
                "⚠️ 重要考點：EMT-1 嚴禁施行靜脈注射、不可給予口服藥物、不可插氣管內管！"
            ]
        },
        {
            "title": "緊急醫療救護法 - 關鍵罰則與責任豁免",
            "article": "第 14-2, 17, 23, 37, 44 條",
            "points": [
                "第 14-2 條（善良撒瑪利亞人條款）：救護人員以外之人或非值勤期間救護人員施急救或用AED，適用緊急避難免責。",
                "第 17 條（救護車人員配置）：救護車緊急出勤，應有「救護人員至少二名」，或「救護人員一名及駕駛人一名」以上出勤。",
                "第 23 條（救護紀錄表）：施行救護應填具救護紀錄表，指派單位至少應「保存七年」。",
                "第 29 條（送醫原則）：救護人員應依病患病情及意願，送達「就近適當之醫療機構」。",
                "第 37 條與第 44 條（保密義務）：救護人員因業務知悉之秘密不得無故洩漏，違反者處「新臺幣二萬元以上十萬元以下罰鍰」。"
            ]
        }
    ],

    # 八大生命徵象表
    "vital_signs": {
        "title": "八大生命徵象 (Vital Signs) 正常與危急數值速查",
        "description": "涵蓋成人、小兒與嬰兒正常生理範圍，以及初級救護現場必須立即處置的危急門檻。",
        "table": [
            {
                "item": "意識狀態 (Consciousness)",
                "adult": "清醒警覺 (Alert), GCS 15分",
                "child": "對外界人事物有主動互動",
                "infant": "對父母有眼神注視、哭聲響亮",
                "critical": "AVPU 為 P (痛) 或 U (無反應)；GCS < 14分 (尤其是 ≦ 8分)"
            },
            {
                "item": "呼吸頻率 (Respiration)",
                "adult": "12 ～ 20 次/分",
                "child": "15 ～ 30 次/分",
                "infant": "25 ～ 50 次/分",
                "critical": "成人 > 30 次/分 或 < 10 次/分（嚴重換氣異常）"
            },
            {
                "item": "脈搏心跳 (Pulse)",
                "adult": "60 ～ 100 次/分 (測橈動脈)",
                "child": "80 ～ 120 次/分",
                "infant": "100 ～ 160 次/分 (測肱動脈)",
                "critical": "成人 > 120 次/分 或 < 50 次/分；頸動脈觸摸不到脈搏"
            },
            {
                "item": "血壓 (Blood Pressure)",
                "adult": "收縮壓 90~120 / 舒張壓 60~80 mmHg",
                "child": "收縮壓約 80 + (年齡×2) mmHg",
                "infant": "收縮壓約 70 mmHg 以上",
                "critical": "成人收縮壓 < 90 mmHg (休克警訊) 或 > 180 mmHg (高血壓急症)"
            },
            {
                "item": "體溫 (Body Temp)",
                "adult": "耳溫/口溫約 36.5 ～ 37.5 °C",
                "child": "約 36.5 ～ 37.5 °C",
                "infant": "約 36.5 ～ 37.5 °C",
                "critical": "低體溫 < 35 °C (創傷致命三聯徵)；熱中暑高燒 > 40 °C"
            },
            {
                "item": "膚色與體溫 (Skin)",
                "adult": "粉紅、溫暖、乾燥",
                "child": "粉紅、溫潤",
                "infant": "粉紅、溫潤",
                "critical": "蒼白、發紺（缺氧紫黑）、濕冷盜汗（休克）、潮紅發燙"
            },
            {
                "item": "瞳孔反射 (Pupil)",
                "adult": "雙側對稱、圓形、直徑 2~4mm、照光迅速收縮 (PERRL)",
                "child": "雙側對稱、照光靈敏",
                "infant": "雙側對稱、照光靈敏",
                "critical": "單側瞳孔放大無光反射 (腦疝危急)；針尖樣瞳孔 (鴉片類中毒)"
            },
            {
                "item": "微血管充填時間 (CRT)",
                "adult": "< 2 秒",
                "child": "< 2 秒",
                "infant": "< 2 秒",
                "critical": "> 2 秒（周邊微循環灌流不良、休克或嚴重失血早期徵兆）"
            }
        ]
    },

    # 4. GCS 昏迷指數評分表
    "gcs_table": {
        "title": "格拉斯哥昏迷指數 (Glasgow Coma Scale, GCS) 滿分15分 / 最低3分",
        "description": "E (Eye opening 睜眼 4分) + V (Verbal 語言 5分) + M (Motor 運動 6分)",
        "categories": [
            {
                "category": "睜眼反應 (Eye Opening, E - 滿分4分)",
                "items": [
                    {"score": 4, "desc": "自發性睜眼 (Spontaneous)"},
                    {"score": 3, "desc": "呼喚或聲音刺激睜眼 (To speech)"},
                    {"score": 2, "desc": "疼痛刺激睜眼 (To pain)"},
                    {"score": 1, "desc": "無任何反應 (None)"},
                    {"score": "C", "desc": "眼腫無法評估 (Closed by swelling)"}
                ]
            },
            {
                "category": "語言反應 (Verbal Response, V - 滿分5分)",
                "items": [
                    {"score": 5, "desc": "回答切題、人事時地物清楚 (Oriented)"},
                    {"score": 4, "desc": "言語困惑、混亂對答 (Confused)"},
                    {"score": 3, "desc": "用字不當、語無倫次 (Inappropriate words)"},
                    {"score": 2, "desc": "發出無法理解的呻吟難辨聲 (Incomprehensible sounds)"},
                    {"score": 1, "desc": "無任何發聲反應 (None)"},
                    {"score": "T/E", "desc": "氣切或插管無法發音 (Tracheostomy/Intubated)"}
                ]
            },
            {
                "category": "運動反應 (Motor Response, M - 滿分6分)",
                "items": [
                    {"score": 6, "desc": "能聽從口頭指令動作 (Obeys commands)"},
                    {"score": 5, "desc": "能定位疼痛刺激並撥開 (Localizes pain)"},
                    {"score": 4, "desc": "疼痛刺激產生正常屈曲收縮避縮 (Normal flexion / Withdrawal)"},
                    {"score": 3, "desc": "去大腦皮質僵直：異常屈曲雙手抱胸 (Abnormal flexion)"},
                    {"score": 2, "desc": "去大腦僵直：伸直內旋強直 (Extension)"},
                    {"score": 1, "desc": "無任何肢體活動反應、完全癱軟 (None / Flaccid)"}
                ]
            }
        ],
        "clinical_meaning": [
            {"range": "GCS 13 ～ 15 分", "severity": "輕度腦損傷 (Mild)", "desc": "神智大致清醒，應持續密切觀察意識改變。"},
            {"range": "GCS 9 ～ 12 分", "severity": "中度腦損傷 (Moderate)", "desc": "意識狀態明顯障礙，需高濃度氧氣治療與隨時準備抽吸。"},
            {"range": "GCS 3 ～ 8 分", "severity": "重度腦損傷 (Severe / Coma)", "desc": "重度昏迷！喪失保護性氣道反射，隨時可能呼吸道阻塞窒息，危急個案！"}
        ]
    },

    # 5. 高品質 CPR+AED
    "cpr_aed_guide": {
        "title": "成人生存之鏈與高品質 CPR+AED 五大黃金指標",
        "description": "生存之鏈六環：1.早期求救 ➜ 2.高品質CPR ➜ 3.快速去顫 ➜ 4.高級心臟救命術 ➜ 5.心跳停止後照護 ➜ 6.復原整合照護。",
        "indicators": [
            {
                "rule": "1. 壓胸速率 (Rate)",
                "detail": "100 ～ 120 次/分鐘（節奏約如歌曲 Stayin' Alive）。"
            },
            {
                "rule": "2. 壓胸深度 (Depth)",
                "detail": "成人至少 5 公分，但不可超過 6 公分（小兒約胸廓厚度 1/3，約 5 公分；嬰兒約 4 公分）。"
            },
            {
                "rule": "3. 完全胸回彈 (Recoil)",
                "detail": "每次下壓後必須讓胸廓完全回彈至原始位置，手掌不施加殘餘壓力，以利心臟充分回血充盈。"
            },
            {
                "rule": "4. 減少中斷時間 (Minimize Interruption)",
                "detail": "壓胸中斷時間嚴格控制在 10 秒以內（包含換手、AED分析心律與電擊前離手）。"
            },
            {
                "rule": "5. 避免過度換氣 (Avoid Excessive Ventilation)",
                "detail": "每次吹氣 1 秒鐘，見胸廓有微微起伏即可。過度換氣會增加胸內壓、減少靜脈回流心臟血量。"
            },
            {
                "rule": "6. 壓吹比與輪替",
                "detail": "單人及雙人成人 CPR 一律為 30:2；每 2 分鐘（約 5 個週期）施救者相互輪替壓胸，避免疲勞導致按壓深度不足。"
            }
        ],
        "aed_protocol": [
            {"step": "Step 1", "desc": "開：打開 AED 電源開關（聽從語音指示）。"},
            {"step": "Step 2", "desc": "貼：擦乾胸壁水分，貼上電擊貼片（右鎖骨下方、左乳頭外下側心尖處）。"},
            {"step": "Step 3", "desc": "插：將貼片導線插頭插入主機孔（部分機型已預先插妥）。"},
            {"step": "Step 4", "desc": "聽：聽從語音『正在分析心律，請大家離手！』大聲複誦：大家離手！"},
            {"step": "Step 5", "desc": "電：若建議電擊，確認所有人離手無人接觸傷患後，按下閃爍之電擊鈕；電擊完成立即徒手恢復壓胸！"}
        ],
        "shockable_rhythms": "AED 僅對兩種致命心律給予電擊去顫：心室纖維顫動 (VF) 及無脈性心室頻脈 (pVT)。心搏停止 (Asystole) 及無脈性電氣活動 (PEA) 絕對不予電擊！"
    },

    # 6. 氧氣治療設備與計算公式
    "oxygen_therapy": {
        "title": "常用氧氣治療設備規格與鋼瓶可用時間計算公式",
        "table": [
            {
                "device": "鼻導管 (Nasal Cannula)",
                "flow": "1 ～ 6 L/min",
                "fio2": "24% ～ 44%",
                "desc": "每增加 1 L/min 流量，約提升氧氣濃度 4%。適用於輕度缺氧、呼吸平穩、無法耐受面罩之清醒病患。"
            },
            {
                "device": "簡易面罩 (Simple Mask)",
                "flow": "6 ～ 10 L/min",
                "fio2": "35% ～ 60%",
                "desc": "流量絕對不可低於 6 L/min，以免面罩內蓄積二氧化碳造成重複回吸中毒。適用於中度缺氧病患。"
            },
            {
                "device": "非再吸入型面罩 (NRM)",
                "flow": "10 ～ 15 L/min",
                "fio2": "80% ～ 100%",
                "desc": "初級救護最重要高濃度氧氣設備！使用前必須先用手指輕按單向閥將儲氣袋充盈至 2/3 以上。適用於嚴重呼吸困難、創傷休克、一氧化碳中毒。"
            },
            {
                "device": "甦醒球 (BVM / Ambu-bag)",
                "flow": "15 L/min (接儲氣袋)",
                "fio2": "90% ～ 100%",
                "desc": "配合高濃度氧氣與儲氣袋。成人擠壓約 500~600ml（約單手擠壓 1/2 至 2/3 袋身），每 5~6 秒給一口氣，每次給氣 1 秒看見胸廓起伏。"
            }
        ],
        "formula": {
            "title": "氧氣鋼瓶可用時間 (分鐘) 計算公式",
            "equation": "可用時間 (分鐘) = [ (鋼瓶壓力錶讀數 psi - 安全存量 200 psi) × 鋼瓶常數 ] ÷ 每分鐘給氧流量 (L/min)",
            "constants": [
                {"cylinder": "D 瓶 (攜帶型小鋼瓶)", "constant": "0.16", "safety": "200 psi"},
                {"cylinder": "E 瓶 (攜帶型中鋼瓶)", "constant": "0.28", "safety": "200 psi"},
                {"cylinder": "M 瓶 (救護車固定大鋼瓶)", "constant": "1.56", "safety": "200 psi"}
            ],
            "example": "經典考題範例：D型氧氣鋼瓶壓力為 1200 psi，使用非再吸入型面罩流量 10 L/min，請問可用時間約多久？<br>解法：[(1200 - 200) × 0.16] ÷ 10 = [1000 × 0.16] ÷ 10 = 160 ÷ 10 = 16 分鐘！"
        }
    },

    # 7. 創傷評估處置 XABCDE
    "trauma_care": {
        "title": "創傷評估 XABCDE 與救命處置原則",
        "description": "遵循現代國際創傷生命支持 (ITLS / PHTLS) 與戰傷急救 (TCCC) 核心流程。",
        "steps": [
            {
                "step": "X (eXsanguinating Hemorrhage)",
                "name": "控制致命性外出血",
                "action": "四肢噴射性動脈大出血優先使用「戰術止血帶 (CAT)」，於傷口近心端 5~7cm 施打旋緊直至止血，標記上帶時間，到院前嚴禁自行鬆開。"
            },
            {
                "step": "A (Airway with C-spine)",
                "name": "呼吸道暢通與頸椎限制",
                "action": "懷疑脊椎創傷使用「推下顎法 (Jaw-thrust)」暢通呼吸道，雙手進行頭頸中立固定 (MILS)，適時量測並穿戴硬頸圈。"
            },
            {
                "step": "B (Breathing & Ventilation)",
                "name": "呼吸與胸廓評估",
                "action": "看胸廓起伏與對稱性。吮吸性胸部傷口（開放性氣胸）立即使用不透氣敷料施作「三邊貼緊、留下一邊」單向活瓣包紮。"
            },
            {
                "step": "C (Circulation)",
                "name": "循環與灌流評估",
                "action": "評估橈動脈/頸動脈搏動、CRT (<2秒)、膚色體溫。骨盆骨折慎防大出血，腹部臟器脫出用濕無菌紗布覆蓋保溫（嚴禁推回）。斷肢隔水冷藏。"
            },
            {
                "step": "D (Disability)",
                "name": "神經學功能評估",
                "action": "評估 GCS 昏迷指數或 AVPU 意識量表，檢查雙側瞳孔大小及對光反射反應，檢查四肢末端 CMS/PMS 運動感覺循環。"
            },
            {
                "step": "E (Exposure & Environment)",
                "name": "暴露檢查與環境保溫",
                "action": "剪開衣物檢查隱藏外傷，隨後立即覆蓋救護毯保溫，預防致命創傷三聯徵（低體溫、酸中毒、凝血功能障礙）。"
            }
        ]
    },

    # 8. START 大量傷病患檢傷分類法
    "start_triage": {
        "title": "大量傷病患 START 檢傷分類決策流程 (RPM 法)",
        "description": "Simple Triage And Rapid Treatment：每位傷患評估控制在 30 秒至 1 分鐘內完成。",
        "flowchart": [
            {
                "stage": "Step 1: 走動傷患分流",
                "condition": "凡是能聽懂廣播並自己走動的人員",
                "result": "綠色標籤 (Minor / 輕傷)",
                "action": "引導至綠區安置，待後續檢傷。"
            },
            {
                "stage": "Step 2: 呼吸評估 (Respiration)",
                "condition": "無呼吸 ➜ 暢通呼吸道後：若仍無呼吸 ➜ 黑色；若恢復呼吸 ➜ 紅色。<br>若呼吸速率 > 30 次/分 或 < 10 次/分 ➜ 紅色。",
                "result": "黑色 (死亡) / 紅色 (極重傷)",
                "action": "黑色不予急救；紅色立即維持呼吸道並列第一優先後送。"
            },
            {
                "stage": "Step 3: 循環灌流 (Perfusion)",
                "condition": "呼吸 10~30 次/分 ➜ 檢查循環：摸不到橈動脈 或 CRT > 2 秒 ➜ 紅色。",
                "result": "紅色標籤 (Immediate / 極重傷)",
                "action": "立即控制活動性大出血，抬高下肢。"
            },
            {
                "stage": "Step 4: 意識狀態 (Mental Status)",
                "condition": "呼吸循環皆正常 ➜ 測試簡單口頭指令（如眨眼、握手）：無法聽從指令 ➜ 紅色；能聽從簡單指令 ➜ 黃色。",
                "result": "黃色標籤 (Delayed / 中傷)",
                "action": "黃色無立即生命危險，第二優先後送。"
            }
        ]
    }
}

# Write study data to data/emt_study_data.json
with open("data/emt_study_data.json", "w", encoding="utf-8") as f:
    json.dump(study_data, f, ensure_ascii=False, indent=2)

print("Successfully generated data/emt_study_data.json with aligned statutory articles!")
