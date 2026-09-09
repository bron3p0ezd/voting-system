---
name: python-services
description: Create, change, or review backend Service and DbService contracts, implementations, business exceptions, and Unit of Work boundaries. Use for business rules, orchestration, dependency injection, commit or rollback, and translation to FastAPI errors. Do not use for raw SQLAlchemy queries or router-only work.
---

# Maintain Services and Transactions

## Workflow

1. Inspect the service contract, implementation, repositories or db-services, DI resolver, callers, exceptions, and tests.
2. State the use case and transaction boundary before editing.
3. Keep the public method focused on orchestration; move reusable validation and mapping into focused private methods or policies.
4. Obtain data and validate preconditions before mutation where possible.
5. Commit once at the highest service level that owns the complete successful operation.
6. Translate errors only at the boundary that understands the higher-level meaning.

## Contracts and implementations

- Store abstract contracts in `services.py`, historical `service.py`, or `db_services.py` as established by the domain.
- Derive service contracts from `settings.services.Service` and declare public operations with `@abstractmethod`.
- Store implementations in `impls/services/` or `impls/db_services/` and preserve the project's `Impl` naming convention.
- Name a service by its entity, use case, or policy rather than a generic placeholder.
- Inject stable dependencies through `__init__` and keep them private.

## Boundaries

- Service owns business rules, orchestration, cross-service coordination, and conversion of domain errors to use-case or HTTP errors.
- Service may raise FastAPI `HTTPException` when it is the boundary called by a router; the router must not reproduce the decision.
- Service must not build SQLAlchemy statements or manipulate ORM objects directly.
- DbService is an optional service-layer adapter over repository APIs and does not bypass repositories.
- A `get_*` operation whose contract requires an entity should raise a focused domain exception, commonly derived from `DbEntityNotFoundException`, instead of returning an ambiguous value.

## Unit of Work

- Inject `UOW` into the service layer when the use case controls a transaction.
- Repository never calls `commit` or `rollback`.
- For several related writes, perform one `commit` after all succeed.
- If an error can occur after partial writes, call `rollback` in a focused exception boundary and re-raise.
- A standalone atomic DbService may commit only when it is explicitly the final transaction boundary.
- A DbService participating in higher Service orchestration leaves commit to that Service.
- Read-only and `safe_*` methods do not commit.

## Validation

- Verify contract and implementation signatures and DI construction together: `ServiceFactory` must pass the repository contract into the service implementation, using a repository built from the active `DBM` session.
- Test success, domain failure, and rollback behavior for state-changing scenarios.
- Check that no caller now observes a lower-level infrastructure exception unintentionally.
