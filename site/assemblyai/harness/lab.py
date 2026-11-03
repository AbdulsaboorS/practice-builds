"""Shared pieces for the wall runs: keys, TTS synthesis, the event recorder,
the simulated speaker, and the call mixer.

Everything here talks to the real AssemblyAI APIs:
  STT: wss://streaming.assemblyai.com/v3/ws  (Universal-3.6 Pro Realtime)
  TTS: wss://tts.us.assemblyai.com/v1/ws     (AssemblyAI-TTS-1)

Only the speaker is simulated: a voice agent plays audio at real-time speed,
so we model a playback queue that drains at 16 kHz and record what a caller
would have heard. That is labeled on the page.
"""

import array
import asyncio
import base64
import hashlib
import json
import os
import time
import wave
from pathlib import Path
from urllib.parse import urlencode

from websockets.asyncio.client import connect

HERE = Path(__file__).parent
RAW = HERE / "runs" / "raw"          # gitignored scratch (synth cache)
OUT = HERE.parent / "data"           # committed: what the page replays
SR = 16000                           # 16 kHz mono s16le everywhere
BYTES_PER_MS = SR * 2 // 1000        # 32
CHUNK_MS = 50

STT_URL = "wss://streaming.assemblyai.com/v3/ws"
TTS_URL = "wss://tts.us.assemblyai.com/v1/ws"

CALLER_VOICE = "aai-peter"
AGENT_VOICE = "aai-kyla"


