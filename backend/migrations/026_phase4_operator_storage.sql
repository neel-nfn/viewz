-- Phase 4: operator queue, storage abstraction, filename enforcement, integrity tracking

alter table public.assets
    add column if not exists storage_provider text null,
    add column if not exists storage_path text null,
    add column if not exists public_url text null,
    add column if not exists checksum text null,
    add column if not exists byte_size bigint null,
    add column if not exists mime_type text null,
    add column if not exists storage_object_id uuid null;

create table if not exists public.operator_jobs (
    id uuid primary key,
    org_id uuid not null,
    job_type text not null,
    status text not null default 'QUEUED',
    requested_by uuid null,
    assigned_to uuid null,
    total_items integer not null default 0,
    processed_items integer not null default 0,
    failed_items integer not null default 0,
    storage_provider text not null default 'local_stub',
    input_payload_json jsonb not null default '{}'::jsonb,
    result_payload_json jsonb not null default '{}'::jsonb,
    error_message text not null default '',
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    completed_at timestamp without time zone null,
    constraint operator_jobs_status_check
        check (status in ('QUEUED', 'IN_PROGRESS', 'PARTIAL_SUCCESS', 'COMPLETED', 'FAILED', 'CANCELLED')),
    constraint operator_jobs_storage_provider_check
        check (storage_provider in ('local_stub', 'supabase'))
);

create index if not exists idx_operator_jobs_org_id on public.operator_jobs(org_id, created_at desc);

create table if not exists public.operator_job_items (
    id uuid primary key,
    operator_job_id uuid not null references public.operator_jobs(id) on delete cascade,
    research_submission_id uuid null references public.research_submissions(id) on delete set null,
    asset_id uuid null references public.assets(id) on delete set null,
    script_line_id uuid null references public.script_lines(id) on delete set null,
    status text not null default 'PENDING',
    source_url text not null default '',
    requested_start_time double precision null,
    requested_end_time double precision null,
    normalized_filename text not null default '',
    storage_provider text not null default 'local_stub',
    storage_path text not null default '',
    checksum text null,
    error_message text not null default '',
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    completed_at timestamp without time zone null,
    constraint operator_job_items_status_check
        check (status in ('PENDING', 'PROCESSING', 'STORED', 'FAILED', 'SKIPPED')),
    constraint operator_job_items_storage_provider_check
        check (storage_provider in ('local_stub', 'supabase'))
);

create unique index if not exists idx_operator_job_items_unique_submission
    on public.operator_job_items(operator_job_id, research_submission_id)
    where research_submission_id is not null;

create index if not exists idx_operator_job_items_job_id on public.operator_job_items(operator_job_id, created_at asc);

create table if not exists public.storage_objects (
    id uuid primary key,
    org_id uuid not null,
    asset_id uuid null references public.assets(id) on delete set null,
    provider text not null,
    bucket_or_drive_id text null,
    object_key text not null,
    public_url text null,
    mime_type text null,
    byte_size bigint null,
    checksum text null,
    metadata_json jsonb not null default '{}'::jsonb,
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    constraint storage_objects_provider_check
        check (provider in ('local_stub', 'supabase'))
);

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'assets_storage_object_id_fkey'
    ) then
        alter table public.assets
            add constraint assets_storage_object_id_fkey
            foreign key (storage_object_id) references public.storage_objects(id) on delete set null;
    end if;
end $$;

create unique index if not exists idx_storage_objects_provider_key
    on public.storage_objects(org_id, provider, object_key);

create index if not exists idx_storage_objects_org_id on public.storage_objects(org_id, created_at desc);

create table if not exists public.filename_rules (
    id uuid primary key,
    org_id uuid not null,
    rule_name text not null,
    pattern_template text not null,
    is_active boolean not null default false,
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now()
);

create unique index if not exists idx_filename_rules_one_active_per_org
    on public.filename_rules(org_id)
    where is_active;

create index if not exists idx_filename_rules_org_id on public.filename_rules(org_id, created_at desc);

create table if not exists public.asset_fingerprints (
    id uuid primary key,
    asset_id uuid not null references public.assets(id) on delete cascade,
    fingerprint_type text not null,
    fingerprint_value text not null,
    created_at timestamp without time zone not null default now(),
    constraint asset_fingerprints_type_check
        check (fingerprint_type in ('sha256', 'filename', 'source_url'))
);

create unique index if not exists idx_asset_fingerprints_unique
    on public.asset_fingerprints(asset_id, fingerprint_type, fingerprint_value);

create index if not exists idx_asset_fingerprints_asset_id
    on public.asset_fingerprints(asset_id, created_at desc);
