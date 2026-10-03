# -*- coding: utf-8 -*-
"""
把 data/*.json 打包成前端直接載入的 JS 檔。

- data/data_bundle.js：題庫與講義（首頁就會載入）
- data/laws_bundle.js：法規全文（進入「法規全文」頁才載入）

修改任何 data/*.json 之後都要重跑：python scripts/generate_bundle.py
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


def dump(value):
    # </script 不會出現在資料裡，但仍跳脫 "</" 以防萬一
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def write(name, lines):
    path = os.path.join(ROOT, "data", name)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("// 由 scripts/generate_bundle.py 產生，請勿手動編輯\n")
        f.write("\n".join(lines) + "\n")
    print("%s %.0f KB" % (name, os.path.getsize(path) / 1024))


write("data_bundle.js", [
    "window.APP_QUESTIONS = %s;" % dump(load("questions.json")),
    "window.APP_STUDY_DATA = %s;" % dump(load("study_data.json")),
    "window.APP_EMT_QUESTIONS = %s;" % dump(load("emt_questions.json")),
    "window.APP_EMT_STUDY_DATA = %s;" % dump(load("emt_study_data.json")),
])
write("laws_bundle.js", ["window.APP_LAWS = %s;" % dump(load("laws.json"))])
