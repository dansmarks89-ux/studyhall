/* Study Hall look-up: type a word, a verb form or a sentence and get what the course has on it (its reviewed content,
   tagged "Checked"), and, when the course doesn't have it or on request, Claude's answer (tagged "AI, not reviewed").
   AI answers are for reading only: they never become questions. A saved item is kept in a list that syncs with the
   account, so its AI answers can be checked later and added to the course.

   Load after shared/ui.js. SHLookup.create(cfg) returns one look-up for the page:
     mount(el)        draws the screen into el (again after a re-render: the typed text and results are kept)
     refresh()        searches the course again for the text being typed (more of the course has loaded)
     body()           the saved list as a progress document {saved, gone, v}
     merge(doc)       merges the account copy in; true when this device has something the account copy lacks
     count()          saved items
     clear()          forgets everything (progress reset)
   cfg:
     key              localStorage key
     intro            one line under the title
     placeholder      of the text box
     accents          [letters] for a row of accent keys, or null
     have             heading over the course's exact matches
     linked           heading over the course entries found in an AI answer
     ai               {english: true}  the text is English (Word Power), or
                      {name, code, learner, rules, rom}  the language, who is learning it, style rules for Claude and the
                      romanization's name ("" when it has none)
     loaded()         -> a promise that settles once all the course content find() searches has loaded (or failed to)
     find(text)       -> {exact: [hit], near: [hit]} from the course
     links(texts)     -> [hit] the course entries for the words of these texts (an AI answer's words)
     check(texts)     -> HTML that checks an AI answer's romanization against the course, or "" (optional)
     tx({s, r}, big)  -> HTML of a text in the language (with its romanization); big: as an answer's headline
     play(text)       -> HTML of a play button
     sample()         -> promise of the page's AI (window.claude.use("sample")), or null
     aiError(e)       -> the message for a failed AI call
     changed()        called after the saved list changed (the page marks it for syncing)
   hit: {id, s, r (romanization, where the language has one), en, html() (the full entry), state() (a short status, or ""), addable() (can it go into the reviews
        now?), add() (puts it there), addLabel} */
