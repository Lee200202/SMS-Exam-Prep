# -*- coding: utf-8 -*-
"""
一次重建所有由 data/*.json 衍生的檔案，確保網站、PDF 與稽核表用的是同一份資料。

順序：套用逐題查核 → 資料包 → 三份 PDF → 寫入 pdf/manifest.json → 資料檢查。
任何一步失敗就停止。

用法：python scripts/build_all.py
（要先更新法規條文時，先跑 python scripts/fetch_laws.py）
"""
import datetime
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = [
    "apply_review_2026_10.py",
    "generate_bundle.py",
    "generate_pdf_bank.py",
    "generate_emt_pdf.py",
    "generate_checklist_pdf.py",
]


def run(script):
    print("==>", script)
    result = subprocess.run([sys.executable, os.path.join("scripts", script)], cwd=ROOT)
    if result.returncode != 0:
        sys.exit("%s 失敗，已停止" % script)


def digest(name):
    with open(os.path.join(ROOT, "data", name), "rb") as f:
        return hashlib.sha1(f.read().replace(b"\r\n", b"\n")).hexdigest()


def main():
    for script in STEPS:
        run(script)
    manifest = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "sources": {name: digest(name) for name in ("questions.json", "emt_questions.json", "study_data.json")},
    }
    with open(os.path.join(ROOT, "pdf", "manifest.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    run("validate_data.py")
    print("全部完成。接著請執行 python scripts/test_app.py")


if __name__ == "__main__":
    main()
