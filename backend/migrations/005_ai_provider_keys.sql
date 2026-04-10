-- ai_provider_keys table for Batch-12 Integrations

create table if not exists ai_provider_keys (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null,
  provider text not null default 'gemini',
  api_key_hash text not null,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),
  unique(org_id, provider)
);

create index if not exists idx_ai_key_org on ai_provider_keys(org_id);

-- RLS (org-scoped read/write)
alter table ai_provider_keys enable row level security;

do $$ begin
  create policy ai_key_read on ai_provider_keys
    for select using (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy ai_key_write on ai_provider_keys
    for insert with check (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy ai_key_update on ai_provider_keys
    for update using (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

do $$ begin
  create policy ai_key_delete on ai_provider_keys
    for delete using (org_id = current_setting('request.org_id', true)::uuid);
exception when duplicate_object then null; end $$;