(function () {
  "use strict";
  const esc = SHUI.esc;
  const SAVED_MAX = 200, SAVED_BYTES = 300000, CACHE_MAX = 30, RECENT_MAX = 8, GONE_MS = 180 * 864e5;   // the account's progress table takes a document under 600,000 bytes
  const REGISTERS = { formal: "Formal", informal: "Informal", slang: "Slang", medical: "Medical", literary: "Literary", technical: "Technical", dated: "Dated" };
  const str = (v, n) => String(v == null ? "" : v).replace(/\s+/g, " ").trim().slice(0, n);
  const list = (v, n, f) => (Array.isArray(v) ? v : []).slice(0, n).map(f).filter(Boolean);
  const keyOf = q => String(q).normalize("NFC").toLowerCase().replace(/\s+/g, " ").trim();
  const hasText = q => /[\p{L}\p{N}]/u.test(q);   // punctuation alone is nothing to look up
  const hash = s => { let h = 5381; for (let i = 0; i < s.length; i++) h = (h * 33 + s.charCodeAt(i)) >>> 0; return h.toString(36); };

  function promptFor(A, q) {
    const typed = `"""${q.slice(0, 300)}"""`;
    if (A.english) return `You are a dictionary for an adult native English speaker who is building an advanced vocabulary and general knowledge.
They typed this to look it up (a word, a phrase, an idiom, a name or a reference): ${typed}

Reply with only a JSON object:
{"term": "the word or phrase with its spelling corrected",
"kind": "word" | "phrase" | "idiom" | "reference",
"pos": "part of speech, or empty",
"say": "how to say it, in capitals for the stressed syllable, like uh-BRIJ; empty for a common word or a phrase",
"def": "a clear one-sentence definition of the most common meaning",
"register": "neutral" | "formal" | "informal" | "literary" | "technical" | "slang" | "dated",
"use": "1-2 sentences: when people use it, its tone or connotation, and what it is often confused with",
"senses": [{"def": "a distinct meaning", "ex": "one natural example sentence"}],
"syn": ["up to 5 close synonyms"], "ant": ["up to 4 opposites"], "forms": ["related forms, e.g. the noun or adverb"],
"origin": "one sentence on where it comes from, or empty if you are not sure"}
"senses": up to 3, most common first. Be accurate: if this is not a real word or you are unsure, say so in "use" instead of guessing. No text outside the JSON.`;
    const rom = A.rom ? `, "r": "its ${A.rom}"` : "", T = `{"t": "…"${rom}, "en": "…"`;
    return `You are a bilingual dictionary and translator for ${A.learner}.
${A.rules}
The learner typed this to look it up. It may be ${A.name} or English, and a word, a verb form, a phrase or a whole sentence: ${typed}

Reply with only a JSON object:
{"kind": "word" | "phrase" | "sentence",
"t": "the ${A.name}: for English, the most natural way to say it; for ${A.name}, their text with any mistake corrected"${rom},
"en": "the natural English meaning or translation",
"fixed": "if they typed ${A.name} with a mistake, one short English sentence saying what you corrected; else empty",
"pos": "for one word: its part of speech (nouns with gender where the language has it; a verb form with its dictionary form, tense and person); else empty",
"register": "neutral" | "formal" | "informal" | "slang" | "medical",
"use": "1-2 English sentences: when and with whom it is used, how formal it is, and any common mistake English speakers make with it",
"senses": [{"en": "a distinct meaning", "ex": ${T}}}],
"parts": [${T}}],
"alts": [${T}, "note": "how it differs: more formal, casual, regional…"}],
"lemmas": ["the dictionary forms of the main content words of t, up to 6"]}
"senses": for a word or short phrase, up to 3 meanings, most common first, each with one short natural example sentence; empty for a sentence.
"parts": for a phrase or sentence, the ${A.name} in order in 2-6 chunks, each with what it means or does; empty for one word.
"alts": up to 3 other natural ways to say it (for example the formal and the casual one); empty if there is none worth learning.
Be accurate: if this is not real ${A.name} or you are unsure, say so in "use" instead of guessing. Keep examples short. No text outside the JSON.`;
  }
  /* A reply made safe to draw and to store: known fields only, as trimmed strings and short lists; null when it has no answer. */
  function clean(o, A) {
    if (!o || typeof o !== "object") return null;
    const reg = Object.hasOwn(REGISTERS, o.register) ? o.register : "";
    if (A.english) {
      const out = { term: str(o.term, 120), kind: ["word", "phrase", "idiom", "reference"].includes(o.kind) ? o.kind : "word", pos: str(o.pos, 60), say: str(o.say, 60),
        def: str(o.def, 400), register: reg, use: str(o.use, 600), senses: list(o.senses, 3, s => s && str(s.def, 300) ? { def: str(s.def, 300), ex: str(s.ex, 300) } : null),
        syn: list(o.syn, 5, s => str(s, 60)), ant: list(o.ant, 4, s => str(s, 60)), forms: list(o.forms, 6, s => str(s, 60)), origin: str(o.origin, 400) };
      return out.term && out.def ? out : null;
    }
    const T = x => x && str(x.t, 300) ? { s: str(x.t, 300), r: A.rom ? str(x.r, 500) : "", en: str(x.en, 400) } : null;
    const out = { kind: ["word", "phrase", "sentence"].includes(o.kind) ? o.kind : "phrase", t: T(o), fixed: str(o.fixed, 300),
      pos: str(o.pos, 120), register: reg, use: str(o.use, 600),
      senses: list(o.senses, 3, s => s && str(s.en, 200) ? { en: str(s.en, 200), ex: T(s.ex) } : null), parts: list(o.parts, 6, T),
      alts: list(o.alts, 3, x => { const t = T(x); return t && Object.assign(t, { note: str(x.note, 200) }); }), lemmas: list(o.lemmas, 6, s => str(s, 60)) };
    return out.t && (out.t.en || out.use) ? out : null;   // no meaning: Claude says in "use" that it isn't a word
  }

  function create(cfg) {
    const A = cfg.ai;
    let stored = null;
    try { stored = JSON.parse(localStorage.getItem(cfg.key) || "null"); } catch (e) { /* unreadable: start empty */ }
    // only what has the right shape is taken from the browser's copy (a broken one must not stop the page or its syncing)
    const obj = v => v && typeof v === "object" && !Array.isArray(v) ? v : {};
    const items = o => Object.fromEntries(Object.entries(obj(o)).filter(([, x]) => x && typeof x === "object" && x.at > 0));
    const S = obj(stored);
    const M = { saved: items(S.saved), gone: obj(S.gone), cache: items(S.cache), recent: (Array.isArray(S.recent) ? S.recent : []).filter(x => typeof x === "string") };   // gone: id -> when it was removed
    const keep = () => { try { localStorage.setItem(cfg.key, JSON.stringify(M)); } catch (e) { /* storage full or private mode: kept for this visit */ } };
    const st = { q: "", done: false, exact: [], near: [], links: [], open: new Set(), ai: null };   // ai: null | {busy} | {err} | {out}
    let el = null, seq = 0, ctl = null, typing = null;
    const $ = sel => el.querySelector(sel);
    const hits = () => st.exact.concat(st.near, st.links);
    const aiId = q => "ai:" + hash(keyOf(q));
    const cacheId = q => "q:" + keyOf(q);   // (a prefix keeps typed words like "constructor" from naming something an object already has)
    const answerFor = q => (M.saved[aiId(q)] || M.cache[cacheId(q)] || {}).out || null;

    /* ---------- the saved list ---------- */
    function fit() {   // when the list outgrows its document, the oldest items give way
      const ids = Object.keys(M.saved).sort((a, b) => M.saved[a].at - M.saved[b].at), size = () => new TextEncoder().encode(JSON.stringify(M.saved)).length;
      while (ids.length > SAVED_MAX || (ids.length > 1 && size() > SAVED_BYTES)) { const id = ids.shift(); delete M.saved[id]; M.gone[id] = Date.now(); }
    }
    function save(item) {
      if (M.saved[item.id]) { delete M.saved[item.id]; M.gone[item.id] = Date.now(); }
      else { M.saved[item.id] = Object.assign(item, { at: Date.now() }); fit(); }
      keep(); cfg.changed();
    }
    function body() {
      const cut = Date.now() - GONE_MS;
      for (const id in M.gone) if (M.gone[id] <= cut) delete M.gone[id];   // a removal is remembered for half a year
      return { saved: M.saved, gone: M.gone, v: 1 };
    }
    function merge(d) {
      const rs = (d && d.saved) || {}, rg = (d && d.gone) || {};
      for (const id in rg) if (rg[id] > (M.gone[id] || 0)) M.gone[id] = rg[id];
      for (const id in rs) { const a = M.saved[id], b = rs[id]; if (b && b.at && (!a || b.at > a.at)) M.saved[id] = b; }
      for (const id in M.saved) if ((M.gone[id] || 0) >= M.saved[id].at) delete M.saved[id];
      fit(); keep();
      if (el && !st.q.trim()) draw();
      return Object.keys(M.saved).some(id => !rs[id] || rs[id].at < M.saved[id].at) || Object.keys(body().gone).some(id => (rg[id] || 0) < M.gone[id]);
    }
    function clear() {
      stop(); M.saved = {}; M.gone = {}; M.cache = {}; M.recent = []; keep();
      Object.assign(st, { q: "", done: false, exact: [], near: [], links: [], open: new Set(), ai: null });
      if (el) { $("#lkQ").value = ""; draw(); }
    }

    /* ---------- searching ---------- */
    function search() {
      const r = hasText(st.q) ? cfg.find(st.q) : { exact: [], near: [] };
      st.exact = r.exact; st.near = r.near; st.links = []; st.open = new Set();
    }
    function stop() { seq++; if (ctl) ctl.abort(); ctl = null; }
    function show(out) {
      st.ai = { out };
      const have = new Set(st.exact.concat(st.near).map(h => h.id));
      st.links = cfg.links(A.english ? [out.term, ...out.syn, ...out.ant] : [out.t.s, ...out.lemmas, ...out.alts.map(a => a.s)]).filter(h => !have.has(h.id));
    }
    function found() { search(); st.exact.slice(0, 2).forEach(h => st.open.add(h.id)); }
    async function submit() {
      const q = st.q.trim();
      if (!hasText(q) || (st.done && st.ai && st.ai.busy)) return;   // (pressing Look up again while Claude is answering doesn't ask twice)
      clearTimeout(typing); stop();
      const mine = seq;
      found(); st.done = true; st.ai = null;
      M.recent = [q, ...M.recent.filter(x => keyOf(x) !== keyOf(q))].slice(0, RECENT_MAX); keep();
      const had = answerFor(q);
      if (had) show(had);
      else if (!st.exact.length) {   // Claude is asked only once the whole course has been searched
        st.ai = { busy: true }; draw();
        await cfg.loaded();
        if (mine !== seq) return;
        found();
        if (!st.exact.length) return ask();
        st.ai = null;
      }
      draw();
    }
    async function ask() {
      const q = st.q.trim(), mine = ++seq;
      st.ai = { busy: true }; draw();
      const sample = await cfg.sample();
      if (mine !== seq) return;
      if (!sample) { st.ai = { err: "AI isn't available on this page." }; return draw(); }
      ctl = new AbortController();
      try {
        const out = clean(await sample.json(promptFor(A, q), { signal: ctl.signal, maxTokens: 3000, cache: false, modelTier: "default", effort: "low" }), A);
        if (mine !== seq) return;
        if (!out) throw Object.assign(new Error("The reply came back in an unexpected form. Try again."), { code: "invalid_json" });
        M.cache[cacheId(q)] = { at: Date.now(), out };
        const ks = Object.keys(M.cache);
        if (ks.length > CACHE_MAX) delete M.cache[ks.reduce((a, b) => M.cache[b].at < M.cache[a].at ? b : a)];
        keep(); show(out);
      } catch (e) {
        if (mine !== seq) return;
        st.ai = { err: cfg.aiError(e) || "That didn't work. Try again." };
      }
      ctl = null; draw();
    }

    /* ---------- drawing ---------- */
    const tag = (text, cls) => `<span class="sh-tag${cls ? " " + cls : ""}">${esc(text)}</span>`;
    const AI_TAG = tag("AI, not reviewed", "gold"), CHECKED = tag("Checked", "good");   // in a row of the saved list the AI tag is short
    const row = (attr, text, sub, tags) => `<button class="lk-row" type="button" ${attr}><span class="lk-rt"><b>${text}</b><span>${esc(sub)}</span></span>${tags}</button>`;
    const saveBtn = (what, id) => `<button class="sh-btn sm" type="button" data-save="${esc(what)}">${M.saved[id] ? "Saved" : "Save"}</button>`;
    function hitHTML(h) {
      if (!st.open.has(h.id)) return `<li>${row(`data-hit="${esc(h.id)}"`, cfg.tx(h), h.en, CHECKED)}</li>`;
      const state = h.state();
      return `<li><section class="sh-card lk-card">${h.html()}<div class="lk-foot"><span class="lk-tags">${CHECKED}${state ? tag(state, "mute") : ""}</span>
        <span class="lk-tags">${h.addable() ? `<button class="sh-btn sm" type="button" data-add="${esc(h.id)}">${esc(h.addLabel)}</button>` : ""}${saveBtn("ck:" + h.id, "ck:" + h.id)}</span></div></section></li>`;
    }
    const rows = hs => `<ul class="lk-rows">${hs.map(hitHTML).join("")}</ul>`;
    const NOTE = `<p class="lk-sub">Claude wrote this just now and it hasn't been checked like the course's own content.${A.english ? "" : " Use it like a dictionary; the course's sentences are the ones to copy."}</p>`;
    function aiCard(o) {
      const T = (x, big) => `<div class="lk-t">${cfg.play(x.s)}${cfg.tx(x, big)}</div>`, sub = s => s ? `<span class="lk-sub">${esc(s)}</span>` : "";
      const sect = (h, items, ol) => items.length ? `<h3>${h}</h3><${ol ? "ol" : "ul"} class="lk-list${ol ? " num" : ""}">${items.map(i => `<li>${i}</li>`).join("")}</${ol ? "ol" : "ul"}>` : "";
      const foot = `${NOTE}<div class="lk-foot"><span></span>${saveBtn("ai", aiId(st.q))}</div></section>`;
      if (A.english) {
        const kv = [["Similar", o.syn], ["Opposite", o.ant], ["Forms", o.forms]].filter(x => x[1].length);
        return `<section class="sh-card lk-card"><div class="lk-tags">${AI_TAG}${[o.kind !== "word" && o.kind, o.pos, REGISTERS[o.register]].filter(Boolean).map(t => tag(t, "mute")).join("")}</div>
          <div class="lk-t">${cfg.play(o.term)}<span class="lk-rt"><b class="lk-term">${esc(o.term)}</b>${o.say ? `<span>${esc(o.say)}</span>` : ""}</span></div><p class="lk-en">${esc(o.def)}</p>${o.use ? `<p>${esc(o.use)}</p>` : ""}
          ${sect("Meanings", o.senses.map(s => `<b>${esc(s.def)}</b>${sub(s.ex)}`), true)}
          ${kv.length ? `<dl class="lk-kv">${kv.map(([k, v]) => `<dt>${k}</dt><dd>${esc(v.join(", "))}</dd>`).join("")}</dl>` : ""}
          ${o.origin ? `<p><b>Origin:</b> ${esc(o.origin)}</p>` : ""}${foot}`;
      }
      const texts = [o.t, ...o.senses.map(s => s.ex).filter(Boolean), ...o.alts];
      return `<section class="sh-card lk-card"><div class="lk-tags">${AI_TAG}${[o.kind[0].toUpperCase() + o.kind.slice(1), o.pos, REGISTERS[o.register]].filter(Boolean).map(t => tag(t, "mute")).join("")}</div>
        ${T(o.t, true)}${o.t.en ? `<p class="lk-en">${esc(o.t.en)}</p>` : ""}${o.fixed ? `<p class="lk-fix">${esc(o.fixed)}</p>` : ""}${cfg.check ? cfg.check(texts) : ""}${o.use ? `<p>${esc(o.use)}</p>` : ""}
        ${sect("Meanings", o.senses.map(s => `<b>${esc(s.en)}</b>${s.ex ? T(s.ex) + sub(s.ex.en) : ""}`), true)}
        ${sect("Piece by piece", o.parts.map(p => cfg.tx(p) + sub(p.en)))}
        ${sect("Other ways to say it", o.alts.map(a => T(a) + sub(a.en + (a.note ? ` (${a.note})` : ""))))}${foot}`;
    }
    function aiHTML() {
      const a = st.ai;
      if (!a) return `<div class="lk-ask"><button class="sh-btn" type="button" data-ask>${st.exact.length ? "Ask Claude for more" : "Ask Claude"}</button><span class="lk-sub">Uses one of today's AI replies. The answer isn't reviewed.</span></div>`;
      if (a.busy) return `<section class="sh-card lk-card"><p role="status">Asking Claude…</p><button class="sh-btn sm ghost" type="button" data-stop>Stop</button></section>`;
      if (a.err) return `<div class="lk-ask"><p class="lk-fix" role="status">${esc(a.err)}</p><button class="sh-btn" type="button" data-ask>Try again</button></div>`;
      return aiCard(a.out);
    }
    function home() {
      const saved = Object.values(M.saved).sort((a, b) => b.at - a.at);
      return (M.recent.length ? `<h2 class="lk-h">Recent</h2><div class="lk-chips">${M.recent.map(q => `<button class="sh-tag mute" type="button" data-q="${esc(q)}">${esc(q)}</button>`).join("")}</div>` : "")
        + (saved.length ? `<h2 class="lk-h">Saved (${saved.length})</h2><ul class="lk-rows">${saved.map(x => `<li class="lk-saved">${row(`data-q="${esc(x.q)}"`, cfg.tx(x), x.en, x.src === "ai" ? tag("AI", "gold") : CHECKED)}
            <button class="lk-x" type="button" data-unsave="${esc(x.id)}" aria-label="Remove ${esc(x.s)} from saved">${SHUI.icon("close")}</button></li>`).join("")}</ul>
            <p class="lk-sub">Saved AI answers stay here until they've been checked. Only checked content goes into lessons and reviews.</p>`
          : `<p class="lk-sub">Save an answer to keep it here. Saved items sync with your account.</p>`);
    }
    function draw() {
      const out = $("#lkOut"); if (!out) return;
      if (!st.q.trim()) out.innerHTML = home();
      else if (!st.done) out.innerHTML = hits().length ? rows(hits().slice(0, 8)) : `<p class="lk-sub">${hasText(st.q) ? "Nothing in the course matches this yet. Press Look up to ask Claude." : "Type a word or a sentence."}</p>`;
      else out.innerHTML = (st.exact.length ? `<h2 class="lk-h">${esc(cfg.have)}</h2>${rows(st.exact)}` : "") + aiHTML()
        + (st.links.length ? `<h2 class="lk-h">${esc(cfg.linked)}</h2>${rows(st.links)}` : "") + (st.near.length ? `<h2 class="lk-h">Close matches in the course</h2>${rows(st.near.slice(0, 8))}` : "");
    }
    function setQuery(q) { st.q = q; $("#lkQ").value = q; submit(); window.scrollTo(0, 0); }
    function onClick(e) {
      const b = e.target.closest("button"); if (!b) return;
      const d = b.dataset, hit = id => hits().find(h => h.id === id);
      if (d.hit) { st.open.add(d.hit); draw(); }
      else if (d.add) { hit(d.add).add(); draw(); }
      else if (d.save === "ai") { const o = st.ai.out; save(A.english ? { id: aiId(st.q), q: st.q.trim(), src: "ai", s: o.term, en: o.def, out: o } : { id: aiId(st.q), q: st.q.trim(), src: "ai", s: o.t.s, r: o.t.r, en: o.t.en, out: o }); draw(); }
      else if (d.save) { const h = hit(d.save.slice(3)); save({ id: d.save, q: h.s, src: "ck", s: h.s, r: h.r, en: h.en }); draw(); }
      else if (d.unsave) { save(M.saved[d.unsave]); draw(); }
      else if ("ask" in d) ask();
      else if ("stop" in d) { stop(); st.ai = null; draw(); }
      else if (d.q) setQuery(d.q);
      // the results were drawn again: put the focus back on the card that was acted on
      const next = d.hit || d.add ? `[data-save="ck:${CSS.escape(d.hit || d.add)}"]` : d.save ? `[data-save="${CSS.escape(d.save)}"]` : "ask" in d ? "[data-stop]" : "stop" in d ? "[data-ask]" : null;
      const to = next && $(next); if (to) to.focus({ preventScroll: true });
    }
    function mount(target) {
      el = target; el.classList.add("lk");
      el.innerHTML = `<h1>Look up</h1><p class="lk-sub">${esc(cfg.intro)}</p>
        <form class="lk-form" id="lkForm" role="search"><input type="search" id="lkQ" maxlength="300" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" enterkeyhint="search" placeholder="${esc(cfg.placeholder)}" aria-label="${esc(cfg.placeholder)}"><button class="sh-btn primary" type="submit">Look up</button></form>
        ${cfg.accents ? `<div class="lk-keys">${cfg.accents.map(a => `<button type="button" data-key="${a}" aria-label="Insert ${a}">${a}</button>`).join("")}</div>` : ""}
        <div class="lk-out" id="lkOut"></div>`;
      const inp = $("#lkQ");
      inp.value = st.q;
      inp.oninput = () => { st.q = inp.value; st.done = false; st.ai = null; stop(); clearTimeout(typing); typing = setTimeout(() => { search(); draw(); }, 120); };
      $("#lkForm").onsubmit = e => { e.preventDefault(); inp.blur(); submit(); };
      el.querySelectorAll("[data-key]").forEach(k => k.onclick = () => { inp.setRangeText(k.dataset.key, inp.selectionStart, inp.selectionEnd, "end"); inp.focus(); inp.oninput(); });
      $("#lkOut").onclick = onClick;
      draw();
    }
    function refresh() { if (el && st.q.trim() && !st.done) { const open = st.open; search(); st.open = open; draw(); } }
    return { mount, refresh, body, merge, clear, count: () => Object.keys(M.saved).length };
  }

  window.SHLookup = { create };
})();
