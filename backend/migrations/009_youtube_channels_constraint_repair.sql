-- Migration 009: ensure youtube_channels has updated_at + unique key

create extension if not exists pgcrypto;

alter table if exists youtube_channels
  add column if not exists updated_at timestamptz default now();

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'youtube_channels_google_channel_id_key'
  ) THEN
    ALTER TABLE youtube_channels
      ADD CONSTRAINT youtube_channels_google_channel_id_key
      UNIQUE (google_channel_id);
  END IF;
END$$;


