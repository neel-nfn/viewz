alter table if exists channels add column if not exists ai_credits_used integer default 0;
alter table if exists channels add column if not exists last_synced_at timestamp with time zone;
create index if not exists idx_channels_last_synced_at on channels(last_synced_at);

