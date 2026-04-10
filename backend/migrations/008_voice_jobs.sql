BEGIN;

CREATE TABLE IF NOT EXISTS voice_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL,
  channel_id UUID NOT NULL,
  task_id UUID,
  voice_provider TEXT NOT NULL DEFAULT 'elevenlabs',
  voice_id TEXT,
  input_text TEXT,
  output_url TEXT,
  status TEXT NOT NULL DEFAULT 'queued',
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_voice_jobs_task ON voice_jobs(task_id);
CREATE INDEX IF NOT EXISTS idx_voice_jobs_org ON voice_jobs(org_id, channel_id, created_at);

COMMIT;

