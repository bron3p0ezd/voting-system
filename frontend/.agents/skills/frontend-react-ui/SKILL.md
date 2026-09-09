---
name: frontend-react-ui
description: Implement or change React pages, feature UI, shared components, layouts, route metadata, forms, icons, loading or empty states, and accessibility behavior. Use for `.tsx` work under `src/pages/` and `src/shared/`. Do not use for API transport, service mapping, or global store design.
---

# Maintain React UI

## Workflow

1. Inspect the owning page, its hook contract, neighboring components, shared alternatives, and current responsive states.
2. Decide whether the component is page-specific or genuinely reusable.
3. Define a local `<ComponentName>Props` contract and keep data/control ownership explicit.
4. Render loading, error, empty, not-found, authorized, and disabled states required by the use case.
5. Preserve semantic structure, keyboard access, focus visibility, and ARIA relationships.
6. Register route and page-title metadata when adding a page.
7. Run lint and production build.

## Component conventions

- Place page composition and feature UI in `pages/<feature>/ui/`.
- Place cross-page components in `shared/components/`; keep shared layouts in `shared/layouts/` and small shared display elements in `shared/ui/` where that convention already exists.
- Use named arrow-function exports. Preserve explicit `JSX.Element` return annotations where the neighboring components use them.
- Keep props types beside the component; use discriminated unions for materially different rendering contracts.
- Keep constants and focused pure helpers above the component or in a sibling `.utils.ts` when reused or large.
- Split a component when a subpart has an independent responsibility, state lifecycle, or reuse case; do not split only to reduce line count.

## Rendering and interaction

- Let hooks/services own reusable async orchestration; UI invokes commands and renders their result.
- Use early returns for page-level loading, not-found, or fatal error states when that matches the page flow.
- Use semantic `main`, `section`, `article`, headings, links, labels, lists, and buttons.
- Set `type="button"` for non-submit buttons.
- Pair inputs with labels and stable ids; connect hints/errors with `aria-describedby`, use `aria-invalid`, and announce validation errors appropriately.
- Preserve `focus-visible` styles and keyboard behavior for menus, popups, modals, and custom controls.
- Give decorative SVGs `aria-hidden="true"` and `focusable="false"`; accept standard `SVGProps<SVGSVGElement>` for reusable icons when appropriate.

## Routing and document metadata

- Define stable paths and titles in `shared/constants/pageTitles.ts`.
- Add route elements and `handle.pageTitle` in `app/App.tsx`.
- Keep shared chrome and `Helmet` handling in `AppLayout`; do not duplicate it per page.
- Preserve the identifier-driven user/organization resolution flow for dynamic profile routes.

## Styling

Use `$frontend-tailwind-style` for new tokens, conditional classes, responsive behavior, or reusable class overrides.
