-- Support Tickets table
create table if not exists support_tickets (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null,
    email text not null,
    subject text not null,
    body text not null,
    status text not null default 'open',
    created_at timestamptz default now()
);

create index if not exists idx_support_tickets_org on support_tickets(org_id, created_at desc);
create index if not exists idx_support_tickets_status on support_tickets(status, created_at desc);

alter table support_tickets enable row level security;

do $$
begin
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'support_tickets' and policyname = 'org_support_read') then
        create policy org_support_read on support_tickets for select using (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'support_tickets' and policyname = 'org_support_insert') then
        create policy org_support_insert on support_tickets for insert with check (true);
    end if;
end$$;

