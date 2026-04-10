-- Phase 3: AI editor instruction engine and version history

create table if not exists public.editor_instructions (
    id uuid primary key,
    script_line_id uuid not null references public.script_lines(id) on delete cascade,
    asset_id uuid not null references public.assets(id) on delete restrict,
    instruction_json jsonb not null default '{}'::jsonb,
    instruction_text text not null default '',
    clip_start double precision not null default 0,
    clip_duration double precision not null default 0,
    transition text not null default 'cut',
    motion text not null default 'none',
    text_overlay text not null default '',
    sound_design text not null default '',
    effects text not null default '',
    status text not null default 'GENERATED',
    created_at timestamp without time zone not null default now(),
    updated_at timestamp without time zone not null default now(),
    constraint editor_instructions_status_check
        check (status in ('DRAFT', 'GENERATED', 'APPROVED', 'OVERRIDDEN'))
);

create unique index if not exists idx_editor_instructions_script_line_id
    on public.editor_instructions(script_line_id);

create index if not exists idx_editor_instructions_asset_id
    on public.editor_instructions(asset_id);

create table if not exists public.instruction_versions (
    id uuid primary key,
    instruction_id uuid not null references public.editor_instructions(id) on delete cascade,
    version int not null,
    instruction_json jsonb not null default '{}'::jsonb,
    created_at timestamp without time zone not null default now(),
    constraint instruction_versions_unique_version unique (instruction_id, version)
);

create index if not exists idx_instruction_versions_instruction_id
    on public.instruction_versions(instruction_id, version desc);
