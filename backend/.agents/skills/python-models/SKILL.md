---
name: python-models
description: Create, change, or review SQLAlchemy 2 ORM models in backend `models.py` files. Use for columns, PostgreSQL types, relationships, enums, indexes, constraints, and model registration. Do not use for DTOs, repositories, services, or migration execution.
---

# Maintain SQLAlchemy Models

## Workflow

1. Inspect the existing model, related models, repository queries, DTO mappings, and current database constraints.
2. Use the existing `settings.database.Base` conventions and SQLAlchemy 2 typed declarative style.
3. Define database semantics explicitly, including nullability and delete behavior.
4. Update reverse relationships and consumers when the contract changes.
5. Register a new model in `src/migration_tables.py`.
6. Do not generate or apply an Alembic migration unless the user requests it.

## Mapping rules

- Declare fields with `Mapped[T]` and `mapped_column(...)`.
- Give each model a stable `__tablename__`.
- Specify `nullable`, `ForeignKey`, `unique`, `index`, defaults, server defaults, and `ondelete` where their behavior matters.
- Use PostgreSQL-aware types such as `JSONB` and `UUID` where the persisted shape requires them.
- Use `DateTime(timezone=True)` and timezone-aware values for timestamps.
- Put composite indexes and non-trivial constraints in `__table_args__`.

## Relationships and enums

- Add a relationship only when a real foreign-key relation supports it.
- Type relationships and use a string target name when needed to avoid import cycles.
- Specify the loading strategy explicitly and preserve matching `back_populates` contracts.
- Define domain enums near the owning models, inherit from Python `Enum`, and make `__str__` return `self.value` when the project relies on string conversion.

## Guardrails

- Keep models free of orchestration, external calls, HTTP behavior, and repository queries.
- Do not hide application-side business mutations in ORM events without an explicit architectural reason.
- Preserve existing table and enum names unless a schema migration is part of the request.
- Consider existing rows when adding non-nullable fields or stricter constraints.

## Validation

- Import `src/migration_tables.py` or the affected model module to catch mapping errors without changing the database.
- Check affected repository mappings and focused tests.
