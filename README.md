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
| `vocab/index.html` | Word Power (built file, do not edit by hand) |
| `src/vocab/` | Word Power source: `app.html`, `data/items.json` (2,428 reviewed items), and `content/` (spec, reviewer instructions, review patches, pipeline scripts) |
| `supabase/functions/ai/index.ts` | The AI function (source copy of what is deployed) |
| `sw.js`, `manifest.webmanifest`, `icons/` | Home-screen app support |

Rebuild the Spanish page after changing `src/spanish/app.html` or its data:

```
python3 src/spanish/build.py hosted
```

Rebuild Word Power after changing `src/vocab/app.html` or `src/vocab/data/items.json`:

```
python3 src/vocab/build.py
```

## Adding an app

1. Put the app in its own folder, e.g. `korean/index.html`.
2. In its `<head>` load `../shared/supabase.js`, then `../shared/sh.js`, then `<script>SH.install("korean");</script>`.
3. The app then uses `window.claude.use("user" | "db" | "sample")` exactly like a claude.ai artifact, with progress stored per person under the course name.
4. Add it to the `APPS` list in `index.html`.

## Running it (SQL editor in Supabase)

Invite someone (course names: `spanish`, `vocab`, later `cantonese`, `korean`; `*` = everything):

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
