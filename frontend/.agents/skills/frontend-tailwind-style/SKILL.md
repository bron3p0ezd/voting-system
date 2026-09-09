---
name: frontend-tailwind-style
description: Implement or change frontend visual styling with Tailwind CSS 4, semantic CSS variables, `@theme` mappings, responsive utilities, conditional classes, reusable class overrides, and rare global effects. Use for UI styling and design-system changes. Do not use for component data flow or service logic.
---

# Maintain Tailwind Styling

## Workflow

1. Inspect the nearest components and the semantic tokens in `src/styles/index.css` before choosing classes.
2. Reuse an existing color, surface, border, spacing, radius, shadow, typography, or breakpoint token.
3. Compose layout and visual states with Tailwind utilities in JSX.
4. Add a new CSS variable and `@theme` mapping only when the value is a reusable design decision.
5. Use global CSS only for effects or browser behavior that utilities cannot express cleanly.
6. Verify mobile, desktop, hover, active, disabled, loading, and focus-visible states that apply.

## Token system

- Define raw theme values in `:root`; mirror theme-specific overrides under `.dark` when required.
- Expose semantic Tailwind names in the `@theme` block.
- Prefer tokens such as `text-text-primary`, `text-text-muted`, `bg-surface-soft-*`, `border-rating-card-border`, `rounded-base`, `shadow-rating-card`, and layout spacing/max-width utilities.
- Preserve the always-enabled dark theme set by `src/main.tsx`; do not introduce a second theme mechanism during a style task.
- Reuse the custom responsive breakpoints and mobile-first `sm:`, `mobile:`, `xs:`, and `s:` patterns already in the codebase.

## Class composition

- Write ordinary styling as `className` utility strings.
- Use multiline strings to group layout, spacing, surface, typography, and interaction classes when readability improves.
- Use template strings for small conditional variants already owned by the component.
- Use `tailwind-merge` when a reusable component accepts class overrides that may conflict with defaults.
- Keep a variant's full interactive states together: default, hover, active, focus-visible, and disabled.

## Guardrails

- Do not introduce arbitrary hex colors when a semantic token exists.
- Do not encode domain meaning only through color; preserve text, icons, labels, or accessible state.
- Do not move one-off component styling into global CSS without a reuse or browser-behavior reason.
- Keep CSS variable naming consistent with the existing base-variable and `@theme` mapping pattern, including historical names that are already public utilities.
- Preserve touch targets, readable contrast, wrapping, minimum widths, and overflow behavior across supported viewport sizes.

## Validation

- Inspect the rendered component at narrow and wide viewport sizes when browser testing is available.
- Run `npm run lint` and `npm run build`.
