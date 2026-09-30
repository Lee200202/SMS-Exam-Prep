import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/study_data.json', 'r', encoding='utf-8') as f:
    study_data = json.load(f)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions_data = json.load(f)

all_categories = [
    {
        "id": "documents",
        "name": "一、各式重要 A4 文件與專長證明 (L夾裝好，報到必查)",
        "items": [
            {"id": "doc_callup", "name": "徵集令正本", "must": True, "tip": "入營搭車與報到必備身分查驗，可多印 1~2 份影本備查"},
            {"id": "doc_deduct", "name": "役期折抵成績單正本", "must": True, "tip": "高中、大學教官室蓋章之成績單正本，折抵役期在成功嶺新訓第一週辦理最順"},
            {"id": "doc_post", "name": "郵局存摺正面影本", "must": True, "tip": "每月役男薪資直接匯款發放用，請備妥清晰封面影本（或牢記局帳號）"},
            {"id": "doc_diploma", "name": "最高學歷證明 / 畢業證書影本", "must": False, "tip": "一般替代役選役別時學歷評比重要依據（研替役男可免帶；國外學歷需外館認證）"},
            {"id": "doc_specialty", "name": "役別甄選專長佐證資料 (證照/外語/作品集)", "must": False, "tip": "國家專長證照、外語檢定證明、各類救災/醫療/資訊/水電證書，選役別大利多"},
            {"id": "doc_exam_notes", "name": "印出來的替代役題庫與重點整理", "must": False, "tip": "【高分必備】大餐課或零碎時間背誦，手機管制時的刷題奪高分神器，單張印製"},
            {"id": "doc_emt_notes", "name": "EMT-1 講義與題庫筆記", "must": False, "tip": "【Dcard 傳說神器】上課教官問問題容易找出答案舉手回答，快速累積加分拚榮譽假(榮2提早離營)"},
            {"id": "doc_memo", "name": "隨身記事備忘小卡", "must": False, "tip": "寫下郵局帳號、未來公司全名、家人身分證字號與緊急聯絡電話，填資料免背"}
        ]
    },
    {
        "id": "identities",
        "name": "二、重要證件、金錢配置與隨身電子物品",
        "items": [
            {"id": "id_card", "name": "國民身分證正本", "must": True, "tip": "隨身攜帶，幹部與各項程序查驗身分必備，亦可備影本"},
            {"id": "health_card", "name": "健保 IC 卡", "must": True, "tip": "隨身攜帶，轉診、醫務室掛號必備"},
            {"id": "cash_plan", "name": "現金 2,500 ~ 3,000 元 (含百元鈔與零錢)", "must": True, "tip": "入營預收800扣理髮/洗衣/團拍；備500鈔1張+100鈔15~20張，備足零錢投飲料機與85餐車"},
            {"id": "credit_card", "name": "信用卡 / 提款卡", "must": False, "tip": "【Dcard 史詩好物】放假前洗打時間線上訂高鐵票，綁行動支付叫車，放重櫃應急提款必備"},
            {"id": "coin_pouch", "name": "無品牌素色零錢小包", "must": False, "tip": "【Dcard 推薦】裝紙鈔、零錢、提款卡，放進貴重物品袋隨身帶，避免零散掉落"},
            {"id": "waist_bag", "name": "隨身隨行腰包", "must": False, "tip": "【Dcard 留言推薦】裝手機與貴重物品，晚上洗打時間一背就走，不用手忙腳亂翻櫃子"},
            {"id": "watch_lum", "name": "有夜光/微光功能的電子手錶", "must": True, "tip": "【Dcard 傳說神器】半夜常起床或整理內務被關燈，昏暗中看時間掌控速度超必備"},
            {"id": "phone_powerbank", "name": "手機 + 滿電大容量行動電源 1~2 顆", "must": True, "tip": "營區插座管制不開放充電，帶滿電行充；研替不需灌 MDM，中國廠牌手機亦可帶"},
            {"id": "wired_earphones", "name": "有線耳機 (3.5mm / Type-C)", "must": True, "tip": "洗打時間講電話聽法規必備！特別注意：無線藍牙耳機一律算違禁品會被集中保管"},
            {"id": "glasses_box", "name": "傳統眼鏡 + 眼鏡盒與防掉繩", "must": True, "tip": "【群組&Dcard強烈建議】營區灰塵砂土多且衛生環境差，切勿戴隱形眼鏡/角膜塑形片防感染"},
            {"id": "seal_stamp", "name": "個人私章 (便宜木頭章備用)", "must": False, "tip": "裝備領取蓋章備用，勿帶貴重印鑑，若沒帶通常也可用指印替代"}
        ]
    },
    {
        "id": "god_tier_items",
        "name": "三、生活用餐衛生神物與終極神器 (Dcard 277T/137研替強推)",
        "items": [
            {"id": "heat_bag_5jin", "name": "5斤耐熱袋 (入營天數×3個，約45~60個)", "must": True, "tip": "【Dcard 終極神器】套在餐盤上裝飯菜，吃完袋子一抽丟掉，省去大排長龍搶水槽洗碗時間！資收時請綁好丟棄"},
            {"id": "iron_spoon", "name": "自備鐵湯匙 / 環保湯匙", "must": True, "tip": "【Dcard 傳說神器】公發只有筷子，吃湯泡飯或甜湯極度崩潰，自備鐵湯匙用餐體驗大幅升級"},
            {"id": "dish_soap_sponge", "name": "自備小瓶洗碗精 + 洗碗海綿", "must": False, "tip": "【Dcard 留言替代推薦】若不想用耐熱袋製造垃圾，自備小瓶洗碗精與海綿，吃完先清菜渣上樓洗，比營區稀釋洗碗精乾淨快速"},
            {"id": "febreze_spray", "name": "風倍清消臭噴霧", "must": False, "tip": "【Dcard 傳說神器】寢具、操作服、制服褲除臭消毒，除內衣褲襪三寶外其餘少洗，去味必備"},
            {"id": "toilet_deodorant", "name": "一滴消臭元", "must": False, "tip": "【Dcard 史詩好物】大號時在馬桶滴 1~2 滴，迅速掩蓋異味，多人共用衛浴減少尷尬"},
            {"id": "closet_dehumidifier", "name": "吊掛式除濕除臭袋", "must": False, "tip": "【Dcard 推薦】掛在內務櫃密閉空間防潮、吸濕除臭，避免衣物潮濕發霉異味"},
            {"id": "colored_plastic_bags", "name": "白色以外特殊顏色大塑膠袋 x 2", "must": True, "tip": "【Dcard 史詩好物】藥櫃袋與違禁物袋專用！一百人都是營站白色袋子，特殊顏色1秒找出自己的袋子"},
            {"id": "medicine_zipper_bag", "name": "分裝用透明拉鍊藥袋", "must": False, "tip": "【Dcard 留言推薦】裝個人藥品寫上學號名字，防東翻西翻散落或整個藥袋遺失"},
            {"id": "multi_plastic_bags", "name": "分裝用塑膠袋多個 (非透明)", "must": False, "tip": "裝入營便服、運動鞋、濕毛巾、離營服，乾濕分類收納整齊不混雜"},
            {"id": "mesh_zipper_bag", "name": "額外網格防水拉鍊袋", "must": False, "tip": "【Dcard 史詩好物】裝隨身紙巾類、當鉛筆盒、收納濕掉的輕便雨衣超好用"},
            {"id": "canvas_tote_bag", "name": "手提帆布袋 / 防水提袋", "must": False, "tip": "【Dcard 留言推薦】平日去大餐課、各類演講裝文具包、水壺、雨衣等雜物隨身提著走超方便"},
            {"id": "raincoat_spare", "name": "黃色輕便雨衣 2 件 (自備備用)", "must": True, "tip": "【Dcard 史詩好物】公發雨衣穿脫多次極臭且無法加買，自備 2 件備用雨衣遇連日大雨非常有救"},
            {"id": "sleep_earplugs", "name": "睡覺專用防打呼耳塞", "must": True, "tip": "【Dcard 傳說神器】多人寢室鄰兵打呼如雷，自備高抗噪泡棉/矽膠耳塞能拯救睡眠品質"},
            {"id": "pillow_cover_disposable", "name": "免洗枕頭套", "must": False, "tip": "【Dcard 推薦】墊在公發毛巾或枕頭上，乾淨衛生防過敏"},
            {"id": "umbrella_spare", "name": "折疊雨傘 (放違禁品袋)", "must": False, "tip": "休假出營下雨備用，入營檢查時集中保管於違禁品袋"}
        ]
    },
    {
        "id": "toiletries_med",
        "name": "四、盥洗保養、個人常備藥品與清潔消耗品",
        "items": [
            {"id": "two_toothbrushes", "name": "兩支牙刷法 (檢查用平穩牙刷 + 自備刷牙用) & 牙膏", "must": True, "tip": "【Dcard&記事本實戰】1支放床下臉盆應付檢查(選底部平穩不易滾動)，另1支放內務櫃自用，避免床下灰塵入口"},
            {"id": "three_in_one_soap", "name": "三合一沐浴乳 (洗髮/洗臉/洗澡)", "must": True, "tip": "戰鬥洗澡搶時間神器，推薦好起泡且好沖洗款式，可另帶小條洗面乳"},
            {"id": "box_tissues", "name": "抽取式衛生紙 x 2 包 (標準塑膠大包裝)", "must": True, "tip": "【規格提醒】帶常見塑膠大包，禁加油站紙盒或小餐巾包。1包檢查未拆維持方正，另1包自用"},
            {"id": "pocket_tissues", "name": "袖珍包面紙 15~20 包 (推薦「厚」牌)", "must": True, "tip": "隨身口袋常備，操課擦汗、如廁必備，成功嶺廁所通常無衛生紙，建議帶一整大組厚款"},
            {"id": "alcohol_wipes_or_roll", "name": "酒精濕紙巾 3~5 包 或 酒精滾珠瓶", "must": True, "tip": "【Dcard 傳說神器 + 記事本小撇步】擦拭馬桶蓋、餐桌消毒；使用分裝滾珠瓶裝酒精，安檢絕對不刁難"},
            {"id": "water_wipes", "name": "一般純水濕紙巾 3~5 包", "must": True, "tip": "【Dcard 傳說神器】擦餐具、擦餐盤、擦手、擦屁股，大號清潔救星"},
            {"id": "cool_wipes", "name": "爽身涼感濕紙巾 1~2 包", "must": False, "tip": "GATSBY 涼感黑型，夏日晨跑大出操後擦臉頸部瞬間降溫超爽快"},
            {"id": "prickly_heat_powder", "name": "蛇牌涼感爽身粉 / 止汗劑", "must": False, "tip": "【Dcard 史詩好物】洗澡後或操課前撲在腋下胯下，減少出汗防汗疹"},
            {"id": "shaver_manual", "name": "刮鬍刀：手動款 或 內建鋰電池充電款", "must": True, "tip": "【避坑提醒】嚴禁可拆式乾電池刮鬍刀（違禁品會被沒入），手動或先充飽電的鋰電款才合規"},
            {"id": "nail_clipper_box", "name": "指甲剪 (務必附集屑盒，無尖銳銼刀)", "must": True, "tip": "定期內務檢查，無集屑盒容易掉碎屑被扣內務分，不可含尖銳銼刀（可入營前先剪好）"},
            {"id": "mask_ear_protector", "name": "口罩減壓器 / 自備寬耳口罩", "must": False, "tip": "【Dcard 傳說好物】長時間整天配戴口罩，耳朵不痛的神物"},
            {"id": "mosquito_roll", "name": "滾珠式防蚊液 1~2 瓶", "must": True, "tip": "【記事本&Dcard推薦】成功嶺蚊子超兇，按壓噴霧易被刁難，滾珠瓶最安全，上廁所脫褲前先抹"},
            {"id": "itch_cream", "name": "外用急救藥膏 (曼秀雷敦/綠油精/3M透氣膠布/碘酒消毒棉片)", "must": False, "tip": "【記事本精華】中隊無多餘醫療耗材處理小擦傷，自備3M膠布、碘酒棉片防蚊蟲外傷感染超實用"},
            {"id": "personal_medicine", "name": "個人常備內服藥品 (感冒藥/胃腸藥/軟便劑/益生菌/維他命)", "must": True, "tip": "緊張胃痛、換環境便秘必備；西藥建議完整原包裝，無標示需附處方箋；維他命要有外標示"},
            {"id": "dental_floss", "name": "捲軸式牙線", "must": False, "tip": "【避坑提醒】嚴禁尖頭牙線棒，尖端被列違禁品會被沒入，捲軸牙線合法又乾淨"},
            {"id": "sunscreen", "name": "防曬乳", "must": False, "tip": "在意烈日戶外操課曬黑者可自備"}
        ]
    },
    {
        "id": "stationery_drill",
        "name": "五、文具與內務整理解悶小工具",
        "items": [
            {"id": "erasable_pen", "name": "擦擦筆 (黑 / 藍)", "must": True, "tip": "【Dcard 傳說神器】寫資料、填單、作筆記寫錯直接擦掉，省去找立可帶時間"},
            {"id": "binder_clips", "name": "長尾夾 4~6 個", "must": True, "tip": "折棉被拉角、蚊帳定型、夾內務櫃衣袖、夾未裝訂書籍，內務加分神物"},
            {"id": "double_sided_tape", "name": "雙面膠", "must": False, "tip": "【Dcard 推薦】黏名牌或整理內務邊角固定超實用"},
            {"id": "sudoku_paper", "name": "數獨題目 (單張印製 100~200 回)", "must": False, "tip": "【Dcard 留言解悶交友神器】不可整本裝訂成冊，大餐課打發時間還能分給鄰兵交朋友"},
            {"id": "colored_pens_paper", "name": "彩色筆 / 螢光筆 & 空白 A4 紙數張", "must": False, "tip": "【記事本推薦】公發筆易壞，自備原子筆與彩色筆可在無聊時畫畫、打發時間、玩小遊戲"},
            {"id": "pencil_eraser", "name": "2B 鉛筆與橡皮擦", "must": False, "tip": "填卡劃記考試備用"},
            {"id": "correction_tape", "name": "立可帶", "must": False, "tip": "備用，若有準備擦擦筆幾乎用不到"}
        ]
    },
    {
        "id": "commissary_buy",
        "name": "六、營站採買推薦物品與公發尺寸避坑建議",
        "items": [
            {"id": "slippers_blue", "name": "公發藍白拖鞋 (營站購買)", "must": True, "tip": "營區洗澡與寢室活動必穿，大家都長一樣，可在鞋側做記號"},
            {"id": "undershirt_buy", "name": "排汗阿公內衣 (多買 1~2 件，公發 3 件)", "must": False, "tip": "夏天流汗量極大，晨跑完可以直接換穿，維持清爽"},
            {"id": "boxers_buy", "name": "四角內褲 (多買 1~2 件或自備免洗內褲)", "must": False, "tip": "公發材質較粗糙，可穿自己的免洗或自備純棉內褲，但自備內褲不能送洗"},
            {"id": "socks_buy", "name": "黑色中筒軍襪 (多買 1~2 雙，公發 2 雙)", "must": False, "tip": "下大雨或流汗備用替換"},
            {"id": "towel_buy", "name": "純白毛巾 (多買 1 條，公發 2 條)", "must": False, "tip": "公發毛巾掛床頭供內務檢查，多買一條自用洗臉洗澡或墊枕頭"},
            {"id": "throat_drops_pink", "name": "京都念慈菴粉紅鐵盒喉糖 (營站採買或先買好未拆封)", "must": False, "tip": "【記事本&Dcard推薦】唯一合法零嘴！買粉紅色（枇杷潤喉），切勿買藍色薄荷；入營檢查前切勿拆封"},
            {"id": "earplugs_helmet_pad", "name": "鋼盔海綿墊 & 打靶防震耳塞", "must": False, "tip": "打靶防耳鳴、戴鋼盔舒適度大幅提升，當天靶場也會發"},
            {"id": "shoe_size_sport", "name": "💡 公發運動鞋尺寸：強烈建議拿「大 2~3 號」", "must": True, "tip": "【Dcard 學長血淚經驗】公發運動鞋原號碼穿起來腳趾會擠壓劇痛，拿大2~3號舒服超多！"},
            {"id": "shoe_size_leather", "name": "💡 公發皮鞋尺寸：建議拿原尺寸或大 1 號", "must": True, "tip": "公發黑皮鞋沒有半碼，拿稍大一點比較舒服好走，後面留一指寬"},
            {"id": "canteen_caution", "name": "💡 公發塑膠水壺：千萬別摔到", "must": True, "tip": "公發塑膠水壺摔在水泥地上很容易炸裂漏水，務必套好水壺套"}
        ]
    },
    {
        "id": "control_levels",
        "name": "七、物品管制等級劃分：重度 / 中度 / 輕度管制規範與藏放秘訣 (替代役群組記事本精華)",
        "items": [
            {"id": "ctrl_heavy_wallet", "name": "🔒 【重度管制】錢包與現金 (鎖重櫃)", "must": True, "tip": "大錢放進皮夾鎖入重櫃，鑰匙自行保管；預繳800元後，其餘作為交通費與緊急備用金"},
            {"id": "ctrl_heavy_phone", "name": "🔒 【重度管制】智慧型手機 (鎖重櫃)", "must": True, "tip": "新訓期間平時完全管制鎖重櫃，僅每晚洗打時間統一集中取出使用，結束即上鎖收納"},
            {"id": "ctrl_heavy_powerbank", "name": "🔒 【重度管制】大容量行動電源 (鎖重櫃)", "must": True, "tip": "營區插座嚴禁充電，行充容量愈大愈好，不可有實體插頭插座，平時一律鎖重櫃"},
            {"id": "ctrl_heavy_card", "name": "🔒 【重度管制】提款卡 / 信用卡 (放重櫃)", "must": False, "tip": "防止臨時現金不足或休假購票，放在皮夾內隨同重櫃集中保管，安全防盜"},
            {"id": "ctrl_med_western", "name": "💊 【中度管制】食用內服西藥 (鎖藥櫃)", "must": True, "tip": "西藥最好保留原廠外包裝標示，可拆封；若為診所無標示散裝藥包，務必附上醫師處方箋或藥單"},
            {"id": "ctrl_med_chinese", "name": "💊 【中度管制】中藥預防感冒品 (鎖藥櫃)", "must": False, "tip": "中藥無標示限制，推薦帶龍角散、清肺保等，新訓環境易傳染，喉嚨怪怪時立刻服用預防"},
            {"id": "ctrl_med_special", "name": "💊 【中度管制】特殊疾病個人需用藥物 (入營先報備)", "must": False, "tip": "入營體檢時務必先主動告知醫療中隊，並向所屬中隊幹部報備，隨身備妥診斷證明與處方箋"},
            {"id": "ctrl_med_smoke", "name": "🚬 【中度管制】香菸 (上限1條，放煙櫃)", "must": False, "tip": "若有抽菸者最多不可攜帶超過一條，入營時統一登記入「煙櫃」管理；打火機為完全違禁品嚴禁私藏"},
            {"id": "ctrl_med_clothes", "name": "👟 【中度管制】個人便服鞋子與自備雨衣 (黑大保管)", "must": False, "tip": "新訓期間營區一律穿公發服裝與雨衣，個人便服、運動鞋、雨具僅放假出營穿著，平時集中收納"},
            {"id": "ctrl_light_winter_wear", "name": "🧥 【輕度管制】冬季保暖衣物 (發熱衣/薄毛衣/外套)", "must": False, "tip": "可以帶和穿著，但必須穿在公發制服或外套裡面，外觀完全看不出來，維持隊伍統一"},
            {"id": "ctrl_light_own_towel", "name": "🧼 【輕度管制】自家自備毛巾 (白天完全收好)", "must": False, "tip": "洗澡洗臉可用，但白天內務檢查床頭只能掛公發純白毛巾，自家毛巾白天務必完全藏進黑大深處（不建議帶）"},
            {"id": "ctrl_light_bedding", "name": "🛏️ 【輕度管制】自家枕頭套 / 床套 (白天完全收好)", "must": False, "tip": "若帶自家床套白天必須全部拆下收好，極度耗時繁瑣，強烈建議改帶拋棄式免洗枕頭套墊在毛巾下"},
            {"id": "ctrl_light_stationery_box", "name": "✏️ 【輕度管制】私天文具包 / 鉛筆盒 / 彩色筆 (白天收好)", "must": False, "tip": "公發文具包放表面，私天文具與彩色筆白天必須收進內務櫃底層深處，不可散落表面扣分"},
            {"id": "ctrl_light_disposable_underwear", "name": "🩲 【輕度管制】拋棄式免洗內褲 (留意丟棄時機)", "must": False, "tip": "可以穿著但不能送洗，丟棄時需特別留意垃圾分類與丟棄時機，避免造成中隊垃圾處理意見"},
            {"id": "ctrl_light_cleansers", "name": "🧴 【輕度管制】自備洗面乳 / 刮鬍泡foam (白天藏好)", "must": False, "tip": "臉盆內務檢查絕對只能放「牙刷x1、牙膏x1、洗沐精x1」，自己帶的洗面乳或刮鬍泡白天一律藏進內務櫃"}
        ]
    },
    {
        "id": "authorized_custom",
        "name": "八、准予自備與特殊需求物品 (不屬前三管制類之合規自備、特殊藥品與冬季保暖專區)",
        "items": [
            {"id": "auth_stable_toothbrush", "name": "🪥 平穩不易滾動牙刷 (符合臉盆規格)", "must": True, "tip": "臉盆檢查牙刷刷柄底部平坦或不易滾動款式，刷毛朝上，避免滾動扣內務分"},
            {"id": "auth_plain_undershirt", "name": "👕 白色短袖排汗阿公內衣 (樣式顏色需完全合規)", "must": True, "tip": "自備必須為純白色短袖排汗款式，與公發外觀一致，晨跑後替換極度清爽"},
            {"id": "auth_plain_socks", "name": "🧦 黑色中筒軍襪 (純黑無商標素色)", "must": True, "tip": "純黑色、無明顯Logo的中筒襪，長度過腳踝，與公發標準完全一致"},
            {"id": "auth_plain_slippers", "name": "🩴 公發款藍白拖鞋 (鞋側做微小暗記)", "must": True, "tip": "營區洗澡與就寢必穿，大家都長得一模一樣，可在鞋側或鞋底用原子筆做隱蔽記號防拿錯"},
            {"id": "auth_medical_masks", "name": "😷 素色醫療口罩 (純白或素色無花紋)", "must": True, "tip": "長時間整天佩戴，可自備寬耳減壓款或搭配口罩減壓帶，耳朵不痛"},
            {"id": "auth_religion_jewelry", "name": "📿 宗教信仰飾品 (木質/編織佛珠、十字架，禁金屬)", "must": False, "tip": "宗教項鍊或手環可隨身配戴，但【嚴格禁止金屬材質項鍊或金屬手環】，以防操課碰撞刮傷"},
            {"id": "auth_optical_glasses", "name": "👓 傳統近視光學眼鏡 (附眼鏡盒與防掉繩)", "must": True, "tip": "營區環境灰塵沙土大，洗手衛生不佳，【嚴禁隱形眼鏡與角膜塑形片】，傳統眼鏡最安全安全"},
            {"id": "auth_first_aid_med", "name": "🩹 簡易外傷外用藥 (綠油精/白花油/小護士/3M膠布/碘酒消毒棉片)", "must": False, "tip": "中隊無多餘醫療耗材處理小擦傷，自備3M透氣膠布與碘酒消毒液可自行迅速處理小傷口"},
            {"id": "auth_thick_pocket_tissues", "name": "🧻 隨身面紙買「厚」牌 (大組20多包)", "must": True, "tip": "成功嶺廁所通常無衛生紙，買大組厚包裝隨身攜帶，擦汗如廁最安心"},
            {"id": "auth_sealed_throat_drops", "name": "🍬 未拆封鐵盒喉糖 3~5 盒 (入營檢查前切勿拆封)", "must": False, "tip": "軍中唯一合法合規的零嘴與提神神物！入營安檢前【絕對不可先拆封】，否則會被視為散裝食物被扣"},
            {"id": "auth_blank_paper_pens", "name": "🎨 空白 A4 紙張與彩色筆 / 螢光筆", "must": False, "tip": "大餐課與講座時間漫長無聊，自備空白紙張畫畫、寫字、玩紙上遊戲解悶交朋友"},
            {"id": "auth_certificates_all", "name": "📜 各類專長證照與比賽獎狀影本 (選役別關鍵籌碼)", "must": False, "tip": "職業駕照、律師證、醫療/護理/諮商證、救災/義消證、英日韓德法外語檢定中級以上、原住民身分證明、無人機操作證、水電機電證、園藝證、街頭藝人證、樂器演奏獎狀、作品集等"},
            {"id": "auth_luggage_guide", "name": "🎒 入營包款指南：雙肩後背包或運動提袋 (嚴禁硬殼行李箱)", "must": True, "tip": "【記事本重要提醒】營區內務空間極小，黑大裝不下硬殼托運行李箱，入營務必使用普通後背包或運動圓筒包"}
        ]
    },
    {
        "id": "contraband",
        "name": "九、學長避坑：沒用物品、違禁品與新訓生存新心法 (含最新留言精華)",
        "is_danger": True,
        "items": [
            {"id": "no_marker", "name": "❌ 奇異筆 / 油性麥克筆（違禁品，會被沒入）", "tip": "公發文具包會發筆，私帶奇異筆常被列入管制", "is_danger": True},
            {"id": "no_dry_battery", "name": "❌ 可拆式乾電池（違禁品，會被沒入）", "tip": "嚴禁乾電池刮鬍刀或私帶電池生火點煙，只能帶手動或先充飽的鋰電款", "is_danger": True},
            {"id": "no_contacts", "name": "❌ 隱形眼鏡與角膜塑形片（環境髒易發炎）", "tip": "營區砂土灰塵多，洗手衛生不佳，極易造成角膜感染發炎，請戴傳統眼鏡", "is_danger": True},
            {"id": "no_sewing_kit", "name": "❌ 針線盒（不用買，公所與營區皆有贈送）", "tip": "兵役局或營區通常會直接發放小針線包", "is_danger": True},
            {"id": "no_laundry_bag", "name": "❌ 洗衣袋（不用買，公發直接發 3 個）", "tip": "公發洗衣袋印有專屬中隊分隊號碼，私帶無法送洗", "is_danger": True},
            {"id": "no_heel_pad", "name": "❌ 防磨腳跟貼（新款黑皮鞋不咬腳）", "tip": "新款皮鞋改良後柔軟不咬腳，幾乎用不到", "is_danger": True},
            {"id": "no_floss_picks", "name": "❌ 尖頭牙線棒 / 牙籤（尖端被列違禁品）", "tip": "尖銳物品容易被沒入，請自備捲軸式牙線", "is_danger": True},
            {"id": "ban_smoking", "name": "🚫 打火機、電子菸、加熱菸（點火設備一律沒入）", "tip": "營區全面禁菸，打火機與點火裝置安檢查獲一律沒入並從嚴處分", "is_danger": True},
            {"id": "ban_blades", "name": "🚫 美工刀、剪刀、水果刀等鋒利器具", "tip": "危險物品，安檢直接保管，指甲剪不可附尖銳銼刀", "is_danger": True},
            {"id": "ban_plugs", "name": "🚫 含有插頭的電器（豆腐頭收違禁袋）", "tip": "營區插座嚴格管制，含有插頭形式物品皆須集中保管", "is_danger": True},
            {"id": "ban_wireless", "name": "🚫 藍牙無線耳機、智慧手錶", "tip": "一律收貴重物品袋集中保管，只能用有線耳機與一般手錶", "is_danger": True},
            {"id": "ban_food", "name": "🚫 零食、含糖飲料、外食（未拆封喉糖除外）", "tip": "會招引蟲蟻，嚴重影響寢室內務考核", "is_danger": True},
            {"id": "ban_flashlight", "name": "🚫 手電筒（營區夜間禁用）", "tip": "營區熄燈後嚴禁使用手電筒，避免光害或違反就寢紀律，看時間請用微光手錶", "is_danger": True},
            {"id": "tip_exchange_gear", "name": "💡 【第一二天換全新裝備】：爛蚊帳、臭制服、鞋不合立刻去換！", "tip": "【Dcard 注意事項0】不用管別人眼光，第一天拿到破舊二手裝備立刻找幹部換，高機率換全新！", "is_danger": False},
            {"id": "tip_barber_avoid", "name": "💡 【髮婆理髮避坑】：入營前剃好，剪完千萬別在後面簽名！", "tip": "【Dcard 注意事項20】已剃光頭者剪完在旁邊等，不要去簽名名冊，簽名會被扣48元理髮費", "is_danger": False},
            {"id": "tip_score_bonus", "name": "💡 【爭取榮譽假】：抽血+2分、追蹤社群+2分，保底+4分！", "tip": "【Dcard 注意事項14】EMT上課多舉手回答、自願出公差，輕鬆累積點數拚「榮2」提早離營", "is_danger": False},
            {"id": "tip_blood_donation", "name": "💡 【捐血加分策略】：有捐血習慣者注意避開冷卻期！", "tip": "【Dcard 留言心得】入營前請算好捐血間隔時間，避免入營後剛好卡在捐血「冷卻期」無法抽血加分", "is_danger": False},
            {"id": "tip_mess_crew", "name": "💡 【打飯班是屎缺】：蒼蠅飛，排頭盡早抓交替！", "tip": "【Dcard 注意事項15】每餐打菜洗桶子很累且飯菜易引蒼蠅，排頭1~10號盡早安排輪替", "is_danger": False},
            {"id": "tip_mosquito_net", "name": "💡 【蚊帳一次折好法】：睡覺放空床，應付檢查不重折！", "tip": "【Dcard 留言心得】折好一次後睡覺將蚊帳移至空床或安全處，起床直接拿回床上，二樓蚊子較少", "is_danger": False},
            {"id": "tip_sick_call", "name": "💡 【生病看診與外診】：夜間看診拿轉診單可外出！", "tip": "【Dcard 留言心得】若真的不舒服建議在 EMT-1 課程結束後再去轉診，評估當天行程是否坐在教室吹冷氣更舒適", "is_danger": False},
            {"id": "tip_honor_cap", "name": "💡 【榮譽假上限現實】：榮6通常即為上限！", "tip": "【Dcard 留言心得】規定稱超過6小時榮譽假可補至後續階段，但實務上研替新訓通常榮6即封頂，不會再給", "is_danger": False}
        ]
    }
]

