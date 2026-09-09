---
name: frontend-architecture
description: Preserve and extend the existing layered React frontend architecture. Use when adding a page, feature, entity, shared module, route, adapter, service, or when deciding where new frontend behavior belongs. Do not use for an isolated style-only change whose owning component is already clear.
---

# Extend the Frontend Architecture

## Workflow

1. Trace the complete existing flow for the nearest feature: route → page UI → hook → service → DTO/entity → shared UI.
2. Place the new responsibility in an existing top-level layer; do not introduce a new architecture vocabulary.
3. Follow the closest feature's folder and import patterns, including historical singular file names.
4. Keep API transport details outside JSX and page-specific presentation outside entities.
5. Add the smallest complete vertical slice and update route metadata, env declarations, mocks, or shared abstractions only when the slice requires them.
6. Run lint and production build.

## Existing layers

| Layer | Place here |
|---|---|
| `app` | router composition, global stores, startup and global subscriber hooks |
| `entities` | normalized client-facing domain models |
| `pages/<feature>/ui` | routes, page composition, feature-owned components |
| `pages/<feature>/hooks` | feature state and use-case orchestration |
| `pages/<feature>/adapters` | page-specific view models |
| `services` | HTTP, auth, DTO mapping, cache, mock/network selection |
| `shared` | UI, hooks, layouts, constants and utilities reused across features |
| `types` | backend DTO and transport shapes |
| `styles` | global theme tokens and exceptional common CSS |

## Placement decisions

- Put a reusable domain shape in `entities`; keep backend field names in `types`.
- Put page-only state and transformations under that page.
- Promote code to `shared` only after it has a real cross-page use or represents application-wide infrastructure.
- Put a cross-page singleton state in `app/store`; keep local interaction state in the owning hook or component.
- Register a route in `app/App.tsx` and reuse `ROUTE_PATHS`/`PAGE_TITLES` from `shared/constants/pageTitles.ts`.
- Keep explicit relative imports and concrete file paths; do not add aliases or barrel exports.

## Guardrails

- Treat the layout as a pragmatic hybrid, not strict Feature-Sliced Design. Do not perform broad layer moves during a feature task.
- Preserve existing cross-layer exceptions unless the user requests an architectural cleanup.
- Do not import service response DTOs directly into JSX when an entity or view adapter already exists.
- Do not duplicate a shared component, hook, URL, validation utility, or service method.
- Keep named exports; preserve the few established default exports.

## Related skills

Use `$frontend-api-services`, `$frontend-react-hooks`, `$frontend-mobx-state`, `$frontend-react-ui`, or `$frontend-tailwind-style` for the focused parts of the same vertical slice.
