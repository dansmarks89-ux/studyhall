// Study Hall voice function: speech for the courses (Microsoft Azure neural voices, and Google voices when a
// Google key is set), each clip stored once in the public "audio" bucket; and speech-to-text for speaking practice.
//
// Learner ops (signed-in user's JWT in Authorization, invited to the course):
//   op "catalog" { op, course } -> { voices: Voice[], default: id }   the course's voices that really exist
//   op "say"     { op, course, text, voice? } -> { url }   clip for any text; voice must be in the catalog (else the
//                default). An existing clip is returned without counting; new clips count against SAY_LIMIT per day.
//   op "stt"     { op, course, audio } -> { text, confidence }   audio = base64 16 kHz mono PCM16 WAV, <= 60 s;
//                text "" when nothing was heard. Counts against STT_LIMIT per day (public.stt_usage).
// Admin ops (admin token):
//   op "batch"   { op, token, items: [{course, text, voice, rate?}] } -> per-item results (fixed Azure voices only)
//   op "voices"  { op, token } -> Azure voices for the four languages, and Google voices if the key is set
//   op "sync"    { op, token, course } -> records every clip in <course>/audio.json (from the GitHub repo)
//                that isn't in the bucket yet; restarts itself until done. Progress is in public.tts_sync.
// Errors are { code, error }: bad_request, session_expired, not_granted, rate_limited, upstream, server.
// Clip name = first 32 hex of sha256(voice + "|" + rate + "|" + text); the browser computes the same name.
//
// Secrets: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION, optional GOOGLE_TTS_KEY. The admin token lives in the
// database (private.secrets).
import { createClient } from "npm:@supabase/supabase-js@2";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const out = (status: number, body: unknown) =>
  new Response(JSON.stringify(body), { status, headers: { ...CORS, "Content-Type": "application/json" } });

