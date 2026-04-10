-- feedback_reports (Batch-6 scope)

create table if not exists feedback_reports (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null,
  user_id uuid,
  channel_id uuid,
  url text,
  category text check (category in ('bug','idea','ui','performance','other')) default 'other',
  severity text check (severity in ('low','medium','high','critical')) default 'low',
  title text not null,
  description text,
  metadata jsonb default '{}'::jsonb,
  status text check (status in ('open','triaged','resolved','rejected')) default 'open',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists idx_feedback_org_created on feedback_reports(org_id, created_at desc);
create index if not exists idx_feedback_status on feedback_reports(status);

-- RLS (org-scoped read/write)
alter table feedback_reports enable row level security;

do $$ begin
  create policy feedback_org_read on feedback_reports
    for select using (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy feedback_org_write on feedback_reports
    for insert with check (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy feedback_org_update on feedback_reports
    for update using (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

