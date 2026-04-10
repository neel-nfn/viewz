# Hard Stop Rules - UI Consistency

**Purpose:** Prevent visual debt from creeping back in. These rules are non-negotiable.

## Color Rules

✅ **DO:**
- Use tokens from `src/theme/tokens.js` only
- Reference via Tailwind classes: `text-primary`, `bg-surface`, `border-border`

❌ **DON'T:**
- Use hex colors directly: `text-[#0ea5b7]`
- Use arbitrary colors: `bg-blue-500` (unless it's from design system)
- Create custom color variables in components

## Shadow & Radius Rules

✅ **DO:**
- Use token shadows: `shadow-card`, `shadow-hover`
- Use token radius: `rounded-xl` (maps to 16px), `rounded-2xl` (maps to 24px)

❌ **DON'T:**
- Use arbitrary values: `shadow-[0 2px 4px rgba(0,0,0,0.1)]`
- Use custom border radius: `rounded-[8px]`

## Typography Rules

✅ **DO:**
- Use semantic classes: `text-h1`, `text-h2`, `text-body`
- Reference tokens for consistency

❌ **DON'T:**
- Use arbitrary font sizes: `text-[48px]`
- Mix font families (stick to Inter)

## Component Rules

✅ **DO:**
- Use primitive components: `<Button>`, `<Card>`, `<PageHeader>`
- Wrap content in Cards, not raw divs
- Use PageHeader on every page

❌ **DON'T:**
- Create raw `<button>` elements
- Use raw divs for content containers
- Skip PageHeader on new pages

## Layout Rules

✅ **DO:**
- Max width: `1240px` (use token: `max-w-[1240px]`)
- Padding: `px-6 md:px-8` (tokens: `pagePadding`)
- Section gaps: `space-y-6` or `gap-6`

❌ **DON'T:**
- Full-width content without max-width constraint
- Inconsistent padding (use tokens)
- Random spacing values

## Page Structure Rules

Every page MUST have:

1. **Container with max-width:**
   ```jsx
   <div style={{ maxWidth: tokens.spacing.pageMaxWidth, margin: '0 auto', padding: tokens.spacing.pagePadding.base }}>
   ```

2. **PageHeader:**
   ```jsx
   <PageHeader title="Page Title" subtitle="Description" primaryAction={...} />
   ```

3. **Cards for content:**
   ```jsx
   <Card title="Section" subtitle="Info">
     {content}
   </Card>
   ```

4. **Empty states:**
   ```jsx
   <EmptyState icon={Icon} title="Title" description="Help text" />
   ```

## Pre-Merge Checklist

Before merging any UI changes:

- [ ] No custom colors (use tokens only)
- [ ] No ad-hoc shadows or radii
- [ ] All text uses typographic scale
- [ ] All buttons use `<Button>` component
- [ ] All content wrapped in `<Card>`
- [ ] Page has `<PageHeader>`
- [ ] Max-width container applied
- [ ] Mobile responsive (test at 375px width)
- [ ] No horizontal scroll on mobile

## Enforcement

- Code review must check these rules
- Linter should flag custom colors/shadows (if configured)
- CI can check for hard-coded values (future enhancement)

---

**Last Updated:** 2025-11-02  
**Owner:** UI Team  
**Status:** Active