def api_key() -> str:
    key = os.environ.get("ASSEMBLYAI_API_KEY")
    env = HERE / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("ASSEMBLYAI_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        raise SystemExit("Put ASSEMBLYAI_API_KEY=... in harness/.env")
    return key


def stt_url(**params) -> str:
    q = {"sample_rate": SR, "speech_model": "universal-3-6-pro", "encoding": "pcm_s16le"}
    q.update({k: v for k, v in params.items() if v is not None})
    return f"{STT_URL}?{urlencode(q)}"


def tts_url(voice: str, **params) -> str:
    q = {"voice_id": voice, "sample_rate": SR, "encoding": "pcm_s16le"}
    q.update({k: v for k, v in params.items() if v is not None})
    return f"{TTS_URL}?{urlencode(q)}"


def silence(ms: int) -> bytes:
    return b"\x00\x00" * (SR * ms // 1000)


async def synth(text: str, voice: str) -> bytes:
    """One-shot TTS-1 synthesis to 16 kHz PCM, cached on disk so reruns are free."""
    RAW.mkdir(parents=True, exist_ok=True)
    h = hashlib.sha1(f"{voice}|{text}".encode()).hexdigest()[:16]
    cache = RAW / f"synth-{h}.pcm"
    if cache.exists():
        return cache.read_bytes()
    pcm = bytearray()
    ws = await connect_tts(voice)
    async with ws:
        await ws.send(json.dumps({"type": "Generate", "text": text}))
        await ws.send(json.dumps({"type": "Flush"}))
        async for raw in ws:
            msg = json.loads(raw)
            if msg["type"] == "Audio":
                pcm += base64.b64decode(msg["audio"])
            elif msg["type"] == "FlushDone":
                break
            elif msg["type"] == "Error":
                raise RuntimeError(f"TTS error: {msg}")
        await ws.send(json.dumps({"type": "Terminate"}))
    cache.write_bytes(bytes(pcm))
    return bytes(pcm)


async def synth_many(texts, voice):
    """Synthesize several lines over ONE TTS session (the free tier allows
    5 new TTS sessions a minute), filling the same cache synth() reads."""
    todo = [t for t in dict.fromkeys(texts)
            if not (RAW / f"synth-{hashlib.sha1(f'{voice}|{t}'.encode()).hexdigest()[:16]}.pcm").exists()]
    if not todo:
        return
    RAW.mkdir(parents=True, exist_ok=True)
    ws = await connect_tts(voice)
    async with ws:
        for text in todo:
            pcm = bytearray()
            await ws.send(json.dumps({"type": "Generate", "text": text}))
            await ws.send(json.dumps({"type": "Flush"}))
            async for raw in ws:
                msg = json.loads(raw)
                if msg["type"] == "Audio":
                    pcm += base64.b64decode(msg["audio"])
                elif msg["type"] == "FlushDone":
                    break
                elif msg["type"] == "Error":
                    raise RuntimeError(f"TTS error: {msg}")
            h = hashlib.sha1(f"{voice}|{text}".encode()).hexdigest()[:16]
            (RAW / f"synth-{h}.pcm").write_bytes(bytes(pcm))
        await ws.send(json.dumps({"type": "Terminate"}))


async def connect_tts(voice, **params):
    """Open a TTS session and wait for Begin. On 3009 (new-session rate limit)
    wait the retry_after_seconds the server gives, then try again."""
    for _ in range(4):
        ws = await connect(tts_url(voice, **params), additional_headers={"Authorization": api_key()})
        msg = json.loads(await ws.recv())
        if msg.get("type") == "Begin":
            ws.begin = msg
            return ws
        await ws.close()
        if msg.get("error_code") == 3009:
            wait = msg.get("retry_after_seconds") or 30
            print(f"TTS rate limited (3009), waiting {wait}s: {msg.get('error')}")
            await asyncio.sleep(wait + 1)
            continue
        raise RuntimeError(f"TTS connect failed: {msg}")
    raise RuntimeError("TTS still rate limited after retries")


class Recorder:
    """Timestamped event log. t is ms since the call started."""

    def __init__(self, name: str):
        self.name = name
        self.t0 = time.monotonic()
        self.events = []

    def now(self) -> int:
        return int((time.monotonic() - self.t0) * 1000)

    def log(self, src: str, kind: str, **data):
        ev = {"t": self.now(), "src": src, "kind": kind, **data}
        self.events.append(ev)
        short = {k: v for k, v in data.items() if k not in ("words",)}
        print(f"{ev['t']:>6} ms  {src:<6} {kind:<18} {json.dumps(short)[:140]}")
        return ev


class Speaker:
    """Simulated agent speaker. Audio frames are queued as they arrive from
    TTS and drain at real-time speed, like a phone or browser audio buffer.
    We log what actually 'played' and when, so talk-over can be measured."""

    def __init__(self, rec: Recorder):
        self.rec = rec
        self.queue = bytearray()
        self.play_head_t = None          # ms timestamp the queue started draining
        self.played = []                 # (start_ms, pcm) segments that reached the caller
        self._task = None
        self.playing = False
        self.started_at = None
        self.expecting = False           # a reply is still streaming in (no FlushDone yet)
        self.cur_tag_q = []              # (bytes, tag) in queue order: which reply each byte belongs to

    def push(self, pcm: bytes, tag=None):
        self.cur_tag_q.append((len(pcm), tag))
        self.queue += pcm
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._drain())

    async def _drain(self):
        """Play at real-time speed. If the queue runs dry while the reply is still
        streaming in, a real device plays silence (an underrun) and carries on."""
        self.playing = True
        self.started_at = self.rec.now()
        self.rec.log("speaker", "playback_start", queued_ms=len(self.queue) // BYTES_PER_MS)
        next_t = time.monotonic()
        gap = 0
        while self.queue or (self.expecting and gap < 1500):
            if self.queue:
                if gap >= 30:
                    self.rec.log("speaker", "underrun", gap_ms=gap)
                gap = 0
                n = min(len(self.queue), CHUNK_MS * BYTES_PER_MS, self.cur_tag_q[0][0])
                tag = self.cur_tag_q[0][1]
                self.cur_tag_q[0] = (self.cur_tag_q[0][0] - n, tag)
                if self.cur_tag_q[0][0] <= 0:
                    self.cur_tag_q.pop(0)
                chunk = bytes(self.queue[:n])
                del self.queue[:n]
                self.played.append((self.rec.now(), chunk, tag))
                dur = n / BYTES_PER_MS / 1000
            else:
                gap += 10
                dur = 0.01
            next_t += dur
            await asyncio.sleep(max(0, next_t - time.monotonic()))
        self.playing = False
        self.rec.log("speaker", "playback_end")

    def stop(self, reason: str):
        self.expecting = False
        dropped = len(self.queue) // BYTES_PER_MS
        self.queue.clear()
        self.cur_tag_q.clear()
        self.rec.log("speaker", "playback_stopped", reason=reason, dropped_ms=dropped)

    def buffered_ms(self) -> int:
        return len(self.queue) // BYTES_PER_MS

    async def wait_idle(self):
        while self.playing or self.queue:
            await asyncio.sleep(0.02)


def mix(caller: list, agent: list, total_ms: int) -> array.array:
    """caller/agent: lists of (start_ms, pcm). Returns a mono s16 mix."""
    out = array.array("i", [0]) * (SR * total_ms // 1000 + SR)
    for track in (caller, agent):
        for start, pcm, *_ in track:
            s = array.array("h")
            s.frombytes(pcm)
            off = start * SR // 1000
            for i, v in enumerate(s):
                j = off + i
                if j < len(out):
                    out[j] += v
    return array.array("h", (max(-32768, min(32767, v)) for v in out))


def save_run(rec: Recorder, caller_track: list, speaker: Speaker | None, meta: dict):
    """Write data/<name>.json (events + meta) and data/<name>.mp3 (the call)."""
    OUT.mkdir(parents=True, exist_ok=True)
    total = rec.now() + 500
    agent_track = speaker.played if speaker else []
    pcm = mix(caller_track, agent_track, total)
    wav_path = RAW / f"{rec.name}.wav"
    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    mp3 = OUT / f"{rec.name}.mp3"
    if caller_track or agent_track:
        os.system(f'ffmpeg -loglevel error -y -i "{wav_path}" -ac 1 -b:a 64k "{mp3}"')
    # Merge speaker playback into spans for the timeline (not every 50 ms chunk).
    spans = []
    for start, chunk, tag in agent_track:
        dur = len(chunk) // BYTES_PER_MS
        if spans and start - spans[-1][1] <= CHUNK_MS + 30 and spans[-1][2] == tag:
            spans[-1][1] = start + dur
        else:
            spans.append([start, start + dur, tag])
    data = {
        "name": rec.name,
        "recorded": time.strftime("%Y-%m-%d"),
        "duration_ms": total,
        "meta": meta,
        "caller_audio": [[s, s + len(p) // BYTES_PER_MS] for s, p in caller_track if any(p[:64])],
        "agent_audio": spans,
        "events": rec.events,
    }
    (OUT / f"{rec.name}.json").write_text(json.dumps(data, indent=1))
    print(f"saved {mp3.name} and {rec.name}.json ({total} ms)")
