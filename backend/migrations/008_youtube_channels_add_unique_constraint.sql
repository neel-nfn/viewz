-- Migration 008: Add Unique Constraint to youtube_channels
-- Purpose: Ensure ON CONFLICT in auth_google callback works properly

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'youtube_channels_google_channel_id_key'
  ) THEN
    ALTER TABLE youtube_channels
      ADD CONSTRAINT youtube_channels_google_channel_id_key
      UNIQUE (google_channel_id);
    COMMENT ON CONSTRAINT youtube_channels_google_channel_id_key ON youtube_channels
      IS 'Ensures one record per Google channel ID for conflict-safe upserts.';
  END IF;
END$$;