function secretKey(): string {
  const raw = Deno.env.get("SUPABASE_SECRET_KEYS");
  if (raw) { try { const k = JSON.parse(raw); if (k && k["default"]) return k["default"]; } catch (_) { /* fall through */ } }
  return Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
}
const URL_ = Deno.env.get("SUPABASE_URL")!;
const admin = createClient(URL_, secretKey(), { auth: { persistSession: false, autoRefreshToken: false } });
const clean = (s: string | undefined) => (s || "").trim().replace(/^["']|["']$/g, "");
const AZ_KEY = clean(Deno.env.get("AZURE_SPEECH_KEY"));
const AZ_REGION = clean(Deno.env.get("AZURE_SPEECH_REGION")).toLowerCase().replace(/\s+/g, "");
const G_KEY = clean(Deno.env.get("GOOGLE_TTS_KEY"));

// Candidate voices per course, in the order learners see them; the first is the course default (the voice the
// pre-recorded clips use). A "*" entry matches every voice of that shape the provider lists.
// lang = SSML language, google = Google languageCode, stt = recognition language.
type Course = { lang: string; google: string; stt: string; azure: string[]; googleVoices: string[] };
const chirp = (code: string, names: string[]) => names.map((n) => `${code}-Chirp3-HD-${n}`);
const CHIRP6 = ["Aoede", "Kore", "Leda", "Charon", "Puck", "Fenrir"];
const COURSES: Record<string, Course> = {
  spanish: { lang: "es-MX", google: "es-US", stt: "es-MX",
    azure: ["es-MX-DaliaNeural", "es-MX-JorgeNeural", "es-MX-*:DragonHDLatestNeural", "es-US-PalomaNeural", "es-US-AlonsoNeural", "es-US-*:DragonHDLatestNeural"],
    googleVoices: chirp("es-US", CHIRP6) },
  cantonese: { lang: "zh-HK", google: "yue-HK", stt: "zh-HK",
    azure: ["zh-HK-HiuMaanNeural", "zh-HK-WanLungNeural", "zh-HK-HiuGaaiNeural"], googleVoices: chirp("yue-HK", CHIRP6) },
  korean: { lang: "ko-KR", google: "ko-KR", stt: "ko-KR",
    azure: ["ko-KR-SunHi:DragonHDLatestNeural", "ko-KR-Hyunsu:DragonHDLatestNeural", "ko-KR-SunHiNeural", "ko-KR-InJoonNeural", "ko-KR-HyunsuNeural"],
    googleVoices: chirp("ko-KR", CHIRP6) },
  vocab: { lang: "en-US", google: "en-US", stt: "en-US",
    azure: ["en-US-Ava:DragonHDLatestNeural", "en-US-Andrew:DragonHDLatestNeural", "en-US-Emma:DragonHDLatestNeural", "en-US-Brian:DragonHDLatestNeural", "en-US-AvaNeural", "en-US-AndrewNeural"],
    googleVoices: chirp("en-US", ["Aoede", "Kore", "Charon", "Puck"]) },
};
// The fixed Azure voices of a course: the only voices batch and sync record with.
const fixedVoices = (c: Course) => c.azure.filter((v) => !v.includes("*"));
const ACCENT: Record<string, string> = { "es-MX": "Mexico", "es-US": "US" };
const RATES = new Set(["0%", "-10%", "-20%"]);
const SAY_LIMIT = 600;
const STT_LIMIT = 400;
const MAX_TEXT = 400;
const MAX_WAV = 2.5 * 1024 * 1024;   // decoded recording
const MAX_BODY = 3600 * 1024;        // request body: the recording in base64 plus a little JSON

const xml = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
async function hash(s: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}
const clipName = (voice: string, rate: string, text: string) => hash(voice + "|" + rate + "|" + text);
const publicUrl = (path: string) => `${URL_}/storage/v1/object/public/audio/${path}`;
const errText = (e: unknown) => String((e as Error)?.message || e).slice(0, 200);

function b64decode(s: string): Uint8Array<ArrayBuffer> | null {
  if (!s || s.length % 4 !== 0 || !/^[A-Za-z0-9+/]+={0,2}$/.test(s)) return null;
  try {
    const bin = atob(s), a = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i);
    return a;
  } catch (_) { return null; }
}

async function exists(course: string, name: string): Promise<boolean> {
  const { data } = await admin.storage.from("audio").list(course, { search: name + ".mp3", limit: 2 });
  return !!(data && data.some((f) => f.name === name + ".mp3"));
}
async function put(path: string, mp3: Uint8Array) {
  const { error } = await admin.storage.from("audio").upload(path, mp3, { contentType: "audio/mpeg", cacheControl: "31536000", upsert: true });
  if (error) throw new Error("upload " + error.message);
}

// ---------- provider voice lists (kept 6 hours per warm instance; a failed load isn't kept) ----------
const lists = new Map<string, { at: number; p: Promise<unknown> }>();
function cached<T>(key: string, load: () => Promise<T>): Promise<T> {
  const hit = lists.get(key);
  if (hit && Date.now() - hit.at < 6 * 3600 * 1000) return hit.p as Promise<T>;
  const p = load();
  lists.set(key, { at: Date.now(), p });
  p.catch(() => { if (lists.get(key)?.p === p) lists.delete(key); });
  return p;
}
type AzVoice = { ShortName: string; Locale: string; Gender: string; VoiceType: string; Status: string };
type GVoice = { name: string; languageCodes: string[]; ssmlGender: string };
const azureVoices = () => cached("azure", async () => {
  const r = await fetch(`https://${AZ_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list`, { headers: { "Ocp-Apim-Subscription-Key": AZ_KEY } });
  if (!r.ok) throw new Error(`azure voices ${r.status}`);
  return (await r.json()) as AzVoice[];
});
const googleVoices = (code: string) => cached("google:" + code, async () => {
  const r = await fetch(`https://texttospeech.googleapis.com/v1/voices?languageCode=${encodeURIComponent(code)}`, { headers: { "X-Goog-Api-Key": G_KEY } });
  if (!r.ok) throw new Error(`google voices ${r.status}`);
  return ((await r.json()) as { voices?: GVoice[] }).voices || [];
});

// ---------- catalog ----------
type Voice = { id: string; label: string; provider: "azure" | "google"; hd: boolean; gender: "female" | "male"; accent?: string };
const gender = (g: string): "female" | "male" => (/^male$/i.test(g) ? "male" : "female");
const accentOf = (course: string, id: string) => (course === "spanish" ? ACCENT[id.slice(0, 5)] : undefined);
const voiceLabel = (...parts: Array<string | undefined>) => parts.filter(Boolean).join(" · ");

async function catalog(course: string): Promise<{ voices: Voice[]; default: string }> {
  const c = COURSES[course];
  const az = await azureVoices();
  const voices: Voice[] = [];
  const add = (v: Voice) => { if (!voices.some((x) => x.id === v.id)) voices.push(v); };
  for (const cand of c.azure) {
    const re = new RegExp("^" + cand.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace("*", "[A-Za-z0-9]+") + "$");
    for (const v of az.filter((x) => re.test(x.ShortName)).sort((a, b) => a.ShortName.localeCompare(b.ShortName))) {
      const hd = v.ShortName.endsWith(":DragonHDLatestNeural");
      const name = v.ShortName.slice(v.Locale.length + 1).replace(/:DragonHDLatestNeural$|Neural$/, "");
      const accent = accentOf(course, v.ShortName);
      add({ id: v.ShortName, label: voiceLabel(name, hd ? "HD" : "standard", accent), provider: "azure", hd, gender: gender(v.Gender), ...(accent ? { accent } : {}) });
    }
  }
  if (G_KEY) {
    try {
      const gv = new Map((await googleVoices(c.google)).map((v) => [v.name, v]));
      for (const id of c.googleVoices) {
        const v = gv.get(id);
        if (!v) continue;
        const accent = accentOf(course, id);
        add({ id, label: voiceLabel(id.split("-").pop(), "Google HD", accent), provider: "google", hd: true, gender: gender(v.ssmlGender), ...(accent ? { accent } : {}) });
      }
    } catch (e) { console.error("google voices", errText(e)); }
  }
  const def = voices.some((v) => v.id === c.azure[0]) ? c.azure[0] : (voices[0]?.id || "");
  return { voices, default: def };
}

// The voice "say" uses. The fixed Azure voices (and no voice = the course default) are used as they always were,
// without the voice lists, so the pre-recorded clips keep matching; any other voice must be in the catalog.
async function pickVoice(course: string, requested: string): Promise<{ id: string; provider: "azure" | "google" }> {
  const c = COURSES[course];
  if (fixedVoices(c).includes(requested)) return { id: requested, provider: "azure" };
  if (requested) {
    try {
      const v = (await catalog(course)).voices.find((x) => x.id === requested);
      if (v) return { id: v.id, provider: v.provider };
    } catch (e) { console.error("catalog", errText(e)); }
  }
  return { id: c.azure[0], provider: "azure" };
}

// ---------- synthesis ----------
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
// The HD voices sometimes return no audio for a single very short word; those clips use the standard voice.
const FALLBACK: Record<string, string> = { "ko-KR-SunHi:DragonHDLatestNeural": "ko-KR-SunHiNeural", "ko-KR-Hyunsu:DragonHDLatestNeural": "ko-KR-HyunsuNeural" };
async function synth(text: string, voice: string, rate: string, lang: string): Promise<Uint8Array> {
  for (let attempt = 0; ; attempt++) {
    try { return await synthOnce(text, voice, rate, lang); }
    catch (e) {
      const m = String((e as Error).message || e);
      if (attempt < 6 && /azure (429|5\d\d)/.test(m)) { await sleep(Math.min(30000, 2500 * (attempt + 1))); continue; }
      if (/returned only/.test(m) && FALLBACK[voice]) return await synthOnce(text, FALLBACK[voice], rate, lang);
      throw e;
    }
  }
}
async function synthOnce(text: string, voice: string, rate: string, lang: string): Promise<Uint8Array> {
  const body = `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="${lang}"><voice name="${voice}"><prosody rate="${rate}">${xml(text)}</prosody></voice></speak>`;
  const r = await fetch(`https://${AZ_REGION}.tts.speech.microsoft.com/cognitiveservices/v1`, {
    method: "POST",
    headers: {
      "Ocp-Apim-Subscription-Key": AZ_KEY,
      "Content-Type": "application/ssml+xml",
      "X-Microsoft-OutputFormat": "audio-24khz-48kbitrate-mono-mp3",
      "User-Agent": "studyhall",
    },
    body,
  });
  if (!r.ok) {
    const t = (await r.text().catch(() => "")).slice(0, 200);
    throw new Error(`azure ${r.status} ${t}`);
  }
  const buf = new Uint8Array(await r.arrayBuffer());
  if (buf.length < 500) throw new Error(`azure returned only ${buf.length} bytes`);
  return buf;
}
async function synthGoogle(text: string, voice: string, languageCode: string): Promise<Uint8Array> {
  const r = await fetch("https://texttospeech.googleapis.com/v1/text:synthesize", {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Goog-Api-Key": G_KEY },
    body: JSON.stringify({ input: { text }, voice: { languageCode, name: voice }, audioConfig: { audioEncoding: "MP3" } }),
  });
  const j = await r.json().catch(() => null) as { audioContent?: string; error?: { message?: string } } | null;
  if (!r.ok) throw new Error(`google ${r.status} ${String(j?.error?.message || "").slice(0, 200)}`);
  const mp3 = b64decode(String(j?.audioContent || ""));
  if (!mp3 || mp3.length < 500) throw new Error(`google returned only ${mp3 ? mp3.length : 0} bytes`);
  return mp3;
}

// batch: validate, then record the clip unless it already exists.
async function ensure(course: string, text: string, voice: string, rate: string) {
  const c = COURSES[course];
  if (!c) throw new Error("bad course");
  if (!fixedVoices(c).includes(voice)) throw new Error("bad voice");
  if (!RATES.has(rate)) throw new Error("bad rate");
  if (!text || text.length > MAX_TEXT) throw new Error("bad text");
  const name = await clipName(voice, rate, text);
  const path = `${course}/${name}.mp3`;
  if (await exists(course, name)) return { made: false, bytes: 0, path };
  const mp3 = await synth(text, voice, rate, c.lang);
  await put(path, mp3);
  return { made: true, bytes: mp3.length, path };
}

// ---------- sync: record everything listed in the course's audio.json ----------
const REPO_RAW = "https://raw.githubusercontent.com/dansmarks89-ux/studyhall/main/";
async function existingNames(course: string): Promise<Set<string>> {
  const names = new Set<string>();
  for (let offset = 0; ; offset += 1000) {
    const { data, error } = await admin.storage.from("audio").list(course, { limit: 1000, offset, sortBy: { column: "name", order: "asc" } });
    if (error) throw new Error("list " + error.message);
    (data || []).forEach((f) => names.add(f.name.replace(/\.mp3$/, "")));
    if (!data || data.length < 1000) break;
  }
  return names;
}
async function sync(course: string, token: string) {
  const c = COURSES[course];
  if (!c) return out(400, { code: "bad_request", error: "Bad course" });
  const voices = fixedVoices(c);
  const started = Date.now();
  const r = await fetch(REPO_RAW + course + "/audio.json", { cache: "no-store" });
  if (!r.ok) return out(502, { code: "upstream", error: "Couldn't read audio.json: " + r.status });
  const list = (await r.json()) as Array<{ n: string; t: string; v: string; r: string }>;
  const have = await existingNames(course);
  const todo = list.filter((x) => !have.has(x.n));
  const { data: prev } = await admin.from("tts_sync").select("*").eq("course", course).maybeSingle();
  let made = 0, failed = 0, lastError = "";
  for (const x of todo) {
    if (Date.now() - started > 100000) break;
    try {
      if (!voices.includes(x.v) || !RATES.has(x.r)) throw new Error("bad voice/rate " + x.v);
      if ((await clipName(x.v, x.r, x.t)) !== x.n) throw new Error("name mismatch for " + x.t.slice(0, 20));
      await put(`${course}/${x.n}.mp3`, await synth(x.t, x.v, x.r, c.lang));
      made++;
    } catch (e) {
      failed++; lastError = (x.t.slice(0, 30) + ": " + String((e as Error).message || e)).slice(0, 300);
      if (/azure 40[13]/.test(lastError)) break;  // bad key or region: stop
    }
  }
  const remaining = todo.length - made;
  await admin.from("tts_sync").upsert({ course, total: list.length, existing: have.size, made: (prev?.made || 0) + made, failed: (prev?.failed || 0) + failed,
    remaining, last_error: lastError || prev?.last_error || null, runs: (prev?.runs || 0) + 1, updated_at: new Date().toISOString() });
  const again = remaining > 0 && made > 0 && ((prev?.runs || 0) < 400);
  if (again) {
    // keep going in a fresh invocation
    // deno-lint-ignore no-explicit-any
    (globalThis as any).EdgeRuntime?.waitUntil(fetch(`${URL_}/functions/v1/tts`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ op: "sync", token, course }) }).catch(() => {}));
  }
  return out(200, { total: list.length, existing: have.size, made, failed, remaining, continuing: again, lastError });
}

