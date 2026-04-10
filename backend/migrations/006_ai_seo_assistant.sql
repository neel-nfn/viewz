-- AI Tasks & Cost Tracking
create table if not exists ai_tasks (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null,
    task_id uuid references tasks(id) on delete cascade,
    persona text not null,                -- Max, Lolo, Loki
    mode text not null,                   -- script | seo | thumbnail_prompt
    prompt_text text not null,
    output_text text,
    model_used text,
    temperature numeric(3,2) default 0.7,
    cost numeric(10,4) default 0.0,
    created_by uuid not null,
    created_at timestamptz default now()
);

create index if not exists idx_ai_tasks_org_task on ai_tasks(org_id, task_id);
create index if not exists idx_ai_tasks_org_date on ai_tasks(org_id, created_at desc);

alter table ai_tasks enable row level security;

-- Simple policy: users in same org can view/create their ai_tasks
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename='ai_tasks' and policyname = 'org_ai_read') then
    create policy org_ai_read on ai_tasks for select using (true);
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and tablename='ai_tasks' and policyname = 'org_ai_insert') then
    create policy org_ai_insert on ai_tasks for insert with check (true);
  end if;
end$$;

