"""Build reg-e-pack/index.html (one-screen summary) and details.html.

Usage: python3 build_report.py
Reads ../rules.json, ../scenarios.json, the SOP versions, and for each
round in ../runs/round*/ its replies.json, blind_key.json and grades.json.
Version letters: A = draft SOP, B = round-1 fix, C = round-2 fix,
D and E = two independent runs of the bare-bones realistic SOP.
"""
import glob, json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
load = lambda *a: json.load(open(P(*a)))

rules = load("rules.json")
scen = load("scenarios.json")
meta = load("runs", "meta.json")
SOPS = {"A": "sop_v1_draft.md", "B": "sop_v2_fixed.md", "C": "sop_v3_final.md",
        "D": "sop_v0_realistic.md", "E": "sop_v0_realistic.md"}

def sop_lines(name):
    out = {}
    for line in open(P(name)):
        m = re.match(r"^(\d+)\. (.*)", line.strip())
        if m:
            out[int(m.group(1))] = m.group(2)
    return out

def diff(v1, v2):
    a, b = sop_lines(SOPS[v1]), sop_lines(SOPS[v2])
    return [{"n": n, "old": a[n], "new": b[n]} for n in sorted(a) if a[n] != b.get(n)]

results = {v: {} for v in SOPS}
for rd in sorted(glob.glob(P("runs", "round*"))):
    key = json.load(open(os.path.join(rd, "blind_key.json")))
    grades = json.load(open(os.path.join(rd, "grades.json")))
    for bid, k in key.items():
        results[k["version"]].setdefault(k["scenario"], {})["grades"] = grades[bid]
    for r in json.load(open(os.path.join(rd, "replies.json"))):
        results[r["version"]][r["id"]].update(reply=r["reply"], actions=r["actions"])

for v in SOPS:
    for s in scen["scenarios"]:
        g = results[v][s["id"]]["grades"]
        missing = [c["id"] for c in s["checks"] if c["id"] not in g]
        assert not missing, (v, s["id"], missing)

def tally(v):
    t = {"PASS": 0, "FAIL": 0, "WARN": 0, "NA": 0, "scen_pass": 0, "crit_fail": 0}
    for s in scen["scenarios"]:
        g = results[v][s["id"]]["grades"]
        ok = True
        for c in s["checks"]:
            verdict = g[c["id"]]["verdict"]
            t[verdict] += 1
            if verdict == "FAIL":
                ok = False
                t["crit_fail"] += c["severity"] == "critical"
        t["scen_pass"] += ok
    return t

data = {
    "rules": rules, "scen": scen, "meta": meta, "results": results,
    "diffs": {"B": diff("A", "B"), "C": diff("B", "C")},
    "tally": {v: tally(v) for v in SOPS},
    "nchecks": sum(len(s["checks"]) for s in scen["scenarios"]),
}
# Verbatim excerpts for the one-screen page; fail the build if any drifts.
def quote(v, sid, text):
    assert text in results[v][sid]["reply"], (v, sid, text)
    return text
bad_line = sop_lines(SOPS["A"])[4]
data["example"] = {
    "caller": next(s for s in scen["scenarios"] if s["id"] == "S05")["caller"],
    "sop_line": bad_line,
    "bad": quote("A", "S05", "because the one-time code was shared, the transaction is treated as authorized under our policy, which means it isn't eligible for a dispute."),
    "good": quote("C", "S05", "I'm locking your account right now until your credentials are reset. I'm opening a dispute on the $900 transfer today"),
}
T = data["tally"]
data["bare"] = {"pass": T["D"]["scen_pass"] + T["E"]["scen_pass"], "n": 2 * len(scen["scenarios"])}

def render(tpl, out):
    html = open(P("tools", tpl)).read().replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    open(P(out), "w").write(html)
render("details_template.html", "details.html")
# index.html is now hand-written (Dispute SOP Check); only details.html is generated.
for v in SOPS:
    print(v, T[v])
print("bare", data["bare"])
