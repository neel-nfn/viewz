-- Analytics v2: add velocity & variance fields
alter table if exists analytics_snapshots
    add column if not exists views_7d integer default 0,
    add column if not exists views_28d integer default 0,
    add column if not exists ctr_7d numeric(6,3) default 0,
    add column if not exists ctr_28d numeric(6,3) default 0,
    add column if not exists views_velocity_7d numeric(8,4) default 0,          -- (views - views_7d)/nullif(views_7d,0)
    add column if not exists views_velocity_28d numeric(8,4) default 0,
    add column if not exists ctr_delta_7d numeric(8,4) default 0,               -- ctr - ctr_7d
    add column if not exists ctr_delta_28d numeric(8,4) default 0,
    add column if not exists variance_7d numeric(12,6) default 0;               -- rolling var for basic outlier calc

create index if not exists idx_analytics_snapshots_channel_date
    on analytics_snapshots(channel_id, date);

-- Research ideas captured from extension/UI
create table if not exists research_ideas (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null,
    channel_id uuid not null,
    source text not null,                              -- 'youtube', 'manual', 'extension'
    title text not null,
    url text,
    metadata jsonb default '{}'::jsonb,
    created_by uuid not null,
    created_at timestamptz default now()
);

-- Scores produced by /research/score
create table if not exists research_scores (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null,
    channel_id uuid not null,
    idea_id uuid references research_ideas(id) on delete cascade,
    score numeric(6,2) not null,
    components jsonb not null,                         -- breakdown {ctr_z, views_vel, freshness, ...}
    created_by uuid not null,
    created_at timestamptz default now()
);

create index if not exists idx_research_ideas_org_channel on research_ideas(org_id, channel_id, created_at desc);
create index if not exists idx_research_scores_org_channel on research_scores(org_id, channel_id, created_at desc);

-- Minimal RLS scaffolding (assumes org_id scoping helpers already exist)
alter table research_ideas enable row level security;
alter table research_scores enable row level security;

do $$
begin
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'research_ideas' and policyname = 'org_read_ideas') then
        create policy org_read_ideas on research_ideas for select using (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'research_ideas' and policyname = 'org_write_ideas') then
        create policy org_write_ideas on research_ideas for insert with check (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'research_scores' and policyname = 'org_read_scores') then
        create policy org_read_scores on research_scores for select using (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'research_scores' and policyname = 'org_write_scores') then
        create policy org_write_scores on research_scores for insert with check (true);
    end if;
end$$;

