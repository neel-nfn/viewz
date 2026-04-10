# Batch-10 Deployment Checklist

## Pre-Deployment

- [x] Code merged to `main`
- [x] Tag `v1.0.0-beta` created and pushed
- [x] Frontend build successful (677KB bundle)
- [x] Release artifacts created
- [x] Completion log generated

## Deployment Steps

### Backend
1. [ ] SSH to production server
2. [ ] `cd /path/to/viewz/backend`
3. [ ] `export $(grep -v "^#" .env.prod | xargs)`
4. [ ] `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Or use Dokploy UI to configure service
5. [ ] Verify health endpoint: `curl https://api.viewz.getarainc.com/health`

### Frontend
1. [ ] Deploy `frontend/dist/` to static hosting
   - Vercel: `vercel --prod`
   - Netlify: `netlify deploy --prod`
   - Dokploy: Upload `frontend/dist/` to static service
2. [ ] Configure environment variables (`.env.prod`)
3. [ ] Verify deployment: `curl -sI https://viewz.getarainc.com/`

## Post-Deployment Smoke Tests

```bash
# Backend Health
curl -sI https://api.viewz.getarainc.com/health

# Support API Test
curl -s -X POST https://api.viewz.getarainc.com/api/v1/support/ticket \
  -H "Content-Type: application/json" \
  -d '{"email":"qa@example.com","subject":"Smoke Test","body":"Testing support API"}'

# Frontend Public Pages
curl -sI https://viewz.getarainc.com/public/terms
curl -sI https://viewz.getarainc.com/public/privacy
curl -sI https://viewz.getarainc.com/public/roadmap
curl -sI https://viewz.getarainc.com/public/changelog
curl -sI https://viewz.getarainc.com/public/faq
curl -sI https://viewz.getarainc.com/public/support
curl -sI https://viewz.getarainc.com/public/pricing
```

## E2E Tests

1. [ ] Onboarding wizard flow
   - Visit: `https://viewz.getarainc.com/onboarding`
   - Complete: Connect/Demo → Persona → First Task
   - Verify: Redirects to pipeline

2. [ ] Support ticket submission
   - Visit: `https://viewz.getarainc.com/public/support`
   - Submit ticket
   - Verify: Receives ticket ID

3. [ ] Tier enforcement
   - Connect channel via OAuth
   - Verify: Limit enforced correctly

## AppSumo Preparation

- [ ] Capture 5-7 production screenshots:
  - Landing page
  - Onboarding wizard
  - Pipeline board
  - Research page
  - AI SEO Assistant
  - Dashboard
  - Settings
- [ ] Save screenshots to `release/appsumo/screenshots/`
- [ ] Verify all public URLs are live
- [ ] Submit AppSumo listing