study_data['packing_list']['categories'] = all_categories
study_data['packing_list']['title'] = "成功嶺新訓必備用品建議檢核表 (2024-2026 最新梯次、Dcard實測與群組記事本管制全集)"
study_data['packing_list']['description'] = "完整整合 257T 考古文件、Dcard 277T/137研替好物分享與替代役群組記事本物品管制等級分類（重/中/輕度管制與准予自備規範）。"

# Save updated study_data.json
with open('data/study_data.json', 'w', encoding='utf-8') as f:
    json.dump(study_data, f, ensure_ascii=False, indent=2)

# Update data_bundle.js
bundle_content = f"""// Auto-generated data bundle for offline & GitHub Pages support
// Updated with complete Google Doc text, 2024-2026 legal standards, shooting chunk, and Dcard & group notebook checklist
window.APP_QUESTIONS = {json.dumps(questions_data, ensure_ascii=False)};
window.APP_STUDY_DATA = {json.dumps(study_data, ensure_ascii=False)};
"""

with open('data/data_bundle.js', 'w', encoding='utf-8') as f:
    f.write(bundle_content)

total_items = sum(len(c['items']) for c in all_categories)
print(f"Successfully updated study_data.json and data_bundle.js with {len(all_categories)} categories and {total_items} items!")
