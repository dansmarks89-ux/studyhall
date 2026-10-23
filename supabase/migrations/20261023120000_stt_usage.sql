-- Speech-to-text use per person per day (the "stt" op of the tts function), same shape as tts_usage.
-- Only the function (service role) reads or writes it: RLS on, no policies.
create table if not exists public.stt_usage (
  user_id uuid not null references auth.users (id) on delete cascade,
  day date not null,
  n int not null default 0,
  primary key (user_id, day)
);
alter table public.stt_usage enable row level security;

-- Counts one use for today (Chicago time) and returns today's count, or null once the limit is reached.
create or replace function public.stt_consume(uid uuid, lim int)
returns int
language plpgsql
security definer
set search_path = ''
as $$
declare
  d date := (now() at time zone 'America/Chicago')::date;
  used int;
begin
  if lim < 1 then return null; end if;
  insert into public.stt_usage as s (user_id, day, n) values (uid, d, 1)
  on conflict (user_id, day) do update set n = s.n + 1 where s.n < lim
  returning s.n into used;
  return used;
end;
$$;

revoke all on function public.stt_consume(uuid, int) from public, anon, authenticated;
grant execute on function public.stt_consume(uuid, int) to service_role;
