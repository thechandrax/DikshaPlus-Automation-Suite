import json
import glob
import re

def normalize_text(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("\u201b", "'")
    text = text.replace("“", '"').replace("”", '"').replace("„", '"')
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("–", "-").replace("—", "-").replace("\u2013", "-").replace("\u2014", "-")
    text = text.replace("\u00a0", " ")
    return re.sub(r'\s+', ' ', text).strip()

def clean_dict_or_list(obj):
    if isinstance(obj, dict):
        return {k: clean_dict_or_list(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_dict_or_list(elem) for elem in obj]
    elif isinstance(obj, str):
        return normalize_text(obj)
    return obj

files = glob.glob("data/**/*.json", recursive=True)
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as file:
            data = json.load(file)
        cleaned = clean_dict_or_list(data)
        with open(f, "w", encoding="utf-8") as file:
            json.dump(cleaned, file, indent=2, ensure_ascii=False)
        print(f"Normalized: {f}")
    except Exception as ex:
        print(f"Error {f}: {ex}")
