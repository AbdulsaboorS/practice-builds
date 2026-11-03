"""Run one scenario against the real AssemblyAI APIs and save it for the page.

  python run.py baseline
  python run.py cutoff naive|fixed
  python run.py bargein naive|cancel_only|fixed
  python run.py mute naive|fixed
  python run.py retry

A scripted caller (TTS-1 voice) talks to a scripted agent. The caller's audio
streams into Universal-3.6 Pro Realtime at real-time pace, the agent answers
through a TTS-1 session, and every event is logged with its time. Agent
replies are scripted on purpose: this tests the voice pipeline, not an LLM.
"""

import asyncio
import json
import sys
import time

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

import lab
from lab import BYTES_PER_MS, CHUNK_MS, Recorder, Speaker

CHUNK = CHUNK_MS * BYTES_PER_MS


class Call:
    def __init__(self, name, stt_params=None, barge_in="full", flush=True,
                 replies=(), on_reply=None, on_final=None, reply_for=None):
        self.rec = Recorder(name)
        self.speaker = Speaker(self.rec)
        self.stt_params = stt_params or {}
        self.barge_in = barge_in          # ignore | cancel_only | full
        self.flush = flush                # send Flush after each reply
        self.replies = list(replies)      # agent lines, one per final turn
        self.reply_for = reply_for        # or: transcript -> agent line
        self.on_reply = on_reply          # hook(call, reply_index) after a reply is sent
        self.on_final = on_final          # hook(call, turn) when a final arrives
        self.caller_buf = bytearray()
        self.caller_track = []            # (start_ms, pcm) for each caller line
        self.finals = []
        self.reply_i = 0
        self.dropping = False             # between our Cancel and its Cancelled
        self.flush_sent_at = {}
        self.first_audio_seen = set()
        self.done = False
        self.stt = self.tts = None
        self.last_reply_t = None

    # caller side --------------------------------------------------------
    async def sender(self):
        """Send caller audio (or silence) every 50 ms, like a live phone line."""
        next_t = time.monotonic()
        while not self.done:
            if self.caller_buf:
                chunk = bytes(self.caller_buf[:CHUNK]).ljust(CHUNK, b"\x00")
                del self.caller_buf[:CHUNK]
            else:
                chunk = b"\x00" * CHUNK
            try:
                await self.stt.send(chunk)
            except ConnectionClosed:
                return
            next_t += CHUNK_MS / 1000
            await asyncio.sleep(max(0, next_t - time.monotonic()))

    async def say(self, text):
        pcm = await lab.synth(text, lab.CALLER_VOICE)
        start = self.rec.now() + len(self.caller_buf) // BYTES_PER_MS
        self.caller_track.append((start, pcm))
        self.rec.log("caller", "say_start", text=text, at=start, dur_ms=len(pcm) // BYTES_PER_MS)
        self.caller_buf += pcm
        while self.caller_buf:
            await asyncio.sleep(0.01)
        self.rec.log("caller", "say_end", text=text)

    async def pause(self, ms):
        self.caller_buf += lab.silence(ms)
        while self.caller_buf:
            await asyncio.sleep(0.01)

    async def wait_agent(self, timeout_ms=14000, after_ms=500):
        """Wait for the agent's reply to start playing and finish, or give up
        after timeout_ms of waiting. Returns False if the caller gave up."""
        mark = self.reply_i
        t_start = self.rec.now()
        t_end = time.monotonic() + timeout_ms / 1000
        heard = False
        while heard or time.monotonic() < t_end:
            replied = self.reply_i > mark
            started = self.speaker.started_at is not None and self.last_reply_t is not None \
                and self.speaker.started_at >= self.last_reply_t and self.last_reply_t >= t_start
            if replied and (started or self.speaker.playing):
                heard = True
            if heard and not self.speaker.playing and not self.speaker.queue:
                break
            await asyncio.sleep(0.02)
        else:
            self.rec.log("caller", "gave_up_waiting", waited_ms=timeout_ms)
            return False
        await asyncio.sleep(after_ms / 1000)
        return True

    async def wait_playback(self, ms):
        """Wait until the agent has been audible for `ms` (for barge-in)."""
        while not self.speaker.started_at:
            await asyncio.sleep(0.01)
        while self.speaker.started_at and self.rec.now() - self.speaker.started_at < ms:
            await asyncio.sleep(0.01)

    # STT side -----------------------------------------------------------
    async def stt_reader(self):
        try:
            async for raw in self.stt:
                m = json.loads(raw)
                t = m.get("type")
                if t == "Begin":
                    self.rec.log("stt", "begin", config=m.get("configuration"))
                elif t == "SpeechStarted":
                    self.rec.log("stt", "speech_started", audio_ts=m.get("timestamp"))
                    await self.handle_barge_in()
                elif t == "Turn":
                    if m.get("end_of_turn"):
                        self.rec.log("stt", "final", turn=m["turn_order"], text=m["transcript"],
                                     eot_conf=m.get("end_of_turn_confidence"))
                        self.finals.append(m)
                        if self.on_final:
                            await self.on_final(self, m)
                        await self.agent_reply()
                    else:
                        self.rec.log("stt", "partial", turn=m["turn_order"], text=m["transcript"])
                elif t == "Termination":
                    self.rec.log("stt", "termination")
                elif t == "Error":
                    self.rec.log("stt", "error", code=m.get("error_code"), error=m.get("error"))
        except ConnectionClosed as e:
            self.rec.log("stt", "closed", code=e.rcvd.code if e.rcvd else None)

    # agent / TTS side ---------------------------------------------------
    async def agent_reply(self):
        if self.reply_for:
            text = self.reply_for(self.finals[-1]["transcript"])
        elif self.reply_i < len(self.replies):
            text = self.replies[self.reply_i]
        else:
            text = "Sorry, could you say that again?"
        i = self.reply_i
        self.reply_i += 1
        self.last_reply_t = self.rec.now()
        self.rec.log("agent", "reply_sent", i=i, text=text, flushed=self.flush)
        self.speaker.expecting = True
        try:
            await self.tts.send(json.dumps({"type": "Generate", "text": text + " "}))
            if self.flush:
                await self.tts.send(json.dumps({"type": "Flush"}))
        except ConnectionClosed:
            self.rec.log("agent", "tts_send_failed", note="TTS session already closed")
        if self.on_reply:
            await self.on_reply(self, i)

    async def handle_barge_in(self):
        if not (self.speaker.playing or self.speaker.queue):
            return
        if self.barge_in == "ignore":
            self.rec.log("agent", "barge_in_ignored", buffered_ms=self.speaker.buffered_ms())
            return
        self.rec.log("agent", "cancel_sent", buffered_ms=self.speaker.buffered_ms())
        try:
            await self.tts.send(json.dumps({"type": "Cancel"}))
        except ConnectionClosed:
            pass
        if self.barge_in == "full":
            self.dropping = True
            self.speaker.stop("barge_in")

    async def tts_reader(self):
        try:
            async for raw in self.tts:
                m = json.loads(raw)
                t = m.get("type")
                if t == "Audio":
                    fid = m["flush_id"]
                    pcm = lab.base64.b64decode(m["audio"])
                    if self.dropping:
                        self.rec.log("tts", "audio_dropped", flush_id=fid, ms=len(pcm) // BYTES_PER_MS)
                        continue
                    if fid not in self.first_audio_seen:
                        self.first_audio_seen.add(fid)
                        self.rec.log("tts", "first_audio", flush_id=fid,
                                     since_reply_ms=self.rec.now() - (self.last_reply_t or 0))
                    self.speaker.push(pcm, fid)
                elif t == "FlushDone":
                    self.speaker.expecting = False
                    self.rec.log("tts", "flush_done", flush_id=m["flush_id"], audio_ms=m.get("audio_duration_ms"))
                elif t == "Cancelled":
                    self.dropping = False
                    self.speaker.expecting = False
                    self.rec.log("tts", "cancelled", audio_s=m.get("audio_duration_seconds"))
                elif t == "Error":
                    self.rec.log("tts", "error", code=m.get("error_code"), error=m.get("error"),
                                 error_type=m.get("error_type"))
                elif t == "Termination":
                    self.rec.log("tts", "termination")
        except ConnectionClosed as e:
            self.rec.log("tts", "closed", code=e.rcvd.code if e.rcvd else None)

    # run ----------------------------------------------------------------
    async def run(self, script, meta, tts_params=None, caller_lines=()):
        key = lab.api_key()
        await lab.synth_many(caller_lines, lab.CALLER_VOICE)
        tts = await lab.connect_tts(lab.AGENT_VOICE, **(tts_params or {}))
        self.rec = Recorder(self.rec.name)
        self.speaker.rec = self.rec
        self.rec.log("tts", "begin", inactivity_timeout=tts.begin["configuration"].get("inactivity_timeout"))
        async with connect(lab.stt_url(**self.stt_params), additional_headers={"Authorization": key}) as stt, tts:
            self.stt, self.tts = stt, tts
            tasks = [asyncio.create_task(c) for c in (self.sender(), self.stt_reader(), self.tts_reader())]
            await asyncio.sleep(0.3)
            await script(self)
            await self.speaker.wait_idle()
            await asyncio.sleep(0.5)
            self.done = True
            try:
                await stt.send(json.dumps({"type": "Terminate"}))
                await tts.send(json.dumps({"type": "Terminate"}))
            except ConnectionClosed:
                pass
            await asyncio.sleep(1.0)
            for t in tasks:
                t.cancel()
        lab.save_run(self.rec, self.caller_track, self.speaker, meta)


# scenarios -------------------------------------------------------------

async def baseline():
    async def script(c):
        await c.say("Hi, I'd like to move my appointment to next week.")
        await c.wait_agent()
        await c.say("Thursday afternoon, if you have it.")
        await c.wait_agent()
        await c.say("Yes, please.")
        await c.wait_agent()
    call = Call("baseline", stt_params={"mode": "balanced"}, replies=[
        "Sure, I can help with that. What day works best for you?",
        "Thursday at two is open. Want me to book it?",
        "Done. You're booked for Thursday at two.",
    ])
    await call.run(script, {"title": "A normal call", "mode": "balanced"}, caller_lines=[
        "Hi, I'd like to move my appointment to next week.", "Thursday afternoon, if you have it.", "Yes, please."])


async def cutoff(variant):
    """Snappy agents run min_latency mode. A held entity ends at max_turn_silence
    (640 ms there), so a caller who pauses longer between digit groups gets split."""
    async def script(c):
        await c.say("Hi, I need someone to call me back about my order.")
        await c.wait_agent()
        await c.say("Sure, it's seven one three,")
        await c.pause(900)
        await c.say("five five five,")
        await c.pause(900)
        await c.say("zero one three four.")
        await c.wait_agent(timeout_ms=6000)

    async def on_reply(c, i):
        # Fixed: the agent just asked for a number, so hold turns open longer.
        if variant == "fixed" and i == 0:
            msg = {"type": "UpdateConfiguration", "min_turn_silence": 1000, "max_turn_silence": 1300}
            await c.stt.send(json.dumps(msg))
            c.rec.log("agent", "update_config", **{k: v for k, v in msg.items() if k != "type"})

    async def on_final(c, turn):
        # Fixed: once the number is in, go back to the snappy preset.
        if variant == "fixed" and len(c.finals) == 2:
            await c.stt.send(json.dumps({"type": "UpdateConfiguration", "mode": "min_latency"}))
            c.rec.log("agent", "update_config", mode="min_latency")

    call = Call(f"cutoff-{variant}", stt_params={"mode": "min_latency"}, on_reply=on_reply, on_final=on_final,
                replies=["Happy to. What's the best number to reach you?",
                         "Thanks. Someone will call you back within the hour."])
    await call.run(script, {"title": "Cut off mid phone number", "variant": variant, "mode": "min_latency"}, caller_lines=[
        "Hi, I need someone to call me back about my order.", "Sure, it's seven one three,", "five five five,", "zero one three four."])


async def bargein(variant):
    async def script(c):
        await c.say("What are your hours this weekend?")
        await c.wait_playback(1800)
        await c.say("Sorry, I meant the downtown store.")
        await c.wait_agent()
    call = Call(f"bargein-{variant}", stt_params={"mode": "balanced"},
                barge_in={"naive": "ignore", "cancel_only": "cancel_only", "fixed": "full"}[variant],
                replies=["This weekend we're open Saturday from nine in the morning to six in the evening, "
                         "and Sunday from eleven to five. Holiday hours can be different, so if you're planning "
                         "a visit around a holiday, it's worth checking the store page first.",
                         "Got it. The downtown store is open ten to four on both days."])
    await call.run(script, {"title": "Talk-over after barge-in", "variant": variant}, caller_lines=[
        "What are your hours this weekend?", "Sorry, I meant the downtown store."])


async def mute(variant):
    """Without Flush, short text never plays and long text waits for more."""
    async def ask(c, line):
        await c.say(line)
        if not await c.wait_agent(timeout_ms=5000):
            await c.say("Hello, are you still there?")
            await c.wait_agent(timeout_ms=6000)

    async def script(c):
        await ask(c, "Hi, can you check if my package shipped?")
        await ask(c, "Great. Can you text me the tracking link?")

    def reply_for(text):
        t = text.lower()
        if "shipped" in t:
            return ("Yes, it shipped yesterday afternoon. It's with the carrier now and should arrive "
                    "by Friday. You'll get an email when it's out for delivery.")
        if "tracking" in t:
            return "Sure."
        if "there" in t or "hello" in t:
            return "Yes, sorry, I'm here."
        return "Sorry, could you say that again?"

    call = Call(f"mute-{variant}", stt_params={"mode": "balanced"}, flush=(variant == "fixed"), reply_for=reply_for)
    await call.run(script, {"title": "The agent goes mute", "variant": variant}, caller_lines=[
        "Hi, can you check if my package shipped?", "Great. Can you text me the tracking link?",
        "Hello, are you still there?"])


async def retry():
    """Same close code, opposite right answer. Uses one bad key and a short
    burst of real session starts on the good key. No audio is sent."""
    rec = Recorder("retry")
    key = lab.api_key()

    async def attempt(product, url, auth, label):
        try:
            async with connect(url, additional_headers={"Authorization": auth}, open_timeout=10) as ws:
                async for raw in ws:
                    m = json.loads(raw)
                    if m.get("type") == "Begin":
                        rec.log(product, "begin", label=label)
                        await ws.send(json.dumps({"type": "Terminate"}))
                    elif m.get("type") == "Error":
                        rec.log(product, "error", label=label, code=m.get("error_code"), error=m.get("error"),
                                error_type=m.get("error_type"), retryable=m.get("retryable"))
        except ConnectionClosed as e:
            rec.log(product, "closed", label=label, code=e.rcvd.code if e.rcvd else None)
        except Exception as e:  # handshake refused
            rec.log(product, "handshake_failed", label=label, error=str(e)[:120])

    # 1. A naive client retries every 1008 with backoff. With a bad key that never ends.
    for n in range(4):
        await attempt("stt", lab.stt_url(), "not-a-real-key", f"bad key, attempt {n + 1}")
        await asyncio.sleep(0.5 * 2 ** n)
    await attempt("tts", lab.tts_url(lab.AGENT_VOICE), "not-a-real-key", "bad key")
    # 2. A burst of new sessions on the good key, until the per-minute limit answers.
    for n in range(12):
        await attempt("stt", lab.stt_url(), key, f"burst session {n + 1}")
        if any(e.get("label") == f"burst session {n + 1}" and e.get("code") == 1008 for e in rec.events):
            break
    # 3. Same burst on TTS-1, which reports its rate limit with its own code.
    for n in range(8):
        await attempt("tts", lab.tts_url(lab.AGENT_VOICE), key, f"burst session {n + 1}")
        if any(e.get("label") == f"burst session {n + 1}" and e.get("src") == "tts" and e.get("code") == 3009
               for e in rec.events):
            break
    lab.save_run(rec, [], None, {"title": "A 1008 that shouldn't be retried"})


if __name__ == "__main__":
    name, variant = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else None)
    fn = {"baseline": baseline, "cutoff": cutoff, "bargein": bargein, "mute": mute, "retry": retry}[name]
    asyncio.run(fn(variant) if variant else fn())
