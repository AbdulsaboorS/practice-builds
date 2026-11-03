# Voice Agent Wall Report

**What it is:** a small voice agent on AssemblyAI's Universal-3.6 Pro Realtime (speech to text) and AssemblyAI-TTS-1 (text to speech), broken four ways on purpose against the real APIs, with the fix for each. Every run is recorded (audio plus every event with its time) and replayable on the page.

**Built for:** AssemblyAI. Concept work, not affiliated. Built with a free-tier key.

**What it proves:** I can run a customer's stack the way their customers do, hit the walls those customers are about to hit, and turn each one into a fix, a docs or product note, and a triage playbook entry. That's the loop in their Forward Deployed Engineer, Triage role.

**Live:** https://assemblyai-wall-report.pages.dev

## The four walls (recorded 2026-11-03)

| Wall | Naive | Fixed |
|---|---|---|
| Cut off mid phone number (`min_latency` mode, caller pauses 900 ms between digit groups) | Split into 3 turns, the agent answered "Sure, it's 713-" | 1 turn, "713-555-0134", 1.1 s after the last digit |
| Talk-over after barge-in | The old reply kept playing 11.6 s (11.5 s with `Cancel` alone: TTS-1 had already delivered all 13 s) | 0.4 s |
| The agent goes mute (`Generate` without `Flush`) | 6.9 s from question to first sound, caller asked "are you still there?" twice | About 0.1 s |
| A 1008 that shouldn't be retried | STT uses 1008 for both a bad key and the new-session rate limit ("Too many concurrent sessions" with 0 open) | Retry on the error text. TTS-1 reports the same limit as 3009 |

A normal call for comparison: final transcript about 200 ms after the caller stops, TTS-1 first audio about 110 ms after the reply is sent.

## How it was recorded

- `harness/run.py`: a TTS-1 voice plays the caller and streams into Universal-3.6 Pro Realtime at real-time pace in 50 ms chunks. A scripted agent answers through one TTS-1 WebSocket session per call. Agent lines are scripted on purpose: this tests the voice pipeline, not an LLM.
- The agent's speaker is simulated: audio drains at real-time speed, like a phone's audio buffer, so what the caller would hear can be measured. There's no echo path.
- `harness/film/`: the demo video is rendered frame by frame from the same recordings (`film.html` + `make_film.mjs`), with the matching slices of recorded audio underneath.
- Run it yourself: put `ASSEMBLYAI_API_KEY=...` in `harness/.env` (gitignored), then `python run.py baseline`, `cutoff naive|fixed`, `bargein naive|cancel_only|fixed`, `mute naive|fixed`, `retry`. Needs Python 3.10+ and `websockets` 14+.

## Things I'd file

- LLM Gateway answers a request with no key with "Your account does not have access to LLM Gateway. Please upgrade." That points at billing when the fix is the missing key.
- The docs say the retired v2 streaming URL fails with HTTP 410. Without a key it returns a plain 404.
- STT Error frames have no `retryable` or `error_type`. TTS-1 Error frames do.
