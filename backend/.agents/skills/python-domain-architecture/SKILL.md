---
name: python-domain-architecture
description: Design or change a backend domain, choose the correct FastAPI application layer, and wire contracts through dependency injection. Use when adding a domain, moving logic between models, repositories, services, db-services, routers, policies, or DI. Do not use for an isolated edit whose layer and contract are already established.
---

# Design Backend Domain Changes

## Workflow

1. Inspect the affected domain, its public contracts, implementations, DI registrations, callers, and tests.
2. Follow the domain's existing singular file names and `impls/` layout; do not rename historical `service.py` or `router.py` only to normalize it.
3. Assign each responsibility to one layer before writing code.
4. Define or update the abstract contract before its implementation when the behavior is injected through `ServiceFactory`.
5. Wire new implementations into the existing resolver or builder path under `src/settings/di/`.
6. Check that no new dependency points from a lower layer to a higher layer.
7. Validate the smallest complete vertical slice, including its callers and tests.

## Layer boundaries

| Layer | Owns | Must not own |
|---|---|---|
| Model | ORM mapping, database constraints, relationships | orchestration, external calls |
| DTO | typed data exchanged between layers | ORM session, business side effects |
| Repository | SQLAlchemy queries and ORM-to-DTO mapping | business rules, HTTP errors, transactions |
| DbService | reusable data operations through repositories | SQLAlchemy statements, cross-domain orchestration |
| Service | use cases, validation, orchestration, transaction boundary | direct ORM queries |
| Router | HTTP contract and dependency acquisition | business rules, implementation construction |
| Policy | deterministic domain decision | persistence and transport concerns |

## Domain layout

Prefer the existing subset of these files rather than creating empty layers:

```text
src/apps/<domain>/
  models.py
  dtos.py
  schemas.py
  repositories.py
  db_services.py
  services.py
  routers.py
  exceptions.py
  policies.py
  impls/
    repositories/
    db_services/
    services/
```

## Guardrails

- Keep contracts in the domain root and implementations under `impls/`.
- Use domain-oriented names that state responsibility; preserve established `Impl` suffix conventions.
- Reuse a public service contract for cross-domain behavior instead of importing another domain's implementation.
- Keep infrastructure shared by multiple domains under `src/settings/`; keep domain behavior in `src/apps/<domain>/`.
- Do not add an abstraction without at least one real caller and a clear boundary.
- Register a new ORM model in `src/migration_tables.py`.
- Do not create or apply an Alembic migration unless the user requests the schema change workflow.

## Related skills

Load the focused skill for each modified layer: `$python-models`, `$python-dtos`, `$python-repositories`, `$python-services`, `$python-routers`, or `$python-testing`.
