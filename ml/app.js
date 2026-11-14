/* Machine Learning course for Study Hall.
   Sign-in, saved progress and access come from shared/sh.js (SH.install("ml") in index.html).
   Lessons are not in this public repository: they are read after sign-in from the Supabase table
   course_content, which only accounts invited to "ml" by name can read and only the service role can write.
   Each row's body is a unit file that pushes its lessons onto window.COURSE_UNITS. */
(() => {
  'use strict';

  const SECTIONS = ['core', 'worked', 'code'];
  const SEC_NAME = { core: 'Core', worked: 'Worked example', code: 'Python' };
  const SEC_TIME = { core: 'about 5 minutes', worked: 'about 10 minutes', code: 'about 15 minutes' };
  // Each length covers the sections up to `upto` and takes at most `reviews` due questions first.
  const MODES = [
    { id: 'short', label: '5 min', detail: 'Core', upto: 0, reviews: 6 },
    { id: 'medium', label: '15 min', detail: '+ worked', upto: 1, reviews: 10 },
    { id: 'long', label: '30 min', detail: '+ Python', upto: 2, reviews: 15 }
  ];
  const BACKLOG = 8; // a 5-minute session is review only once this many questions are due
  const GAPS = [1, 1, 3, 7, 16, 35]; // days until a question returns, by box
  const TEST_BOX = 2; // a question passed in a test-out starts here, as if answered right twice: back in GAPS[2] = 3 days
  const POINTS = 10;
  const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const REDUCED_MOTION = SHUI.reducedMotion();
  const app = document.getElementById('app');

  // Filled once the lessons have loaded. UNIT_FIGURES: figures a unit file brings with it, by name.
  let UNITS = [], LESSONS = [], QUESTIONS = new Map(), TERMS = [], UNIT_FIGURES = {};

  // ---------- small helpers ----------

  const el = (tag, props = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === 'html') n.innerHTML = v;
      else if (k.startsWith('on')) n.addEventListener(k.slice(2), v);
      else if (k in n) n[k] = v;
      else n.setAttribute(k, v);
    }
    n.append(...kids.flat().filter(k => k != null));
    return n;
  };

  const set = (node, attrs) => {
    for (const [k, v] of Object.entries(attrs)) node.setAttribute(k, v);
    return node;
  };

  const svg = (tag, attrs = {}, ...kids) => {
    const n = set(document.createElementNS('http://www.w3.org/2000/svg', tag), attrs);
    n.append(...kids);
    return n;
  };

  let uid = 0;
  const nextId = prefix => `${prefix}-${++uid}`;
  const clone = o => JSON.parse(JSON.stringify(o));
  const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
  const lessonNumber = lesson => LESSONS.indexOf(lesson) + 1;
  const num = n => String(n).replace('-', '−');
  const fmt = (n, places) => num(n.toFixed(places));
  const readNumber = text => parseFloat(text.replace(/[%,\s]/g, '').replace('−', '-'));
  const near = (a, b) => Math.abs(a - b) <= 0.01;
  const icon = name => el('span', { class: 'ico', html: SHUI.icon(name) });

  const today = () => {
    const d = new Date();
    return Math.floor((d.getTime() - d.getTimezoneOffset() * 60000) / 86400000);
  };

  const shuffled = list => {
    const a = [...list];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  };

  // Random choices handed to question generators, so a review tests the skill and not a remembered number.
  const RANDOM = {
    int: (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1)),
    pick: list => list[Math.floor(Math.random() * list.length)]
  };
  const materialize = q => (q.gen ? { ...q, ...q.gen(RANDOM) } : q);

  // Coalesce slider events so a figure redraws at most once per frame.
  const perFrame = draw => {
    let queued = false;
    return () => {
      if (queued) return;
      queued = true;
      requestAnimationFrame(() => { queued = false; draw(); });
    };
  };

  const local = {
    get(key) { try { return JSON.parse(localStorage.getItem(key)); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* storage blocked: the account copy still saves */ } }
  };

  // ---------- lessons ----------

  // Reads the lessons from the database, keeping a copy on this device for use offline.
  const loadLessons = async user => {
    const key = `ml:lessons:${user}`;
    let rows = null;
    try {
      const r = await SH.sb.from('course_content').select('doc,body').eq('course', 'ml').order('doc');
      if (r.error) throw r.error;
      rows = r.data;
      local.set(key, rows);
    } catch {
      rows = local.get(key);
    }
    if (!rows || !rows.length) return false;
    window.COURSE_UNITS = [];
    for (const row of rows) new Function(row.body)();
    UNITS = window.COURSE_UNITS.sort((a, b) => a.n - b.n);
    UNIT_FIGURES = Object.assign({}, ...UNITS.map(u => u.figures));
    LESSONS = UNITS.flatMap(u => u.lessons);
    QUESTIONS = new Map(LESSONS.flatMap(lesson => lesson.questions.map(q => [q.id, { q, lesson }])));
    TERMS = LESSONS.flatMap((lesson, li) => lesson.terms.map(t => ({
      ...t,
      li,
      order: li * SECTIONS.length + SECTIONS.indexOf(t.sec || 'core'),
      re: t.nolink ? null : new RegExp(`\\b(?:${t.m || t.t})\\b`, 'i')
    })));
    return true;
  };

  // ---------- progress: this device first, the Study Hall account when reachable ----------

  const isProgress = s => s && s.v === 2 && s.q && s.lessons && s.streak;
  const blank = () => ({ v: 2, updated: 0, pts: 0, streak: { day: 0, count: 0 }, lessons: {}, q: {} });

  let S = blank();
  let storeKey = '';

  const save = () => {
    S.updated = Date.now();
    local.set(storeKey, S);
  };

  const doneOf = lesson => S.lessons[lesson.id] || {};
  const resumeAt = (lesson, sec) => (doneOf(lesson)[sec] ? 0 : (doneOf(lesson).at || {})[sec] || 0);

  // Two devices can each hold progress the other lacks, so keep the fuller record of every item.
  const merge = (a, b) => {
    const q = { ...a.q };
    for (const [id, r] of Object.entries(b.q)) {
      const mine = q[id];
      if (!mine || r.right + r.wrong > mine.right + mine.wrong) q[id] = r;
    }
    const lessons = { ...a.lessons };
    for (const [id, l] of Object.entries(b.lessons)) lessons[id] = { ...l, ...lessons[id] };
    return {
      v: 2,
      updated: Math.max(a.updated, b.updated),
      pts: Math.max(a.pts, b.pts),
      streak: b.streak.day > a.streak.day ? b.streak : a.streak,
      lessons,
      q,
      ...(a.py || b.py ? { py: true } : {}),
      ...(a.missed || b.missed ? { missed: { ...b.missed, ...a.missed } } : {})
    };
  };

  // The summary Study Hall's home page shows on this course's tile.
  const statsDoc = () => {
    const next = LESSONS.find(l => !doneOf(l).core);
    return { pts: S.pts, level: SHUI.points.levelOf(S.pts).level, next: next ? `Lesson ${lessonNumber(next)}: ${next.title}` : 'Review and practice', due: dueIds().length };
  };

  const Store = {
    col: null,
    sent: 0,
    statsSent: '',
    writing: false,
    ok: false,

    async init(db, user) {
      this.col = db.collection(`data/users/${user}`);
      const snap = await this.col.get();
      const doc = snap.docs.find(d => d.id === 'progress');
      const remote = doc ? clone(doc.data()) : null;
      if (isProgress(remote)) {
        S = merge(S, remote);
        local.set(storeKey, S);
        if (JSON.stringify(remote) === JSON.stringify(S)) this.sent = S.updated;
      }
      this.ok = true;
      await this.push();
    },

    async push() {
      if (!this.col || this.writing) return;
      this.writing = true;
      try {
        while (this.sent !== S.updated) {
          this.sent = S.updated;
          await this.col.doc('progress').set(clone(S));
        }
        const stats = statsDoc(), key = JSON.stringify(stats);
        if (key !== this.statsSent) {
          await this.col.doc('stats').set({ ...stats, at: Date.now() });
          this.statsSent = key;
        }
        this.ok = true;
      } catch {
        this.sent = 0; // retried on the next save
        this.ok = false;
      }
      this.writing = false;
    }
  };

  // ---------- scheduling ----------

  const dueIds = () => {
    const t = today();
    return Object.keys(S.q)
      .filter(id => QUESTIONS.has(id) && S.q[id].due <= t)
      .sort((a, b) => S.q[a].due - S.q[b].due);
  };

  // Records an answer. Returns true when it earns points: right, and due today. An early answer keeps its schedule unless it is missed.
  const grade = (id, ok) => {
    const t = today();
    const r = S.q[id] || { box: 0, due: t, right: 0, wrong: 0 };
    const wasDue = r.due <= t;
    if (ok) {
      r.right++;
      if (wasDue) {
        r.box = Math.min(r.box + 1, GAPS.length - 1);
        r.due = t + GAPS[r.box];
      }
    } else {
      r.wrong++;
      r.box = 0;
      r.due = t + GAPS[0];
    }
    S.q[id] = r;
    return ok && wasDue;
  };

  const markDone = (lesson, sec, t) => {
    const { at, ...rest } = doneOf(lesson);
    const left = Object.entries(at || {}).filter(([k]) => k !== sec);
    S.lessons[lesson.id] = { ...rest, [sec]: t, ...(left.length ? { at: Object.fromEntries(left) } : {}) };
  };

  // Records a test-out answer. Right: the section is marked done and the question is scheduled from TEST_BOX.
  // Missed: nothing is scheduled, because the lesson teaches it; the question is noted so a retake asks another where it can.
  // Returns true when it earns points, by the same rule as grade().
  const gradeTest = (step, ok) => {
    const t = today();
    const { id } = step.q;
    if (!ok) {
      S.missed = { ...S.missed, [id]: t };
      return false;
    }
    const r = S.q[id] || { box: 0, due: t, right: 0, wrong: 0 };
    const wasDue = r.due <= t;
    r.right++;
    if (r.box < TEST_BOX) {
      r.box = TEST_BOX;
      r.due = t + GAPS[TEST_BOX];
    }
    S.q[id] = r;
    markDone(step.lesson, step.sec, t);
    return wasDue;
  };

  // Questions a test may ask for a section: never a recall question, which the learner grades alone.
  const testPool = (lesson, sec) => lesson.questions.filter(q => q.sec === sec && q.type !== 'recall');

  // Sections of a unit a test-out can ask about, in reading order: not yet done, with a question to ask.
  const testable = unit => unit.lessons.flatMap(lesson => SECTIONS
    .filter(sec => !doneOf(lesson)[sec] && testPool(lesson, sec).length)
    .map(sec => [lesson, sec]));

  // A "Work it out" question first, because a number cannot be guessed. A question missed in an earlier test only when no other is left.
  const testQuestion = (lesson, sec) => {
    const pool = testPool(lesson, sec);
    const unmissed = pool.filter(q => !(S.missed || {})[q.id]);
    const from = unmissed.length ? unmissed : pool;
    const nums = from.filter(q => q.type === 'num');
    return RANDOM.pick(nums.length ? nums : from);
  };

  const testSteps = unit => testable(unit).map(([lesson, sec]) => ({ kind: 'q', lesson, sec, q: testQuestion(lesson, sec), test: true }));

  const testNote = asked => {
    const passed = asked.filter(s => s.passed).length;
    return `${passed} of ${plural(asked.length, 'section')} passed and marked done.${passed ? ` Their questions come back for review in ${GAPS[TEST_BOX]} days.` : ''} Sections not passed stay in your lessons.`;
  };

  // How firmly a lesson's questions are held, from 0 to 1.
  const memory = lesson => lesson.questions.reduce((sum, q) => sum + (S.q[q.id] ? S.q[q.id].box : 0), 0) / (lesson.questions.length * (GAPS.length - 1));

  // One section as steps: each card is followed at once by the questions that test it.
  const sectionSteps = (lesson, sec, from = 0) => {
    const cards = lesson[sec];
    const qs = lesson.questions.filter(q => q.sec === sec);
    const ask = q => ({ kind: 'q', q, lesson });
    const steps = cards.slice(from).flatMap((card, k) => [
      { kind: 'card', lesson, sec, card, n: from + k + 1, of: cards.length },
      ...qs.filter(q => q.after === from + k + 1).map(ask)
    ]);
    steps.push(...qs.filter(q => !q.after).map(ask));
    if (sec === 'core') steps.push({ kind: 'card', lesson, sec, card: { h: 'Key ideas', body: [{ keys: lesson.key }] } });
    return steps;
  };

  const reviewSteps = ids => ids.map(id => ({ kind: 'q', ...QUESTIONS.get(id), review: true }));
  const tally = steps => `${plural(steps.filter(s => s.kind === 'card' && s.n).length, 'card')}, ${plural(steps.filter(s => s.kind === 'q').length, 'question')}`;

  // Today's session: due reviews first, then the next new material for the chosen length.
  const planToday = mode => {
    const due = dueIds();
    const reviewOnly = mode.id === 'short' && due.length >= BACKLOG;
    const target = SECTIONS.slice(0, mode.upto + 1);
    const lesson = reviewOnly ? null : LESSONS.find(l => target.some(sec => !doneOf(l)[sec]));
    const parts = lesson ? target.filter(sec => !doneOf(lesson)[sec]).map(sec => [lesson, sec]) : [];
    const reviews = shuffled(due.slice(0, reviewOnly ? 12 : mode.reviews));
    const fresh = parts.flatMap(([l, sec]) => sectionSteps(l, sec, resumeAt(l, sec)));
    let steps = [...reviewSteps(reviews), ...fresh];
    const bits = [];
    if (reviews.length) bits.push(plural(reviews.length, 'review question'));
    if (lesson) {
      const resuming = parts.some(([l, sec]) => resumeAt(l, sec));
      bits.push(`Lesson ${lessonNumber(lesson)}, ${lesson.title}: ${parts.map(([, sec]) => SEC_NAME[sec]).join(' + ')} (${tally(fresh)}${resuming ? ', picking up where you stopped' : ''})`);
    }
    let text = bits.join(', then ') + '.';
    if (reviewOnly) text = `${due.length} questions are due, so this session is review only: ${reviews.length} of them. New material returns once fewer than ${BACKLOG} are due.`;
    else if (!lesson && steps.length) text += ' Every lesson written so far is finished at this length.';
    if (!steps.length) {
      const weakest = Object.keys(S.q).filter(id => QUESTIONS.has(id))
        .sort((a, b) => S.q[a].box - S.q[b].box || S.q[a].due - S.q[b].due).slice(0, 6);
      steps = reviewSteps(shuffled(weakest));
      text = `Nothing is due today and every lesson written so far is finished at this length. Practise your ${plural(weakest.length, 'weakest question')}.`;
    }
    return { steps, parts, text };
  };

  // ---------- glossary ----------

  // A bottom sheet that closes on a tap outside it. `build` receives the close function and returns the contents.
  const openSheet = (label, build) => {
    const dialog = el('dialog', { class: 'sh-dialog bottom', 'aria-label': label });
    dialog.append(el('div', { class: 'sh-dialog-in' }, build(() => dialog.close())));
    dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
    dialog.addEventListener('close', () => dialog.remove());
    document.body.append(dialog);
    dialog.showModal();
  };

  const closeButton = close => el('button', { type: 'button', class: 'sh-btn block', textContent: 'Close', onclick: close });

  const showTerm = term => openSheet(term.t, close => [
    el('h2', { textContent: term.t }),
    el('p', { textContent: term.d }),
    el('p', { class: 'sh-muted', textContent: `From Lesson ${term.li + 1}: ${LESSONS[term.li].title}` }),
    closeButton(close)
  ]);

  // Make the first use of each already-taught term tappable. `before` is the reading position: lesson index × 3 + section index.
  const linkTerms = (root, before) => {
    const open = new Set(TERMS.filter(t => t.re && t.order < before));
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) {
      if (!walker.currentNode.parentElement.closest('pre, button, figure, th, h1, .py, .steps')) nodes.push(walker.currentNode);
    }
    let linked = 0;
    for (const node of nodes) {
      let rest = node;
      while (open.size && linked < 5) {
        let best = null;
        for (const term of open) {
          const m = term.re.exec(rest.data);
          if (m && (!best || m.index < best.m.index || (m.index === best.m.index && m[0].length > best.m[0].length))) best = { term, m };
        }
        if (!best) break;
        const hit = rest.splitText(best.m.index);
        rest = hit.splitText(best.m[0].length);
        const { term } = best;
        hit.replaceWith(el('button', { type: 'button', class: 'term', textContent: hit.data, onclick: () => showTerm(term) }));
        open.delete(term);
        linked++;
      }
    }
  };

  // ---------- Python, run in a background worker so an endless loop can be stopped ----------

  // Libraries the code imports (numpy, pandas, scikit-learn) download on first use, under their own, longer time limit.
  const Py = (() => {
    const source = `importScripts(${JSON.stringify(PYODIDE + 'pyodide.js')});
const boot = loadPyodide({ indexURL: ${JSON.stringify(PYODIDE)} }).then(py => {
  // pandas 2.2 warns on every import about a library it will need in version 3. It says nothing about the learner's code.
  py.runPython("import warnings; warnings.filterwarnings('ignore', message='(?s).*Pyarrow will become a required dependency', category=DeprecationWarning)");
  return py;
});
boot.then(() => postMessage({ ready: true }), () => postMessage({ ready: false }));
onmessage = async e => {
  const py = await boot;
  let failed = false; // a download that fails is reported through errorCallback, not thrown
  try { await py.loadPackagesFromImports(e.data, { messageCallback: () => {}, errorCallback: () => { failed = true; } }); }
  catch { failed = true; }
  if (failed) { postMessage({ out: '', err: 'library' }); return; }
  postMessage({ loaded: true });
  let out = '';
  const add = line => { out += line + '\\n'; };
  py.setStdout({ batched: add });
  py.setStderr({ batched: add });
  try { await py.runPythonAsync(e.data); postMessage({ out }); }
  catch (err) { postMessage({ out, err: String(err.message || err) }); }
};`;
    let worker = null;
    let ready = null;

    const stop = () => { worker.terminate(); worker = null; };

    const boot = () => {
      worker = new Worker(URL.createObjectURL(new Blob([source], { type: 'text/javascript' })));
      ready = new Promise((resolve, reject) => {
        const fail = () => { clearTimeout(timer); stop(); reject(new Error('load')); };
        const timer = setTimeout(fail, 60000);
        worker.onerror = fail;
        worker.onmessage = e => { if (e.data.ready) { clearTimeout(timer); resolve(); } else fail(); };
      });
    };

    const exec = async code => {
      if (!worker) boot();
      await ready;
      return new Promise(resolve => {
        let timer = 0;
        const limit = (ms, err) => {
          clearTimeout(timer);
          timer = setTimeout(() => { stop(); resolve({ out: '', err }); }, ms);
        };
        limit(180000, 'library');
        worker.onmessage = e => {
          if (e.data.loaded) limit(8000, 'timeout');
          else { clearTimeout(timer); resolve(e.data); }
        };
        worker.postMessage(code);
      });
    };

    // One run at a time: a second Run waits for the first to finish.
    let last = Promise.resolve();
    const run = code => (last = last.catch(() => {}).then(() => exec(code)));

    return { run };
  })();

  // Turn a Python traceback into one line a beginner can act on.
  const explainError = err => {
    if (err === 'timeout') return 'Stopped after 8 seconds. The code may contain a loop that never ends.';
    if (err === 'library') return 'A Python library this code uses could not download. Check your connection and run it again.';
    const lines = err.trim().split('\n');
    const where = [...err.matchAll(/File "<exec>", line (\d+)/g)].pop();
    return (where ? `Line ${where[1]}: ` : '') + lines[lines.length - 1];
  };

  // A code box with an output area. `buttons` receives the pieces and returns the action button.
  const editor = (code, label, buttons) => {
    const id = nextId('code');
    const area = el('textarea', { id, value: code, rows: code.split('\n').length + 1, spellcheck: false, autocapitalize: 'off', autocomplete: 'off' });
    const out = el('pre', { class: 'out', 'aria-live': 'polite' });
    const show = (text, cls) => { out.textContent = text; out.className = `out ${cls}`; };
    const reset = el('button', { type: 'button', class: 'sh-btn sm ghost', textContent: 'Reset', onclick: () => { area.value = code; show('', ''); } });
    return el('div', { class: 'py' }, el('label', { for: id, html: label }), area, el('div', { class: 'pyrow' }, buttons(area, show), reset), out);
  };

  const WAITING = 'Running. The first run loads Python, and any library the code uses, so it takes longer.';
  const NO_PYTHON = 'Python could not load here. Check your connection and try again.';

  const pyBlock = b => editor(b.py, 'Python you can edit and run', (area, show) => {
    const run = el('button', {
      type: 'button', class: 'sh-btn sm primary', textContent: 'Run',
      onclick: async () => {
        run.disabled = true;
        show(WAITING, 'wait');
        try {
          const r = await Py.run(area.value);
          if (r.err) show(r.out + explainError(r.err), 'err');
          else show(r.out || '(No output. Use print to show a value.)', 'ok');
        } catch {
          show(`${NO_PYTHON}\nThe original code prints:\n${b.expect}`, 'err');
        }
        run.disabled = false;
      }
    });
    return run;
  });

  // A coding exercise: the learner's code runs, followed by a hidden check, and the output must match.
  const taskBlock = t => {
    let misses = 0;
    const answer = el('pre', { class: 'code', textContent: t.solution, hidden: true });
    const reveal = el('button', { type: 'button', class: 'sh-btn sm ghost', textContent: 'Show a solution', hidden: true, onclick: () => { answer.hidden = false; reveal.hidden = true; } });
    const box = editor(t.start, `<b>Exercise.</b> ${t.goal}`, (area, show) => {
      const check = el('button', {
        type: 'button', class: 'sh-btn sm primary', textContent: 'Check',
        onclick: async () => {
          check.disabled = true;
          show(WAITING, 'wait');
          let solved = false;
          try {
            const r = await Py.run(`${area.value}\n${t.check}`);
            const got = r.out.trim();
            solved = !r.err && got === t.expect;
            if (r.err) show(r.out + explainError(r.err), 'err');
            else if (solved) { show(`Correct. Your code prints:\n${got}`, 'ok'); reveal.hidden = true; }
            else show(`Not yet.\nYour code prints:\n${got || '(nothing)'}\nIt should print:\n${t.expect}`, 'err');
          } catch {
            show(NO_PYTHON, 'err');
            misses = 2;
          }
          if (!solved && ++misses >= 2 && answer.hidden) reveal.hidden = false;
          check.disabled = false;
        }
      });
      return check;
    });
    box.classList.add('task');
    box.append(reveal, answer);
    return box;
  };

  // ---------- lesson content ----------

  const tableBlock = t => el('div', { class: 'scroll' },
    el('table', {},
      el('thead', {}, el('tr', {}, t.head.map(c => el('th', { html: c })))),
      el('tbody', {}, t.rows.map(r => el('tr', {}, r.map(c => el('td', { html: c })))))));

  const flowBlock = boxes => el('ol', { class: 'flow' },
    boxes.map(b => el('li', {}, el('b', { textContent: b.t }), el('span', { textContent: b.d }))));

  const aside = (cls, title, html) => el('aside', { class: cls }, el('b', { textContent: title }), el('p', { html }));

  // Guided practice: one small numeric step at a time, each explained once it is solved or after two tries.
  const stepsBlock = s => {
    const box = el('div', { class: 'steps' }, el('p', { html: s.intro }));
    const add = k => {
      const step = s.list[k];
      const input = el('input', { id: nextId('step'), type: 'text', inputMode: 'decimal', autocomplete: 'off', 'aria-label': `Step ${k + 1} answer` });
      const note = el('p', { class: 'stepnote', 'aria-live': 'polite' });
      let tries = 0;
      const check = () => {
        const value = readNumber(input.value);
        if (Number.isNaN(value)) return;
        const ok = near(value, step.a);
        if (!ok && ++tries < 2) {
          note.textContent = 'Not yet. Try once more.';
          input.select();
          return;
        }
        input.disabled = true;
        input.value = num(step.a);
        input.className = ok ? 'right' : 'shown';
        button.remove();
        note.innerHTML = (ok ? '' : `The answer is ${num(step.a)}. `) + step.done;
        if (k + 1 < s.list.length) add(k + 1).querySelector('input').focus();
      };
      const button = el('button', { type: 'button', class: 'sh-btn sm', textContent: 'Check', onclick: check });
      input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); check(); } });
      const row = el('div', { class: 'step' }, el('p', { html: `<b>${k + 1}.</b> ${step.ask}` }), el('div', { class: 'steprow' }, input, button), note);
      box.append(row);
      return row;
    };
    add(0);
    return box;
  };

  const block = b => {
    if (typeof b === 'string') return el('p', { html: b });
    if (b.eq) return el('div', { class: 'eq', html: b.eq });
    if (b.note) return aside('note', 'Applied to AF prediction', b.note);
    if (b.tip) return aside('tip', 'Quick maths', b.tip);
    if (b.keys) return el('ul', { class: 'keys' }, b.keys.map(k => el('li', { textContent: k })));
    if (b.table) return tableBlock(b.table);
    if (b.flow) return flowBlock(b.flow);
    if (b.widget) return (FIGURES[b.widget] || UNIT_FIGURES[b.widget])(KIT);
    if (b.pic) return el('figure', { class: 'pic' }, el('div', { html: b.pic }), b.cap ? el('figcaption', { html: b.cap }) : null);
    if (b.steps) return stepsBlock(b.steps);
    if (b.task) return taskBlock(b.task);
    return pyBlock(b);
  };

  // ---------- interactive figures: built once, then only attributes change ----------

  const ruleText = (w, b) => `y = ${fmt(w, 1)} × x ${b < 0 ? '−' : '+'} ${fmt(Math.abs(b), 1)}`;
  const mse = (predict, points) => points.reduce((sum, [x, y]) => sum + (predict(x) - y) ** 2, 0) / points.length;

  // A small x-y chart with a clipped drawing layer.
  const chart = (xMax, yMin, yMax, yStep, xName, yName) => {
    const W = 320, H = 232, L = 34, R = 10, T = 20, B = 34;
    const sx = x => L + (x / xMax) * (W - L - R);
    const sy = y => T + ((yMax - y) / (yMax - yMin)) * (H - T - B);
    const clip = nextId('clip');
    const text = (x, y, anchor, value) => {
      const t = svg('text', { x, y, class: 'tick', 'text-anchor': anchor });
      t.textContent = value;
      return t;
    };
    const root = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'chart', role: 'img' },
      svg('clipPath', { id: clip }, svg('rect', { x: L, y: T, width: W - L - R, height: H - T - B })));
    for (let x = 0; x <= xMax; x++) root.append(svg('line', { x1: sx(x), x2: sx(x), y1: T, y2: H - B, class: 'grid' }), text(sx(x), H - 20, 'middle', x));
    for (let y = yMin; y <= yMax; y += yStep) root.append(svg('line', { x1: L, x2: W - R, y1: sy(y), y2: sy(y), class: y === 0 ? 'axis' : 'grid' }), text(L - 6, sy(y) + 4, 'end', num(y)));
    root.append(text(W - R, H - 4, 'end', xName), text(2, 10, 'start', yName));
    const layer = svg('g', { 'clip-path': `url(#${clip})` });
    root.append(layer);
    const segment = (w, b) => ({ x1: sx(0), y1: sy(b), x2: sx(xMax), y2: sy(w * xMax + b) });
    const dots = (points, cls) => points.map(([x, y]) => svg('circle', { cx: sx(x), cy: sy(y), r: 5, class: cls }));
    return { root, layer, sx, sy, segment, dots };
  };

  const slider = (label, min, max, step, value, draw) => {
    const id = nextId('slider');
    const name = el('label', { for: id, textContent: label });
    const input = el('input', { id, type: 'range', min, max, step, value, oninput: perFrame(draw) });
    return { input, name, row: el('div', { class: 'slider' }, name, input) };
  };

  const toggle = (label, pressed, onclick, detail) => el('button', { type: 'button', class: (pressed ? 'on' : '') + (detail ? ' len' : ''), 'aria-pressed': String(pressed), onclick },
    detail ? [el('b', { textContent: label }), el('span', { textContent: detail })] : label);

  const FIGURES = {
    machine() {
      const cells = ['x', '× 2', '', '+ 1', 'y'].map((text, k) => el('span', { class: k % 2 ? 'op' : 'val', textContent: text }));
      const draw = () => {
        const x = Number(s.input.value);
        cells[0].textContent = `x = ${x}`;
        cells[2].textContent = 2 * x;
        cells[4].textContent = `y = ${2 * x + 1}`;
      };
      const s = slider('Input x', 0, 10, 1, 3, draw);
      draw();
      const arrow = () => el('i', { 'aria-hidden': 'true', textContent: '→' });
      return el('figure', { class: 'widget' }, s.row, el('div', { class: 'chain', 'aria-live': 'polite' }, cells.flatMap((cell, k) => (k ? [arrow(), cell] : [cell]))));
    },

    line() {
      const c = chart(5, -4, 16, 4, 'x', 'y');
      const rule = svg('line', { class: 'rule' });
      const dot = svg('circle', { r: 6, class: 'dot' });
      c.layer.append(rule, dot);
      const read = el('p', { class: 'readout' });
      const draw = () => {
        const w = Number(sw.input.value), b = Number(sb.input.value), y = w * 4 + b;
        set(rule, c.segment(w, b));
        set(dot, { cx: c.sx(4), cy: c.sy(y) });
        c.root.setAttribute('aria-label', `Line for ${ruleText(w, b)}`);
        read.textContent = `${ruleText(w, b)}. When x = 4, y = ${fmt(y, 1)}.`;
      };
      const sw = slider('Weight w', -2, 3, 0.5, 2, draw);
      const sb = slider('Bias b', -4, 4, 1, 1, draw);
      draw();
      return el('figure', { class: 'widget' }, c.root, sw.row, sb.row, read);
    },

    loss() {
      const points = [[1, 2], [2, 5], [3, 6], [4, 9]];
      const c = chart(5, -2, 12, 2, 'x', 'y');
      const rule = svg('line', { class: 'rule' });
      const misses = points.map(([x, y]) => svg('line', { x1: c.sx(x), x2: c.sx(x), y1: c.sy(y), class: 'miss' }));
      c.layer.append(rule, ...misses, ...c.dots(points, 'dot'));
      const read = el('p', { class: 'readout' });
      let best = Infinity;
      const draw = () => {
        const w = Number(sw.input.value), b = Number(sb.input.value);
        const loss = mse(x => w * x + b, points);
        best = Math.min(best, loss);
        set(rule, c.segment(w, b));
        points.forEach(([x], k) => misses[k].setAttribute('y2', c.sy(w * x + b)));
        c.root.setAttribute('aria-label', `Four data points and the line ${ruleText(w, b)}, loss ${loss.toFixed(2)}`);
        read.textContent = `${ruleText(w, b)}. Loss = ${loss.toFixed(2)}. Lowest you have found: ${best.toFixed(2)}. The lowest possible for a straight line here is 0.20.`;
      };
      const sw = slider('Weight w', 0, 4, 0.1, 1, draw);
      const sb = slider('Bias b', -3, 3, 0.5, 0, draw);
      draw();
      return el('figure', { class: 'widget' }, c.root, sw.row, sb.row, read);
    },

    bowl() {
      const points = [[1, 2], [2, 4], [3, 6]];
      const lossAt = w => mse(x => w * x, points);
      const c = chart(4, 0, 20, 5, 'weight w', 'loss');
      const curve = Array.from({ length: 41 }, (_, k) => `${c.sx(k / 10)},${c.sy(lossAt(k / 10))}`).join(' ');
      const dot = svg('circle', { r: 7, class: 'dot' });
      c.layer.append(svg('polyline', { points: curve, class: 'rule' }), dot);
      const read = el('p', { class: 'readout' });
      const draw = () => {
        const w = Number(s.input.value), loss = lossAt(w);
        set(dot, { cx: c.sx(w), cy: c.sy(loss) });
        c.root.setAttribute('aria-label', `Loss plotted against the weight, with the weight at ${w.toFixed(2)}`);
        read.textContent = `Weight ${w.toFixed(2)} gives a loss of ${loss.toFixed(2)}.${loss === 0 ? ' This is the bottom of the bowl.' : ''}`;
      };
      const s = slider('Weight w', 0, 4, 0.25, 0.5, draw);
      draw();
      return el('figure', { class: 'widget' }, c.root, s.row, read);
    },

    fit() {
      const train = [[1, 1.8], [2, 1.2], [3, 3.8], [4, 3.2], [5, 5.8], [6, 5.2]];
      const fresh = [[1.4, 1.5], [2.4, 2.3], [3.6, 3.7], [4.6, 4.5], [5.4, 5.5]];
      const nearest = x => train.reduce((a, b) => (Math.abs(b[0] - x) < Math.abs(a[0] - x) ? b : a))[1];
      const models = { line: x => x, memo: nearest };
      const c = chart(7, 0, 8, 2, 'measurement', 'outcome');
      const edges = [0, ...train.slice(1).map(([x]) => x - 0.5), 7];
      const paths = {
        line: `M${c.sx(0)},${c.sy(0)} L${c.sx(7)},${c.sy(7)}`,
        memo: train.map(([, y], k) => `${k ? 'L' : 'M'}${c.sx(edges[k])},${c.sy(y)} H${c.sx(edges[k + 1])}`).join(' ')
      };
      const rule = svg('path', { class: 'rule' });
      const miss = points => points.map(([x, y]) => svg('line', { x1: c.sx(x), x2: c.sx(x), y1: c.sy(y), class: 'miss' }));
      const trainMiss = miss(train), freshMiss = miss(fresh);
      const freshLayer = svg('g', {}, ...freshMiss, ...c.dots(fresh, 'dot fresh'));
      c.layer.append(rule, ...trainMiss, ...c.dots(train, 'dot'), freshLayer);
      const read = el('p', { class: 'readout' });
      const controls = el('div', { class: 'sh-seg', role: 'group', 'aria-label': 'Model' });
      const reveal = el('button', { type: 'button', class: 'sh-btn sm' });
      let model = 'line', shown = false;
      const draw = () => {
        const predict = models[model];
        rule.setAttribute('d', paths[model]);
        train.forEach(([x], k) => trainMiss[k].setAttribute('y2', c.sy(predict(x))));
        fresh.forEach(([x], k) => freshMiss[k].setAttribute('y2', c.sy(predict(x))));
        freshLayer.style.display = shown ? '' : 'none';
        controls.replaceChildren(
          toggle('Straight line', model === 'line', () => { model = 'line'; draw(); }),
          toggle('Memoriser', model === 'memo', () => { model = 'memo'; draw(); }));
        reveal.textContent = shown ? 'Hide new patients' : 'Show new patients';
        c.root.setAttribute('aria-label', `Six training patients${shown ? ' and five new patients' : ''} with the ${model === 'line' ? 'straight line' : 'memoriser'}`);
        read.textContent = `Training loss ${mse(predict, train).toFixed(2)}. ${shown ? `New-patient loss ${mse(predict, fresh).toFixed(2)}.` : 'New patients are hidden.'}`;
      };
      reveal.addEventListener('click', () => { shown = !shown; draw(); });
      draw();
      return el('figure', { class: 'widget' },
        el('p', { class: 'legend', html: '<span class="key"></span> training patient <span class="key fresh"></span> new patient. Red bars are errors.' }),
        c.root, controls, reveal, read);
    },

    folds() {
      const blocks = [1, 2, 3, 4, 5].map(n => el('span', { textContent: n }));
      const read = el('p', { class: 'readout' });
      let round = 1;
      const draw = () => {
        blocks.forEach((b, k) => { b.className = k + 1 === round ? 'fold score' : 'fold'; });
        read.textContent = `Round ${round} of 5. Train on folds ${[1, 2, 3, 4, 5].filter(n => n !== round).join(', ')}. Score on fold ${round}.${round === 5 ? ' Every fold has now been scored once.' : ''}`;
      };
      draw();
      return el('figure', { class: 'widget' },
        el('div', { class: 'folds', role: 'img', 'aria-label': 'Five folds, one highlighted as the scoring fold' }, blocks),
        read,
        el('button', { type: 'button', class: 'sh-btn sm', textContent: 'Next round', onclick: () => { round = round % 5 + 1; draw(); } }));
    },

    threshold() {
      const patients = [[90, 1], [80, 1], [70, 0], [60, 1], [50, 0], [40, 1], [30, 0], [20, 0], [10, 0], [5, 0]];
      const W = 320, H = 96, L = 14, R = 14, mid = 44;
      const sx = pct => L + (pct / 100) * (W - L - R);
      const band = svg('rect', { y: 8, height: 64, class: 'flagged' });
      const cut = svg('line', { y1: 4, y2: 76, class: 'cut' });
      const root = svg('svg', { viewBox: `0 0 ${W} ${H}`, class: 'chart', role: 'img' },
        band,
        svg('line', { x1: sx(0), x2: sx(100), y1: mid, y2: mid, class: 'axis' }),
        cut,
        ...patients.map(([risk, af]) => svg('circle', { cx: sx(risk), cy: mid, r: 8, class: af ? 'dot' : 'dot hollow' })),
        ...[0, 50, 100].map(p => {
          const t = svg('text', { x: sx(p), y: H - 4, class: 'tick', 'text-anchor': 'middle' });
          t.textContent = (p / 100).toFixed(1);
          return t;
        }));
      const names = ['Caught (true positives)', 'False alarms', 'Missed', 'Correctly left alone', 'Sensitivity', 'Specificity', 'PPV'];
      const values = names.map(() => el('dd'));
      const share = (a, b) => (b ? `${a} of ${b} (${Math.round(100 * a / b)}%)` : 'none flagged');
      const draw = () => {
        const at = Number(s.input.value);
        const count = (flagged, af) => patients.filter(([risk, has]) => (risk >= at) === flagged && has === af).length;
        const tp = count(true, 1), fp = count(true, 0), fn = count(false, 1), tn = count(false, 0);
        set(band, { x: sx(at), width: sx(100) - sx(at) });
        set(cut, { x1: sx(at), x2: sx(at) });
        root.setAttribute('aria-label', `Ten patients by risk with the threshold at ${(at / 100).toFixed(2)}`);
        s.name.textContent = `Threshold ${(at / 100).toFixed(2)}`;
        [tp, fp, fn, tn, share(tp, tp + fn), share(tn, tn + fp), share(tp, tp + fp)].forEach((v, k) => { values[k].textContent = v; });
      };
      const s = slider('', 5, 95, 5, 50, draw);
      draw();
      return el('figure', { class: 'widget' },
        el('p', { class: 'legend', html: '<span class="key"></span> developed AF <span class="key hollow"></span> did not. Shaded = flagged.' }),
        root, s.row,
        el('dl', { class: 'stats' }, names.flatMap((name, k) => [el('dt', { textContent: name }), values[k]])));
    },

    sample() {
      // A drawn EGM-like trace over one second: two sharp deflections and two slow bumps.
      const spike = (t, at) => { const u = (t - at) / 0.006; return -0.9 * 1.6487 * u * Math.exp(-u * u / 2); };
      const bump = (t, at) => 0.25 * Math.exp(-((t - at) ** 2) / (2 * 0.03 ** 2));
      const signal = t => spike(t, 0.3) + spike(t, 0.8) + bump(t, 0.42) + bump(t, 0.92);
      const c = chart(1, -1, 1, 1, 'seconds', '');
      const truth = Array.from({ length: 501 }, (_, k) => `${c.sx(k / 500).toFixed(1)},${c.sy(signal(k / 500)).toFixed(1)}`).join(' ');
      const stored = svg('polyline', { class: 'rule thin' });
      const marks = svg('path', { class: 'marks' });
      c.layer.append(svg('polyline', { points: truth, class: 'ghost' }), stored, marks);
      const read = el('p', { class: 'readout' });
      const draw = () => {
        const rate = Number(s.input.value);
        const at = Array.from({ length: rate }, (_, k) => [c.sx(k / rate).toFixed(1), c.sy(signal(k / rate)).toFixed(1)]);
        stored.setAttribute('points', at.map(p => p.join(',')).join(' '));
        marks.setAttribute('d', at.map(([x, y]) => `M${x},${y}h0`).join(''));
        c.root.setAttribute('aria-label', `A one-second trace sampled ${rate} times`);
        read.textContent = `At ${rate} samples per second, this second is stored as ${rate} numbers. The grey curve is the true signal.`;
      };
      const s = slider('Samples per second', 20, 200, 20, 200, draw);
      draw();
      return el('figure', { class: 'widget' }, c.root, s.row, read);
    }
  };

  // Calls frame(seconds since start) on every animation frame until it returns false or the figure leaves the screen.
  // Start it from a button press, once the figure is on screen.
  const animate = (node, frame) => {
    const start = performance.now();
    const tick = now => { if (node.isConnected && frame((now - start) / 1000) !== false) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  };

  // The drawing tools a unit file's own figures receive: figures: { name: kit => element }.
  const KIT = { el, svg, set, chart, slider, toggle, perFrame, fmt, num, mse, nextId, animate, reducedMotion: REDUCED_MOTION };

  // ---------- screens ----------

  let view = 'home';
  let mode = MODES[0];
  let keys = null; // keyboard handler of the screen in view

  // Optional pieces of a screen arrive as null and are left out (replaceChildren would print them as the text "null").
  const show = (name, ...nodes) => {
    view = name;
    keys = null;
    app.replaceChildren(...nodes.filter(Boolean));
    window.scrollTo(0, 0);
  };

  const chip = () => el('span', { html: SHUI.chip(S.pts) }).firstChild;
  const backButton = (label, onclick) => el('button', { type: 'button', class: 'sh-btn sm ghost back', onclick }, icon('back'), label);
  const topBar = (back, label) => el('header', { class: 'top' }, back, label ? el('span', { class: 'brand', textContent: label }) : null, chip());

  // Shown until Python has run once on some device signed in to this account.
  const pythonCheck = () => {
    if (S.py) return null;
    const result = el('p', { class: 'checks', 'aria-live': 'polite' });
    const button = el('button', {
      type: 'button', class: 'sh-btn sm', textContent: 'Run the check',
      onclick: async () => {
        button.disabled = true;
        button.textContent = 'Checking. This can take 20 seconds.';
        let ok = false;
        try {
          const r = await Py.run('print(6 * 7)');
          ok = !r.err && r.out.trim() === '42';
        } catch { /* reported below */ }
        result.className = `checks ${ok ? 'pass' : 'fail'}`;
        result.textContent = ok ? '✓ Python runs on this device.' : '✗ Python did not load. Lessons still work, but code cannot be run. Check your connection and try again.';
        if (ok) { S.py = true; save(); Store.push(); }
        button.disabled = false;
        button.textContent = 'Run the check again';
        button.hidden = ok;
      }
    });
    return el('section', { class: 'sh-card' },
      el('h2', { textContent: 'Check Python on this device' }),
      el('p', { class: 'sh-muted', textContent: 'The Python sections run code on your phone or computer. One tap confirms it works here.' }),
      button, result);
  };

  const todayCard = () => {
    const plan = planToday(mode);
    return el('section', { class: 'sh-card' },
      el('h2', { textContent: 'Today' }),
      el('div', { class: 'sh-seg', role: 'group', 'aria-label': 'Session length' },
        MODES.map(m => toggle(m.label, m === mode, () => { mode = m; renderHome(); }, m.detail))),
      el('p', { class: 'summary', textContent: plan.text }),
      plan.steps.length
        ? el('button', { type: 'button', class: 'sh-btn primary block', onclick: () => runSession(plan.steps, plan.parts) }, icon('start'), 'Start today\'s session')
        : null);
  };

  const meter = share => el('span', { class: 'meter', role: 'img', 'aria-label': `Memory strength ${Math.round(100 * share)}%` },
    el('i', { style: `transform:scaleX(${share})` }));

  const lessonTile = lesson => {
    const done = doneOf(lesson);
    const finished = SECTIONS.filter(sec => done[sec]).map(sec => SEC_NAME[sec]);
    const seen = lesson.questions.some(q => S.q[q.id]);
    return el('button', { type: 'button', class: 'sh-tile', onclick: () => renderLesson(lesson) },
      el('span', { class: done.core ? 'sh-ic done' : 'sh-ic', textContent: lessonNumber(lesson) }),
      el('span', { class: 'tx' },
        el('b', { textContent: lesson.title }),
        el('span', { textContent: `${lesson.about} ${finished.length ? `Done: ${finished.join(', ')}.` : 'Not started.'}` }),
        seen ? meter(memory(lesson)) : null));
  };

  const courseMap = () => window.COURSE_PARTS.flatMap(part => [
    el('h3', { textContent: part.title }),
    el('ol', { class: 'map' }, part.units.map(u => {
      const written = UNITS.some(x => x.n === u.n);
      return el('li', { class: written ? 'written' : '' },
        el('b', { textContent: `Unit ${u.n}: ${u.title}` }),
        el('span', { textContent: u.about }),
        el('em', { textContent: written ? 'Written' : 'Not written yet' }));
    }))
  ]);

  const settingsDialog = () => {
    const themes = el('div');
    SHUI.theme.picker(themes);
    openSheet('Settings', close => [
      el('h2', { textContent: 'Settings' }),
      el('h3', { textContent: 'Color scheme' }),
      el('p', { class: 'sh-muted', textContent: 'One choice for all of Study Hall on this device.' }),
      themes,
      closeButton(close)
    ]);
  };

  // ---------- test-outs ----------

  // Each unit's test-out in order, stopping after the first unit where fewer than half the sections pass.
  const startPlacement = units => {
    let k = 0, current = testSteps(units[0]), stopped = false;
    runSession(current, [], {
      more: () => {
        stopped = 2 * current.filter(s => s.passed).length < current.length;
        if (stopped || ++k === units.length) return [];
        current = testSteps(units[k]);
        return current;
      },
      after: () => (stopped && k + 1 < units.length ? ` The test stopped at Unit ${units[k].n}, where fewer than half the sections were passed. Start your lessons there.` : '')
    });
  };

  const NO_GUESSING = 'Not sure? Tap “I don\'t know”. A lucky guess would skip a section you need.';

  // Offered while any written section is not done.
  const placementCard = () => {
    const units = UNITS.filter(u => testable(u).length);
    if (!units.length) return null;
    return el('section', { class: 'sh-card' },
      el('h2', { textContent: 'Placement test' }),
      el('p', { class: 'sh-muted', textContent: `Already know some of this? One question for each section you have not done, unit by unit. Each section you pass is marked done. The test stops after the first unit where you pass fewer than half. ${NO_GUESSING}` }),
      el('button', { type: 'button', class: 'sh-btn block', textContent: 'Start the placement test', onclick: () => startPlacement(units) }));
  };

  const testOutDialog = unit => openSheet(`Test out of Unit ${unit.n}`, close => [
    el('h2', { textContent: `Test out of Unit ${unit.n}` }),
    el('p', { textContent: `${plural(testable(unit).length, 'question')}, one for each section you have not done. A right answer marks its section done, and the question comes back for review in ${GAPS[TEST_BOX]} days. ${NO_GUESSING}` }),
    el('div', { class: 'row2' },
      el('button', { type: 'button', class: 'sh-btn', textContent: 'Cancel', onclick: close }),
      el('button', { type: 'button', class: 'sh-btn primary block', textContent: 'Start', onclick: () => { close(); runSession(testSteps(unit), [], {}); } }))
  ]);

  function renderHome() {
    const lv = SHUI.points.levelOf(S.pts);
    const streak = S.streak.day >= today() - 1 ? S.streak.count : 0;
    show('home',
      topBar(el('a', { class: 'sh-btn sm ghost back', href: SH.root }, icon('back'), 'Study Hall')),
      el('div', { class: 'level' },
        el('span', { html: SHUI.ring(lv.level, lv.pct) }).firstChild,
        el('div', {},
          el('h1', { textContent: 'Machine Learning' }),
          el('p', { class: 'sh-muted', textContent: `${(lv.need - lv.into).toLocaleString('en-US')} points to level ${lv.level + 1} · ${streak ? `${plural(streak, 'day')} in a row` : 'no streak yet'}` }))),
      pythonCheck(),
      todayCard(),
      placementCard(),
      ...UNITS.map(u => el('section', { class: 'stack' },
        el('div', { class: 'unit-head' },
          el('h2', { textContent: `Unit ${u.n}: ${window.COURSE_MAP.find(m => m.n === u.n).title}` }),
          testable(u).length ? el('button', { type: 'button', class: 'sh-btn sm', 'aria-label': `Test out of Unit ${u.n}`, textContent: 'Test out', onclick: () => testOutDialog(u) }) : null),
        u.lessons.map(lessonTile))),
      el('button', { type: 'button', class: 'sh-tile', onclick: renderGlossary },
        el('span', { class: 'sh-ic', html: SHUI.icon('book') }),
        el('span', { class: 'tx' }, el('b', { textContent: 'Glossary' }), el('span', { textContent: `${plural(TERMS.length, 'term')} in plain words. Dotted words inside lessons open the same definitions.` }))),
      el('section', { class: 'stack' },
        el('h2', { textContent: 'The whole course' }),
        el('p', { class: 'sh-muted', textContent: 'Understanding first, then medical statistics. From Part 3 on, every unit ends with the other methods that could do the same job. Maths by hand and Python sit in the longer sessions. Part 5 is optional depth for later.' }),
        courseMap()),
      el('button', { type: 'button', class: 'sh-btn sm ghost gear', onclick: settingsDialog }, icon('settings'), 'Settings'),
      el('p', { class: 'sh-muted foot-note', textContent: Store.ok ? 'Progress is saved to your Study Hall account.' : 'Couldn\'t reach your account just now. Progress is kept on this device and saves when you\'re back online.' }));
  }

  const termList = terms => el('dl', { class: 'terms' }, terms.flatMap(t => [el('dt', { textContent: t.t }), el('dd', { textContent: t.d })]));

  function renderGlossary() {
    show('glossary',
      topBar(backButton('Course', renderHome)),
      el('h1', { textContent: 'Glossary' }),
      ...LESSONS.map((lesson, li) => el('section', { class: 'stack' },
        el('h2', { textContent: `Lesson ${li + 1}: ${lesson.title}` }),
        termList(lesson.terms))));
  }

  function renderLesson(lesson) {
    const done = doneOf(lesson);
    const start = sec => {
      const from = resumeAt(lesson, sec);
      const steps = sectionSteps(lesson, sec, from);
      const state = done[sec] ? '. Done. Open it again any time.' : from ? `. Picks up at card ${from + 1}.` : '';
      return el('button', { type: 'button', class: 'sh-tile', onclick: () => runSession(steps, [[lesson, sec]]) },
        el('span', { class: done[sec] ? 'sh-ic done' : 'sh-ic', textContent: done[sec] ? '✓' : SECTIONS.indexOf(sec) + 1 }),
        el('span', { class: 'tx' }, el('b', { textContent: `${SEC_NAME[sec]}, ${SEC_TIME[sec]}` }), el('span', { textContent: `${tally(steps)}${state}` })));
    };
    show('lesson',
      topBar(backButton('Course', renderHome)),
      el('div', { class: 'stack' },
        el('p', { class: 'sh-label', textContent: `Lesson ${lessonNumber(lesson)}` }),
        el('h1', { textContent: lesson.title }),
        el('p', { class: 'sh-muted', textContent: lesson.about })),
      el('div', { class: 'stack' }, SECTIONS.map(start)),
      el('section', { class: 'sh-card' }, el('h2', { textContent: 'Key ideas' }), block({ keys: lesson.key })),
      el('section', { class: 'stack' }, el('h2', { textContent: 'Terms in this lesson' }), termList(lesson.terms)));
  }

  // `test`, for a test-out: { more?: () => further steps once the queue runs out, after?: () => extra text for the results }.
  function runSession(steps, parts, test = null) {
    const queue = [...steps];
    const levelBefore = SHUI.points.levelOf(S.pts);
    let i = 0, right = 0, earned = 0, flip = false;

    const fill = el('i');
    const bar = el('div', { class: 'sh-progress', role: 'progressbar', 'aria-label': 'Session progress', 'aria-valuemin': 0 }, fill);
    const pts = chip();
    const stage = el('div', { class: 'stage' });
    const progress = n => {
      fill.style.width = `${Math.round(100 * n / queue.length)}%`;
      set(bar, { 'aria-valuemax': queue.length, 'aria-valuenow': n });
    };

    const leave = () => { save(); Store.push(); renderHome(); };

    const finish = () => {
      const t = today();
      for (const [lesson, sec] of parts) markDone(lesson, sec, t);
      if (S.streak.day !== t) S.streak = { day: t, count: S.streak.day === t - 1 ? S.streak.count + 1 : 1 };
      save();
      Store.push();
      const firstTries = queue.filter(s => s.kind === 'q' && !s.retry).length;
      const still = dueIds().length;
      const tomorrow = Object.values(S.q).filter(r => r.due === t + 1).length;
      view = 'results';
      keys = null;
      const results = el('div', { class: 'stage' });
      app.replaceChildren(results);
      window.scrollTo(0, 0);
      SHUI.results(results, {
        title: test ? 'Test done' : firstTries ? 'Session done' : 'Lesson read',
        score: right,
        total: firstTries,
        points: earned,
        levelBefore,
        levelAfter: SHUI.points.levelOf(S.pts),
        note: test
          ? testNote(queue.filter(s => s.test)) + (test.after ? test.after() : '')
          : `${plural(tomorrow, 'question')} will come back tomorrow${still ? `, and ${still} more ${still === 1 ? 'is' : 'are'} still due today` : ''}. Right answers return at longer and longer gaps, with new numbers each time. Missed ones return the next day.`,
        actions: [{ label: 'Back to the course', primary: true, onClick: renderHome }]
      });
    };

    // Forward skips questions already answered, so stepping back to re-read a card never re-asks them.
    const next = () => {
      do i++; while (i < queue.length && queue[i].answered);
      if (i === queue.length && test && test.more) queue.push(...test.more());
      if (i < queue.length) draw();
      else finish();
    };
    const back = () => {
      do i--; while (queue[i].kind !== 'card');
      draw();
    };

    const drawCard = step => {
      const { lesson, sec } = step;
      const li = LESSONS.indexOf(lesson);
      const done = doneOf(lesson);
      if (step.n > 1 && !done[sec] && step.n - 1 > ((done.at || {})[sec] || 0)) {
        S.lessons[lesson.id] = { ...done, at: { ...done.at, [sec]: step.n - 1 } };
        save();
      }
      const article = el('article', { class: 'lesson' },
        el('p', { class: 'sh-label', textContent: `Lesson ${li + 1} · ${SEC_NAME[sec]}${step.n ? ` · ${step.n} of ${step.of}` : ''}` }),
        el('h1', { textContent: step.card.h }),
        step.card.body.map(block));
      linkTerms(article, li * SECTIONS.length + SECTIONS.indexOf(sec));
      const hasEarlierCard = queue.slice(0, i).some(s => s.kind === 'card');
      stage.replaceChildren(article, el('div', { class: 'sh-cta row2' },
        hasEarlierCard ? el('button', { type: 'button', class: 'sh-btn', textContent: 'Back', onclick: back }) : null,
        el('button', { type: 'button', class: 'sh-btn primary block', textContent: 'Continue', onclick: next })));
    };

    const drawQuestion = step => {
      const q = step.view || (step.view = materialize(step.q));
      const known = (LESSONS.indexOf(step.lesson) + 1) * SECTIONS.length;
      let answered = false;
      const cta = el('div', { class: 'sh-cta row2' });

      const settle = (ok, verdict) => {
        answered = true;
        step.answered = true;
        if (step.test) step.passed = ok;
        if (!step.retry) {
          if (step.test ? gradeTest(step, ok) : grade(q.id, ok)) { SHUI.points.award(S, POINTS, pts); earned += POINTS; }
          if (ok) right++;
          else if (!step.test) queue.push({ ...step, answered: false, retry: true });
        }
        save();
        const why = q.why ? el('p', { html: q.why }) : null;
        if (why) linkTerms(why, known);
        const sheet = el('div', { class: `sh-sheet ${ok ? 'good' : 'bad'}`, role: 'status' },
          el('div', { class: 'sh-verdict', html: SHUI.icon(ok ? 'check' : 'close') }, el('span', { textContent: verdict || (ok ? 'Correct!' : 'Not quite') })),
          why,
          el('button', { type: 'button', class: `sh-btn block ${ok ? 'good' : 'primary'}`, textContent: 'Continue', onclick: next }));
        cta.replaceWith(sheet);
        progress(i + 1);
        sheet.lastChild.focus({ preventScroll: true });
        return sheet;
      };

      // In a test, "I don't know" counts as not passed and shows the answer, so nobody has to guess.
      const unsure = reveal => (step.test
        ? [el('button', { type: 'button', class: 'sh-btn', textContent: 'I don\'t know', onclick: () => { if (!answered) reveal(settle(false, 'Left for the lesson')); } })]
        : []);

      const kind = q.type === 'recall' ? 'Recall' : q.code ? 'Read the code' : q.type === 'num' ? 'Work it out' : 'Check';
      const where = `Lesson ${LESSONS.indexOf(step.lesson) + 1}`;
      const article = el('article', { class: 'question' },
        el('p', { class: 'sh-label', textContent: step.retry ? 'One more try' : step.test ? `Test · ${where} · ${SEC_NAME[step.sec]}` : step.review ? `Review · ${where}` : kind }),
        el('h1', { class: 'prompt', html: q.prompt }),
        q.code ? el('pre', { class: 'code', textContent: q.code }) : null);
      stage.replaceChildren(article, cta);

      if (q.type === 'recall') {
        const answer = el('p', { class: 'recall', html: q.answer, hidden: true });
        article.append(el('p', { class: 'sh-muted', textContent: 'Answer in your head or out loud first. Then compare.' }), answer);
        cta.append(el('button', {
          type: 'button', class: 'sh-btn primary block', textContent: 'Show the answer',
          onclick: () => {
            answer.hidden = false;
            linkTerms(answer, known);
            cta.replaceChildren(
              el('button', { type: 'button', class: 'sh-btn', textContent: 'Not yet', onclick: () => settle(false, 'It will come back tomorrow.') }),
              el('button', { type: 'button', class: 'sh-btn primary block', textContent: 'I had it', onclick: () => settle(true) }));
          }
        }));
        return;
      }

      if (q.type === 'num') {
        const input = el('input', { id: 'answer', type: 'text', inputMode: 'decimal', autocomplete: 'off', 'aria-label': 'Your answer' });
        const hint = el('p', { class: 'sh-muted', textContent: q.hint, hidden: true });
        const showAnswer = sheet => sheet.querySelector('.sh-verdict').insertAdjacentElement('afterend', el('p', { html: `The answer is <b>${num(q.a)}</b>.` }));
        const check = () => {
          const value = readNumber(input.value);
          if (answered || Number.isNaN(value)) return;
          input.disabled = true;
          const ok = near(value, q.a);
          input.className = ok ? 'right' : 'wrong';
          const sheet = settle(ok);
          if (!ok) showAnswer(sheet);
        };
        article.append(input);
        if (q.hint) article.append(el('button', { type: 'button', class: 'hint', textContent: 'Show a hint', onclick: e => { hint.hidden = false; e.target.hidden = true; } }), hint);
        cta.append(...unsure(sheet => { input.disabled = true; showAnswer(sheet); }),
          el('button', { type: 'button', class: 'sh-btn primary block', textContent: 'Check', onclick: check }));
        // preventDefault: otherwise the same key press lands on the Continue button that settle() focuses.
        keys = e => { if (e.key === 'Enter' && !answered) { e.preventDefault(); check(); } };
        input.focus();
        return;
      }

      const order = shuffled(q.opts.map((_, k) => k));
      const buttons = order.map((k, pos) => el('button', {
        type: 'button', class: 'sh-opt',
        onclick: () => {
          if (answered) return;
          const ok = k === q.a;
          buttons.forEach((b, p) => {
            b.disabled = true;
            b.className = `sh-opt ${order[p] === q.a ? (ok ? 'right' : 'reveal') : p === pos ? 'wrong' : 'dim'}`;
          });
          settle(ok);
        }
      }, el('span', { class: 'sh-key', textContent: pos + 1 }), el('span', { textContent: q.opts[k] })));
      article.append(el('div', { class: 'opts' }, buttons));
      cta.append(...unsure(() => buttons.forEach((b, p) => {
        b.disabled = true;
        b.className = `sh-opt ${order[p] === q.a ? 'reveal' : 'dim'}`;
      })));
      keys = e => { const b = buttons[Number(e.key) - 1]; if (b && !answered) b.click(); };
    };

    const draw = () => {
      keys = null;
      progress(i);
      flip = !flip;
      stage.className = `stage ${REDUCED_MOTION ? '' : flip ? 'sh-enter' : 'sh-enter-b'}`;
      (queue[i].kind === 'card' ? drawCard : drawQuestion)(queue[i]);
      window.scrollTo(0, 0);
    };

    show('session',
      el('header', { class: 'qtop' },
        el('button', { type: 'button', class: 'sh-btn sm ghost x', 'aria-label': 'End session', html: SHUI.icon('close'), onclick: leave }),
        bar, pts),
      stage);
    draw();
  }

  // ---------- start ----------

  const message = (title, text) => show('message', el('section', { class: 'sh-card' }, el('h2', { textContent: title }), el('p', { textContent: text })),
    el('a', { class: 'sh-btn block', href: SH.root }, 'Back to Study Hall'));

  document.addEventListener('keydown', e => { if (keys) keys(e); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) Store.push(); });

  (async () => {
    const [db, user] = await Promise.all([window.claude.use('db'), window.claude.use('user')]);
    let id;
    try { id = await user.id(); } catch { return; } // SH.install is sending this page to sign-in
    if (!await loadLessons(id)) {
      message('Lessons unavailable', 'The lessons could not be loaded. Check your connection and reload. If this keeps happening, your account may not have this course.');
      return;
    }
    storeKey = `ml:progress:${id}`;
    const saved = local.get(storeKey);
    if (isProgress(saved)) S = saved;
    renderHome();
    try { await Store.init(db, id); } catch { Store.ok = false; }
    if (view === 'home') renderHome();
  })();
})();
