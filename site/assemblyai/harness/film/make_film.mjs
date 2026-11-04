// Renders film.html frame by frame (exact times, so audio cannot drift), then
// lays the matching slices of the recorded call audio under each clip scene.
//   node make_film.mjs <base-url> [url-to-show-on-end-card]
// base-url serves site/ (e.g. http://127.0.0.1:8765). Needs playwright + ffmpeg.
import { chromium } from "playwright";
import { execFileSync, spawn } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FPS = 30;
const here = path.dirname(fileURLToPath(import.meta.url));
const site = path.resolve(here, "../..");                 // site/assemblyai
const [base, endUrl = ""] = process.argv.slice(2);
const work = mkdtempSync(path.join(tmpdir(), "film-"));

const browser = await chromium.launch({ executablePath: process.env.CHROME_PATH || undefined });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
await page.goto(`${base}/assemblyai/harness/film/film.html?url=${encodeURIComponent(endUrl)}`);
await page.waitForFunction(() => window.ready === true, null, { timeout: 30000 });
const { scenes, total } = await page.evaluate(() => ({ scenes: window.SCENES, total: window.TOTAL }));

// Video: one PNG per frame piped into ffmpeg.
const silentVideo = path.join(work, "video.mp4");
const enc = spawn("ffmpeg", ["-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
  "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-g", String(FPS), "-tune", "animation", silentVideo], { stdio: ["pipe", "inherit", "inherit"] });
const frames = Math.ceil(total / 1000 * FPS);
for (let f = 0; f < frames; f++) {
  await page.evaluate(ms => window.renderAt(ms), f * 1000 / FPS);
  const png = await page.screenshot({ type: "png" });
  if (!enc.stdin.write(png)) await new Promise(r => enc.stdin.once("drain", r));
  if (f % 100 === 0) console.log(`frame ${f}/${frames}`);
}
enc.stdin.end();
await new Promise(r => enc.on("close", r));
await browser.close();

// Audio: each clip scene's window of its run's mp3, placed at the scene's start.
const inputs = [], filters = [];
for (const sc of scenes) {
  if (sc.type !== "clip") continue;
  const n = inputs.length / 2;
  inputs.push("-i", path.join(site, "data", `${sc.run}.mp3`));
  const len = (sc.to - sc.from) / 1000;
  filters.push(`[${n}:a]atrim=start=${sc.from / 1000}:end=${sc.to / 1000},asetpts=PTS-STARTPTS,afade=t=in:d=0.05,afade=t=out:st=${len - 0.08}:d=0.08,adelay=${sc.start}|${sc.start}[a${n}]`);
}
const n = inputs.length / 2;
const audio = path.join(work, "audio.m4a");
execFileSync("ffmpeg", ["-loglevel", "error", "-y", ...inputs, "-f", "lavfi", "-t", String(total / 1000), "-i", "anullsrc=r=48000:cl=stereo", "-filter_complex",
  `${filters.join(";")};[${n}:a]${Array.from({ length: n }, (_, i) => `[a${i}]`).join("")}amix=inputs=${n + 1}:normalize=0:duration=first[out]`,
  "-map", "[out]", "-ac", "2", "-c:a", "aac", "-b:a", "128k", audio]);

const out = path.join(site, "video.mp4");
execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-i", silentVideo, "-i", audio, "-map", "0:v", "-map", "1:a",
  "-c:v", "copy", "-c:a", "copy", "-t", String(total / 1000), "-movflags", "+faststart", out]);
execFileSync("ffmpeg", ["-loglevel", "error", "-y", "-ss", "1.5", "-i", out, "-frames:v", "1", "-q:v", "3", path.join(site, "video-poster.jpg")]);
console.log("wrote", out, `${total / 1000}s`);
