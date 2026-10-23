/* Study Hall voice: server voices (clips from the "tts" function), the microphone, and speech-to-text.
   Load after shared/sh.js. Defines window.SHVoice:
     setup({course, fallback})  fallback(text, rate) = the app's device-voice speak
     voices()                   -> Promise<Voice[]>  ([] when offline or not signed in)
     current() / choose(id)     chosen voice id; "" = course default, "device" = the device voice
     url(text, {voice})         -> Promise<url|null>
     play(text, {voice, rate})  -> Promise<"clip"|"device"|"none">  (on any failure the fallback speaks)
     stop()
     picker(el, {sample})       voice <select> + "Play sample" button
     mic.supported, mic.start({maxMs, silenceMs, onLevel}) -> Promise<Rec>
                                Rec.stop() -> Promise<Blob audio/wav 16 kHz mono>; Rec.cancel();
                                Rec.done -> Promise<Blob|null>: settles when recording ends (tap, silence or maxMs);
                                null if cancelled. onLevel(0..1) is called about 20 times a second.
     listen(blob)               -> Promise<{text, confidence}>  (text "" if nothing was heard)
   Rejections carry .code: session_expired, not_granted, rate_limited, mic_denied, mic_unavailable, upstream, offline. */
(function () {
  "use strict";
  var FN = "https://wbrssohmepioxapwbcne.supabase.co/functions/v1/tts";
  var CLIP_BASE = "https://wbrssohmepioxapwbcne.supabase.co/storage/v1/object/public/audio/";
  var CODES = ["session_expired", "not_granted", "rate_limited", "upstream", "offline"];
  var CATALOG_MS = 12 * 3600 * 1000, CLIP_CAP = 3000;
  var RATE = 16000, START_RMS = 0.02, QUIET_RMS = 0.01;

  var course = "", fallback = null, clips = new Map(), saveTimer = 0, lastError = null;

  function err(code, message) { var e = new Error(message || code); e.code = code; return e; }
  function lsGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { /* storage full or blocked */ } }

  async function call(payload) {
    if (!course) throw err("upstream", "SHVoice.setup() hasn't been called.");
    var s = null;
    try { s = window.SH && (await window.SH.sb.auth.getSession()).data.session; } catch (e) { /* treated as signed out */ }
    if (!s) throw err("session_expired", "Sign in again to use the voices.");
    var res;
    try {
      res = await fetch(FN, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + s.access_token },
        body: JSON.stringify(payload)
      });
    } catch (e) { throw err("offline", "Couldn't reach the server. Check your internet connection."); }
    var j = null;
    try { j = await res.json(); } catch (e) { /* not JSON */ }
    if (!res.ok || !j) {
      var code = j && CODES.indexOf(j.code) >= 0 ? j.code : "upstream";
      throw err(code, (j && j.error) || "The voice server had a problem. Try again later.");
    }
    return j;
  }

  /* ---------- voices ---------- */
  function catKey() { return "sh:voice-list:" + course; }
  function readCatalog() {
    try {
      var c = JSON.parse(lsGet(catKey()) || "null");
      return c && Array.isArray(c.voices) && typeof c.def === "string" && typeof c.t === "number" ? c : null;
    } catch (e) { return null; }
  }
  var catalogP = null;
  async function voices() {
    var c = readCatalog();
    if (c && Date.now() - c.t < CATALOG_MS) return c.voices;
    if (!catalogP) {
      catalogP = call({ op: "catalog", course: course }).then(function (j) {
        var list = (Array.isArray(j.voices) ? j.voices : []).filter(function (v) { return v && typeof v.id === "string" && typeof v.label === "string"; });
        var fresh = { t: Date.now(), voices: list, def: typeof j.default === "string" ? j.default : "" };
        lsSet(catKey(), JSON.stringify(fresh));
        return fresh;
      });
      catalogP.then(function () { catalogP = null; }, function () { catalogP = null; });
    }
    try { return (await catalogP).voices; }
    catch (e) { lastError = e; return c ? c.voices : []; }
  }
  function defaultVoice() { var c = readCatalog(); return c ? c.def : ""; }
  function current() { return course ? lsGet("sh:voice:" + course) || "" : ""; }
  function choose(id) { lsSet("sh:voice:" + course, id ? String(id) : null); }
  function voiceOf(opts) { return opts && opts.voice !== undefined && opts.voice !== null ? String(opts.voice) : current(); }

  /* ---------- clips ----------
     Saved compactly (a 53-bit hash of voice|text -> the clip's path in the bucket), so a full cache stays near
     200 KB per course and never crowds out the sign-in session that shares this site's storage. */
  function clipKey() { return "sh:clips:" + course; }
  function textKey(s) {
    var h1 = 0xdeadbeef, h2 = 0x41c6ce57;
    for (var i = 0; i < s.length; i++) { var c = s.charCodeAt(i); h1 = Math.imul(h1 ^ c, 2654435761); h2 = Math.imul(h2 ^ c, 1597334677); }
    h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
    h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
    return (4294967296 * (2097151 & h2) + (h1 >>> 0)).toString(36);
  }
  function loadClips() {
    clips = new Map();
    try {
      var a = JSON.parse(lsGet(clipKey()) || "[]");
      if (Array.isArray(a)) a.forEach(function (p) { if (Array.isArray(p) && typeof p[0] === "string" && typeof p[1] === "string") clips.set(p[0], p[1]); });
    } catch (e) { /* start empty */ }
  }
  function remember(k, u) {
    clips.delete(k); clips.set(k, u.indexOf(CLIP_BASE) === 0 ? u.slice(CLIP_BASE.length) : u);
    while (clips.size > CLIP_CAP) clips.delete(clips.keys().next().value);
    clearTimeout(saveTimer);
    var key = clipKey(), entries = Array.from(clips.entries());
    saveTimer = setTimeout(function () { lsSet(key, JSON.stringify(entries)); }, 500);
  }
  async function url(text, opts) {
    text = String(text === undefined || text === null ? "" : text).trim();
    var v = voiceOf(opts);
    if (!text || !course || v === "device") return null;
    var k = textKey(v + "|" + text), hit = clips.get(k);
    if (hit) return /^https:\/\//.test(hit) ? hit : CLIP_BASE + hit;
    var j;
    try { j = await call({ op: "say", course: course, text: text, voice: v || undefined }); }
    catch (e) { lastError = e; return null; }
    if (typeof j.url !== "string" || !/^https:\/\//.test(j.url)) return null;
    remember(k, j.url);
    return j.url;
  }

  /* ---------- playback: one shared <audio> ---------- */
  var audio = null, unlocked = false, silence = "", seq = 0;
  function player() {
    if (!audio) { audio = new Audio(); audio.preload = "auto"; audio.preservesPitch = true; }
    return audio;
  }
  function stop() {
    seq++;
    if (audio) { try { audio.pause(); } catch (e) { /* nothing playing */ } }
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  }
  async function play(text, opts) {
    opts = opts || {};
    stop();
    var my = seq, a = player(), rate = Number(opts.rate) > 0 ? Number(opts.rate) : 1;
    function device() {
      if (my !== seq || !fallback) return "none";
      fallback(String(text), opts.rate);
      return "device";
    }
    if (voiceOf(opts) === "device") return device();
    if (!unlocked) {
      // Play a moment of silence inside the tap, so iOS lets this element play the clip after the network wait.
      if (!silence) silence = URL.createObjectURL(encodeWav(new Float32Array(RATE / 10)));
      a.src = silence;
      var p = a.play();
      if (p) p.then(function () { unlocked = true; }, function () { /* not inside a tap; try again next time */ });
    }
    var u = await url(text, opts);
    if (my !== seq) return "none";
    if (!u) return device();
    a.src = u;
    a.defaultPlaybackRate = rate; a.playbackRate = rate;
    try { await a.play(); unlocked = true; return my === seq ? "clip" : "none"; }
    catch (e) { lastError = e; return device(); }
  }

  /* ---------- voice picker ---------- */
  function picker(el, opts) {
    var sample = (opts && opts.sample) || "";
    el.textContent = "";
    var lab = document.createElement("label"), sel = document.createElement("select"),
        btn = document.createElement("button"), note = document.createElement("span");
    lab.className = "sh-voice"; sel.style.minHeight = "44px";
    lab.appendChild(document.createTextNode("Voice ")); lab.appendChild(sel);
    btn.type = "button"; btn.className = "sh-voice-sample"; btn.textContent = "Play sample"; btn.style.minHeight = "44px";
    note.className = "sh-voice-note"; note.setAttribute("aria-live", "polite");
    el.appendChild(lab); el.appendChild(btn); el.appendChild(note);
    function option(value, text) { var o = document.createElement("option"); o.value = value; o.textContent = text; sel.appendChild(o); }
    function fill(list) {
      var def = defaultVoice(), cur = current();
      sel.textContent = "";
      if (!list.some(function (v) { return v.id === def; })) option("", "Course voice");
      list.forEach(function (v) { option(v.id === def ? "" : v.id, v.id === def ? v.label + " (default)" : v.label); });
      option("device", "Device voice");
      sel.value = Array.prototype.some.call(sel.options, function (o) { return o.value === cur; }) ? cur : "";
    }
    fill([]);
    voices().then(fill);
    sel.onchange = function () { choose(sel.value); note.textContent = ""; };
    btn.onclick = function () {
      note.textContent = "";
      lastError = null;
      play(sample, { voice: sel.value }).then(function (r) {
        if (r === "device" && sel.value !== "device") {
          note.textContent = lastError && lastError.code === "rate_limited" ? "Today's voice limit is used up, so the device voice played."
            : "That voice isn't available right now, so the device voice played.";
        } else if (r === "none" && !fallback) note.textContent = "Couldn't play the sample.";
      });
    };
  }

  /* ---------- microphone ---------- */
  var AC = window.AudioContext || window.webkitAudioContext;
  var mic = { supported: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && AC) };
  var WORKLET = "registerProcessor('sh-rec',class extends AudioWorkletProcessor{constructor(){super();this.b=new Float32Array(2048);this.n=0;this.on=true;this.port.onmessage=()=>{this.on=false;};}" +
    "process(i){const c=i[0]&&i[0][0];if(c){for(let k=0;k<c.length;k++){this.b[this.n++]=c[k];if(this.n===2048){this.port.postMessage(this.b,[this.b.buffer]);this.b=new Float32Array(2048);this.n=0;}}}return this.on;}});";
  // open = recordings holding the AudioContext (it is suspended when the last one ends); gen = the latest start().
  var ctx = null, workletCtx = null, workletP = null, active = null, open = 0, gen = 0;

  // Average each window of input samples into one 16 kHz sample (a simple low-pass for speech).
  function downsample(x, rate) {
    if (rate === RATE) return x;
    var ratio = rate / RATE, n = Math.floor(x.length / ratio), y = new Float32Array(n);
    for (var i = 0; i < n; i++) {
      var a = Math.floor(i * ratio), b = Math.min(x.length, Math.floor((i + 1) * ratio)), s = 0;
      for (var k = a; k < b; k++) s += x[k];
      y[i] = b > a ? s / (b - a) : x[a];
    }
    return y;
  }
  // 16 kHz mono 16-bit PCM WAV.
  function encodeWav(samples) {
    var buf = new ArrayBuffer(44 + samples.length * 2), dv = new DataView(buf);
    function str(o, s) { for (var i = 0; i < s.length; i++) dv.setUint8(o + i, s.charCodeAt(i)); }
    str(0, "RIFF"); dv.setUint32(4, 36 + samples.length * 2, true); str(8, "WAVE");
    str(12, "fmt "); dv.setUint32(16, 16, true); dv.setUint16(20, 1, true); dv.setUint16(22, 1, true);
    dv.setUint32(24, RATE, true); dv.setUint32(28, RATE * 2, true); dv.setUint16(32, 2, true); dv.setUint16(34, 16, true);
    str(36, "data"); dv.setUint32(40, samples.length * 2, true);
    for (var i = 0; i < samples.length; i++) {
      var v = Math.max(-1, Math.min(1, samples[i]));
      dv.setInt16(44 + i * 2, v < 0 ? v * 0x8000 : v * 0x7fff, true);
    }
    return new Blob([buf], { type: "audio/wav" });
  }

  async function captureNode() {
    if (ctx.audioWorklet && typeof AudioWorkletNode === "function") {
      try {
        if (workletCtx !== ctx) {
          workletCtx = ctx;
          workletP = ctx.audioWorklet.addModule(URL.createObjectURL(new Blob([WORKLET], { type: "application/javascript" })));
        }
        await workletP;
        return new AudioWorkletNode(ctx, "sh-rec", { numberOfInputs: 1, numberOfOutputs: 1, channelCount: 1, channelCountMode: "explicit" });
      } catch (e) { workletCtx = null; /* fall back to ScriptProcessor */ }
    }
    return ctx.createScriptProcessor(4096, 1, 1);
  }

  // Call from a tap handler: iOS only allows the AudioContext to start inside the tap.
  function start(opts) {
    opts = opts || {};
    if (!mic.supported) return Promise.reject(err("mic_unavailable", "This browser can't record audio."));
    var maxMs = Math.min(60000, Math.max(1000, Number(opts.maxMs) || 20000));
    var silenceMs = Math.min(10000, Math.max(300, Number(opts.silenceMs) || 1600));
    var onLevel = typeof opts.onLevel === "function" ? opts.onLevel : null;
    if (active) active.cancel();
    try { if (!ctx || ctx.state === "closed") ctx = new AC(); }
    catch (e) { return Promise.reject(err("mic_unavailable", "This browser can't record audio.")); }
    var resumed = ctx.resume(), my = ++gen, held = true;
    open++;
    function release() {
      if (!held) return;
      held = false;
      if (--open === 0) ctx.suspend().catch(function () { /* already closed */ });
    }
    return (async function () {
      var stream;
      try { stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true } }); }
      catch (e) {
        release();
        if (e && (e.name === "NotAllowedError" || e.name === "SecurityError")) throw err("mic_denied", "Microphone access is off. Allow it in your browser settings, or type instead.");
        throw err("mic_unavailable", "No microphone is available.");
      }
      var chunks = [], frames = 0, heard = false, lastLoud = 0, ended = null, timer = 0, rate = ctx.sampleRate;
      var src, node, sink, resolveDone, done = new Promise(function (r) { resolveDone = r; });
      function teardown() {
        clearTimeout(timer);
        stream.getTracks().forEach(function (t) { t.stop(); });
        if (node) {
          if (node.port) { node.port.onmessage = null; node.port.postMessage("stop"); } else node.onaudioprocess = null;
          node.disconnect();
        }
        if (src) src.disconnect();
        if (sink) sink.disconnect();
        if (active === rec) active = null;
        release();
      }
      function finish() {
        if (!ended) {
          teardown();
          var all = new Float32Array(frames), o = 0;
          chunks.forEach(function (c) { all.set(c, o); o += c.length; });
          chunks = [];
          var blob = encodeWav(downsample(all, rate));
          resolveDone(blob);
          ended = Promise.resolve(blob);
        }
        return ended;
      }
      function onChunk(x) {
        if (ended) return;
        var s = 0;
        for (var i = 0; i < x.length; i++) s += x[i] * x[i];
        var rms = Math.sqrt(s / (x.length || 1));
        chunks.push(x); frames += x.length;
        if (rms > START_RMS || (heard && rms > QUIET_RMS)) { heard = true; lastLoud = frames; }
        if (onLevel) { try { onLevel(Math.min(1, rms * 5)); } catch (e) { /* the app's callback failed */ } }
        if (heard && (frames - lastLoud) * 1000 / rate >= silenceMs) finish();
      }
      var rec = {
        stop: finish,
        cancel: function () { if (!ended) { teardown(); chunks = []; resolveDone(null); ended = Promise.resolve(null); } },
        done: done
      };
      try {
        await resumed;
        node = await captureNode();
        if (node.port) node.port.onmessage = function (e) { onChunk(e.data); };
        else node.onaudioprocess = function (e) { onChunk(new Float32Array(e.inputBuffer.getChannelData(0))); };
        src = ctx.createMediaStreamSource(stream);
        sink = ctx.createGain(); sink.gain.value = 0;
        src.connect(node); node.connect(sink); sink.connect(ctx.destination);
      } catch (e) {
        teardown();
        throw err("mic_unavailable", "The microphone couldn't start. Try again.");
      }
      if (my !== gen) { rec.cancel(); return rec; }   // a newer start() (e.g. a double tap) replaced this one
      timer = setTimeout(finish, maxMs);
      active = rec;
      return rec;
    })();
  }
  mic.start = start;

  /* ---------- speech to text ---------- */
  function base64(blob) {
    return new Promise(function (resolve, reject) {
      var r = new FileReader();
      r.onload = function () { resolve(String(r.result).slice(String(r.result).indexOf(",") + 1)); };
      r.onerror = function () { reject(err("mic_unavailable", "The recording couldn't be read.")); };
      r.readAsDataURL(blob);
    });
  }
  async function listen(blob) {
    if (!(blob instanceof Blob) || blob.size <= 44 + RATE * 2 / 10) return { text: "", confidence: 0 };  // under 0.1 s
    var j = await call({ op: "stt", course: course, audio: await base64(blob) });
    return { text: typeof j.text === "string" ? j.text : "", confidence: Number(j.confidence) || 0 };
  }

  function setup(o) {
    course = String((o && o.course) || "");
    fallback = o && typeof o.fallback === "function" ? o.fallback : null;
    loadClips();
  }

  window.SHVoice = { setup: setup, voices: voices, current: current, choose: choose, url: url, play: play, stop: stop,
    picker: picker, mic: mic, listen: listen };
})();
