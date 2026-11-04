// Voice Agent Wall Report: replay player + wall cards.
// All timing data comes from data/<run>.json, recorded by harness/run.py.

const WALLS = [
  {
    id: "cutoff",
    title: "1. Cut off mid phone number",
    ticket: "Our agent keeps grabbing half the callback number. Callers read it in chunks and the bot jumps in after the area code.",
    variants: [["naive", "Naive (min_latency)", "bad"], ["fixed", "Fixed", "good"]],
    why: `Snappy agents run <code>mode=min_latency</code>. Entity-aware endpointing holds a turn open while a number is still coming, but only until <code>max_turn_silence</code>, which is 640 ms in that mode. This caller pauses 900 ms between digit groups, like someone reading off a card, so the turn ended at "713-" and the agent thanked them for a three-digit number. The fix raises the silence limits only while the agent is waiting for the number, then puts the snappy preset back.`,
    fix: `# The agent just asked for a number: give the caller room.
stt.send({"type": "UpdateConfiguration",
          "min_turn_silence": 1000, "max_turn_silence": 1300})

# Number captured: back to the snappy preset.
stt.send({"type": "UpdateConfiguration", "mode": "min_latency"})`,
    playbook: [
      ["Symptom", "Entities split across turns, agent talks over the rest of the number."],
      ["User error, bug, or gap?", "Usage. The model held the entity as documented; the preset's max_turn_silence is shorter than the caller's pauses."],
      ["Check first", "Begin.configuration.mode, then the gap between the split finals vs that mode's max_turn_silence."],
      ["Reply with", "Raise min/max_turn_silence mid-stream when the agent asks for an entity, then re-apply the mode."],
      ["Product note", "Agents know when they asked for a number. A one-line \"expect_entity\" hint, or a docs recipe per framework (Pipecat, LiveKit), would prevent this ticket."],
    ],
    sources: [
      ["Turn detection: entity-aware endpointing", "https://www.assemblyai.com/docs/streaming/turn-detection"],
      ["LiveKit agents #8065: max turn silence vs mode preset", "https://github.com/livekit/agents/pull/8065"],
    ],
  },
  {
    id: "bargein",
    title: "2. Talk-over after barge-in",
    ticket: "When a caller interrupts, our agent keeps talking for a few seconds. We already send Cancel.",
    variants: [["naive", "Ignores interruption", "bad"], ["cancel_only", "Sends Cancel only", "bad"], ["fixed", "Fixed", "good"]],
    why: `TTS-1 synthesizes several times faster than real time. In this run the whole 13 second reply reached the client within about 1.5 s, so when the caller cut in, there was nothing left on the server to cancel (<code>Cancelled</code> came back with 0.0 s) and about 11 s sat in the local buffer. <code>Cancel</code> stops the server, not the speaker. The caller-side cost of the fix is the detection delay: balanced mode waits 500 ms (<code>interruption_delay</code>) before <code>SpeechStarted</code>.`,
    fix: `on SpeechStarted (STT):
    tts.send({"type": "Cancel"})
    speaker.clear()          # stop what's already buffered
    dropping = True          # ignore Audio until Cancelled
on Cancelled (TTS):
    dropping = False`,
    playbook: [
      ["Symptom", "Agent keeps speaking for seconds after the caller starts talking, even with Cancel wired up."],
      ["User error, bug, or gap?", "Usage. Cancel works as documented; the client never flushes its own playback queue."],
      ["Check first", "Does the client stop local playback on SpeechStarted? Are Audio frames between Cancel and Cancelled dropped?"],
      ["Reply with", "The three-line handler above, plus a link to the Cancel section of Message frames."],
      ["Product note", "The barge-in tutorial covers this. A short \"Cancel doesn't stop your speaker\" callout on the Cancel frame itself would catch people who skip the tutorial."],
    ],
    sources: [
      ["TTS message frames: Cancel", "https://www.assemblyai.com/docs/tts/message-frames"],
      ["Turn detection: SpeechStarted as the barge-in signal", "https://www.assemblyai.com/docs/streaming/turn-detection"],
      ["LiveKit agents #8246: interrupt on STT start of speech", "https://github.com/livekit/agents/pull/8246"],
    ],
  },
  {
    id: "mute",
    title: "3. The agent goes mute",
    ticket: "Our agent goes quiet, then answers the previous question when the caller says hello. Short replies like \"Sure.\" never play at all. No errors anywhere.",
    variants: [["naive", "Generate only", "bad"], ["fixed", "Generate + Flush", "good"]],
    why: `<code>Generate</code> only buffers text. The server starts speaking on its own once enough text piles up, so a client that never sends <code>Flush</code> can look fine in testing. In this run a three-sentence reply (139 characters) sat silent until the caller's "hello?" produced the next reply and pushed the buffer over the line. A one-word reply like "Sure." is never spoken on its own. No Error frame, and the socket stays open.`,
    fix: `tts.send({"type": "Generate", "text": reply + " "})
tts.send({"type": "Flush"})   # every reply, every time`,
    playbook: [
      ["Symptom", "Intermittent silence on short replies, no Error frame, session stays open."],
      ["User error, bug, or gap?", "Usage, but a sharp edge: the failure is silent and only shows on short text."],
      ["Check first", "Is there a FlushDone for every reply? A reply with no Audio and no FlushDone was never flushed."],
      ["Reply with", "Flush after every reply (and after each sentence when streaming from an LLM)."],
      ["Product note", "A warning frame, or a FlushDone-less timer in the SDKs, would turn a silent bug into a loud one."],
    ],
    sources: [
      ["TTS message frames: Generate and Flush", "https://www.assemblyai.com/docs/tts/message-frames"],
      ["Pipecat #6322: AssemblyAI TTS service", "https://github.com/pipecat-ai/pipecat/pull/6322"],
    ],
  },
];

