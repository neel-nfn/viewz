-- Migration 011: ensure Local Dev Org exists for FK fallback

insert into organizations (id, name, created_at)
values ('00000000-0000-0000-0000-000000000000', 'Local Dev Org', now())
on conflict (id) do nothing;


