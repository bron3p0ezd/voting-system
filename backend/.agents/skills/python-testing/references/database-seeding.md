# Database Seed Data

## Contents

- [Standard flow](#standard-flow)
- [JSON contract](#json-contract)
- [Dates and identifiers](#dates-and-identifiers)
- [Relationships and load order](#relationships-and-load-order)
- [Scenario consistency](#scenario-consistency)
- [Validation checklist](#validation-checklist)

## Standard flow

DB-backed API and integration tests use this chain:

```text
setup_test_data
  -> fill_database_with_mock_data
  -> prepare_database
  -> _open_mock_json
  -> _parse_dates / parse_date
  -> insert(model).values(records)
```

Name a seed file `test_data/mock_<model>.json`. The `model_name` passed to `prepare_database` must match `<model>`.

When a new seed file is required:

1. Add valid records to `mock_<model>.json`.
2. Add or reuse related parent records.
3. Register `prepare_database(...)` in `utils/fill_database_with_mock_data.py`.
4. Place the call after its FK dependencies and before dependent tables.
5. Use the scenario through `setup_test_data`.

## JSON contract

- Store a JSON array of objects without comments or trailing commas.
- Use only real SQLAlchemy model fields accepted by the insert.
- Provide every required field that has no database or application default.
- Respect column types, primary keys, foreign keys, unique constraints, nullability, and check constraints.
- Keep payloads realistic but limited to fields needed for insertion or the tested contract.

## Dates and identifiers

- Store fields listed in `date_keys` as `%Y-%m-%d %H:%M:%S.%f %z`.
- Use timezone-aware datetime strings.
- Use deterministic integer IDs that do not collide with the existing seed set.
- Continue the domain's established ID ranges and account for sequence synchronization after explicit inserts.
- Avoid current time, random UUIDs, and other nondeterministic values unless the scenario specifically tests them.

## Relationships and load order

- Ensure every foreign key references a record present before the dependent insert.
- Review `fill_database_with_mock_data.py` as a dependency-ordered list, not an arbitrary registry.
- When adding a new dependency, update both parent and child seed files if necessary.
- Do not leave a JSON file used by tests unregistered in the standard seed flow.

## Scenario consistency

- Keep JSON rows, `test_dtos/` values, fixtures, and expected response models aligned on identifiers and key fields.
- Prefer extending an existing dataset when the scenario shares its business meaning.
- Add a new named scenario when extending the old one would make unrelated tests ambiguous.
- Use `utils.sql_methods` only for a minimal state change unique to one test; it does not replace shared seed data.
- Do not rewrite historical mock structure or rename keys without a task-driven reason.

## Validation checklist

- Parse the changed JSON files.
- Compare keys and value types with the owning ORM models.
- Confirm FK load order in `fill_database_with_mock_data.py`.
- Run the narrow API or integration test using the data.
- Run other tests that consume the same seed file when shared records changed.
