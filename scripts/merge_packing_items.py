# -*- coding: utf-8 -*-
"""
Merge Google Doc 2024-08 packing checklist items into structured categories,
enrich tips/quantities/legal repellent details, and remove the raw full_text block.
"""
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open("data/study_data.json", "r", encoding="utf-8") as f:
    study_data = json.load(f)

pack = study_data["packing_list"]

# 1. Update/Enrich items in categories
# Category 1: documents
doc_cat = next((c for c in pack["categories"] if c["id"] == "documents"), None)
if doc_cat:
    # Check if doc_memo or other doc items exist
    doc_ids = {it["id"]: it for it in doc_cat["items"]}
    if "doc_exam_notes" in doc_ids:
        doc_ids["doc_exam_notes"]["tip"] = "【高分必備】印成一張一張的，大餐課或零碎時間背誦，手機管制時的刷題奪高分神器"
    if "doc_specialty" in doc_ids:
        doc_ids["doc_specialty"]["tip"] = "專長證照、英文/外語檢定證明、COVID-19/疫苗證明、各類證書，選役別大利多"

# Category 2: identities
id_cat = next((c for c in pack["categories"] if c["id"] == "identities"), None)
if id_cat:
    id_items = {it["id"]: it for it in id_cat["items"]}
    if "cash_plan" in id_items:
        id_items["cash_plan"]["name"] = "現金 2,500 ~ 3,000 元 (含百元鈔與零錢)"
        id_items["cash_plan"]["tip"] = "【257T需要收約800元現金雜費】(照相、洗衣、理髮等)，準備500元1張+100元15~20張，零錢高機率用不到但可備少量投飲料，多餘大鈔放皮夾"
    if "keys" not in id_items:
        id_cat["items"].append({
            "id": "keys",
            "name": "家裡鑰匙",
            "must": True,
            "tip": "結訓放假離營回家必備，收進防水零錢包放貴重物品袋避免散落"
        })
    if "credit_card" in id_items:
        id_items["credit_card"]["name"] = "提款卡、悠遊卡 / 信用卡"
        id_items["credit_card"]["tip"] = "結訓放假搭乘高鐵/台鐵/客運購票返家備用，可收進防水零錢包放貴重袋"
    if "coin_pouch" in id_items:
        id_items["coin_pouch"]["name"] = "防水零錢包"
        id_items["coin_pouch"]["tip"] = "裝多的紙鈔、零錢、提款卡、鑰匙等，放進貴重物品袋避免散落"
    if "wired_earphones" in id_items:
        id_items["wired_earphones"]["name"] = "有線耳機 (3.5mm / Type-C)"
        id_items["wired_earphones"]["tip"] = "放風時間通話聽語音必備；【重點：無線藍牙耳機是違禁品，會被沒入集中保管】"
    if "plug_adapter" not in id_items:
        id_cat["items"].append({
            "id": "plug_adapter",
            "name": "豆腐頭 / 充電器插頭",
            "must": False,
            "tip": "【專訓高機率會用到】新訓期間入營安檢集中於違禁品袋保管，專訓下單位時即可使用"
        })

# Category 3: god_tier_items (生活實用、收納神器與衛生好物)
god_cat = next((c for c in pack["categories"] if c["id"] == "god_tier_items"), None)
if god_cat:
    god_items = {it["id"]: it for it in god_cat["items"]}
    if "three_plastic_bags" not in god_items:
        god_cat["items"].append({
            "id": "three_plastic_bags",
            "name": "塑膠袋 x 3 (貴重、違禁、藥品)",
            "must": True,
            "tip": "【入營當天必備】分為「貴重物品袋」、「違禁品袋」、「藥品袋」第一天安檢裝袋必備；亦可多備大塑膠袋裝髒衣服防臭"
        })

