# practice-builds

Working demos I built for startups I want to work with. Instead of telling a founder I can do the job, I build something for their product first.

Live site: deploys from `site/` as one Cloudflare Pages project (link coming once it's live).

| Build | Built for | Folder |
|---|---|---|
| Reg E dispute test pack | Lorikeet | [site/lorikeet/reg-e-test-pack](site/lorikeet/reg-e-test-pack) |
| Voice concierge | Lorikeet | [site/lorikeet/voice-concierge](site/lorikeet/voice-concierge) |
| tour-lens | EliseAI | [site/eliseai](site/eliseai) |
| Hear It at Your Practice | Prosper AI | [site/prosper](site/prosper) |
| FairHouse AI | Box + AWS hackathon (2nd place) | [site/fairhouse-ai](site/fairhouse-ai) |

Each folder is self-contained with its own README. Rules for how builds get made live in [AGENTS.md](AGENTS.md).

## Run it locally

```
python3 -m http.server -d site 8080
```

Then open http://localhost:8080.
