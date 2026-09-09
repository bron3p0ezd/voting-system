---
name: python-testing
description: Create, change, diagnose, or review pytest tests under `src/tests/`, including API, integration, and unit tests, fixtures, test DTOs, JSON seed data, database helpers, and assertions. Do not use for unrelated production-code generation.
---

# Maintain Backend Tests

Apply `src/tests/AGENTS.md` together with this workflow.

## Workflow

1. Classify the test as API, integration, or unit and inspect neighboring tests first.
2. Identify one observable responsibility and name the test after that scenario.
3. Reuse existing fixtures, test DTOs, mock JSON, assertion messages, and helpers.
4. For DB-backed API or integration tests, use `setup_test_data` as the baseline.
5. Add stable scenario data to JSON seed files; use `sql_methods` only for the minimal per-test delta.
6. Structure the body as Arrange → Act → Assert with one main action.
7. Run the narrowest relevant pytest path, then the containing domain suite when shared setup changes.

## Test kinds

- `api_tests/<domain>/`: exercise HTTP request, response, authentication, and status contracts through the app.
- `integration_tests/<domain>/`: exercise collaboration between real layers or database behavior without the HTTP boundary.
- `unit_tests/<domain>/`: isolate deterministic logic; mocks are allowed when isolation is the purpose.
- Do not use `Mock` in API or integration tests to conceal missing standard setup.

## Assertions and fixtures

- Keep one reason for failure per test. Split pagination, collection contents, item schema, and nested relationships into separate tests.
- Every assert uses a reusable Russian message from `utils/assert_messages.py`.
- Prefer `utils.compare_models` for an owned response/model contract.
- Do not import fixtures into test modules merely to register them.
- Place reusable fixtures under `fixtures/<domain>/` and follow existing exports through fixture `__init__.py` files and `conftest.py`.

## Seed data

Read [references/database-seeding.md](references/database-seeding.md) whenever adding or changing `test_data/*.json`, `setup_test_data`, or `fill_database_with_mock_data.py`.

## Guardrails

- A request to write tests does not authorize unrelated service, repository, or router implementations.
- Do not change production behavior merely to weaken a valid assertion.
- Preserve existing mock formats and identifiers unless the scenario requires a change.
- Never run tests against the production database configuration.
