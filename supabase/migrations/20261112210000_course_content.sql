-- Lessons kept out of this public repository. Each row's body is a unit file (JavaScript) that the course page
-- reads after sign-in and runs to add its lessons. Only the service role (SQL editor, migrations) can write rows,
-- so the bodies are as trusted as the site's own code.
create table public.course_content (
  course text not null check (course ~ '^[a-z0-9-]{1,40}$'),
  doc text not null check (doc ~ '^[A-Za-z0-9_.:-]{1,60}$'),
  body text not null,
  updated_at timestamptz not null default now(),
  primary key (course, doc)
);

create trigger course_content_touch before update on public.course_content
  for each row execute function public.touch_updated_at();

-- True when the signed-in person's invite names course c itself. Unlike private.has_course, an invite to
-- every course ('*') does not count, so a course can be kept to the people invited to it by name.
create function private.has_course_by_name(c text) returns boolean
  language sql stable security definer set search_path = ''
as $$
  select exists (
    select 1 from public.invites i
    where i.email = lower((select auth.jwt()) ->> 'email') and c = any (i.courses)
  );
$$;
revoke all on function private.has_course_by_name(text) from public, anon;
grant execute on function private.has_course_by_name(text) to authenticated;

alter table public.course_content enable row level security;
revoke all on table public.course_content from anon;
-- Read only. No insert, update or delete policy: nobody signed in through the site can change lessons.
create policy "course_content: read when invited by name" on public.course_content
  for select to authenticated using (private.has_course_by_name(course));
