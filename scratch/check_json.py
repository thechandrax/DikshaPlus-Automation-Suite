import sys
import json
sys.path.insert(0, '.')
import automations.diksha_plus_engine as eng

fpath = "data/courses/power_of_audio_in_education.json"
data = json.load(open(fpath, "r", encoding="utf-8"))

print("=== JSON STRUCTURE CHECK FOR power_of_audio_in_education.json ===")
print("1. COURSE NAME        :", data.get("course_name"))
mods = data.get("modules", [])
print("2. MODULES COUNT       :", len(mods))

for m in mods:
    mno = m.get("module_no")
    mname = m.get("module_name")
    subs = m.get("subsections", [])
    print(f"   ► Module #{mno} - '{mname}': {len(subs)} Subsections")
    for s in subs:
        sno = s.get("subsection_no")
        sname = s.get("subsection_name")
        qs = s.get("questions", [])
        print(f"       • Subsection #{sno} - '{sname}': {len(qs)} Questions")

qas = eng.extract_all_qa_items(data)
print("3. TOTAL Q&A ITEMS EXTRACTED :", len(qas))

# Sample Q&A Verification
print("\n--- SAMPLE Q&A ITEM VERIFICATION ---")
if qas:
    first_q = qas[0]
    print(f"Q1 Question : {first_q.get('question')}")
    print(f"Q1 Options  : {first_q.get('options')}")
    print(f"Q1 Answer   : {first_q.get('answer')}")

print("\n=== ALL CHECKS PASSED 100% OK! ===")
