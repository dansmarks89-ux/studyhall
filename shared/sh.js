/* Study Hall shared code: sign-in, saved progress and AI for every app.
   Each app page loads shared/supabase.js, then this file, then calls SH.install("<course id>").
   install() provides window.claude.use("user" | "db" | "sample"), the same interface the apps
   were written against on claude.ai, backed by Supabase instead. */
(function () {
  "use strict";
  var URL_ = "https://wbrssohmepioxapwbcne.supabase.co";
  var KEY = "sb_publishable_eXcCzWKT7zJBtnPnpb2Zow_NouHoSW6";
  var ROOT = new URL("../", document.currentScript.src).href; // site root (folder above /shared/)

  var sb = window.supabase.createClient(URL_, KEY, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false, storageKey: "studyhall-auth" }
  });

  function err(code, message) { var e = new Error(message || code); e.code = code; return e; }

  async function currentUser() {
    var r = await sb.auth.getSession();
    return r.data && r.data.session ? r.data.session.user : null;
  }
  async function myCourses() {
    var r = await sb.from("invites").select("courses").maybeSingle();
    if (r.error) throw r.error;
    return (r.data && r.data.courses) || [];
  }
  function allowed(courses, course) { return courses.indexOf("*") >= 0 || courses.indexOf(course) >= 0; }

  /* Pull the JSON object/array out of a model reply (tolerates ```json fences or stray text). */
  function parseJSON(text) {
    var t = String(text || "").trim();
    if (!t) throw err("empty_completion", "Empty reply");
    t = t.replace(/^```(?:json)?\s*/i, "").replace(/\s*```\s*$/, "");
    try { return JSON.parse(t); } catch (e) { /* fall through */ }
    var a = t.search(/[\[{]/);
    if (a >= 0) {
      var close = t[a] === "{" ? "}" : "]", b = t.lastIndexOf(close);
      if (b > a) { try { return JSON.parse(t.slice(a, b + 1)); } catch (e) { /* fall through */ } }
    }
    throw err("invalid_json", "The reply came back in an unexpected form. Try again.");
  }

  function install(course) {
    var ready = (async function () {
      var user = await currentUser();
      if (!user) { location.replace(ROOT + "?next=" + encodeURIComponent(course)); throw err("session_expired"); }
      var courses = [];
      try { courses = await myCourses(); } catch (e) { /* offline: let the app run from this device */ courses = [course]; }
      if (!allowed(courses, course)) { location.replace(ROOT + "?denied=" + encodeURIComponent(course)); throw err("not_granted"); }
      return user;
    })();
    ready.catch(function () {});

    document.addEventListener("DOMContentLoaded", function () {
      ready.then(function (user) {
        var el = document.getElementById("shwho");
        if (!el) return;
        el.textContent = "";
        var s = document.createElement("span"); s.textContent = user.email;
        var b = document.createElement("button"); b.type = "button"; b.textContent = "Sign out";
        b.onclick = async function () { await sb.auth.signOut(); location.replace(ROOT); };
        el.appendChild(s); el.appendChild(b);
      }).catch(function () {});
    });

    var userCap = { id: async function () { var u = await ready; return u.id; } };

    var dbCap = {
      collection: function () {
        return {
          get: async function () {
            var u = await ready;
            var r = await sb.from("progress").select("doc,data").eq("user_id", u.id).eq("course", course);
            if (r.error) throw r.error;
            return { docs: r.data.map(function (row) { return { id: row.doc, data: function () { return row.data; } }; }) };
          },
          doc: function (id) {
            return {
              set: async function (body) {
                var u = await ready;
                var r = await sb.from("progress").upsert({ user_id: u.id, course: course, doc: id, data: body }, { onConflict: "user_id,course,doc" });
                if (r.error) throw r.error;
              }
            };
          }
        };
      }
    };

    async function ask(prompt, opts) {
      opts = opts || {};
      await ready;
      var s = (await sb.auth.getSession()).data.session;
      if (!s) throw err("session_expired");
      var res;
      try {
        res = await fetch(URL_ + "/functions/v1/ai", {
          method: "POST",
          headers: { "Content-Type": "application/json", apikey: KEY, Authorization: "Bearer " + s.access_token },
          body: JSON.stringify({ course: course, prompt: String(prompt), max_tokens: opts.maxTokens }),
          signal: opts.signal
        });
      } catch (e) {
        if (e && e.name === "AbortError") throw err("cancelled");
        throw err("network", "Couldn't reach the server. Check your internet connection.");
      }
      var j = null; try { j = await res.json(); } catch (e) { /* ignore */ }
      if (!res.ok) throw err((j && j.code) || "server", (j && j.error) || "Something went wrong. Try again.");
      return (j && j.text) || "";
    }
    var sampleCap = {
      text: function (prompt, opts) { return ask(prompt, opts); },
      json: async function (prompt, opts) { return parseJSON(await ask(prompt, opts)); }
    };

    window.claude = {
      use: async function (name) {
        if (name === "user") return userCap;
        if (name === "db") return dbCap;
        if (name === "sample") return sampleCap;
        return null;
      }
    };
  }

  window.SH = { sb: sb, root: ROOT, currentUser: currentUser, myCourses: myCourses, allowed: allowed, install: install, parseJSON: parseJSON };

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () { navigator.serviceWorker.register(ROOT + "sw.js").catch(function () {}); });
  }
})();