const FILE_NOTES = [
  ["LLM Gateway tells a keyless caller to upgrade",
   "A POST to llm-gateway.assemblyai.com with no Authorization header answers 401 with \"Your account does not have access to LLM Gateway. Please upgrade.\" That points a developer at billing when the fix is the missing key. Seen without a key."],
  ["Retired v2 streaming URL: docs say 410, I got 404",
   "Common session errors says the v2 endpoint fails with HTTP 410 on upgrade. A keyless upgrade to api.assemblyai.com/v2/realtime/ws returns a plain 404 \"Not found\" from the load balancer. A 410 (or the docs) would save a support thread. Seen without a key."],
  ["Three endpoints, three error shapes",
   "/v2/transcript returns {\"error\"}, the streaming token endpoint returns a FastAPI style {\"detail\": [...]} 422, and LLM Gateway returns {\"error\",\"status\",\"request_id\"}. One shape (with a request_id everywhere) makes errors easy for customers and for a triage agent to parse."],
];

// ---------------------------------------------------------------------------

const $ = (s, el = document) => el.querySelector(s);
const h = (tag, attrs = {}, html = "") => { const e = document.createElement(tag); Object.assign(e, attrs); if (html) e.innerHTML = html; return e; };
const fmt = ms => (ms / 1000).toFixed(1) + " s";
const cache = {};

async function load(name) {
  if (!cache[name]) cache[name] = fetch(`data/${name}.json`).then(r => r.ok ? r.json() : null).catch(() => null);
  return cache[name];
}

function overlapMs(a, b) {
  let t = 0;
  for (const [s1, e1] of a) for (const [s2, e2] of b) t += Math.max(0, Math.min(e1, e2) - Math.max(s1, s2));
  return t;
}
function overlaps(a, b) {
  const out = [];
  for (const [s1, e1] of a) for (const [s2, e2] of b) { const s = Math.max(s1, s2), e = Math.min(e1, e2); if (e > s) out.push([s, e]); }
  return out;
}

// Metrics per run, all derived from recorded events.
function metrics(d) {
  const ev = d.events;
  const talkOver = overlapMs(d.caller_audio, d.agent_audio);
  const finals = ev.filter(e => e.kind === "final");
  const replies = ev.filter(e => e.kind === "reply_sent");
  const silentReplies = replies.filter((r, i) => {
    const next = replies[i + 1] ? replies[i + 1].t : Infinity;
    return !ev.some(e => e.kind === "first_audio" && e.t > r.t && e.t < next);
  }).length;
  // Response time: end of caller speech -> agent audio starts playing.
  const resp = [];
  for (const r of replies) {
    const callerEnd = Math.max(...d.caller_audio.filter(([s, e]) => e <= r.t).map(([s, e]) => e), -1);
    const play = ev.find(e => e.kind === "playback_start" && e.t >= r.t);
    const fin = [...finals].reverse().find(f => f.t <= r.t);
    if (callerEnd > 0 && play) resp.push({ endpoint: fin ? fin.t - callerEnd : null, total: play.t - callerEnd, tts: play.t - r.t });
  }
  return { talkOver, finals: finals.length, replies: replies.length, silentReplies, resp, gaveUp: ev.some(e => e.kind === "gave_up_waiting") };
}

