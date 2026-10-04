# -*- coding: utf-8 -*-
"""
把 data/*.json 打包成前端直接載入的 JS 檔。

- data/data_bundle.js：題庫與講義（首頁就會載入）
- data/laws_index.js：法規清單（名稱、日期、條數、附件清單；進入「法規全文」頁才載入）
- data/laws/<pcode>.js：單一法規的全文與附件文字（展開或搜尋時才載入）

修改任何 data/*.json 之後都要重跑：python scripts/generate_bundle.py
"""
import glob
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = "// 由 scripts/generate_bundle.py 產生，請勿手動編輯\n"


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def dump(value):
    # </script 不會出現在資料裡，但仍跳脫 "</" 以防萬一
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def write(name, body):
    path = os.path.join(ROOT, "data", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for attempt in range(6):
        try:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(HEADER + body + "\n")
            break
        except OSError:
            # Windows 上檔案被防毒或預覽程式暫時鎖住時會寫入失敗，稍等再試
            if attempt == 5:
                raise
            time.sleep(1.5)
    return os.path.getsize(path)


def main():
    size = write("data_bundle.js", "\n".join([
        "window.APP_QUESTIONS = %s;" % dump(load("questions.json")),
        "window.APP_STUDY_DATA = %s;" % dump(load("study_data.json")),
        "window.APP_EMT_QUESTIONS = %s;" % dump(load("emt_questions.json")),
        "window.APP_EMT_STUDY_DATA = %s;" % dump(load("emt_study_data.json")),
    ]))
    print("data_bundle.js %.0f KB" % (size / 1024))

    laws = load("laws.json")
    for stale in glob.glob(os.path.join(ROOT, "data", "laws", "*.js")):
        os.remove(stale)
    index = {"source": laws["source"], "fetched_at": laws["fetched_at"], "laws": []}
    total = 0
    for law in laws["laws"]:
        index["laws"].append({
            "pcode": law["pcode"], "group": law["group"], "name": law["name"],
            "date_label": law["date_label"], "date": law["date"], "url": law["url"],
            "article_count": law["article_count"],
            # 清單只放附件的名稱與狀態，擷取出的文字留在各法規檔案
            "attachments": [{k: a.get(k) for k in ("file_id", "name", "format", "url", "fetched", "pages")}
                            for a in law.get("attachments", [])],
        })
        total += write("laws/%s.js" % law["pcode"],
                       "(window.APP_LAW_DATA = window.APP_LAW_DATA || {})[%s] = %s;" % (json.dumps(law["pcode"]), dump(law)))
    size = write("laws_index.js", "window.APP_LAWS_INDEX = %s;" % dump(index))
    print("laws_index.js %.0f KB；laws/ %d 部共 %.0f KB" % (size / 1024, len(laws["laws"]), total / 1024))
    old = os.path.join(ROOT, "data", "laws_bundle.js")
    if os.path.exists(old):
        os.remove(old)  # 舊版單一檔案，已改為按法規分檔


if __name__ == "__main__":
    main()
