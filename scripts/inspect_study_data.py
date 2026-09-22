import json

with open('data/study_data.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

for k, v in d.items():
    if isinstance(v, dict):
        print(f"=== {k} ===")
        for sub_k, sub_v in v.items():
            if sub_k == 'sections':
                print(f"  sections: {len(sub_v)}")
                for sec in sub_v:
                    print(f"    * {sec.get('title', '')}")
                    if 'content' in sec:
                        print(f"      content lines: {len(sec['content'])}")
                    if 'table' in sec:
                        print(f"      table rows: {len(sec['table'].get('rows', []))}")
                    if 'items' in sec:
                        print(f"      items: {len(sec['items'])}")
            elif sub_k == 'categories':
                print(f"  categories: {len(sub_v)}")
                for cat in sub_v:
                    print(f"    * {cat.get('name', '')}: {len(cat.get('items', []))} items")
            elif isinstance(sub_v, list):
                print(f"  {sub_k}: list with {len(sub_v)} items")
            elif isinstance(sub_v, dict):
                print(f"  {sub_k}: dict with keys {list(sub_v.keys())}")
            else:
                print(f"  {sub_k}: {type(sub_v).__name__}")
