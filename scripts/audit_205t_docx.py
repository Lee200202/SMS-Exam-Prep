"""Index the 205T recollection DOCX against the site's new-recruit questions.

This is a mechanical candidate search, not a ruling that two questions are the
same or that the 2019 answer remains correct. The output deliberately omits
the third-party question text; reviewers should read the original document.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


WORD = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraphs(path: Path) -> list[str]:
    with ZipFile(path) as docx:
        root = ET.fromstring(docx.read("word/document.xml"))
    return [
        text
        for node in root.iter(WORD + "p")
        if (text := "".join(part.text or "" for part in node.iter(WORD + "t")).strip())
    ]


def normalize(text: str, *, multiple_choice: bool = False) -> str:
    if multiple_choice:
        text = re.split(r"\s*[（(]1[)）]", text, maxsplit=1)[0]
    return "".join(ch for ch in text if ch.isalnum()).casefold()


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python scripts/audit_205t_docx.py SOURCE.docx OUTPUT.csv")
    source, output = map(Path, sys.argv[1:])
    lines = paragraphs(source)
    try:
        true_false_start = next(i for i, line in enumerate(lines) if line.startswith("壹、是非題")) + 1
        multiple_choice_start = next(i for i, line in enumerate(lines) if line.startswith("貳、選擇題"))
    except StopIteration as exc:
        raise ValueError("205T document headings were not found") from exc
    true_false = lines[true_false_start:multiple_choice_start]
    multiple_choice = lines[multiple_choice_start + 1 :]
    if len(true_false) != 25 or len(multiple_choice) != 25:
        raise ValueError(f"Expected 25+25 questions; got {len(true_false)}+{len(multiple_choice)}")

    bank = json.loads(Path("data/questions.json").read_text(encoding="utf-8"))["questions"]
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "205T題型",
                "205T卷內題號",
                "來源文字SHA256前12碼",
                "來源前12字定位",
                "網站候選1",
                "相似度1",
                "網站候選2",
                "相似度2",
                "網站候選3",
                "相似度3",
                "裁定",
                "現行法核對",
            ]
        )
        for kind, questions in (("是非", true_false), ("選擇", multiple_choice)):
            for number, question in enumerate(questions, 1):
                key = normalize(question, multiple_choice=kind == "選擇")
                scores = sorted(
                    (
                        (SequenceMatcher(None, key, normalize(item["question"])).ratio(), item["id"])
                        for item in bank
                        if item["id"].startswith("TF") == (kind == "是非")
                    ),
                    reverse=True,
                )[:3]
                writer.writerow(
                    [
                        kind,
                        number,
                        hashlib.sha256(question.encode("utf-8")).hexdigest()[:12],
                        question[:12],
                        scores[0][1],
                        f"{scores[0][0]:.3f}",
                        scores[1][1],
                        f"{scores[1][0]:.3f}",
                        scores[2][1],
                        f"{scores[2][0]:.3f}",
                        "待人工逐句對照；相似度不是來源核定",
                        "未核；原作者未附解答",
                    ]
                )
    print(f"indexed {len(true_false)} true/false and {len(multiple_choice)} multiple choice questions")


if __name__ == "__main__":
    main()
