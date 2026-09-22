import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

with open('data/gdoc1_full.txt', 'r', encoding='utf-8') as f:
    text = f.read()

lines = text.splitlines()

print(f"Total lines in gdoc1: {len(lines)}")

# Locate sections
indices = {}
for i, line in enumerate(lines):
    s = line.strip()
    if s == '替代役實施條例' and i > 500:
        if 'regulations_act' not in indices:
            indices['regulations_act'] = i
    elif s == '志願服務法' and i > 1500:
        if 'volunteer_act' not in indices:
            indices['volunteer_act'] = i
    elif s == '重點整理' and i > 2000:
        if 'key_points' not in indices:
            indices['key_points'] = i
    elif s == '權益部分' and i > 2300:
        if 'rights' not in indices:
            indices['rights'] = i
    elif s == '替代役訓練服勤管理部分' and i > 2500:
        if 'management' not in indices:
            indices['management'] = i
    elif s == '打靶訓練' and i > 2600:
        if 'shooting' not in indices:
            indices['shooting'] = i
    elif s.startswith('新訓用品建議檢核表') and i > 2700:
        if 'packing' not in indices:
            indices['packing'] = i

print("Found section indices:", indices)