// ---------------------------------------------------------------------------
// Replay player: audio + two lanes + event marks + live caption.

// Cloudflare Pages answers Range requests with a full 200, and Chrome can't
// seek media without 206. Loading each file into a blob makes seeking local.
const blobs = {};
function mediaUrl(url) {
  blobs[url] = blobs[url] || fetch(url).then(r => { if (!r.ok) throw new Error(r.status); return r.blob(); })
    .then(b => URL.createObjectURL(b)).catch(() => url);
  return blobs[url];
}

function player(d) {
  const root = h("div", { className: "player" });
  if (!d) { root.innerHTML = `<p class="note">Recording not available yet.</p>`; return root; }
  const audio = new Audio();
  audio.preload = "auto";
  const ready = mediaUrl(`data/${d.name}.mp3`).then(u => { audio.src = u; return new Promise(r => audio.readyState >= 1 ? r() : audio.addEventListener("loadedmetadata", r, { once: true })); });
  const dur = d.duration_ms;
  const pct = ms => (100 * ms / dur) + "%";
  const btn = h("button", { className: "play", type: "button", ariaLabel: "Play recording" }, "&#9654;");
  const back = h("button", { className: "skip", type: "button", ariaLabel: "Back 5 seconds" }, "&#8634; 5s");
  const fwd = h("button", { className: "skip", type: "button", ariaLabel: "Forward 5 seconds" }, "5s &#8635;");
  const time = h("span", { className: "time" }, `0.0 s / ${fmt(dur)}`);
  const controls = h("div", { className: "controls" }); controls.append(btn, back, fwd, time);
  const tl = h("div", { className: "tl", tabIndex: 0, role: "slider", ariaLabel: "Seek recording" });
  tl.setAttribute("aria-valuemin", "0"); tl.setAttribute("aria-valuemax", String(Math.round(dur / 1000)));
  const track = h("div", { className: "track" });
  const laneC = h("div", { className: "lane" }, `<span class="lbl">Caller</span>`);
  const laneA = h("div", { className: "lane" }, `<span class="lbl">Agent</span>`);
  d.caller_audio.forEach(([s, e]) => laneC.append(h("div", { className: "bar caller", style: `left:${pct(s)};width:${pct(e - s)}` })));
  d.agent_audio.forEach(([s, e]) => laneA.append(h("div", { className: "bar agent", style: `left:${pct(s)};width:${pct(e - s)}` })));
  overlaps(d.caller_audio, d.agent_audio).forEach(([s, e]) => laneA.append(h("div", { className: "bar over", style: `left:${pct(s)};width:${pct(e - s)}`, title: "Talk-over" })));
  const marks = h("div", { className: "marks" });
  const kinds = { final: "final", cancel_sent: "cancel", playback_stopped: "stop", error: "err", speech_started: "" };
  d.events.filter(e => e.kind in kinds).forEach(e => marks.append(h("div", { className: "mk " + kinds[e.kind], style: `left:${pct(e.t)}`, title: e.kind })));
  const head = h("div", { className: "head", style: "left:0" });
  track.append(laneC, laneA, marks, head);
  tl.append(track);
  const legend = h("div", { className: "legend" }, `<span><i style="background:var(--caller)"></i>Caller speaking</span><span><i style="background:var(--agent)"></i>Agent speaking</span><span><i style="background:var(--bad)"></i>Talk-over</span><span><i style="background:var(--good)"></i>Final transcript</span><span><i style="background:var(--warn)"></i>Cancel / stop</span><span><i style="background:var(--muted)"></i>Speech started</span>`);
  const caption = h("div", { className: "caption" }, `<span class="who">Live transcript</span>Press play, or drag the timeline.`);
  root.append(controls, tl, legend, caption);

  const textEvents = d.events.filter(e => ["partial", "final", "reply_sent", "error", "gave_up_waiting", "cancel_sent", "playback_stopped", "update_config"].includes(e.kind));
  function render(ms) {
    head.style.left = pct(Math.min(ms, dur));
    time.textContent = `${fmt(ms)} / ${fmt(dur)}`;
    tl.setAttribute("aria-valuenow", String(Math.round(ms / 1000)));
    const last = [...textEvents].reverse().find(e => e.t <= ms);
    if (!last) { caption.innerHTML = `<span class="who">Live transcript</span>&nbsp;`; return; }
    const lines = {
      partial: ["Caller (partial transcript)", last.text],
      final: ["Caller (final transcript)", last.text],
      reply_sent: ["Agent reply sent to TTS-1", last.text],
      error: ["Error frame", `${last.code}: ${last.error}`],
      gave_up_waiting: ["Caller", `waited ${fmt(last.waited_ms)} and heard nothing`],
      cancel_sent: ["Agent", `caller interrupted: Cancel sent (${last.buffered_ms} ms already buffered)`],
      playback_stopped: ["Agent", `local playback stopped, ${last.dropped_ms} ms of buffered audio dropped`],
      update_config: ["Agent", "UpdateConfiguration " + JSON.stringify(Object.fromEntries(Object.entries(last).filter(([k]) => !["t", "src", "kind"].includes(k))))],
    }[last.kind];
    caption.innerHTML = `<span class="who">${lines[0]} at ${fmt(last.t)}</span>${escapeHtml(lines[1] || "")}`;
  }
  // Position shown while the audio element catches up to a seek.
  let pos = 0, raf;
  const tick = () => { if (!audio.seeking) pos = audio.currentTime * 1000; render(pos); if (!audio.paused) raf = requestAnimationFrame(tick); };
  async function seek(ms) {
    pos = Math.max(0, Math.min(dur, ms)); render(pos);
    await ready;
    audio.currentTime = pos / 1000;
    if (audio.ended || pos >= dur) audio.pause();
  }
  btn.onclick = async () => {
    document.querySelectorAll("audio,video").forEach(a => a !== audio && a.pause && a.pause());
    document.querySelectorAll(".player").forEach(p => p._audio && p._audio !== audio && p._audio.pause());
    if (!audio.paused) return audio.pause();
    await ready;
    if (pos >= dur - 50) audio.currentTime = pos = 0;
    audio.play();
  };
  back.onclick = () => seek(pos - 5000);
  fwd.onclick = () => seek(pos + 5000);
  audio.onplay = () => { btn.innerHTML = "&#10074;&#10074;"; btn.ariaLabel = "Pause"; tick(); };
  audio.onpause = audio.onended = () => { btn.innerHTML = "&#9654;"; btn.ariaLabel = "Play recording"; cancelAnimationFrame(raf); render(pos); };
  audio.onseeked = () => { if (audio.paused) render(pos); };
  // Drag to scrub. Pointer capture keeps the drag alive outside the track.
  const at = ev => { const r = track.getBoundingClientRect(); return dur * Math.max(0, Math.min(1, (ev.clientX - r.left) / r.width)); };
  let dragging = false;
  tl.onpointerdown = ev => { dragging = true; tl.setPointerCapture(ev.pointerId); seek(at(ev)); };
  tl.onpointermove = ev => { if (dragging) seek(at(ev)); };
  tl.onpointerup = tl.onpointercancel = () => { dragging = false; };
  tl.onkeydown = ev => {
    const step = { ArrowLeft: -1000, ArrowRight: 1000, Home: -Infinity, End: Infinity }[ev.key];
    if (step !== undefined) { ev.preventDefault(); seek(isFinite(step) ? pos + step : (step < 0 ? 0 : dur)); }
    else if (ev.key === " ") { ev.preventDefault(); btn.click(); }
  };
  root._audio = audio;
  render(0);
  return root;
}

