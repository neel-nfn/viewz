create table if not exists marketplace_assets (
  id uuid primary key default gen_random_uuid(),
  uploader_user_id uuid not null,
  org_id uuid references organizations(id) on delete set null,
  type text not null check (type in ('template','persona','workflow')),
  title text not null,
  metadata jsonb not null default '{}'::jsonb,
  price_cents integer not null default 0,
  rating numeric(2,1),
  is_public boolean not null default false,
  created_at timestamp with time zone default now()
);

create index if not exists idx_marketplace_type on marketplace_assets(type);
create index if not exists idx_marketplace_public on marketplace_assets(is_public);

