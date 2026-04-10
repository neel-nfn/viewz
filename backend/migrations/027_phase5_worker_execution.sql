-- Phase 5: background worker, retries, and job locking

alter table public.operator_jobs
    add column if not exists locked_by uuid null,
    add column if not exists locked_at timestamp without time zone null;

alter table public.operator_job_items
    add column if not exists retry_count integer not null default 0,
    add column if not exists max_retries integer not null default 3,
    add column if not exists last_retry_at timestamp without time zone null;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conname = 'operator_job_items_retry_count_check'
    ) then
        alter table public.operator_job_items
            add constraint operator_job_items_retry_count_check
            check (retry_count >= 0);
    end if;

    if not exists (
        select 1
        from pg_constraint
        where conname = 'operator_job_items_max_retries_check'
    ) then
        alter table public.operator_job_items
            add constraint operator_job_items_max_retries_check
            check (max_retries >= 0);
    end if;
end $$;

create index if not exists idx_operator_jobs_locking
    on public.operator_jobs(status, locked_at, created_at);

create index if not exists idx_operator_job_items_retry_state
    on public.operator_job_items(operator_job_id, status, retry_count, last_retry_at);
