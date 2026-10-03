# -*- coding: utf-8 -*-
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open("data/study_data.json", "r", encoding="utf-8") as f:
    d = json.load(f)

pack = d["packing_list"]
print(f"Categories count: {len(pack['categories'])}")

existing_item_names = set()
for cat in pack["categories"]:
    print(f"\n[{cat['id']}] {cat['name']} ({len(cat['items'])} items)")
    for it in cat["items"]:
        existing_item_names.add(it["name"].strip())
        print(f"  - {it['id']}: {it['name']} -> {it.get('tip', '')[:60]}")

# Check full_text items
if "full_text" in pack:
    print(f"\n--- full_text items ({len(pack['full_text']['items'])}) ---")
    for line in pack["full_text"]["items"]:
        print("RAW:", line)
