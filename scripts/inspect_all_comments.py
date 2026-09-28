import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/all_dcard_comments.json', 'r', encoding='utf-8') as f:
    comments = json.load(f)

print(f"Total entries: {len(comments)}")
with open('data/all_comments_formatted.txt', 'w', encoding='utf-8') as out:
    for c in comments:
        if c['type'] == 'root':
            out.write(f"\n==========================================\n")
            out.write(f"B{c['floor']} [{c['id']}] ({c.get('school', '')}):\n")
            out.write(f"{c['content']}\n")
        else:
            out.write(f"   ↳ B{c['parentFloor']}-{c['floor']} [{c['id']}] ({c.get('school', '')}):\n")
            out.write(f"     {c['content']}\n")
print("Saved data/all_comments_formatted.txt")

