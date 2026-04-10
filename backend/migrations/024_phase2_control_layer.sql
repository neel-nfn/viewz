-- Phase 2: approval, validation, state enforcement, reuse suggestions

alter table public.research_requests
    drop constraint if exists research_requests_status_check;

alter table public.research_requests
    add constraint research_requests_status_check
    check (status in ('PENDING', 'IN_PROGRESS', 'SUBMITTED', 'APPROVED', 'REJECTED'));

alter table public.research_requests
    alter column status set default 'PENDING';

alter table public.research_submissions
    drop constraint if exists research_submissions_status_check;

alter table public.research_submissions
    add constraint research_submissions_status_check
    check (status in ('PENDING_REVIEW', 'APPROVED', 'REJECTED'));

alter table public.research_submissions
    alter column status set default 'PENDING_REVIEW';

alter table public.assets
    drop constraint if exists assets_status_check;

alter table public.assets
    add constraint assets_status_check
    check (status in ('PENDING_VALIDATION', 'READY', 'REJECTED'));

alter table public.assets
    alter column status set default 'PENDING_VALIDATION';

alter table public.assets
    add column if not exists research_submission_id uuid null references public.research_submissions(id) on delete set null;

alter table public.script_lines
    drop constraint if exists script_lines_status_check;

alter table public.script_lines
    add constraint script_lines_status_check
    check (status in ('NEEDS_RESEARCH', 'RESEARCH_IN_PROGRESS', 'READY_FOR_LINK', 'LINKED'));

alter table public.script_lines
    alter column status set default 'NEEDS_RESEARCH';

alter table public.script_lines
    add column if not exists suggested_asset_id uuid null references public.assets(id) on delete set null;

alter table public.script_lines
    add column if not exists suggested_match_confidence double precision null;

alter table public.script_lines
    add column if not exists suggestion_notes text null;

create table if not exists public.asset_validation_logs (
    id uuid primary key,
    asset_id uuid not null references public.assets(id) on delete cascade,
    validation_type text not null,
    result text not null,
    notes text not null default '',
    validated_by uuid null,
    created_at timestamp without time zone not null default now()
);

create index if not exists idx_asset_validation_logs_asset_id on public.asset_validation_logs(asset_id);

create table if not exists public.workflow_events (
    id uuid primary key,
    entity_type text not null,
    entity_id uuid not null,
    action text not null,
    from_status text null,
    to_status text null,
    payload_jsonb jsonb not null default '{}'::jsonb,
    actor_id uuid null,
    created_at timestamp without time zone not null default now()
);

create index if not exists idx_workflow_events_entity on public.workflow_events(entity_type, entity_id);
