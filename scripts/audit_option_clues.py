"""Audit answer clues and option origin across the four public question banks."""
import csv
import json
import re
from pathlib import Path
from build_provenance import norm, parse_source

ROOT = Path(__file__).resolve().parent.parent
PREFIX = re.compile(r"^\s*[（(][A-Ea-e][）)]\s*")
ENGLISH = re.compile(r"[A-Za-z]{2,}")
ORIGINAL = {("是非" if item["kind"] == "TF" else "選擇") + f' {item["no"]}': item
            for item in parse_source()}


def clean(value):
    return PREFIX.sub("", value).strip()


def items():
    for bank, name in (
        ("新訓", "questions.json"),
        ("EMT來源", "emt_questions.json"),
        ("EMT自編", "emt_practice_questions.json"),
    ):
        data = json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))
        for q in data["questions"]:
            if q["type"] != "multiple_choice":
                continue
            p = q.get("provenance", {})
            origin = p.get("class", "site_authored" if bank == "EMT自編" else "unknown")
            options = [clean(s) for s in q["options"]]
            original = ORIGINAL.get(p.get("source_item", "")) if bank == "新訓" and p.get("source_id") == "R01" else None
            if original and original["options"]:
                source_compare = "逐字" if [norm(s) for s in options] == [norm(s) for s in original["options"]] else "後製改寫"
            elif p.get("options_by") == "source":
                source_compare = "來源轉錄"
            else:
                source_compare = "自編或未有逐字選項"
            answer = q["answer"]
            sizes = [len(re.sub(r"\s", "", s)) for s in options]
            order = sorted(sizes, reverse=True)
            longest = sizes[answer] == order[0] and (len(order) == 1 or order[0] > order[1])
            english = [bool(ENGLISH.search(s)) for s in options]
            sole_english = english[answer] and sum(english) == 1
            prefix_count = sum(bool(PREFIX.match(s)) for s in q["options"])
            yield {
                "bank": bank, "id": q["id"], "origin": origin,
                "options_by": p.get("options_by", ""), "source_compare": source_compare,
                "answer": "ABCDE"[answer],
                "lengths": "/".join(map(str, sizes)),
                "longest_gap": sizes[answer] - order[1] if longest else 0,
                "unique_longest": int(longest), "sole_english_answer": int(sole_english),
                "prefixed_options": prefix_count,
                "question": q["question"],
                "options": " ／ ".join(options),
            }


def main():
    rows = list(items())
    path = ROOT / "docs" / "選項線索逐題稽核_2026-10-04.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for bank in dict.fromkeys(r["bank"] for r in rows):
        group = [r for r in rows if r["bank"] == bank]
        print(bank, len(group), "唯一最長", sum(r["unique_longest"] for r in group),
              "唯一英文正解", sum(r["sole_english_answer"] for r in group),
              "原資料有選項標號", sum(bool(r["prefixed_options"]) for r in group))
    print(path)


if __name__ == "__main__":
    main()
