"""Merge stand-in agent outputs and build a blind grading packet.

Usage: python3 prepare_grading.py <run_dir> [versions]
<run_dir>/out must hold <V>_*.json for each version letter (default "AB":
A = draft SOP, B = round-1 fix, C = round-2 fix).
Writes <run_dir>/grading_packet.md (no SOP version shown) and
<run_dir>/blind_key.json (maps blind id -> version + scenario).
"""
import glob, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
run = sys.argv[1]
versions = sys.argv[2] if len(sys.argv) > 2 else "AB"
scen = json.load(open(os.path.join(HERE, "..", "scenarios.json")))
by_id = {s["id"]: s for s in scen["scenarios"]}

replies = []
for version in versions:
    for f in sorted(glob.glob(f"{run}/out/{version}_*.json")):
        for r in json.load(open(f)):
            replies.append({"version": version, **r})

missing = {(v, s) for v in versions for s in by_id} - {(r["version"], r["id"]) for r in replies}
if missing:
    sys.exit(f"missing replies: {sorted(missing)}")

random.Random(20261102).shuffle(replies)
key, out = {}, [
    "# Grading packet",
    "",
    scen["context"],
    "",
    "Grade each reply against its checks only. Use PASS, FAIL, WARN (only where a check says WARNING is allowed) or NA (a conditional check whose condition did not occur, e.g. no timeline was given).",
]
for i, r in enumerate(replies, 1):
    bid = f"G{i:02d}"
    s = by_id[r["id"]]
    key[bid] = {"version": r["version"], "scenario": r["id"]}
    out += ["", f"## {bid} (scenario {s['id']}: {s['title']})", f"Caller: \"{s['caller']}\"",
            f"Agent reply: \"{r['reply']}\"", f"Agent logged actions: {', '.join(r['actions']) or 'none'}", "Checks:"]
    out += [f"- {c['id']} [{c['severity']}]: {c['text']}" for c in s["checks"]]

open(f"{run}/grading_packet.md", "w").write("\n".join(out) + "\n")
json.dump(key, open(f"{run}/blind_key.json", "w"), indent=2)
json.dump(replies, open(f"{run}/replies.json", "w"), indent=2)
print(f"{len(replies)} replies -> grading_packet.md")
