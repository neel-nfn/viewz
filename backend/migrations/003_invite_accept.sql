-- 003_invite_accept.sql

alter table invitations
  add column if not exists expires_at timestamp with time zone default (now() + interval '72 hours'),
  add column if not exists consumed_at timestamp with time zone,
  add column if not exists consumed_by uuid;


create index if not exists invitations_token_idx on invitations(token);
create unique index if not exists invitations_token_unique_pending on invitations(token) where status = 'pending';

-- optional safety: prevent accepting expired/consumed via a check on update path is enforced in app logic


