/* Study Hall design system runtime: window.SHUI (color schemes, points and levels, results screen, helpers).
   Load it in <head> with a plain <script src> right after shared/ui.css: it sets <html data-theme> while the page
   is still loading, so the page never paints in the wrong colors. Plain ES2017, no dependencies.
   See the top of ui.css for the markup each component expects. */
(function () {
  "use strict";
  var KEY = "sh:theme", NAMES = ["auto", "bold", "night", "soft"];
  var root = document.documentElement;
  var darkQ = window.matchMedia ? matchMedia("(prefers-color-scheme: dark)") : null;
  var motionQ = window.matchMedia ? matchMedia("(prefers-reduced-motion: reduce)") : null;

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
  function reducedMotion() { return !!(motionQ && motionQ.matches); }

  /* ---------- color schemes ---------- */
  function stored() { try { var t = localStorage.getItem(KEY); return NAMES.indexOf(t) > 0 ? t : "auto"; } catch (e) { return "auto"; } }
  var choice = stored();
  function apply() {
    root.setAttribute("data-theme", choice === "auto" ? (darkQ && darkQ.matches ? "night" : "bold") : choice);
    var meta = document.querySelector('meta[name="theme-color"]'), bg = getComputedStyle(root).getPropertyValue("--bg").trim();
    if (meta && bg) meta.setAttribute("content", bg);
  }
  function setTheme(name) {
    if (NAMES.indexOf(name) < 0) return;
    choice = name;
    try { localStorage.setItem(KEY, name); } catch (e) { /* private mode: applies to this page only */ }
    apply();
  }
  var THEME_INFO = [
    ["auto", "Automatic", "Bold by day, Night when your phone is in dark mode"],
    ["bold", "Bold", "Bright colors and strong outlines"],
    ["night", "Night", "Dark and easy on the eyes"],
    ["soft", "Soft", "Pastel colors and lighter lines"]
  ];
  var APPS = ["spanish", "cantonese", "korean", "vocab"], pickers = 0;
  function picker(el) {
    var name = "sh-theme-" + (++pickers);
    var sw = function (t) { // the scheme's background with the four app colors as it draws them
      return '<span class="sh-sw" data-theme="' + t + '">' + APPS.map(function (a) { return '<i data-app="' + a + '"></i>'; }).join("") + '</span>';
    };
    el.innerHTML = '<div class="sh-themes" role="radiogroup" aria-label="Color scheme">' + THEME_INFO.map(function (o) {
      return '<label class="sh-theme"><input type="radio" name="' + name + '" value="' + o[0] + '"' + (o[0] === choice ? " checked" : "") + '>' +
        '<span class="sh-swatch" aria-hidden="true">' + (o[0] === "auto" ? sw("bold") + sw("night") : sw(o[0])) + '</span>' +
        '<b>' + o[1] + '</b><span>' + o[2] + '</span></label>';
    }).join("") + '</div>';
    el.querySelectorAll("input").forEach(function (r) { r.onchange = function () { setTheme(r.value); }; });
  }
  apply();
  document.addEventListener("touchstart", function () {}, { passive: true }); // iOS Safari shows :active (the button press) only when a touch listener exists
  if (darkQ) darkQ.addEventListener("change", function () { if (choice === "auto") apply(); });
  window.addEventListener("storage", function (e) { if (e.key === KEY) { choice = stored(); apply(); } }); // another tab changed it

  /* ---------- points and levels ---------- */
  function levelOf(pts) { // level n -> n+1 needs 500 + 250(n-1) points (a lesson earns roughly 300-500)
    var left = Math.max(0, Math.floor(+pts || 0)), level = 1, need = 500;
    while (left >= need) { left -= need; level++; need += 250; }
    return { level: level, into: left, need: need, pct: Math.floor(100 * left / need) };
  }
  function chip(pts, opts) {
    opts = opts || {};
    return '<span class="sh-chip"' + (opts.id ? ' id="' + esc(opts.id) + '"' : "") + '>' + icon("star", 16) + '<span data-pts>' + fmt(pts || 0) + '</span>' +
      (opts.unit ? '<span>' + esc(opts.unit) + '</span>' : '<span class="sh-vh">points</span>') + '</span>';
  }
  function award(state, n, el) {
    n = Math.max(0, Math.round(+n || 0));
    state.pts = Math.max(0, Math.round(+state.pts || 0)) + n;
    if (el) {
      var t = el.querySelector("[data-pts]") || el;
      t.textContent = fmt(state.pts);
      if (n && !reducedMotion()) {
        el.classList.remove("sh-bump"); void el.offsetWidth; el.classList.add("sh-bump");
        var r = el.getBoundingClientRect(), p = document.createElement("span");
        p.className = "sh-plus"; p.setAttribute("aria-hidden", "true"); p.textContent = "+" + n;
        p.style.left = (r.left + r.width / 2) + "px"; p.style.top = (r.bottom + 6) + "px";
        p.addEventListener("animationend", function () { p.remove(); });
        document.body.appendChild(p);
      }
    }
    return state.pts;
  }

  /* ---------- level ring ---------- */
  function ring(level, pct, accentVar) {
    var C = 150.8, p = Math.max(0, Math.min(100, +pct || 0));
    return '<svg class="sh-ring" width="64" height="64" viewBox="0 0 60 60" role="img" aria-label="Level ' + level + ', ' + Math.round(p) + ' percent of the way to level ' + (level + 1) + '">' +
      '<circle cx="30" cy="30" r="24" style="fill:var(--surface);stroke:var(--border);stroke-width:2"/>' +
      '<circle cx="30" cy="30" r="24" style="fill:none;stroke:var(--surface-2);stroke-width:7"/>' +
      (p > 0 ? '<circle class="sh-ring-fill" cx="30" cy="30" r="24" stroke-dasharray="' + C + '" stroke-dashoffset="' + (C * (1 - p / 100)).toFixed(1) +
        '" transform="rotate(-90 30 30)" style="fill:none;stroke:var(' + (accentVar || "--accent") + ');stroke-width:7;stroke-linecap:round"/>' : "") +
      '<text x="30" y="36" text-anchor="middle" style="fill:var(--ink);font:800 18px var(--font)">' + level + '</text></svg>';
  }

  /* ---------- end-of-session screen ----------
     o: {score, total, points, newWords, spoken, levelBefore, levelAfter, review: [strings], actions: [{label, primary, onClick}],
         title (default "Session done"), note (one short paragraph)}. levelBefore / levelAfter are SHUI.points.levelOf() results.
     Stats that are 0 or left out are not shown. */
  function results(el, o) {
    var lb = o.levelBefore, la = o.levelAfter, up = la.level > lb.level, i = 0;
    var stats = [[o.points, "+", "points"], [o.newWords, "", "new words"], [o.spoken, "", "said aloud"]].filter(function (s) { return +s[0] > 0; });
    var count = function (v, pre) { return pre + '<span data-to="' + (+v || 0) + '">' + (reducedMotion() ? fmt(v || 0) : "0") + '</span>'; };
    var h = '<section class="sh-results">' +
      '<div class="sh-badge"><b>' + count(o.score, "") + '</b><span>of ' + fmt(o.total || 0) + ' right</span></div>' +
      '<h1 class="sh-in" tabindex="-1" style="--i:' + (i++) + '">' + esc(o.title || "Session done") + '</h1>' +
      (o.note ? '<p class="sh-in" style="--i:' + (i++) + ';text-align:center">' + esc(o.note) + '</p>' : "") +
      (stats.length ? '<div class="sh-stats sh-in" style="--i:' + (i++) + '">' + stats.map(function (s) {
        return '<div class="sh-stat"><b>' + count(s[0], s[1]) + '</b><span>' + s[2] + '</span></div>';
      }).join("") + '</div>' : "") +
      '<div class="sh-card sh-level sh-in" style="--i:' + (i++) + '"><div><span>' + (up ? "Level up! Level " : "Level ") + la.level + '</span>' +
        '<span class="sh-muted">' + fmt(la.need - la.into) + ' points to level ' + (la.level + 1) + '</span></div>' +
        '<div class="sh-progress" role="progressbar" aria-label="Progress to level ' + (la.level + 1) + '" aria-valuemin="0" aria-valuemax="100" aria-valuenow="' + la.pct + '">' +
        '<i style="width:' + (reducedMotion() ? la.pct : up ? 0 : lb.pct) + '%"></i></div></div>' +
      (o.review && o.review.length ? '<div class="sh-in" style="--i:' + (i++) + ';display:flex;flex-direction:column;gap:10px"><h2 style="font-size:18px">Review next time</h2>' +
        '<ul class="sh-review">' + o.review.map(function (r) { return '<li class="sh-tag mute">' + esc(r) + '</li>'; }).join("") + '</ul></div>' : "") +
      '<div class="sh-actions"></div></section>';
    el.innerHTML = h;
    var acts = el.querySelector(".sh-actions");
    (o.actions || []).forEach(function (a) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "sh-btn block" + (a.primary ? " primary" : ""); b.textContent = a.label; b.onclick = a.onClick;
      acts.appendChild(b);
    });
    el.querySelector("h1").focus({ preventScroll: true });
    if (reducedMotion()) return;
    var bar = el.querySelector(".sh-level i");
    setTimeout(function () { bar.style.width = la.pct + "%"; }, 600);
    var nums = el.querySelectorAll("[data-to]"), start = performance.now() + 250, dur = 1100;
    (function tick(now) {
      var p = Math.max(0, Math.min(1, (now - start) / dur)), e = 1 - Math.pow(1 - p, 3);
      nums.forEach(function (n) { n.textContent = fmt(+n.dataset.to * e); });
      if (p < 1 && el.contains(bar)) requestAnimationFrame(tick);
    })(performance.now());
  }

  /* Line icons shared by every app (24×24, stroke = currentColor; play and star are filled). SHUI.icon(name, size?) -> SVG string. */
  var ICONS = {
    listen: '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/>',
    speak: '<path d="M4 5h16v10H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    words: '<rect x="3" y="5" width="13" height="15" rx="2"/><path d="M8 5V3h11a2 2 0 0 1 2 2v13h-5"/><path d="M7 10h5M7 14h4"/>',
    grammar: '<path d="M4 19h16"/><path d="M6 15l4-10 4 10M7.5 11.5h5"/><path d="M16 9h4M18 7v4"/>',
    tones: '<path d="M3 17c3 0 3-10 6-10s3 6 6 6 3-4 6-4"/>',
    letters: '<path d="M2.5 19L8 5l5.5 14M4.6 14h6.8"/><circle cx="18" cy="15.5" r="3.5"/><path d="M21.5 12v7"/>',
    review: '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v5h-5"/>',
    weak: '<path d="M12 3l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
    chat: '<path d="M4 5h11v8H8l-4 3z"/><path d="M15 9h5v8l-3-2h-6v-2"/>',
    cards: '<rect x="3" y="7" width="13" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-3"/>',
    settings: '<path d="M4 7h9M17 7h3M4 17h3M11 17h9"/><circle cx="15" cy="7" r="2"/><circle cx="9" cy="17" r="2"/>',
    back: '<path d="M15 6l-6 6 6 6"/>',
    play: '<path d="M7 4.5v15l12-7.5z" fill="currentColor" stroke="none"/>',
    pause: '<path d="M8 5v14M16 5v14"/>',
    mic: '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    start: '<path d="M7 4.5v15l12-7.5z"/>',
    check: '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    close: '<path d="M6 6l12 12M18 6L6 18"/>',
    star: '<path d="M12 2.5l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4l-5.9 3.1 1.2-6.5L2.5 9.4l6.6-.9z" fill="currentColor" stroke="none"/>',
    book: '<path d="M12 6.5C10 5 7 4.6 3 5v13.5c4-.4 7 0 9 1.5 2-1.5 5-1.9 9-1.5V5c-4-.4-7 0-9 1.5z"/><path d="M12 6.5V20"/>',
    blocks: '<rect x="3" y="13" width="8" height="8" rx="1.5"/><rect x="13" y="13" width="8" height="8" rx="1.5"/><rect x="8" y="3" width="8" height="8" rx="1.5"/>',
    columns: '<path d="M3 21h18M4 9.5h16M12 3l8 4H4z"/><path d="M6 9.5V18M10 9.5V18M14 9.5V18M18 9.5V18M4 18h16"/>',
    globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/>',
    find: '<circle cx="11" cy="11" r="6"/><path d="M20 20l-4.5-4.5"/>',
    clinic: '<path d="M12 5v14M5 12h14"/>',
    bulb: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.3 1.1 2.2h5c0-.9.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>',
    practice: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    today: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    tracks: '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/>',
    progress: '<path d="M5 20v-8M12 20V5M19 20v-12"/>'
  };
  function icon(name, size) {
    var body = ICONS[name]; if (!body) return "";
    var n = size || 24;
    return '<svg class="sh-icon" width="' + n + '" height="' + n + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + body + '</svg>';
  }

  window.SHUI = {
    theme: { get: function () { return choice; }, set: setTheme, picker: picker },
    points: { levelOf: levelOf, award: award },
    results: results,
    ring: ring,
    chip: chip,
    icon: icon,
    esc: esc,
    reducedMotion: reducedMotion
  };
})();
