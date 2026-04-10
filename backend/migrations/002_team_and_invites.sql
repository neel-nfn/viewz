-- 002_team_and_invites.sql

create table if not exists invitations (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  email text not null,
  role text not null check (role in ('admin','manager','writer','editor')),
  token text not null,
  status text not null default 'pending' check (status in ('pending','accepted','expired','revoked')),
  invited_by uuid not null references users(id),
  created_at timestamp with time zone default now(),
  accepted_at timestamp with time zone
);

create unique index if not exists invitations_org_email_unique
on invitations(org_id, email) where status = 'pending';

alter table organization_users
  add column if not exists status text not null default 'active' check (status in ('active','invited','removed'));

-- RLS (ensure enabled at project level)
alter table invitations enable row level security;

create policy "org members read their invitations"
on invitations for select
using (
  exists (
    select 1 from organization_users ou
    where ou.org_id = invitations.org_id
      and ou.user_id = auth.uid()
      and ou.status = 'active'
  )
);

create policy "only admins/managers create invites"
on invitations for insert
with check (
  exists (
    select 1
    from organization_users ou
    where ou.org_id = invitations.org_id
      and ou.user_id = auth.uid()
      and ou.role in ('admin','manager')
      and ou.status = 'active'
  )
);

create policy "admins revoke invites"
on invitations for update
using (
  exists (
    select 1 from organization_users ou
    where ou.org_id = invitations.org_id
      and ou.user_id = auth.uid()
      and ou.role in ('admin','manager')
  )
)
with check (true);
