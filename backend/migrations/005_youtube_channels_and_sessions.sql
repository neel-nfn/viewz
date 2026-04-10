-- Create youtube_channels table if not exists
create table if not exists youtube_channels(
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null,
  google_channel_id text not null,
  youtube_channel_id text not null unique,
  title text,
  logo_url text,
  status text default 'connected',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_youtube_channels_org on youtube_channels(org_id);
create unique index if not exists idx_youtube_channels_org_channel on youtube_channels(org_id, youtube_channel_id);

-- Create user_sessions table if not exists
create table if not exists user_sessions(
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  session_token text not null unique,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '30 days')
);

create index if not exists idx_user_sessions_token on user_sessions(session_token);
create index if not exists idx_user_sessions_user on user_sessions(user_id);

