---
name: git-commits
description: Create Git commits and merge branches in Province-Rate repositories. Use when the user asks to commit changes, write a commit message, or merge into dev or main; enforce Conventional Commits and protected-branch validation.
---

# Manage Git Commits and Protected Merges

Git mutations still require an explicit user request. Loading this skill does not authorize a commit, merge, push, rebase, reset, or history rewrite.

## Commits

1. Read the applicable `AGENTS.md`, then inspect the current branch, status, and diff.
2. Preserve unrelated user changes. Stage only files that belong to the requested commit unless the user explicitly asks to include everything.
3. Write the message in Conventional Commits format:

   ```text
   <type>(<optional-scope>): <description>
   ```

   Use `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`, or `revert`. Keep the description concise, imperative, and in English. Use `!` and a `BREAKING CHANGE:` footer when the change is breaking.
4. Checks are optional before an ordinary commit. Do not run them solely because a commit was requested, unless the user also requests checks or the applicable repository instructions independently require them for the current task.
5. Before committing, review the staged diff and confirm that the final message describes only the staged change.

## Merge into `dev` or `main`

Treat `dev` and `main` as protected targets, including fast-forward, merge-commit, and squash workflows.

1. Read the target repository's `AGENTS.md`, package scripts, and CI configuration to discover its complete locally available validation suite.
2. Before the merge, run every non-destructive check that can be executed locally for that repository. This includes the full test suite, lint and formatting checks, type or static analysis, framework checks, migration validation, and production build whenever those checks exist.
3. For a merge spanning multiple repositories, validate every affected repository independently.
4. Do not merge while any required check fails. Do not bypass, weaken, or omit a check to obtain a passing result.
5. If a check cannot run because of missing credentials, dependencies, services, or environment configuration, stop and report the exact blocker instead of merging.
6. After all checks pass, merge with `git merge --no-ff` so the target branch receives an explicit merge commit. Do not use a fast-forward merge.

Do not push the result unless the user explicitly requests a push.
