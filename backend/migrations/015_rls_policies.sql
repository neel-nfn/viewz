alter table organizations enable row level security;
alter table organization_users enable row level security;
alter table billing_plans enable row level security;
alter table invoices enable row level security;
alter table marketplace_assets enable row level security;
alter table ab_tests enable row level security;

create policy org_select on organizations for select using (
  exists(select 1 from organization_users ou where ou.org_id = organizations.id and ou.user_id = auth.uid() and ou.status='active')
);

create policy org_users_select on organization_users for select using (
  organization_users.user_id = auth.uid()
  or exists(select 1 from organization_users ou where ou.org_id = organization_users.org_id and ou.user_id = auth.uid() and ou.status='active')
);

create policy billing_select on billing_plans for select using (
  exists(select 1 from organization_users ou where ou.org_id = billing_plans.org_id and ou.user_id = auth.uid() and ou.status='active')
);

create policy invoices_select on invoices for select using (
  exists(select 1 from organization_users ou where ou.org_id = invoices.org_id and ou.user_id = auth.uid() and ou.status='active')
);

create policy marketplace_public on marketplace_assets for select using (
  marketplace_assets.is_public = true
  or exists(select 1 from organization_users ou where ou.org_id = marketplace_assets.org_id and ou.user_id = auth.uid() and ou.status='active')
);

create policy abtests_select on ab_tests for select using (
  exists(select 1 from organization_users ou where ou.org_id = ab_tests.org_id and ou.user_id = auth.uid() and ou.status='active')
);

