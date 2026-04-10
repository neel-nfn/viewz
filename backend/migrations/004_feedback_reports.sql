create type feedback_status as enum ('open','resolved');

create table if not exists feedback_reports(
  id uuid primary key,
  org_id uuid not null,
  user_id uuid,
  channel_id uuid,
  category text not null,
  severity text not null,
  message text not null,
  metadata jsonb,
  status feedback_status not null default 'open',
  created_at timestamptz not null default now()
);

create index if not exists idx_feedback_org on feedback_reports(org_id, status);

