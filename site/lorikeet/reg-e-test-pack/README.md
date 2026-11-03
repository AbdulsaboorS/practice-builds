# Reg E Dispute Test Pack

**The AI mostly knew the rules. The SOP broke them.**

An AI support agent was tested on 17 disputed-payment calls under US Regulation E, using three kinds of dispute procedure (SOP):

| SOP | Calls that passed every check |
|---|---|
| Bare-bones, six lines, says nothing about Reg E (`sop_v0_realistic.md`), run twice | 30 of 34 |
| Contains the mistakes CFPB's FAQ calls out (`sop_v1_draft.md`) | 3 of 17 |
| Same SOP, fixed in two rounds (`sop_v2_fixed.md`, then `sop_v3_final.md`) | 15, then 17 of 17 |

Left to its own judgment, the agent never required a police report, never sent a caller to the merchant first, and never denied the caller who kept the PIN with the card. It did give no timeline in all 6 calls where the caller asked for one. Given a flawed SOP, it followed the SOP's mistakes, for example telling a scam victim their $900 loss "isn't eligible for a dispute."

So what: fintechs hand over procedures written for humans, and the agent follows them faithfully. Before going live, test the SOP, not just the agent. This pack does that in 17 calls with 29 checks, each tied to a quoted rule.

Unofficial concept, mock data only. Pinecrest and everything about it is fictional. Not affiliated with Lorikeet. Not legal advice.

## What's in here

- `index.html`: the one-screen summary, readable in about 10 seconds. `details.html`: every call, verdict, fix and rule.
- `scenarios.json`: the 17 scenarios with caller lines, rules tested and checks (critical or warning).
- `rules.json`: the 13 rules, each with its citation, a verbatim quote and a link.
- `sop_v0_realistic.md`, `sop_v1_draft.md`, `sop_v2_fixed.md`, `sop_v3_final.md`: the procedure versions.
- `runs/round0/` (bare-bones SOP, two runs), `runs/round1/`, `runs/round2/`: every agent reply, the blind grading packet, the blind key and the grader's verdicts with evidence quotes.
- `tools/`: `prepare_grading.py` (merge replies, shuffle, build the blind packet), `build_report.py` + `index_template.html` + `details_template.html` (rebuild both pages).
- `screenshots/`: summary on desktop and phone, details with a scenario opened.

## How it was run

1. Each stand-in agent was a fresh Claude Sonnet sub-agent per batch of calls. It saw only one SOP and the caller lines, never the rules or checks. With the bare-bones SOP it was told to use its own judgment where the SOP was silent.
2. A separate Claude grader saw only the caller, reply, logged actions and checks, never the SOP. Replies were shuffled under blind IDs, and every verdict carries the quote it was based on. I spot-checked verdicts against the replies.
3. Limits: small samples (two runs for the bare-bones SOP, one for each other version), single-turn calls, debit and account disputes only (no credit cards, EBT or prepaid-specific rules).

## Rebuild the page

```
python3 tools/build_report.py
```

## 10-second walkthrough

1. Read the headline and the three numbers: 30 of 34, 3 of 17, 17 of 17.
2. Read the one call: the bad SOP line, what the agent said because of it, and what it said after the fix.
3. Click "See every call and check" only if you want proof.

## Sources

- 12 CFR 1005.11: https://www.consumerfinance.gov/rules-policy/regulations/1005/11/
- 12 CFR 1005.6: https://www.consumerfinance.gov/rules-policy/regulations/1005/6/
- Official interpretation of 1005.11: https://www.consumerfinance.gov/rules-policy/regulations/1005/interp-11/
- CFPB Electronic Fund Transfers FAQs: https://www.consumerfinance.gov/compliance/compliance-resources/deposit-accounts-resources/electronic-fund-transfers/electronic-fund-transfers-faqs/
- Lorikeet Forward Deployed Product Manager posting (verified live Nov 1, 2026): https://jobs.ashbyhq.com/lorikeet/078c3133-7512-4f62-9b34-fda0434a09e1
