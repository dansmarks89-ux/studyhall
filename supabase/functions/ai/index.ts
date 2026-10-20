// Study Hall AI proxy.
// The browser sends: { course: "spanish", prompt: "...", max_tokens?: number }
// with the signed-in user's access token in the Authorization header.
// This function checks the user is invited to that course and under today's limit,
// then calls the Claude API with the key stored as the ANTHROPIC_API_KEY secret.
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
const admin = createClient(Deno.env.get("SUPABASE_URL")!, secretKey(), {
  auth: { persistSession: false, autoRefreshToken: false },
});

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return out(405, { code: "bad_request", error: "POST only" });

  // 1. Who is calling?
  const token = (req.headers.get("Authorization") || "").replace(/^Bearer\s+/i, "");
  if (!token) return out(401, { code: "session_expired", error: "Not signed in" });
  const { data: u, error: ue } = await admin.auth.getUser(token);
  if (ue || !u?.user) return out(401, { code: "session_expired", error: "Sign in again" });
  const user = u.user;

  // 2. What do they want?
  let body: { course?: string; prompt?: string; max_tokens?: number };
  try { body = await req.json(); } catch (_) { return out(400, { code: "bad_request", error: "Bad JSON" }); }
  const course = String(body.course || "");
  const prompt = String(body.prompt || "");
  if (!/^[a-z0-9-]{1,40}$/.test(course)) return out(400, { code: "bad_request", error: "Bad course" });
  if (!prompt || prompt.length > 60000) return out(400, { code: "bad_request", error: "Prompt missing or too long" });
  const maxTokens = Math.min(Math.max(Number(body.max_tokens) || 4000, 256), 8000);

  // 3. Are they invited to this course?
  const email = (user.email || "").toLowerCase();
  const { data: inv } = await admin.from("invites").select("courses").eq("email", email).maybeSingle();
  const courses: string[] = inv?.courses || [];
  if (!courses.includes("*") && !courses.includes(course)) return out(403, { code: "not_granted", error: "Not invited to this course" });

  const key = Deno.env.get("ANTHROPIC_API_KEY");
  if (!key) return out(503, { code: "server", error: "AI isn't set up yet. Ask Dan." });

  // 4. Settings and today's limit
  const { data: rows } = await admin.from("settings").select("key,value").in("key", ["ai_daily_limit", "ai_model"]);
  const st: Record<string, unknown> = {};
  (rows || []).forEach((r: { key: string; value: unknown }) => { st[r.key] = r.value; });
  const limit = Number(st["ai_daily_limit"]) || 40;
  const model = String(st["ai_model"] || "claude-sonnet-5-5").replace(/^"|"$/g, "");
  const { data: used, error: ce } = await admin.rpc("ai_consume", { uid: user.id, lim: limit });
  if (ce) return out(500, { code: "server", error: "Usage check failed" });
  if (used === null) return out(429, { code: "rate_limited", error: `Daily limit of ${limit} AI replies reached. It resets at midnight Chicago time.` });

  // 5. Call Claude
  let r: Response;
  try {
    r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model, max_tokens: maxTokens, messages: [{ role: "user", content: prompt }] }),
    });
  } catch (_) { return out(502, { code: "upstream", error: "Couldn't reach Claude" }); }
  const j = await r.json().catch(() => null);
  if (!r.ok) {
    console.error("anthropic", r.status, JSON.stringify(j).slice(0, 500));
    if (r.status === 429 || r.status === 529) return out(429, { code: "rate_limited", error: "Claude is busy. Try again in a minute." });
    return out(502, { code: "upstream", error: "Claude returned an error" });
  }
  const text = (j?.content || []).filter((b: { type: string }) => b.type === "text").map((b: { text: string }) => b.text).join("");
  return out(200, { text, used, limit });
});
