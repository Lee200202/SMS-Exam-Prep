import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/gdoc1_full.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Load current study_data as base
with open('data/study_data.json', 'r', encoding='utf-8') as f:
    study_data = json.load(f)

with open('data/questions.json', 'r', encoding='utf-8') as f:
    questions_data = json.load(f)

# ----------------------------------------------------
# 1. Parse 替代役實施條例 全文 (Lines 1386 to 2158)
# ----------------------------------------------------
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
        curr_art = {'article': s, 'content': []}
        if curr_chap is None:
            curr_chap = {'chapter': '總則', 'articles': []}
            reg_chapters.append(curr_chap)
        curr_chap['articles'].append(curr_art)
    elif curr_art is not None:
        curr_art['content'].append(s)

study_data['regulations']['full_act'] = {
    'title': '《替代役實施條例》法規條文全文 (第1條至第63條)',
    'amend_date': '民國 110 年 01 月 27 日修正公布（現行法規最新標準）',
    'chapters': reg_chapters
}

# ----------------------------------------------------
# 2. Parse 志願服務法 全文 (Lines 2158 to 2382)
# ----------------------------------------------------
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
        curr_art = {'article': s, 'content': []}
        if curr_chap is None:
            curr_chap = {'chapter': '總則', 'articles': []}
            vol_chapters.append(curr_chap)
        curr_chap['articles'].append(curr_art)
    elif curr_art is not None:
        curr_art['content'].append(s)

study_data['volunteer']['full_act'] = {
    'title': '《志願服務法》法規條文全文 (第1條至第25條)',
    'amend_date': '民國 109 年 01 月 15 日修正公布（現行法規最新標準）',
    'chapters': vol_chapters
}

# ----------------------------------------------------
# 3. Parse 重點整理 (Lines 2382 to 2534)
# ----------------------------------------------------
key_lines = lines[2382:2534]
key_points_raw = [l.strip() for l in key_lines if l.strip() and l.strip() != '重點整理']
study_data['regulations']['key_points_full'] = {
    'title': '替代役新訓核心重點整理 (全文 52 條全錄與名詞定義)',
    'items': key_points_raw
}

# ----------------------------------------------------
# 4. Parse 權益部分 (Lines 2534 to 2654)
# ----------------------------------------------------
rights_lines = lines[2534:2654]
rights_points_raw = [l.strip() for l in rights_lines if l.strip() and l.strip() != '權益部分' and l.strip() != '________________']
study_data['rights_and_management']['rights_points_full'] = {
    'title': '役男法定權益保障重點全覽 (全文 53 條全錄)',
    'items': rights_points_raw
}

# ----------------------------------------------------
# 5. Parse 替代役訓練服勤管理部分 (Lines 2654 to 2756)
# ----------------------------------------------------
mgmt_lines = lines[2654:2756]
mgmt_points_raw = [l.strip() for l in mgmt_lines if l.strip() and l.strip() != '替代役訓練服勤管理部分' and l.strip() != '________________']
study_data['rights_and_management']['management_points_full'] = {
    'title': '替代役訓練與服勤管理法規重點全覽 (全文 40 條全錄)',
    'items': mgmt_points_raw
}

# ----------------------------------------------------
# 6. Parse 打靶訓練 (Lines 2756 to 2826)
# ----------------------------------------------------
shoot_lines = lines[2756:2826]
shoot_points_raw = [l.strip() for l in shoot_lines if l.strip() and l.strip() != '打靶訓練' and l.strip() != '________________']
study_data['shooting']['full_text'] = {
    'title': '成功嶺打靶射擊訓練全攻略與 257T 最新試題 (完整原文)',
    'items': shoot_points_raw
}

# ----------------------------------------------------
# 7. Parse 新訓用品建議檢核表 2024年8月 (Lines 2826 to 2975)
# ----------------------------------------------------
pack_lines = lines[2826:2975]
pack_points_raw = [l.strip() for l in pack_lines if l.strip() and l.strip() != '________________']
study_data['packing_list']['full_text'] = {
    'title': '新訓用品建議檢核表 2024年8月版 (完整原文條列與備註)',
    'items': pack_points_raw
}

# ----------------------------------------------------
# 8. Parse 註腳 [1] 至 [25] (Lines 2975 to 3059)
# ----------------------------------------------------
note_lines = lines[2975:]
note_items = []
current_note = None

for l in note_lines:
    s = l.strip()
    if not s or s == '________________':
        continue
    m = re.match(r'^\[(\d+)\]\s*(.*)', s)
    if m:
        current_note = {'num': int(m.group(1)), 'text': m.group(2)}
        note_items.append(current_note)
    elif current_note:
        current_note['text'] += ' ' + s
    else:
        # Pre-notes warnings (e.g. 沒用的東西, 防蚊液說明)
        note_items.append({'num': 0, 'text': s})

study_data['footnotes'] = {
    'title': '歷年新訓學科考題註腳與法規陷阱精解 [1] 至 [25] 全覽',
    'notes': note_items
}

# Save updated study_data.json
with open('data/study_data.json', 'w', encoding='utf-8') as f:
    json.dump(study_data, f, ensure_ascii=False, indent=2)

# Save updated bundle
bundle_content = f"""// Auto-generated data bundle for offline & GitHub Pages support
// Updated with complete Google Doc text, 2024-2026 legal standards and all 262 questions
window.APP_QUESTIONS = {json.dumps(questions_data, ensure_ascii=False)};
window.APP_STUDY_DATA = {json.dumps(study_data, ensure_ascii=False)};
"""

with open('data/data_bundle.js', 'w', encoding='utf-8') as f:
    f.write(bundle_content)

print("Successfully merged all Google Doc text and updated data_bundle.js!")
