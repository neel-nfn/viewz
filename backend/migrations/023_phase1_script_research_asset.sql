-- Phase 1 backbone: script -> script_line -> research -> asset -> link

create table if not exists public.scripts (
    id uuid primary key,
    org_id uuid not null,
    title text not null,
    source_text text not null,
    status text not null default 'DRAFT',
    created_by uuid not null,
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    constraint scripts_status_check check (status in ('DRAFT', 'ACTIVE', 'ARCHIVED'))
);

create index if not exists idx_scripts_org_id on public.scripts(org_id);

create table if not exists public.assets (
    id uuid primary key,
    org_id uuid not null,
    source_url text not null,
    start_time double precision not null,
    end_time double precision not null,
    filename text not null,
    status text not null default 'ACTIVE',
    created_at timestamp without time zone not null default now(),
    constraint assets_status_check check (status in ('ACTIVE', 'ARCHIVED'))
);

create index if not exists idx_assets_org_id on public.assets(org_id);

create table if not exists public.script_lines (
    id uuid primary key,
    script_id uuid not null references public.scripts(id) on delete cascade,
    line_number integer not null,
    raw_text text not null,
    status text not null default 'NEED_RESEARCH',
    matched_asset_id uuid null references public.assets(id) on delete set null,
    research_request_id uuid null,
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    constraint script_lines_status_check check (status in ('NEED_RESEARCH', 'LINKED')),
    constraint script_lines_script_line_unique unique (script_id, line_number)
);

create index if not exists idx_script_lines_script_id on public.script_lines(script_id);
create index if not exists idx_script_lines_request_id on public.script_lines(research_request_id);

create table if not exists public.research_requests (
    id uuid primary key,
    script_line_id uuid not null references public.script_lines(id) on delete cascade,
    org_id uuid not null,
    keyword text not null,
    status text not null default 'OPEN',
    assigned_to uuid null,
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    constraint research_requests_status_check check (status in ('OPEN', 'SUBMITTED', 'APPROVED', 'REJECTED', 'LINKED'))
);

create index if not exists idx_research_requests_org_id on public.research_requests(org_id);
create index if not exists idx_research_requests_script_line_id on public.research_requests(script_line_id);

alter table public.script_lines
    add constraint script_lines_research_request_fk
    foreign key (research_request_id)
    references public.research_requests(id)
    on delete set null;

create table if not exists public.research_submissions (
    id uuid primary key,
    research_request_id uuid not null references public.research_requests(id) on delete cascade,
    source_url text not null,
    start_time double precision not null,
    end_time double precision not null,
    relevance_type text not null,
    notes text not null default '',
    status text not null default 'SUBMITTED',
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    constraint research_submissions_status_check check (status in ('SUBMITTED', 'APPROVED', 'REJECTED')),
    constraint research_submissions_relevance_check check (relevance_type in ('DIRECT_MATCH', 'RELATED_MATCH'))
);

create index if not exists idx_research_submissions_request_id on public.research_submissions(research_request_id);

create table if not exists public.line_asset_links (
    id uuid primary key,
    script_line_id uuid not null references public.script_lines(id) on delete cascade,
    asset_id uuid not null references public.assets(id) on delete cascade,
    selected_start double precision not null,
    duration double precision not null,
    created_at timestamp without time zone not null default now(),
    constraint line_asset_links_line_unique unique (script_line_id)
);

create index if not exists idx_line_asset_links_asset_id on public.line_asset_links(asset_id);