function escapeHtml(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

function metricTiles(wall, d, m) {
  if (!d) return "";
  const ev = d.events, tiles = [];
  const fixed = wall.variant === "fixed";
  if (wall.id === "cutoff") {
    const numberFinals = ev.filter(e => e.kind === "final").slice(1);
    const lastSay = ev.filter(e => e.kind === "say_start").pop();
    const callerDone = lastSay.at + lastSay.dur_ms;
    const lastFinal = numberFinals[numberFinals.length - 1];
    tiles.push([numberFinals.length, numberFinals.length === 1 ? "turn for the callback number" : "turns the callback number got split into", fixed ? "good" : "bad"]);
    tiles.push([`"${escapeHtml(numberFinals[0].text)}"`, "what the agent answered", fixed ? "good" : "bad"]);
    if (lastFinal && fixed) tiles.push([fmt(lastFinal.t - callerDone), "last digit to final transcript (the cost of the fix)", ""]);
  } else if (wall.id === "bargein") {
    const cut = ev.filter(e => e.kind === "say_start")[1].at;
    const stale = d.agent_audio.filter(a => a[2] === 0).reduce((t, [s, e]) => t + Math.max(0, e - Math.max(s, cut)), 0);
    const c = ev.find(e => e.kind === "cancel_sent");
    tiles.push([fmt(stale), "the old reply kept playing after the caller cut in", fixed ? "good" : "bad"]);
    tiles.push([c ? fmt(c.buffered_ms) : "n/a", c ? "of the old reply already in the local buffer at Cancel time" : "no Cancel sent", ""]);
    const cancelled = ev.find(e => e.kind === "cancelled");
    if (cancelled) tiles.push([cancelled.audio_s + " s", "audio the server still had in flight (from Cancelled)", ""]);
  } else if (wall.id === "mute") {
    const q = ev.find(e => e.kind === "final");
    const play = ev.find(e => e.kind === "playback_start" && e.t > q.t);
    const asks = ev.filter(e => e.kind === "say_start" && /still there/.test(e.text)).length;
    tiles.push([play ? fmt(play.t - q.t) : "never", "from the first question to the agent's first sound", fixed ? "good" : "bad"]);
    tiles.push([asks, "times the caller had to ask \"are you still there?\"", asks ? "bad" : "good"]);
  }
  return `<div class="metrics">${tiles.map(([v, k, c]) => `<div class="metric"><div class="v ${c}">${v}</div><div class="k">${k}</div></div>`).join("")}</div>`;
}

async function wallCard(w) {
  const card = h("article", { className: "card", id: w.id });
  card.innerHTML = `<h2>${w.title}</h2><div class="ticket">&ldquo;${w.ticket}&rdquo;<br><span class="note" style="font-style:normal">Example ticket, written from the symptom.</span></div>`;
  const seg = h("div", { className: "seg", role: "group", ariaLabel: "Version" });
  const body = h("div");
  card.append(seg, body);
  const detail = h("div", {}, `
    <div class="grid2">
      <div><h3>Why it happens</h3><p>${w.why}</p><h3>The fix</h3><pre><code>${escapeHtml(w.fix)}</code></pre></div>
      <div><h3>Triage playbook entry</h3><table class="playbook">${w.playbook.map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join("")}</table>
      <h3>Sources</h3><p class="src">${w.sources.map(([t, u]) => `<a href="${u}" target="_blank" rel="noopener">${t}</a>`).join("<br>")}</p></div>
    </div>`);
  card.append(detail);
  async function show(variant) {
    seg.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === variant));
    body.querySelectorAll("audio").forEach(a => a.pause());
    const old = body.querySelector(".player"); if (old && old._audio) old._audio.pause();
    const d = await load(`${w.id}-${variant}`);
    body.innerHTML = metricTiles({ ...w, variant }, d, d ? metrics(d) : null);
    body.append(player(d));
  }
  w.variants.forEach(([v, label, tone]) => {
    const b = h("button", { type: "button", className: tone }, label); b.dataset.v = v; b.onclick = () => show(v); seg.append(b);
  });
  await show(w.variants[0][0]);
  return card;
}

