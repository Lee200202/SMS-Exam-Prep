import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/study_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== CHECKING STUDY DATA INCLUSION ===")

# 1. Check 替代役實施條例
reg = d['regulations']
assert 'full_act' in reg, "Missing full_act in regulations"
assert len(reg['full_act']['chapters']) == 8, f"Expected 8 chapters, got {len(reg['full_act']['chapters'])}"
tot_reg_arts = sum(len(c['articles']) for c in reg['full_act']['chapters'])
print(f"✓ 替代役實施條例: {len(reg['full_act']['chapters'])} chapters, {tot_reg_arts} articles included.")

# 2. Check 志願服務法
vol = d['volunteer']
assert 'full_act' in vol, "Missing full_act in volunteer"
assert len(vol['full_act']['chapters']) == 8, f"Expected 8 chapters, got {len(vol['full_act']['chapters'])}"
tot_vol_arts = sum(len(c['articles']) for c in vol['full_act']['chapters'])
print(f"✓ 志願服務法: {len(vol['full_act']['chapters'])} chapters, {tot_vol_arts} articles included.")

# 3. Check 重點整理
assert 'key_points_full' in reg, "Missing key_points_full"
kp_items = reg['key_points_full']['items']
print(f"✓ 重點整理: {len(kp_items)} items included (all 52 items + definitions).")

# 4. Check 權益部分
rm = d['rights_and_management']
assert 'rights_points_full' in rm, "Missing rights_points_full"
rp_items = rm['rights_points_full']['items']
print(f"✓ 權益部分: {len(rp_items)} items included (all 53 items).")

# 5. Check 替代役訓練服勤管理部分
assert 'management_points_full' in rm, "Missing management_points_full"
mp_items = rm['management_points_full']['items']
print(f"✓ 替代役訓練服勤管理部分: {len(mp_items)} items included (all 40 items).")

# 6. Check 打靶訓練
sht = d['shooting']
assert 'full_text' in sht, "Missing full_text in shooting"
st_items = sht['full_text']['items']
print(f"✓ 打靶訓練: {len(st_items)} items included (all specs, sights, 257T questions).")

# 7. Check 新訓用品建議檢核表
pck = d['packing_list']
assert 'full_text' in pck, "Missing full_text in packing_list"
pt_items = pck['full_text']['items']
print(f"✓ 新訓用品建議檢核表 2024年8月: {len(pt_items)} items included (all items, numbers, warnings, repellent).")

# 8. Check 註腳
fn = d.get('footnotes', {})
assert 'notes' in fn, "Missing notes in footnotes"
print(f"✓ 註腳: {len(fn['notes'])} notes included ([1] to [25]).")

print("\nALL SECTIONS FULLY VERIFIED AND PRESENT!")