// ---------- speech to text ----------
// Length in seconds of a WAV the recognizer accepts (PCM, mono, 16 kHz, 16-bit); null for anything else.
function wavSeconds(b: Uint8Array): number | null {
  const dv = new DataView(b.buffer, b.byteOffset, b.byteLength);
  const tag = (o: number) => String.fromCharCode(b[o], b[o + 1], b[o + 2], b[o + 3]);
  if (b.length < 44 || tag(0) !== "RIFF" || tag(8) !== "WAVE") return null;
  let fmtOk = false;
  for (let o = 12; o + 8 <= b.length;) {
    const id = tag(o), size = dv.getUint32(o + 4, true);
    if (id === "fmt ") {
      if (size < 16 || o + 24 > b.length) return null;
      fmtOk = dv.getUint16(o + 8, true) === 1 && dv.getUint16(o + 10, true) === 1 && dv.getUint32(o + 12, true) === 16000 && dv.getUint16(o + 22, true) === 16;
      if (!fmtOk) return null;
    } else if (id === "data") {
      if (!fmtOk || size === 0 || o + 8 + size > b.length) return null;
      return size / 32000;
    }
    o += 8 + size + (size & 1);
  }
  return null;
}
async function recognize(wav: Uint8Array<ArrayBuffer>, language: string): Promise<{ text: string; confidence: number }> {
  const r = await fetch(`https://${AZ_REGION}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1?language=${language}&format=detailed`, {
    method: "POST",
    headers: { "Ocp-Apim-Subscription-Key": AZ_KEY, "Content-Type": "audio/wav; codecs=audio/pcm; samplerate=16000", Accept: "application/json" },
    body: wav,
  });
  if (!r.ok) throw new Error(`azure stt ${r.status} ${(await r.text().catch(() => "")).slice(0, 200)}`);
  const j = await r.json() as { RecognitionStatus?: string; DisplayText?: string; NBest?: Array<{ Display?: string; Confidence?: number }> };
  if (j.RecognitionStatus === "Success") {
    const best = j.NBest?.[0];
    return { text: String(best?.Display ?? j.DisplayText ?? ""), confidence: Number(best?.Confidence) || 0 };
  }
  if (j.RecognitionStatus === "NoMatch" || j.RecognitionStatus === "InitialSilenceTimeout") return { text: "", confidence: 0 };
  throw new Error(`azure stt status ${String(j.RecognitionStatus).slice(0, 40)}`);
}

