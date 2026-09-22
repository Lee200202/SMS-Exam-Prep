import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/gdoc1_full.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()

# Boundaries:
# 1386: 替代役實施條例
# 2158: 志願服務法
# 2382: 重點整理
# 2534: 權益部分
# 2654: 替代役訓練服勤管理部分
# 2756: 打靶訓練
# 2826: 新訓用品建議檢核表 2024年8月
# 2975: 註腳及備註

# 1. Parse 替代役實施條例
reg_lines = lines[1386:2158]
reg_chapters = []
curr_chap = None
curr_art = None

for line in reg_lines:
    s = line.strip()
    if not s:
        continue
    if s.startswith('第') and '章' in s:
        curr_chap = {'chapter': s, 'articles': []}
        reg_chapters.append(curr_chap)
        curr_art = None
    elif s.startswith('第') and '條' in s:
        curr_art = {'article': s, 'text': []}
        if curr_chap is None:
            curr_chap = {'chapter': '前言', 'articles': []}
            reg_chapters.append(curr_chap)
        curr_chap['articles'].append(curr_art)
    elif curr_art is not None:
        curr_art['text'].append(s)

print(f"替代役實施條例 chapters parsed: {len(reg_chapters)}")
tot_arts = sum(len(c['articles']) for c in reg_chapters)
print(f"Total articles parsed: {tot_arts}")

# 2. Parse 志願服務法
vol_lines = lines[2158:2382]
vol_chapters = []
curr_chap = None
curr_art = None

for line in vol_lines:
    s = line.strip()
    if not s:
        continue
    if s.startswith('第') and '章' in s:
        curr_chap = {'chapter': s, 'articles': []}
        vol_chapters.append(curr_chap)
        curr_art = None
    elif s.startswith('第') and '條' in s:
        curr_art = {'article': s, 'text': []}
        if curr_chap is None:
            curr_chap = {'chapter': '總則', 'articles': []}
            vol_chapters.append(curr_chap)
        curr_chap['articles'].append(curr_art)
    elif curr_art is not None:
        curr_art['text'].append(s)

print(f"志願服務法 chapters parsed: {len(vol_chapters)}")
tot_vol_arts = sum(len(c['articles']) for c in vol_chapters)
print(f"Total volunteer articles parsed: {tot_vol_arts}")

# 3. Parse 重點整理
key_lines = lines[2382:2534]
key_points = [l.strip() for l in key_lines if l.strip() and l.strip() != '重點整理']
print(f"重點整理 non-empty lines: {len(key_points)}")

# 4. Parse 權益部分
rights_lines = lines[2534:2654]
rights_points = [l.strip() for l in rights_lines if l.strip() and l.strip() != '權益部分' and l.strip() != '________________']
print(f"權益部分 non-empty lines: {len(rights_points)}")

# 5. Parse 替代役訓練服勤管理部分
mgmt_lines = lines[2654:2756]
mgmt_points = [l.strip() for l in mgmt_lines if l.strip() and l.strip() != '替代役訓練服勤管理部分' and l.strip() != '________________']
print(f"替代役訓練服勤管理部分 non-empty lines: {len(mgmt_points)}")

# 6. Parse 打靶訓練
shoot_lines = lines[2756:2826]
shoot_points = [l.strip() for l in shoot_lines if l.strip() and l.strip() != '打靶訓練' and l.strip() != '________________']
print(f"打靶訓練 non-empty lines: {len(shoot_points)}")

# 7. Parse 新訓用品建議檢核表 2024年8月
pack_lines = lines[2826:2975]
pack_points = [l.strip() for l in pack_lines if l.strip() and l.strip() != '________________']
print(f"新訓用品建議檢核表 non-empty lines: {len(pack_points)}")

# 8. Parse 註腳
note_lines = lines[2975:]
notes_clean = [l.strip() for l in note_lines if l.strip() and l.strip() != '________________']
print(f"註腳及備註 non-empty lines: {len(notes_clean)}")
