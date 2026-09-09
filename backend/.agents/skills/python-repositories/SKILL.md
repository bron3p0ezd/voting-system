---
name: python-repositories
description: Create, change, or review backend repository contracts and implementations in `repositories.py` and `impls/repositories/`. Use for SQLAlchemy queries, persistence operations, joins, pagination, and ORM or row mapping to DTOs. Do not use for business orchestration or HTTP behavior.
---

# Maintain Repository Contracts

## Workflow

1. Inspect the abstract repository, its implementation, DTOs, model, callers, and base classes in `src/settings/repositories.py` and `src/settings/alchemy_repositories.py`.
2. Add or update the abstract method before changing an injected implementation.
3. Keep one repository method focused on one data-access operation.
4. Return a domain/repository DTO or scalar that callers can use without knowing SQLAlchemy row internals.
5. Update DI wiring if a new repository contract or implementation is introduced.
6. Validate the query against representative empty, single-row, and multi-row results as relevant.

## Query conventions

- Set `cls_model` on `AlchemyRepository` implementations and use `self.model` for the repository's root model.
- Use `self.session` for execution.
- Directly reference other ORM classes only when the query needs a join, alias, subquery, `exists`, or related update.
- Keep filtering, ordering, pagination, and aggregation explicit.
- Do not rely on row ordering unless the query includes `order_by`.

## Mapping

- Never leak `Row`, `RowMapping`, tuple, or an untyped mapping across the repository boundary.
- Convert composed query rows to Pydantic DTOs with `model_validate` when the DTO is configured for attribute input.
- For non-trivial or repeated mapping, use a focused private mapper such as `__map_row_to_dto`.
- Use `cast` only to describe a runtime shape already guaranteed by the query; do not use it to conceal an incompatible result.

## Boundaries

- Repository owns SQLAlchemy statements, persistence, and mapping.
- Repository does not own business rules, cross-domain orchestration, FastAPI `HTTPException`, `commit`, or `rollback`.
- A write method may execute or flush a statement; the owning service controls the transaction boundary.
- Keep HTTP schemas out of repository contracts.

## Validation

- Check abstract and concrete method signatures together.
- Run focused repository or integration tests against the test database when query behavior changes.
- Confirm that callers handle empty results using the repository's declared contract.
