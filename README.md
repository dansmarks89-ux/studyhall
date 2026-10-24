# Study Hall

Language and study apps with sign-in, saved progress and AI practice, for a small invited group.

- **Site:** static files served by GitHub Pages (this repo).
- **Accounts, progress and AI:** Supabase project `studyhall` (`wbrssohmepioxapwbcne`).
- **AI:** the Supabase Edge Function `ai` calls the Claude API with a key stored as the secret `ANTHROPIC_API_KEY`. The key is never in this repo or in the browser.

## Layout

| Path | What it is |
|---|---|
| `index.html` | Home: email-code sign-in and the list of apps the person is invited to |
| `shared/sh.js` | Shared sign-in, progress saving and AI calls for every app |
| `shared/supabase.js` | Supabase browser library (v2.117.2, vendored) |
| `spanish/index.html` | Clinic Spanish course (built file, do not edit by hand) |
| `src/spanish/` | Course source: `app.html`, compiled data, original content and specs |
| `vocab/` | Word Power, built: `index.html` plus hashed `data.*.json` and `gloss.*.json` (do not edit by hand) |
| `src/vocab/` | Word Power source: `app.html`; `data/items.json` (8,820 reviewed cards), `data/passages.json` (390 reading passages), `data/gloss.json` (tap-to-define dictionary); `content/` (round 1) and `content/round2/` (specs, reviewer instructions, review patches, pipeline scripts) |
| `cantonese/index.html`, `korean/index.html` | Cantonese and Korean courses (built files, do not edit by hand). `audio.json` beside each lists every recorded clip |
| `src/lang/` | Shared engine for both courses: `app.html`, `build.py`, `tools/check_level.py` (content checker), `tools/ko_pron.py` (Korean pronunciation) |
| `src/cantonese/content/`, `src/korean/content/` | Course content: `SPEC.md`, `levels/L1–L10.json` (checked and independently reviewed), `bank/` (original phrase banks) |
| `supabase/functions/ai/index.ts` | The AI function (source copy of what is deployed) |
| `supabase/functions/tts/index.ts` | The voice function: records course audio with Microsoft Azure neural voices into the public `audio` bucket, and reads AI replies aloud |
| `sw.js`, `manifest.webmanifest`, `icons/` | Home-screen app support |

Rebuild the Spanish page after changing `src/spanish/app.html` or its data:

```
python3 src/spanish/build.py hosted
```

Rebuild Word Power after changing `src/vocab/app.html` or anything in `src/vocab/data/`:

```
python3 src/vocab/build.py
```

Rebuild the Cantonese and Korean courses after changing `src/lang/app.html` or any level file
(check a level first with `python3 src/lang/tools/check_level.py yue|ko <file>`):

```
pip install --break-system-packages ToJyutping pycantonese g2pk2 kiwipiepy korean-romanizer
python3 src/lang/build.py all
```

After pushing, record any new audio (SQL editor; it restarts itself until every clip in `audio.json` exists, progress in `public.tts_sync`):

```sql
select net.http_post(url := 'https://wbrssohmepioxapwbcne.supabase.co/functions/v1/tts',
  headers := '{"Content-Type":"application/json"}'::jsonb,
  body := jsonb_build_object('op','sync','course','cantonese','token',(select v from private.secrets where k='tts_admin')),
  timeout_milliseconds := 120000);
```

## Adding an app

1. Put the app in its own folder, e.g. `korean/index.html`.
2. In its `<head>` load `../shared/supabase.js`, then `../shared/sh.js`, then `<script>SH.install("korean");</script>`.
3. The app then uses `window.claude.use("user" | "db" | "sample")` exactly like a claude.ai artifact, with progress stored per person under the course name.
4. Add it to the `APPS` list in `index.html`.

## Running it (SQL editor in Supabase)

Invite someone (course names: `spanish`, `vocab`, `cantonese`, `korean`; `*` = everything):

```sql
insert into public.invites (email, courses, note)
values ('person@example.com', '{spanish}', 'Their name');
```

Give someone another app:

```sql
update public.invites set courses = array_append(courses, 'korean')
where email = 'person@example.com';
```