# Category 4: toiletries_med (生活盥洗、個人藥品與日常消耗品)
toilet_cat = next((c for c in pack["categories"] if c["id"] == "toiletries_med"), None)
if toilet_cat:
    toilet_items = {it["id"]: it for it in toilet_cat["items"]}
    if "two_toothbrushes" in toilet_items:
        toilet_items["two_toothbrushes"]["name"] = "牙刷 (要能平躺) & 牙膏"
        toilet_items["two_toothbrushes"]["tip"] = "【重點：牙刷要能平躺！】臉盆檢查刷柄底部需平坦或不易滾動款式，刷毛朝上；牙膏選一般尺寸即可"
    if "three_in_one_soap" in toilet_items:
        toilet_items["three_in_one_soap"]["name"] = "三合一沐浴乳 (洗髮/沐浴/洗臉)"
        toilet_items["three_in_one_soap"]["tip"] = "洗澡時間緊迫，推薦好起泡、好沖洗款式，洗頭洗臉洗身體一罐搞定"
    if "box_tissues" in toilet_items:
        toilet_items["box_tissues"]["name"] = "抽取式衛生紙 x 2~3 包"
        toilet_items["box_tissues"]["tip"] = "【自用 + 檢查有一包絕對不能拆封！】營區內務檢查床頭衛生紙需方正未開封，另一包或搭配袖珍包自用"
    if "pocket_tissues" in toilet_items:
        toilet_items["pocket_tissues"]["name"] = "袖珍包衛生紙 15~20 包"
        toilet_items["pocket_tissues"]["tip"] = "成功嶺廁所通常無衛生紙，買大組隨身攜帶，操課擦汗、如廁必備"
    if "mosquito_roll" in toilet_items:
        toilet_items["mosquito_roll"]["name"] = "防蚊液 1~2 瓶 (【重點：不可使用噴霧型！】)"
        toilet_items["mosquito_roll"]["tip"] = "【防蚊液法定有效成分詳細說明】必須含有法定有效成分：敵避 (DEET)、派卡瑞丁 (Picaridin，比較不刺激皮膚，買12小時版本，乳液最好用)、IR3535 (伊默寧)。成功嶺小黑蚊極兇，可帶兩瓶，會用完；【嚴禁按壓噴霧式氣體瓶】！"
    if "itch_cream" in toilet_items:
        toilet_items["itch_cream"]["name"] = "止癢涼感藥品 / 外用藥膏"
        toilet_items["itch_cream"]["tip"] = "被蚊蟲跳蚤叮咬立即塗抹消腫止癢，綠油精、白花油、小護士、曼秀雷敦皆可"
    if "throat_drops_pink" not in toilet_items:
        toilet_items["throat_drops_pink"] = {
            "id": "throat_drops_pink",
            "name": "喉糖 (【未開封】)",
            "must": True,
            "tip": "【入營檢查前切勿拆封！】軍中唯一合法合規的零嘴與開嗓聖品，喊口號喉嚨沙啞必備，京都念慈菴或利口樂未開封鐵盒"
        }
        toilet_cat["items"].append(toilet_items["throat_drops_pink"])
    if "dental_floss" in toilet_items:
        toilet_items["dental_floss"]["name"] = "牙線 (捲軸式)"
        toilet_items["dental_floss"]["tip"] = "【注意：尖頭牙線棒容易被列為尖銳違禁品沒入】，捲軸式牙線最安全合規"
    if "deodorant" not in toilet_items:
        toilet_cat["items"].append({
            "id": "deodorant",
            "name": "止汗劑",
            "must": False,
            "tip": "大出汗體味較重者必備，滾珠式止汗劑維持身體清爽"
        })
    if "mask_ear_protector" in toilet_items:
        toilet_items["mask_ear_protector"]["name"] = "口罩 (藍色醫療口罩) + 口罩減壓帶"
        toilet_items["mask_ear_protector"]["tip"] = "全天長時間佩戴，藍色醫療口罩多備幾片，搭配減壓帶雙耳不痛"

# Category 5: stationery_drill (文具、休閒讀物與內務整理小工具)
stat_cat = next((c for c in pack["categories"] if c["id"] == "stationery_drill"), None)
if stat_cat:
    stat_items = {it["id"]: it for it in stat_cat["items"]}
    if "stationery_pens" not in stat_items:
        stat_cat["items"].insert(0, {
            "id": "stationery_pens",
            "name": "文具筆類 (公發有藍筆*2 + 紅筆*1)",
            "must": False,
            "tip": "公發會發藍筆x2與紅筆x1；可自備黑/藍原子筆、擦擦筆，填寫大兵手記與資料"
        })
    if "binder_clips" in stat_items:
        stat_items["binder_clips"]["name"] = "長尾夾 4~6 個 (內務整理用)"
        stat_items["binder_clips"]["tip"] = "折蚊帳與棉被神物！夾住邊角定型，平整挺拔不扣分"
    if "books" not in stat_items:
        stat_cat["items"].append({
            "id": "books",
            "name": "休閒讀物 (印成一張一張的)",
            "must": False,
            "tip": "小說、雜誌、文章、佛經等，必須印成一張一張的單張紙，不可整本帶進；印製撲克牌不能剪開"
        })

