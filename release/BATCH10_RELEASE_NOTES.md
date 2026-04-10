# Batch-10: Public Release & AppSumo Launch

## Release Date
November 2, 2025

## Version
v1.0.0-beta

## Overview
Public release package ready for AppSumo launch with onboarding wizard, support desk, tier gates, and all public-facing pages.

## Features Delivered

### Public Pages
- ✅ Terms of Service (`/public/terms`, `/terms`)
- ✅ Privacy Policy (`/public/privacy`, `/privacy`)
- ✅ Public Roadmap (`/public/roadmap`, `/roadmap`) - loads from `docs/beta/ROADMAP_PUBLIC.md`
- ✅ Changelog (`/public/changelog`) - loads from `docs/beta/CHANGELOG.md`
- ✅ FAQ (`/public/faq`)
- ✅ Pricing Page (`/public/pricing`) - displays tier information
- ✅ Support Desk (`/public/support`) - ticket submission form

### Onboarding Wizard
- ✅ 3-step flow (`/onboarding`)
  - Step 1: Connect YouTube channel or skip to demo
  - Step 2: Choose AI persona (Max, Lolo, Loki)
  - Step 3: Create first task from template
- ✅ Success screen with navigation to Pipeline and Research

### Support Desk
- ✅ Backend API: `POST /api/v1/support/ticket`
- ✅ Database: `support_tickets` table with RLS
- ✅ Frontend form with email, subject, message
- ✅ Ticket confirmation with ticket ID

### AppSumo Tier Enforcement
- ✅ Tier limits: Tier 1 (1 channel), Tier 2 (5 channels), Tier 3 (20 channels)
- ✅ Enforcement in OAuth callback (`auth_google.py`)
- ✅ Utility module: `tier_enforcement.py`
- ✅ Channel limit checks before saving new channels

### AppSumo Assets
- ✅ `listing_copy.md` - Product listing copy
- ✅ `roadmap_link.txt` - Public roadmap URL
- ✅ `privacy_link.txt` - Privacy policy URL
- ✅ `terms_link.txt` - Terms of service URL
- ✅ Extension zip: `viewz_outlier_extension_mv3.zip`

## Release Bundle
- ✅ `viewz_public_release_bundle.zip` (230KB)
  - Contains: docs, appsumo assets, frontend/dist, extension zip

## Database Migrations
- ✅ `007_support_tickets.sql` - Support tickets table

## API Endpoints

### New Endpoints
- `POST /api/v1/support/ticket` - Create support ticket

### Enhanced Endpoints
- `GET /api/v1/auth/callback` - Now includes tier limit checks

## Public Routes
All public routes are accessible without authentication:
- `/public/terms` or `/terms`
- `/public/privacy` or `/privacy`
- `/public/roadmap` or `/roadmap`
- `/public/changelog`
- `/public/faq`
- `/public/support`
- `/public/pricing`
- `/onboarding`

## Landing Page Updates
- ✅ "Get Started" button links to `/onboarding`
- ✅ "Try Demo" button links to `/demo`
- ✅ "See Pricing" button links to `/public/pricing`

## Deployment Checklist

### Pre-Deployment
- [ ] Verify all environment variables in `backend/.env.prod`
- [ ] Verify all environment variables in `frontend/.env.prod`
- [ ] Test OAuth flow end-to-end
- [ ] Test onboarding wizard flow
- [ ] Test support ticket submission
- [ ] Verify tier limits enforce correctly

### Deployment Steps
1. Deploy backend to production server
2. Deploy frontend to static hosting (Vercel/Netlify)
3. Configure domain: `viewz.getarainc.com` and `api.viewz.getarainc.com`
4. Update AppSumo links to production URLs
5. Upload screenshots to AppSumo listing

### Post-Deployment Verification
- [ ] All public pages load without auth
- [ ] Onboarding wizard completes successfully
- [ ] Support tickets create in database
- [ ] Tier limits enforce on channel connection
- [ ] Roadmap and Changelog load markdown correctly

## AppSumo Listing Checklist
- [x] Listing headline and description
- [x] Key features listed
- [x] Tier pricing table
- [x] Privacy Policy link (provided)
- [x] Terms of Service link (provided)
- [x] Roadmap link (provided)
- [x] Support desk available
- [x] Extension zip ready
- [ ] Screenshots (5-7 PNGs) - **TO DO**: Capture from production

## Files Created/Modified

### Backend (7 files)
- `backend/migrations/007_support_tickets.sql`
- `backend/app/api/support.py`
- `backend/app/schemas/support_schemas.py`
- `backend/app/utils/tier_enforcement.py`
- `backend/app/api/auth_google.py` (enhanced)
- `backend/app/main.py` (router added)

### Frontend (18 files)
- `frontend/src/pages/Public/Terms.jsx`
- `frontend/src/pages/Public/Privacy.jsx`
- `frontend/src/pages/Public/Roadmap.jsx` (enhanced)
- `frontend/src/pages/Public/Changelog.jsx`
- `frontend/src/pages/Public/FAQ.jsx`
- `frontend/src/pages/Public/Pricing.jsx`
- `frontend/src/pages/Public/Support.jsx`
- `frontend/src/pages/Onboarding/Wizard.jsx`
- `frontend/src/components/Onboarding/StepConnect.jsx`
- `frontend/src/components/Onboarding/StepPersona.jsx`
- `frontend/src/components/Onboarding/StepFirstTask.jsx`
- `frontend/src/pages/Public/Landing.jsx` (enhanced)
- `frontend/src/router/AppRouter.jsx` (routes added)

### Release Assets (4 files)
- `release/appsumo/listing_copy.md`
- `release/appsumo/roadmap_link.txt`
- `release/appsumo/privacy_link.txt`
- `release/appsumo/terms_link.txt`

## Known Issues
- Large bundle size warning (677KB) - consider code splitting for future optimization
- Screenshots not yet captured - need production screenshots for AppSumo

## Next Steps
1. Deploy to production
2. Capture screenshots from production
3. Complete AppSumo listing submission
4. Monitor support tickets
5. Gather user feedback

---

**Ready for Public Launch** 🚀

