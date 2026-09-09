---
name: python-dtos
description: Create, change, or review backend DTOs in `dtos.py` and HTTP request or response models in `schemas.py`. Use for dataclasses, Pydantic transfer models, repository result shapes, and transport contracts. Do not use for ORM models or business logic.
---

# Maintain DTOs and HTTP Schemas

## Workflow

1. Identify every producer and consumer of the data shape.
2. Decide whether the shape belongs to an internal layer contract or the HTTP boundary.
3. Reuse an existing focused model when its semantics match; do not reuse only because fields happen to match.
4. Add validation only at the boundary that owns it.
5. Update mappings and tests together with the model.

## DTOs

- Store internal transfer models in `src/apps/<domain>/dtos.py` and use the `DTO` suffix.
- Use `@dataclass` for lightweight inter-service commands, results, and value objects.
- Use `@dataclass(frozen=True)` when the value must not change after construction.
- Use Pydantic `BaseModel` for repository DTOs that need `model_validate`, `model_dump`, or attribute-based validation.
- Set `ConfigDict(from_attributes=True)` when DTOs are built from ORM objects or SQLAlchemy rows.
- Use nested DTOs for structured payloads instead of untyped dictionaries.
- Keep provider-facing DTOs distinct from internal domain DTOs.

## HTTP schemas

- Store request and response models in `src/apps/<domain>/schemas.py`.
- Name input models `*Request` and output models `*Response`.
- Do not use one class as both request and response when the contracts have different meaning or mutability.
- Keep repository DTOs out of `response_model` and HTTP schemas out of repositories.

## Guardrails

- DTOs do not depend on an ORM session, inherit ORM models, perform I/O, or own side effects.
- Prefer `T | None` for optional values in new code. Use `Literal` or an existing domain enum for closed value sets.
- Do not expose persistence-only fields through HTTP accidentally.
- Preserve wire compatibility unless the user explicitly requests an API contract change.

## Validation

- Check all construction sites and field aliases after renaming or changing a field.
- Validate representative ORM/row mapping for repository DTOs.
- Run focused API tests when a request or response schema changes.
