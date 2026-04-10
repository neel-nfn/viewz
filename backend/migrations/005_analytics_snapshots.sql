BEGIN;

CREATE TABLE IF NOT EXISTS analytics_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id UUID NOT NULL,
  date DATE NOT NULL,
  views BIGINT DEFAULT 0,
  watch_time BIGINT DEFAULT 0,
  ctr NUMERIC(5,2),
  impressions BIGINT DEFAULT 0,
  subs BIGINT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_snapshots_channel_date ON analytics_snapshots(channel_id, date);

CREATE TABLE IF NOT EXISTS video_stats (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  channel_id UUID NOT NULL,
  video_id TEXT NOT NULL,
  title TEXT NOT NULL,
  views BIGINT DEFAULT 0,
  watch_time BIGINT DEFAULT 0,
  ctr NUMERIC(5,2),
  last_updated TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_video_stats_channel ON video_stats(channel_id);

COMMIT;

