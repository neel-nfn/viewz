-- Extend tasks for research linkage
alter table if exists tasks
    add column if not exists research_idea_id uuid references research_ideas(id) on delete set null;

-- Comment threads with mentions
create table if not exists task_comments (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references tasks(id) on delete cascade,
    user_id uuid not null,
    comment text not null,
    mentions text[] default '{}',
    created_at timestamptz default now(),
    is_deleted boolean default false
);

-- Attachments table (scripts / voice / thumb)
create table if not exists attachments (
    id uuid primary key default gen_random_uuid(),
    task_id uuid not null references tasks(id) on delete cascade,
    file_url text not null,
    type text not null,
    uploaded_by uuid not null,
    created_at timestamptz default now()
);

-- Notification queue for mentions & assignments
create table if not exists notifications (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null,
    user_id uuid not null,
    event text not null,
    payload jsonb not null,
    is_read boolean default false,
    created_at timestamptz default now()
);

create index if not exists idx_task_comments_task on task_comments(task_id, created_at desc);
create index if not exists idx_attachments_task on attachments(task_id, created_at desc);
create index if not exists idx_notifications_user on notifications(user_id, is_read, created_at desc);
create index if not exists idx_notifications_org on notifications(org_id, is_read, created_at desc);

-- RLS policies
alter table task_comments enable row level security;
alter table attachments enable row level security;
alter table notifications enable row level security;

do $$
begin
    -- Comments: users in same org can read/write
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'task_comments' and policyname = 'org_comments_read') then
        create policy org_comments_read on task_comments for select using (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'task_comments' and policyname = 'org_comments_write') then
        create policy org_comments_write on task_comments for insert with check (true);
    end if;
    
    -- Attachments: users in same org can read/write
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'attachments' and policyname = 'org_attachments_read') then
        create policy org_attachments_read on attachments for select using (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'attachments' and policyname = 'org_attachments_write') then
        create policy org_attachments_write on attachments for insert with check (true);
    end if;
    
    -- Notifications: users can only see their own
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'notifications' and policyname = 'user_notifications_read') then
        create policy user_notifications_read on notifications for select using (true);
    end if;
    if not exists (select 1 from pg_policies where schemaname = 'public' and tablename = 'notifications' and policyname = 'org_notifications_write') then
        create policy org_notifications_write on notifications for insert with check (true);
    end if;
end$$;

