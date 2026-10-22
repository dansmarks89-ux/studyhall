// Study Hall voice function: turns course text into speech with Microsoft Azure neural voices
// and stores each clip once in the public "audio" bucket.
//
//   op "say"    (signed-in, invited user): { op, course, text, voice? } -> { url }
//               Used for text that isn't pre-recorded (AI conversation replies). Daily limit per person.
//   op "batch"  (admin token):  { op, token, items: [{course, text, voice, rate?}] } -> per-item results
//   op "voices" (admin token):  { op, token } -> Cantonese and Korean voices available on the Azure resource
//   op "sync"   (admin token):  { op, token, course } -> records every clip in <course>/audio.json (from the GitHub repo)
//               that isn't in the bucket yet; restarts itself until done. Progress is in public.tts_sync.
//
// Secrets: AZURE_SPEECH_KEY, AZURE_SPEECH_REGION. The admin token lives in the database (private.secrets).
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

// Which voices each course may use, and its SSML language.
const COURSES: Record<string, { lang: string; voices: string[] }> = {
  cantonese: { lang: "zh-HK", voices: ["zh-HK-HiuMaanNeural", "zh-HK-WanLungNeural", "zh-HK-HiuGaaiNeural"] },
  korean: { lang: "ko-KR", voices: ["ko-KR-SunHi:DragonHDLatestNeural", "ko-KR-Hyunsu:DragonHDLatestNeural", "ko-KR-SunHiNeural", "ko-KR-InJoonNeural", "ko-KR-HyunsuNeural"] },
};
const RATES = new Set(["0%", "-10%", "-20%"]);
const SAY_LIMIT = 300;

const xml = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
async function hash(s: string): Promise<string> {
  const d = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, "0")).join("").slice(0, 32);
}
// The browser computes the same name, so it can play a clip without asking this function.
const clipName = (voice: string, rate: string, text: string) => hash(voice + "|" + rate + "|" + text);
const publicUrl = (path: string) => `${URL_}/storage/v1/object/public/audio/${path}`;

async function exists(course: string, name: string): Promise<boolean> {
  const { data } = await admin.storage.from("audio").list(course, { search: name + ".mp3", limit: 2 });
  return !!(data && data.some((f) => f.name === name + ".mp3"));
}

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

async function ensure(course: string, text: string, voice: string, rate: string) {
  const c = COURSES[course];
  if (!c) throw new Error("bad course");
  if (!c.voices.includes(voice)) throw new Error("bad voice");
  if (!RATES.has(rate)) throw new Error("bad rate");
  if (!text || text.length > 400) throw new Error("bad text");
  const name = await clipName(voice, rate, text);
  const path = `${course}/${name}.mp3`;
  if (await exists(course, name)) return { path, url: publicUrl(path), made: false, bytes: 0 };
  const mp3 = await synth(text, voice, rate, c.lang);
  const { error } = await admin.storage.from("audio").upload(path, mp3, { contentType: "audio/mpeg", cacheControl: "31536000", upsert: true });
  if (error) throw new Error("upload " + error.message);
  return { path, url: publicUrl(path), made: true, bytes: mp3.length };
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
      if (!c.voices.includes(x.v) || !RATES.has(x.r)) throw new Error("bad voice/rate " + x.v);
      if ((await clipName(x.v, x.r, x.t)) !== x.n) throw new Error("name mismatch for " + x.t.slice(0, 20));
      const mp3 = await synth(x.t, x.v, x.r, c.lang);
      const { error } = await admin.storage.from("audio").upload(`${course}/${x.n}.mp3`, mp3, { contentType: "audio/mpeg", cacheControl: "31536000", upsert: true });
      if (error) throw new Error("upload " + error.message);
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

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return out(405, { code: "bad_request", error: "POST only" });
  if (!AZ_KEY || !AZ_REGION) return out(503, { code: "server", error: "Voices aren't set up yet." });
  let body: Record<string, unknown>;
  try { body = await req.json(); } catch (_) { return out(400, { code: "bad_request", error: "Bad JSON" }); }
  const op = String(body.op || "");

  if (op === "batch" || op === "voices" || op === "sync") {
    const { data: ok } = await admin.rpc("tts_admin_ok", { t: String(body.token || "") });
    if (ok !== true) return out(403, { code: "not_granted", error: "Admin only" });
    if (op === "voices") {
      const r = await fetch(`https://${AZ_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list`, { headers: { "Ocp-Apim-Subscription-Key": AZ_KEY } });
      if (!r.ok) return out(502, { code: "upstream", status: r.status, error: (await r.text().catch(() => "")).slice(0, 300) });
      const all = await r.json();
      const pick = (all as Array<Record<string, string>>).filter((v) => v.Locale === "zh-HK" || v.Locale === "ko-KR")
        .map((v) => ({ name: v.ShortName, locale: v.Locale, gender: v.Gender, type: v.VoiceType, status: v.Status }));
      return out(200, { count: (all as unknown[]).length, voices: pick });
    }
    if (op === "sync") return await sync(String(body.course || ""), String(body.token || ""));
    const items = Array.isArray(body.items) ? body.items.slice(0, 40) : [];
    const results: unknown[] = [];
    for (const it of items as Array<Record<string, string>>) {
      try {
        const r = await ensure(String(it.course), String(it.text), String(it.voice), String(it.rate || "0%"));
        results.push({ k: it.k, ok: true, made: r.made, bytes: r.bytes, path: r.path });
      } catch (e) {
        results.push({ k: it.k, ok: false, error: String((e as Error).message || e).slice(0, 200) });
      }
    }
    return out(200, { n: results.length, results });
  }

  if (op === "say") {
    const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
    if (!token) return out(401, { code: "session_expired", error: "Not signed in" });
    const { data: u, error: ue } = await admin.auth.getUser(token);
    if (ue || !u?.user) return out(401, { code: "session_expired", error: "Sign in again" });
    const course = String(body.course || "");
    const c = COURSES[course];
    if (!c) return out(400, { code: "bad_request", error: "Bad course" });
    const email = (u.user.email || "").toLowerCase();
    const { data: inv } = await admin.from("invites").select("courses").eq("email", email).maybeSingle();
    const courses: string[] = inv?.courses || [];
    if (!courses.includes("*") && !courses.includes(course)) return out(403, { code: "not_granted", error: "Not invited to this course" });
    const text = String(body.text || "").trim();
    const voice = c.voices.includes(String(body.voice)) ? String(body.voice) : c.voices[0];
    const name = await clipName(voice, "0%", text);
    if (await exists(course, name)) return out(200, { url: publicUrl(`${course}/${name}.mp3`) });
    const { data: used } = await admin.rpc("tts_consume", { uid: u.user.id, lim: SAY_LIMIT });
    if (used === null) return out(429, { code: "rate_limited", error: `Daily limit of ${SAY_LIMIT} new voice clips reached.` });
    try {
      const r = await ensure(course, text, voice, "0%");
      return out(200, { url: r.url });
    } catch (e) {
      console.error("say failed", String((e as Error).message || e).slice(0, 200));
      return out(502, { code: "upstream", error: "Couldn't make the audio. The device voice will be used." });
    }
  }
  return out(400, { code: "bad_request", error: "Unknown op" });
});
