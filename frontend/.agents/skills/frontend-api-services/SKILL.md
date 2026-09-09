---
name: frontend-api-services
description: Implement or change typed frontend API services, transport DTOs, entity mapping, authenticated requests, response validation, service caches, and development mocks. Use for files in `src/services/`, `src/types/`, `src/entities/`, and API constants. Do not use for page rendering or local-only UI state.
---

# Maintain Frontend API Services

## Workflow

1. Inspect the closest service, DTO file, entity model, caller hook, mock provider, and API URL constant.
2. Define the wire contract in `src/types/*.types.ts` using backend field names exactly.
3. Define or reuse a normalized entity model when callers should not depend on wire format.
4. Build URLs and query parameters with `URL`, `URLSearchParams`, and `encodeURIComponent`.
5. Select the correct public or authenticated fetch path.
6. Validate statuses before parsing, map the payload, and return the same contract from mock and network paths.
7. Invalidate or refresh service cache after mutations that make it stale.

## DTO and entity boundary

- Keep API DTO fields in snake_case, including established backend spelling.
- Keep entity and hook-facing models in camelCase.
- Perform normalization in private service mappers or an existing adapter, not inside JSX.
- Parse numeric strings and nullable values deliberately; preserve `null` when it has domain meaning.
- Avoid unsafe casts. If runtime data needs validation, check the relevant field before returning it.
- A service may return a DTO directly only when that is the established feature contract and no normalized entity exists.

## Requests

- Reuse origins and stable endpoint constants from `shared/constants/api.ts`.
- Use `authService.authorizedFetch` for protected endpoints so a 401 can refresh and retry.
- Preserve `credentials: "include"` for cookie-backed auth flows.
- Do not set `Content-Type` manually for `FormData`.
- Treat special statuses according to the service contract: common patterns are `null` for absence, `HttpNotFoundError` for navigational 404, and `Error` for other failures.
- Preserve useful backend `detail` only when the existing caller expects it; do not expose arbitrary payloads as trusted error text.

## Mocks and cache

- Gate service mocks through `shouldUseMocks`, which is active only in Vite dev mode with `VITE_USE_USER_MOCKS=true`.
- Keep mock results deterministic and structurally identical to the network branch's returned frontend contract.
- Place mock source data and lookup helpers in `src/services/mocks/`.
- Keep caches private to the owning service, normalize keys consistently, define an explicit TTL when time-bound, and expose focused invalidation methods when callers need refetch.

## Validation

- Check empty input, success, relevant 401/403/404 behavior, malformed values, and mutation cache invalidation.
- Run `npm run lint` and `npm run build`.
