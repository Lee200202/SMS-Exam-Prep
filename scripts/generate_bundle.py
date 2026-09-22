import json

with open("data/questions.json", "r", encoding="utf-8") as f:
    questions_data = json.load(f)

with open("data/study_data.json", "r", encoding="utf-8") as f:
    study_data = json.load(f)

bundle_content = f"""// Auto-generated data bundle for offline & GitHub Pages support
window.APP_QUESTIONS = {json.dumps(questions_data, ensure_ascii=False)};
window.APP_STUDY_DATA = {json.dumps(study_data, ensure_ascii=False)};
"""

with open("data/data_bundle.js", "w", encoding="utf-8") as f:
    f.write(bundle_content)

print("Generated data/data_bundle.js successfully!")
