import json

with open("trans_out.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def get_pronunciation(data):
    try:
        translations = data.get('translation', [])
        for item in translations:
            if isinstance(item, list) and len(item) >= 3 and isinstance(item[2], str):
                return item[2]
    except Exception:
        pass
    return None

print("Extracted:", get_pronunciation(data))
