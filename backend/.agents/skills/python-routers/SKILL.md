---
name: python-routers
description: Create, change, or review FastAPI routers in backend `routers.py` or `router.py` files. Use for endpoints, request and response schemas, route versioning, authentication dependencies, and `ServiceFactory`. Do not use for business rules, SQLAlchemy queries, or service implementation.
---

# Maintain FastAPI Routers

## Workflow

1. Inspect the domain's router, URL constants, schemas, service contract, authentication dependencies, and API tests.
2. Preserve the existing `APIRouter` grouping and `fastapi-versioning` convention.
3. Define distinct request and response schemas in `schemas.py`.
4. Acquire `ServiceFactory` through `Depends(get_factory)` from `settings.di.dependencies`. Call its domain-specific factory method, which returns the abstract service contract; never construct repository or service implementations in the router.
5. Resolve the abstract service contract, call one use-case method, and return its result.
6. Add or update focused API contract tests.

## Endpoint rules

- Give routers a clear Russian tag consistent with neighboring endpoints.
- Use URL constants from `urls.py` when the domain already centralizes paths there.
- Declare `response_model` and status codes explicitly when they form part of the public contract.
- `VersionedFastAPI` exposes versioned routes under `/api/v{major}`; the health router is unversioned.
- Follow existing router style by omitting a return annotation when `response_model` is the authoritative response contract.

## Dependencies and boundaries

- Resolve services by interface; never instantiate an `Impl` class in a router.
- Keep authentication and request parsing in dependencies or the existing service boundary.
- Router validates transport structure through FastAPI/Pydantic, but does not duplicate business validation.
- Do not construct SQLAlchemy statements, call repositories directly, or raise business `HTTPException` decisions in the router.
- Keep DTOs internal; use `*Request` and `*Response` schemas for HTTP.

## Validation

- Confirm the effective path including `/api/v{major}` and any router prefix.
- Test request validation, status code, response schema, authentication, and relevant failure contracts.
- Check that OpenAPI generation succeeds when schema or dependency signatures change.
