---
name: style-guide
description: Boilerplate style guide page for Next.js/React projects using shadcn/ui. Creates a living documentation page at /style-guide showing all UI components and their states. Use when setting up a new project to establish a component library reference.
---

# Style Guide Generator

This skill provides a boilerplate style guide page for Next.js projects with shadcn/ui. The style guide serves as a **living component library** — a single page showing all UI components, their variants, and states.

## What It Creates

A `/style-guide` page with:
- **Left navigation** — Sticky sidebar with hierarchical section navigation
- **Colors** — Brand palette, category colors, system colors
- **Typography** — Font families, sizes, weights
- **Buttons** — All variants, sizes, states
- **Inputs** — Default, focus, error, disabled states
- **Cards** — Layout variations
- **Avatars** — Sizes and fallback states
- **Dialogs** — Modal patterns
- **Loading/Thinking** — Spinners, indicators, animated states
- **Design Tokens** — Spacing scale, border radius, shadows

## Usage

### 1. Copy the Template

Copy `templates/style-guide-page.tsx` to your project:

```bash
cp templates/style-guide-page.tsx your-app/app/style-guide/page.tsx
```

### 2. Customize for Your Project

1. **Update the header title** — Replace "STYLE GUIDE" with your project name
2. **Add your brand colors** — Update the Colors section with your palette
3. **Add your fonts** — Update the Typography section
4. **Import your components** — Replace placeholder imports with your actual components
5. **Add project-specific sections** — Add sections for custom components

### 3. Maintain the Style Guide

**The style guide is the canonical source for all UI components.**

When building or modifying components:

1. **Check the style guide first** — See if a component exists before creating
2. **Add new components** — Every reusable component gets a section
3. **Show all states** — Normal, hover, focus, disabled, error, loading
4. **Update on changes** — Modify a component? Update its style guide entry

### Maintenance Checklist

For every UI change:

- [ ] Component added to style guide (if new)
- [ ] All states shown (normal, hover, disabled, loading, error)
- [ ] Uses design tokens (colors, spacing, radius from theme)
- [ ] Properly exported from component index

## Template Structure

```
style-guide/
  page.tsx          # The main style guide page
```

The template includes:

### NAV_ITEMS Configuration

Navigation items define the sidebar structure:

```typescript
const NAV_ITEMS = [
  { id: 'colors', label: 'Colors', icon: Palette, children: [
    { id: 'brand', label: 'Brand' },
    { id: 'system', label: 'System' },
  ]},
  { id: 'typography', label: 'Typography', icon: Type },
  { id: 'buttons', label: 'Buttons', icon: MousePointer },
  // ... more sections
]
```

### Section Components

Each section follows this pattern:

```tsx
<section id="buttons">
  <SectionHeader title="Buttons" />
  <div>
    <h4 className="text-xs font-medium text-muted-foreground mb-3 uppercase tracking-wide">
      Variants
    </h4>
    <div className="flex flex-wrap gap-3">
      <Button variant="default">Default</Button>
      <Button variant="secondary">Secondary</Button>
      {/* All variants */}
    </div>
  </div>
</section>
```

### Helper Components

The template includes helper components:

- `SectionHeader` — Consistent section titles with border
- `ColorChip` — Compact color swatch with label and hex code

## Extending the Template

### Adding Custom Component Sections

1. Add to `NAV_ITEMS`:
```typescript
{ id: 'my-component', label: 'My Component', icon: Box },
```

2. Add the section:
```tsx
<section id="my-component">
  <SectionHeader title="My Component" />
  {/* Component variations */}
</section>
```

### Adding Loading/Thinking Components

For AI or async operations, create a "Thinking" section:

```tsx
<section id="thinking">
  <SectionHeader title="Loading States" />
  {/* Spinners, progress, skeleton loaders */}
</section>
```

Common patterns:
- `ToolCallIndicator` — Shows tool/function call status
- `ThinkingDots` — Animated "..." indicator
- `ShimmerBar` — Skeleton loading shimmer
- `TypingIndicator` — Chat typing animation

## Best Practices

1. **Keep it current** — Outdated style guides are worse than none
2. **Show real data** — Use realistic mock data, not "Lorem ipsum"
3. **Test interactions** — Dialogs should open, buttons should click
4. **Document edge cases** — Long text, empty states, loading
5. **Mobile considerations** — Show responsive variants if applicable

## File Location

The style guide should live at:
- **Next.js App Router**: `app/style-guide/page.tsx`
- **Next.js Pages Router**: `pages/style-guide.tsx`

URL: `http://localhost:3000/style-guide`