// ---------- request helpers ----------
// The JSON body, read with a size cap so an oversized upload is refused before it is all in memory.
async function readBody(req: Request): Promise<Record<string, unknown> | Response> {
  const tooBig = () => out(413, { code: "bad_request", error: "The recording is too long." });
  if (Number(req.headers.get("Content-Length") || 0) > MAX_BODY) return tooBig();
  const chunks: Uint8Array[] = [];
  let n = 0;
  if (req.body) {
    const reader = req.body.getReader();
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      n += value.length;
      if (n > MAX_BODY) { await reader.cancel().catch(() => {}); return tooBig(); }
      chunks.push(value);
    }
  }
  const all = new Uint8Array(n);
  let o = 0;
  for (const c of chunks) { all.set(c, o); o += c.length; }
  try {
    const body = JSON.parse(new TextDecoder().decode(all));
    if (body && typeof body === "object" && !Array.isArray(body)) return body as Record<string, unknown>;
  } catch (_) { /* fall through */ }
  return out(400, { code: "bad_request", error: "Bad JSON" });
}
// The signed-in user, if they are invited to the course.
async function member(req: Request, course: string): Promise<{ id: string } | Response> {
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!token) return out(401, { code: "session_expired", error: "Not signed in" });
  const { data: u, error: ue } = await admin.auth.getUser(token);
  if (ue || !u?.user) return out(401, { code: "session_expired", error: "Sign in again" });
  if (!COURSES[course]) return out(400, { code: "bad_request", error: "Bad course" });
  const email = (u.user.email || "").toLowerCase();
  const { data: inv } = await admin.from("invites").select("courses").eq("email", email).maybeSingle();
  const courses: string[] = inv?.courses || [];
  if (!courses.includes("*") && !courses.includes(course)) return out(403, { code: "not_granted", error: "Not invited to this course" });
  return { id: u.user.id };
}
// Counts one more use today; false = the daily limit is reached.
async function consume(fn: "tts_consume" | "stt_consume", uid: string, lim: number): Promise<boolean | Response> {
  const { data, error } = await admin.rpc(fn, { uid, lim });
  if (error) { console.error(fn, errText(error)); return out(500, { code: "server", error: "Usage check failed" }); }
  return data !== null;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return out(405, { code: "bad_request", error: "POST only" });
  if (!AZ_KEY || !AZ_REGION) return out(503, { code: "server", error: "Voices aren't set up yet." });
  const body = await readBody(req);
  if (body instanceof Response) return body;
  const op = String(body.op || "");

  if (op === "batch" || op === "voices" || op === "sync") {
    const { data: ok } = await admin.rpc("tts_admin_ok", { t: String(body.token || "") });
    if (ok !== true) return out(403, { code: "not_granted", error: "Admin only" });
    if (op === "voices") {
      let all: AzVoice[];
      try { all = await azureVoices(); } catch (e) { return out(502, { code: "upstream", error: errText(e) }); }
      const pick = all.filter((v) => /^(zh-HK|ko-KR|en-US|es-)/.test(v.Locale))
        .map((v) => ({ name: v.ShortName, locale: v.Locale, gender: v.Gender, type: v.VoiceType, status: v.Status }));
      const google: unknown[] = [];
      if (G_KEY) {
        for (const code of new Set(Object.values(COURSES).map((c) => c.google))) {
          try { (await googleVoices(code)).forEach((v) => google.push({ name: v.name, languages: v.languageCodes, gender: v.ssmlGender })); }
          catch (e) { google.push({ language: code, error: errText(e) }); }
        }
      }
      return out(200, { count: all.length, voices: pick, google });
    }
    if (op === "sync") return await sync(String(body.course || ""), String(body.token || ""));
    const items = Array.isArray(body.items) ? body.items.slice(0, 40) : [];
    const results: unknown[] = [];
    for (const it of items as Array<Record<string, string>>) {
      try {
        const r = await ensure(String(it.course), String(it.text), String(it.voice), String(it.rate || "0%"));
        results.push({ k: it.k, ok: true, ...r });
      } catch (e) {
        results.push({ k: it.k, ok: false, error: errText(e) });
      }
    }
    return out(200, { n: results.length, results });
  }

  if (op !== "catalog" && op !== "say" && op !== "stt") return out(400, { code: "bad_request", error: "Unknown op" });
  const course = String(body.course || "");
  const user = await member(req, course);
  if (user instanceof Response) return user;
  const c = COURSES[course];

  if (op === "catalog") {
    try { return out(200, await catalog(course)); }
    catch (e) {
      console.error("catalog", errText(e));
      return out(502, { code: "upstream", error: "Couldn't load the voice list." });
    }
  }

  if (op === "say") {
    const text = String(body.text || "").trim();
    if (!text || text.length > MAX_TEXT) return out(400, { code: "bad_request", error: `Text must be 1 to ${MAX_TEXT} characters.` });
    const voice = await pickVoice(course, String(body.voice || ""));
    const name = await clipName(voice.id, "0%", text);
    const path = `${course}/${name}.mp3`;
    if (await exists(course, name)) return out(200, { url: publicUrl(path) });
    const ok = await consume("tts_consume", user.id, SAY_LIMIT);
    if (ok instanceof Response) return ok;
    if (!ok) return out(429, { code: "rate_limited", error: `Daily limit of ${SAY_LIMIT} new voice clips reached.` });
    try {
      await put(path, voice.provider === "google" ? await synthGoogle(text, voice.id, c.google) : await synth(text, voice.id, "0%", c.lang));
      return out(200, { url: publicUrl(path) });
    } catch (e) {
      console.error("say failed", errText(e));
      return out(502, { code: "upstream", error: "Couldn't make the audio. The device voice will be used." });
    }
  }

  // stt
  const wav = b64decode(String(body.audio || ""));
  if (!wav) return out(400, { code: "bad_request", error: "The recording didn't arrive in a readable form." });
  const secs = wav.length > MAX_WAV ? Infinity : wavSeconds(wav);
  if (secs === null) return out(400, { code: "bad_request", error: "The recording isn't in the expected format." });
  if (secs > 60) return out(413, { code: "bad_request", error: "The recording is too long." });
  const ok = await consume("stt_consume", user.id, STT_LIMIT);
  if (ok instanceof Response) return ok;
  if (!ok) return out(429, { code: "rate_limited", error: `Daily limit of ${STT_LIMIT} recordings reached.` });
  try { return out(200, await recognize(wav, c.stt)); }
  catch (e) {
    console.error("stt failed", errText(e));
    return out(502, { code: "upstream", error: "Couldn't understand the recording right now. Try again or type it." });
  }
});
