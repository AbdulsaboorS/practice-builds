# practice-builds

One public repo, one Cloudflare Pages site, every build Abdulsaboor ships during his startup PM
job search. Each build is proof of work for one company: a founder opens one link, sees the
journey, and clicks into the folder made for them.

Why it exists: cold emails lead with a working demo, not claims. A founder can click a demo and
forward it to their team. This repo keeps every demo in one place instead of scattered repos.

## Layout

```
AGENTS.md            public rules (this file)
CLAUDE.md            points Claude Code here
SESSION_CONTEXT.md   local handoff notes, gitignored, never committed or deployed
site/                the deployed folder (Pages output dir). Only this ships.
  index.html         root index: every shipped build, newest first
  <company>/         one folder per company, kebab-case (lorikeet, assemblyai)
    README.md        who the company is, what was built for them, links
    <build>/         one folder per build, self-contained
      index.html     the demo (or its static build output)
      README.md      what it is, who it's for, what it proves, live link
```

A company with one build can keep it in `site/<company>/` directly. Add a `<build>/` level the
moment a second build lands for that company.

## Session rules

- Start: read SESSION_CONTEXT.md. End: rewrite it with what was done, what's next, open questions.
- Read the brief or plan for the current build before touching code. Plans get approved before
  code gets written.
- When something you verify live conflicts with a brief or this file, the live source wins. Say so.

## Build rules

- Small enough to finish in an evening. Shipped means the link is live and sendable.
- Every control does something visible. A button with no visible result gets feedback or gets cut.
- Mobile first: he opens everything on his phone. Single column under 900px, nothing overlaps,
  tap targets at least 44px.
- Every number is either a count of something visible on the page or labeled illustrative.
- Ground every company claim in a source you read (their docs, their site, their job post).
  Unverified claims get cut or labeled as assumptions.
- Describe Abdulsaboor's experience only from facts he gave. Describe his use of a company's
  product only as he actually used it.

## Copy rules

- Casual, plain, direct, in his voice. Short sentences.
- Use commas, periods, colons, or parentheses where an em dash would go. No em dashes anywhere:
  UI copy, READMEs, code comments, commit messages.
- Outreach copy is his to write. Agents build the proof, not the message.

## Technical rules

- Static first: plain HTML, CSS, vanilla JS. Reach for a framework only when the build needs one,
  and then commit its static build output into the build folder.
- Each build folder is self-contained: relative paths only, no imports across build folders,
  no shared JS that one build's change could break. Opening `site/<company>/<build>/index.html`
  through a local server must fully work.
- Builds that need a server (Workers, AI bindings, secrets) live in their own repo and deploy on
  their own. Their folder here holds a README and a landing page that links out.
- Secrets, API keys, and access codes stay out of the repo. A browser demo that calls a paid API
  uses recorded responses, labeled as recorded.
- No trackers, analytics, or third-party scripts unless a build needs one to work.

## System design rules

- Prefer the boring option that a founder can open on a phone with no setup.
- Recorded or scripted data beats a flaky live call in a demo. Label which is which on screen.
- One source of truth per fact: build details live in that build's README; the root index holds
  one line and a link.

## Git and deploy rules

- In-progress work lives on a branch named `build/<company>-<build>`. Main holds only shipped builds.
- Commit in small steps with plain messages.
- Abdulsaboor pushes, merges to main, and deploys. Agents push, merge, deploy, or open PRs only
  when he says so in the current session.
- Source repos for folded-in builds stay untouched. Copy their static output here.

## Verification before handoff

- Serve `site/` locally (`npx serve site` or `python3 -m http.server -d site`).
- Click every control on the index and every build you touched, at desktop and phone width.
- Report what you clicked and what happened, with screenshots of first screens.
  Anything checked only by reading code gets reported as code-verified, not click-tested.
