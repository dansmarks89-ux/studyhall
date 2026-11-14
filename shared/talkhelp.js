/* Study Hall conversation help: the Help panel under an AI conversation's reply box (Spanish, Cantonese, Korean).
   - A hint for a goal of the role-play, one step at a time: the idea in English, how to start, then a full model
     sentence with audio. Hints are pre-written and reviewed (src/HINTS.md); a goal without one is skipped.
   - "Say it in …": the learner types what he wants to say, in English or mixed with the language, and Claude gives it
     in the language, for this conversation (tagged "AI, not reviewed").
   Neither fills in the reply: the learner says or types it himself, which is what makes it stick.

   Load after shared/ui.js. SHTalkHelp.mount(el, cfg) draws the panel into el; call it again after a re-render (the
   state lives in cfg.state, so what was shown stays shown). cfg:
     state        an object kept with the conversation ({} at its start)
     name         the language's name ("Spanish")
     goals        the role-play's goals; hints: one {en, t: {s, r}, start: {s, r} | null} or null per goal
     done         Set of the goals done so far (hints start with the first goal not done)
     tx(t, big)   -> HTML of a text in the language; play(text) -> HTML of a play button
     translate(text) -> promise of Claude's reply {t, r, en, note}
     check(t)     -> HTML that checks the romanization against the course (optional)
     aiError(e)   -> the message for a failed AI call */
(function () {
  "use strict";
  const esc = SHUI.esc, str = (v, n) => String(v == null ? "" : v).replace(/\s+/g, " ").trim().slice(0, n);
  const STEP = ["Show the idea", "Show how to start", "Show a full sentence"];

  function mount(el, cfg) {
    const S = cfg.state, has = i => !!(cfg.hints && cfg.hints[i]);
    const order = () => { // goals with a hint, those not done first
      const all = cfg.goals.map((_, i) => i).filter(has);
      return all.filter(i => !cfg.done.has(i)).concat(all.filter(i => cfg.done.has(i)));
    };
    if (S.g == null || !has(S.g)) { S.g = order()[0]; S.step = 0; }
    const $ = id => el.querySelector("#" + id);

    function hintHTML() {
      if (S.g == null) return "";
      const h = cfg.hints[S.g], step = S.step, next = step === 1 && !h.start ? 2 : step;   // a one-word model has no start
      const more = order().length > 1;
      return `<h3>Hint for a goal</h3><p class="th-goal">${esc(cfg.goals[S.g])}</p>
        <ol class="th-steps">${step >= 1 ? `<li><span class="sub">The idea</span><span>${esc(h.en)}</span></li>` : ""}
        ${step >= 2 && h.start ? `<li><span class="sub">Start with</span><span>${cfg.tx(h.start)}…</span></li>` : ""}
        ${step >= 3 ? `<li><span class="sub">A full sentence</span><span class="th-t">${cfg.play(h.t.s)}${cfg.tx(h.t, true)}</span></li>` : ""}</ol>
        <div class="row">${step < 3 ? `<button class="sh-btn sm" type="button" id="thNext">${STEP[next]}</button>` : ""}${more ? `<button class="sh-btn sm ghost" type="button" id="thOther">Another goal</button>` : ""}</div>`;
    }
    function trHTML() {
      const a = S.tr;
      if (!a) return "";
      if (a.busy) return `<p>Asking Claude…</p>`;
      if (a.err) return `<p class="th-fix">${esc(a.err)}</p>`;
      const o = a.out;
      return `<div class="th-out"><span class="sh-tag gold">AI, not reviewed</span><span class="th-t">${cfg.play(o.t.s)}${cfg.tx(o.t, true)}</span>
        ${o.en ? `<span class="sub">${esc(o.en)}</span>` : ""}${o.note ? `<p>${esc(o.note)}</p>` : ""}${cfg.check ? cfg.check(o.t) : ""}
        <p class="sub">Now say or type it yourself in your reply.</p></div>`;
    }
    function draw() {
      if (!el.isConnected) return;
      const open = el.querySelector("details") ? el.querySelector("details").open : !!S.open;
      el.innerHTML = `<details class="sh-card th"${open ? " open" : ""}><summary>Stuck? Get help</summary><div class="th-in">
        ${hintHTML()}
        <h3>Say it in ${esc(cfg.name)}</h3>
        <form class="th-form" id="thForm"><input type="text" id="thIn" maxlength="300" autocomplete="off" spellcheck="false" value="${esc(S.q || "")}"
          placeholder="In English, or mixed with the ${esc(cfg.name)} you know" aria-label="What you want to say, in English or mixed with ${esc(cfg.name)}">
          <button class="sh-btn" type="submit"${S.tr && S.tr.busy ? " disabled" : ""}>Show me</button></form>
        <div id="thOut" role="status">${trHTML()}</div><p class="sub">Each one uses one of today's AI replies.</p></div></details>`;
      el.querySelector("details").ontoggle = e => { S.open = e.target.open; };
      const refocus = () => { const f = $("thNext") || $("thOther"); if (f) f.focus(); };   // the buttons were drawn again
      if ($("thNext")) $("thNext").onclick = () => { S.step = S.step === 1 && !cfg.hints[S.g].start ? 3 : S.step + 1; draw(); refocus(); };
      if ($("thOther")) $("thOther").onclick = () => { const o = order(); S.g = o[(o.indexOf(S.g) + 1) % o.length]; S.step = 0; draw(); refocus(); };
      $("thIn").oninput = e => { S.q = e.target.value; };
      $("thForm").onsubmit = e => { e.preventDefault(); ask(); };
    }
    function showOut() { // only the answer and the button change, so the text box keeps its focus and the keyboard stays up
      if (!el.isConnected) return;
      $("thOut").innerHTML = trHTML(); $("thForm").querySelector("button").disabled = !!(S.tr && S.tr.busy);
    }
    async function ask() {
      const q = (S.q || "").trim();
      if (!/[\p{L}\p{N}]/u.test(q) || (S.tr && S.tr.busy)) return;
      S.tr = { busy: true }; showOut();
      try {
        const o = await cfg.translate(q), s = str(o && o.t, 300);
        if (!s) throw Object.assign(new Error("The reply came back in an unexpected form. Try again."), { code: "invalid_json" });
        S.tr = { out: { t: { s, r: str(o.r, 500) }, en: str(o.en, 400), note: str(o.note, 300) } };
      } catch (e) {
        S.tr = { err: cfg.aiError(e) || "That didn't work. Try again." };
      }
      S.show();   // the panel as it is now (the conversation may have been drawn again meanwhile)
    }
    S.show = showOut;
    draw();
  }
  window.SHTalkHelp = { mount };
})();