# Category 6: commissary_buy (營站採買推薦物品與公發耗材補充)
comm_cat = next((c for c in pack["categories"] if c["id"] == "commissary_buy"), None)
if comm_cat:
    comm_items = {it["id"]: it for it in comm_cat["items"]}
    if "undershirt_buy" in comm_items:
        comm_items["undershirt_buy"]["name"] = "純白短袖排汗內衣 (公發 3 件，可買 1~2 件)"
        comm_items["undershirt_buy"]["tip"] = "夏天流汗量極大，多買 1~2 件備用替換，晨跑後換穿清爽舒適"
    if "boxers_buy" in comm_items:
        comm_items["boxers_buy"]["name"] = "內褲 (公發 2 件，可買 1~2 件)"
        comm_items["boxers_buy"]["tip"] = "公發內褲通常較不合身不好穿，建議可自備或在營站多買 1~2 件合身四角褲"
    if "socks_buy" in comm_items:
        comm_items["socks_buy"]["name"] = "黑色中筒軍襪 (公發 2 雙，可買 1~2 雙)"
        comm_items["socks_buy"]["tip"] = "行軍與跑步易磨損流汗，多買 1~2 雙備用替換"
    if "towel_buy" in comm_items:
        comm_items["towel_buy"]["name"] = "純白毛巾 (公發 2 條，可買 1 條)"
        comm_items["towel_buy"]["tip"] = "公發毛巾需掛床頭供內務檢查不能動，多買 1 條自用洗澡洗臉"
    if "earplugs_helmet_pad" in comm_items:
        # Separate into earplugs and helmet sponge
        comm_items["earplugs_helmet_pad"]["name"] = "耳塞 (打靶用，當天也會發)"
        comm_items["earplugs_helmet_pad"]["tip"] = "打靶防噪音保護聽力，打靶當天也會發，亦可自備一副備用"
        if "helmet_sponge" not in comm_items:
            comm_cat["items"].append({
                "id": "helmet_sponge",
                "name": "鋼盔海綿墊 (打靶用)",
                "must": False,
                "tip": "打靶與防護演練戴鋼盔時墊在頭頂減壓吸汗，避免鋼盔晃動磨頭"
            })
    if "spare_clothes" not in comm_items:
        comm_cat["items"].append({
            "id": "spare_clothes",
            "name": "休假時穿的衣服一套、帽子",
            "must": True,
            "tip": "放假離營時換穿便服，入營時折整齊收進黑色大行李袋（黑大）底層"
        })

# Category 8: contraband (學長避坑：沒用物品 (避坑防雷)、違禁品與新訓生存新心法)
contra_cat = next((c for c in pack["categories"] if c["id"] == "contraband"), None)
if contra_cat:
    contra_items = {it["id"]: it for it in contra_cat["items"]}
    if "no_marker" in contra_items:
        contra_items["no_marker"]["name"] = "❌ 奇異筆 / 油性麥克筆（違禁品，不用買）"
        contra_items["no_marker"]["tip"] = "【避坑防雷】公發文具包會發原子筆，私帶奇異筆常被列入違禁品沒入"
    if "no_sewing_kit" in contra_items:
        contra_items["no_sewing_kit"]["name"] = "❌ 針線盒（不用買，257T有送）"
        contra_items["no_sewing_kit"]["tip"] = "【避坑防雷】兵役局行前說明會或營區 257T 皆會贈送小針線包，不用花錢買"
    if "no_laundry_bag" in contra_items:
        contra_items["no_laundry_bag"]["name"] = "❌ 洗衣袋（不用買，公發直接發 3 個）"
        contra_items["no_laundry_bag"]["tip"] = "【避坑防雷】公發洗衣袋印有專屬中隊分隊號碼，私帶無法送洗，完全不用買"
    if "no_heel_pad" in contra_items:
        contra_items["no_heel_pad"]["name"] = "❌ 防磨腳跟貼（257T換新款皮鞋不會磨腳）"
        contra_items["no_heel_pad"]["tip"] = "【避坑防雷】257T 已全面換裝新款柔軟黑皮鞋，不會咬腳磨腳，幾乎用不到"
    if "ban_rule_note" not in contra_items:
        contra_cat["items"].insert(0, {
            "id": "ban_rule_note",
            "name": "💡 【違禁品處理原則：想帶還是可以帶】",
            "must": False,
            "tip": "違禁品第一天入營安檢判斷，之後會統一收起來保管，結訓離營前全數發還，不用過度恐慌",
            "is_danger": False
        })
    if "no_spray_repellent" not in contra_items:
        contra_cat["items"].append({
            "id": "no_spray_repellent",
            "name": "❌ 噴霧式防蚊液 / 壓力氣體瓶（嚴格禁用）",
            "must": False,
            "tip": "【違禁品提醒】有氣體噴霧與易燃風險一律沒入，防蚊液請務必挑選滾珠液態或乳液款",
            "is_danger": True
        })

# Remove full_text from packing_list
if "full_text" in pack:
    del pack["full_text"]
    print("Removed redundant full_text block from packing_list!")

# Save updated study_data.json
with open("data/study_data.json", "w", encoding="utf-8") as f:
    json.dump(study_data, f, ensure_ascii=False, indent=2)

print("Successfully merged all 2024-08 items and enriched study_data.json!")