async function retryCard() {
  const d = await load("retry");
  const card = h("article", { className: "card", id: "retry" });
  const rows = d ? d.events.filter(e => ["error", "begin", "handshake_failed"].includes(e.kind)).map(e => {
    const bad = e.kind === "error" || e.kind === "handshake_failed";
    return `<div class="${bad ? "e" : "ok"}">${String(e.t).padStart(6)} ms  ${e.src.toUpperCase()}  ${escapeHtml(e.label || "")}  ${e.kind === "error" ? `${e.code} ${escapeHtml(e.error || "")}${e.retryable === false ? "  (retryable: false)" : ""}` : e.kind === "begin" ? "session opened (then closed right away)" : escapeHtml(e.kind)}</div>`;
  }).join("") : `<div>Recording not available yet.</div>`;
  card.innerHTML = `<h2>4. A 1008 that shouldn't be retried</h2>
    <div class="ticket">&ldquo;Our streaming client hammers your API in a reconnect loop and never recovers.&rdquo;<br><span class="note" style="font-style:normal">Example ticket, written from the symptom.</span></div>
    <p>On streaming STT, close code <code>1008</code> means two opposite things. A bad key, an expired token, or no funds fails forever until someone fixes it. "Too many concurrent sessions" is a limit on new sessions per minute, so backing off and retrying is exactly right. In this run it fired on the 6th session start even though every earlier session was already closed, which matches the docs' note that the wording is misleading. TTS-1 splits the two cases apart (<code>3009</code> with the allowance and a retry time, <code>1008</code> with <code>retryable: false</code>), so one client has to handle the two products differently. Both allowed 5 new sessions a minute on this free-tier account.</p>
    <h3>Recorded run</h3><div class="log">${rows}</div>
    <div class="grid2" style="margin-top:14px"><div><h3>The fix</h3><pre><code>${escapeHtml(`def should_retry(product, code, error):
    if product == "stt" and code == 1008:
        return error.startswith("Unauthorized Connection: Too many")
    if product == "tts":
        return code in (1006, 1011, 3005, 3009)
    return code not in (1008, 3006, 3012, 3014)`)}</code></pre></div>
    <div><h3>Triage playbook entry</h3><table class="playbook">
      <tr><td>Symptom</td><td>Reconnect loop, every attempt closes 1008. Or the reverse: a client that never retries 1008 drops calls during a burst.</td></tr>
      <tr><td>User error, bug, or gap?</td><td>Usage, set up by a product inconsistency: one code, two meanings on STT.</td></tr>
      <tr><td>Check first</td><td>The error text of the Error frame before the close, not the close code.</td></tr>
      <tr><td>Product note</td><td>Give the STT rate limit its own code (like TTS 3009), or add <code>retryable</code> to STT Error frames the way TTS already does.</td></tr>
    </table></div></div>
    <p class="src"><a href="https://www.assemblyai.com/docs/streaming/common-session-errors-and-closures" target="_blank" rel="noopener">Streaming: common session errors and closures</a><br><a href="https://www.assemblyai.com/docs/tts/error-handling" target="_blank" rel="noopener">TTS: error handling</a></p>`;
  return card;
}

