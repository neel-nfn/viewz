create extension if not exists pgcrypto;

create table if not exists youtube_channels(
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null,
  google_channel_id text not null,
  title text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(org_id, google_channel_id)
);

create index if not exists idx_yc_org on youtube_channels(org_id);

create table if not exists youtube_tokens(
  channel_id uuid primary key references youtube_channels(id) on delete cascade,
  refresh_token text not null,
  scopes text[] default '{}',
  updated_at timestamptz not null default now()
);

