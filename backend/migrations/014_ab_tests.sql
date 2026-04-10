create table if not exists ab_tests (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  channel_id uuid not null references channels(id) on delete cascade,
  video_id text not null,
  variant_a jsonb not null,
  variant_b jsonb not null,
  ctr_a numeric(5,2),
  ctr_b numeric(5,2),
  watch_a integer,
  watch_b integer,
  winner text check (winner in ('a','b')),
  status text not null default 'running' check (status in ('running','stopped','completed')),
  created_at timestamp with time zone default now()
);

create index if not exists idx_abtests_org on ab_tests(org_id);
create index if not exists idx_abtests_channel on ab_tests(channel_id);

