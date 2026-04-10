-- Migration 012: Create youtube_tokens table

create extension if not exists pgcrypto;

create table if not exists public.youtube_tokens (
    id uuid primary key default gen_random_uuid(),
    channel_id uuid not null references youtube_channels(id) on delete cascade,
    refresh_token text not null,
    scopes text default '',
    updated_at timestamptz default now()
);

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'youtube_tokens_channel_id_key'
  ) THEN
    ALTER TABLE public.youtube_tokens
      ADD CONSTRAINT youtube_tokens_channel_id_key
      UNIQUE (channel_id);
  END IF;
END$$;

create index if not exists youtube_tokens_channel_id_idx
    on public.youtube_tokens (channel_id);


