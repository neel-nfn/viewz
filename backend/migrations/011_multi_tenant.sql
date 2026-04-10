create table if not exists organizations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  logo_url text,
  owner_user_id uuid not null,
  plan_type text default 'free',
  plan_start timestamp with time zone,
  plan_end timestamp with time zone,
  usage_credits integer default 0,
  billing_provider text default 'stripe',
  created_at timestamp with time zone default now()
);

create table if not exists organization_users (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  user_id uuid not null,
  role text not null check (role in ('admin','manager','writer','editor')),
  status text not null default 'active' check (status in ('active','invited','removed')),
  created_at timestamp with time zone default now(),
  unique(org_id, user_id)
);

alter table if exists users add column if not exists default_org_id uuid;
alter table if exists users add column if not exists is_active boolean default true;
alter table if exists channels add column if not exists org_id uuid;

update channels c set org_id = (select ou.org_id from organization_users ou where ou.user_id = c.owner_user_id limit 1) where org_id is null;

alter table channels alter column org_id set not null;

create index if not exists idx_org_users_org on organization_users(org_id);
create index if not exists idx_channels_org on channels(org_id);

