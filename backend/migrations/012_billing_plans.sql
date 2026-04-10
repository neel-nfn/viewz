create table if not exists billing_plans (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  tier text not null,
  ai_credit_limit integer not null default 0,
  price_cents integer not null default 0,
  active boolean not null default true,
  created_at timestamp with time zone default now()
);

create table if not exists invoices (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  external_id text,
  amount_cents integer not null,
  status text not null default 'pending',
  created_at timestamp with time zone default now()
);

create index if not exists idx_billing_plans_org on billing_plans(org_id);
create index if not exists idx_invoices_org on invoices(org_id);