async function baselineSection() {
  const d = await load("baseline");
  const sec = $("#baseline");
  sec.innerHTML = `<h2>First, a normal call</h2><p class="lede">Three turns, balanced mode, everything wired up the way the docs say. This is the bar each wall falls below.</p>`;
  const card = h("div", { className: "card" });
  if (d) {
    const m = metrics(d);
    const med = arr => { const s = arr.filter(x => x != null).sort((a, b) => a - b); return s.length ? s[Math.floor(s.length / 2)] : null; };
    const ep = med(m.resp.map(r => r.endpoint)), tot = med(m.resp.map(r => r.total)), tts = med(m.resp.map(r => r.tts));
    card.innerHTML = `<div class="metrics">
      <div class="metric"><div class="v">${ep != null ? ep + " ms" : "n/a"}</div><div class="k">caller stops talking to final transcript (median of ${m.resp.length} turns)</div></div>
      <div class="metric"><div class="v">${tts != null ? tts + " ms" : "n/a"}</div><div class="k">reply sent to first agent audio playing (TTS-1, median)</div></div>
      <div class="metric"><div class="v">${tot != null ? tot + " ms" : "n/a"}</div><div class="k">caller stops to agent starts speaking (median)</div></div>
      <div class="metric"><div class="v ${m.talkOver ? "bad" : "good"}">${fmt(m.talkOver)}</div><div class="k">talk-over</div></div></div>`;
    $("#recDate").textContent = d.recorded;
  }
  card.append(player(d));
  sec.append(card);
}

function fileSection() {
  $("#file").innerHTML = `<h2>Things I'd file</h2><p class="lede">Found while setting this up. Small, but each one is a support thread that doesn't need to happen.</p>
    <div class="card"><ul class="files">${FILE_NOTES.map(([t, d]) => `<li><b>${t}.</b> ${escapeHtml(d)}</li>`).join("")}</ul></div>`;
}

(async function main() {
  const v = h("video", { controls: true, playsInline: true, preload: "auto", poster: "video-poster.jpg" });
  mediaUrl("video.mp4").then(u => { v.src = u; });
  v.onerror = () => { $("#video").innerHTML = `<span>Demo video coming soon</span>`; };
  $("#video").innerHTML = ""; $("#video").append(v);
  await baselineSection();
  const walls = $("#walls");
  for (const w of WALLS) walls.append(await wallCard(w));
  walls.append(await retryCard());
  fileSection();
})();
