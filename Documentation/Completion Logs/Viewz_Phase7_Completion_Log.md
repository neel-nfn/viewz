# AppSumo Listing — Draft

## Title

Viewz — YouTube Studio OS for faceless channels

## Subtitle

Plan, write, design, edit, schedule, and analyze — from one fast board.

## Who it's for

Solo creators, agency pods, media ops teams running 1–20+ channels.

## Key Benefits

- One board for the entire pipeline

- Role-aware moves (writer/editor/manager)

- Analytics sidebar + AI assist for titles/summary

- Works offline; connect your data later

## Features

- Kanban pipeline (7 stages) with drag/drop and next/back

- Task drawer: comments + activity timeline

- Analytics sidebar: per-stage counts, overdue, last-24h activity

- Multi-user personas + invites (demo)

- AI assist (demo): suggest titles, summarize notes

- PWA, dark mode, SPA 404 fallback

## Plans (example)

- Starter — 1 channel

- Growth — 5 channels

- Studio — 20 channels

## FAQs

- Does it work without YouTube API? Yes, demo data works offline.

- Can I import my clients? Soon via Basix REST provider.

- Is there AI writing? Title/summarize demo now; full AI layer later.

# Beta QA Checklist

- / loads, PWA install works, theme persists

- /demo board: drag/drop, next/back, role gating blocks backward for writer/editor

- Drawer: comments add, activity updates after moves

- Analytics: A toggles; stats refresh on move

- AI: G opens; suggest title; apply updates card

- Feedback form stores locally; bug inbox lists reports

# Changelog — Local Beta

- Added ProviderFactory (demo/basix)

- Implemented Kanban + Drawer + Analytics + Filters

- Multi-user personas + role gating + demo invites

- AI Drawer (title/summarize) with optimistic updates

- Public pages (Landing/Terms/Privacy/Roadmap/Feedback)

- Bug Inbox, Theme system, PWA shell + SW, SEO meta, 404 fallback

- Lazy-loaded Analytics/AI drawers

# Viewz — YouTube Studio OS (Local Beta)

## Core

- Kanban Pipeline (research → writing → design → editing → scheduled → published → archived)

- Drag & Drop + Next/Back actions with role gating

- Task Drawer: Comments + Activity timeline

- Analytics Sidebar: per-stage counts, overdue, last 24h moves/comments

- Filters: All / Overdue / Assigned to Me

- Multi-user personas: Admin, Manager, Writer, Editor (demo) + Invite modal (local queue)

- AI Assist (demo): Suggest Title, Summarize, Apply Title

- ProviderFactory: demo provider now; basix provider stub ready

## Product Shell

- Public pages: Landing, Terms, Privacy, Roadmap, Feedback

- Bug Inbox (/debug/bugs)

- Theme switch: system/light/dark (persisted)

- PWA shell (installable), SEO meta, 404 fallback, lazy-loaded drawers

## What's Next

- Hook basix REST, channel templates, publish checklist, MCP (later)

# Privacy (Draft)

- Demo mode: no personal data sent to servers; stored in browser storage.

- Connected mode (future): data processed under your org's Basix policies.

- No sale of personal data.

# Viewz — Local Beta Usage

## Start

npm install

npm run dev

Open http://localhost:5173

## Demo controls

A: Analytics · G: AI · C: Comments · [: Back · ]: Next · U: Cycle user · Esc: Close

## Switch data source

# demo (default): .env.local VITE_DATA_SOURCE=demo

# basix (later):  VITE_DATA_SOURCE=basix and set VITE_BASIX_API_URL

# Public Roadmap

## Now

- Basix REST provider hookup

- Channel templates (briefs/checklists)

- Quick publish checklist

## Next

- Simple analytics charts, workload heatmap

- AppSumo onboarding flow + license gate (stub)

## Later

- MCP provider (Basix as MCP server)

- AB test titles/thumbnails

- Team capacity planning

# SLA (Draft)

- Uptime target (beta): best effort

- Data: Demo mode stores locally. When connected to Basix, org data stays under your tenancy.

- Support: Email within 1–2 business days during beta.

# Terms (Draft)

- Beta software; features may change.

- Customer responsible for content uploaded.

- Trademarks belong to their respective owners.