Remove someone (they can no longer sign in, read or save progress, or use AI):

```sql
delete from public.invites where email = 'person@example.com';
```

Change the daily AI limit per person, or the model:

```sql
update public.settings set value = '60' where key = 'ai_daily_limit';
update public.settings set value = '"claude-sonnet-5-5"' where key = 'ai_model';
```

See AI use by person and day:

```sql
select i.note, u.email, a.day, a.n
from public.ai_usage a
join auth.users u on u.id = a.user_id
left join public.invites i on i.email = lower(u.email)
order by a.day desc, a.n desc;
```

## Round 3: big vocabulary tracks, examples, voices and speaking

**Content (all written, then checked by an independent reviewer; reviewer patches live in `rev/` next to `out/`).**
- Clinic Spanish: `src/spanish/content/vocab2/src/{out,rev}` → `gen_vocab2.py` → `src/spanish/data/vocab2.json` → build writes `spanish/vocab2.<hash>.json`. Everyday track VE01–VE30 (~2,900 most useful words, frequency order), extra clinic words per medical level (VMB1–8, after each VM set), and 2 more examples for every older word (`more`, keyed `<level>:<index>`).
- Cantonese / Korean: `src/<course>/content/vocab2/{out,rev}` (`ev-N.json` = Everyday set N+1, `extra-N.json` = 3 more examples for the older words) → `python3 src/lang/build.py all` writes `<course>/vocab2.<hash>.json` and adds every new sentence to `<course>/audio.json`.
- Word Power: every card has 4 examples (`src/vocab/data/items.json`); the page shows 2 and a "More examples" toggle.
- The apps build their questions from these entries in the browser (ids are based on entry ids, so editing content keeps progress).

**Voices and speech** (`shared/voice.js` + the `tts` function): natural server voices with a picker in each app's Settings, clips cached once per voice and sentence in the `audio` bucket, and speech-to-text for "Say it" and talk-out-loud conversations. Limits per person per day: 600 new clips (`tts_usage`), 400 recognitions (`stt_usage`, migration `supabase/migrations/20261023120000_stt_usage.sql`). Google Chirp 3 HD voices appear automatically if the secret `GOOGLE_TTS_KEY` is set. `tools/voice-test.html` lists the voices, plays samples and tests the microphone.

Record the new Cantonese/Korean clips in the default voices (admin token from `private.secrets`):
```sql
select net.http_post('https://wbrssohmepioxapwbcne.supabase.co/functions/v1/tts',
  jsonb_build_object('op','sync','course','cantonese','token',(select v from private.secrets where k='tts_admin')),
  headers => '{"Content-Type":"application/json"}'::jsonb);
-- progress: select * from public.tts_sync;
```

## Round 4: structured paths and the new look

- **Design system:** `shared/ui.css` + `shared/ui.js` (`window.SHUI`) used by every page: color schemes Automatic / Bold / Night / Soft (Settings → Color scheme, saved per device), one accent per app, tactile buttons, answer feedback motion, results screen, points and levels (level n→n+1 needs 500 + 250·(n−1) points), shared line icons (`SHUI.icon`). Reduced-motion settings are respected.
- **Learning structure** (spec: Learn · Practice · Settings tabs): a first-visit placement test, then one path of units and lessons with a single Continue button. Lessons (short ≈ 10 min, long ≈ 15 min) run Meet → Recognize → Recall → Grammar/Verbs → Sentences (build, shadow, Say it) → optional AI chat, with spaced reviews mixed in, and a unit check unlocks the next unit.
  - Spanish: two paths, Everyday and Clinic (built in `src/spanish/build.py`; grammar units shared). Verb drills use `src/spanish/data/conj.json` + `conj2.json` (every course verb; `content/pipeline/conj2.py`).
  - Cantonese: a Tones unit first, optional Characters practice. Korean: Hangul first, verb endings from `src/korean/content/conj/conj.json` (`build_conj.py`).
  - Word Power keeps its own structure, restyled, with points.
- Each app writes a small `stats` progress doc that the home page reads.
