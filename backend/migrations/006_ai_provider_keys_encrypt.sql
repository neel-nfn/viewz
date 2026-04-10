-- BYOK Encryption Patch: Add AES-GCM encrypted columns for AI keys

alter table if exists ai_provider_keys
  add column if not exists enc_key_base64 text,
  add column if not exists iv_base64 text,
  add column if not exists tag_base64 text,
  add column if not exists key_hint text;

-- Optional: keep api_key_hash for legacy detection; mark as deprecated
-- alter table ai_provider_keys drop column api_key_hash; -- (only if you're ready)

create index if not exists idx_ai_keys_org_provider on ai_provider_keys(org_id, provider);

-- If a row has only api_key_hash, mark it as requiring re-entry
update ai_provider_keys
set key_hint = coalesce(key_hint, 'LEGACY_HASH')
where api_key_hash is not null and enc_key_base64 is null;

