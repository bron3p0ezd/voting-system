---
name: frontend-react-hooks
description: Implement or change React hooks that own asynchronous page or shared state, service orchestration, effects, cancellation, polling, debouncing, pagination, reload, and derived view data. Use in `src/app/hooks/`, `src/pages/*/hooks/`, and `src/shared/hooks/`. Do not use for pure visual components or global MobX store design.
---

# Maintain React State Workflows

## Workflow

1. Inspect the caller component, service contract, current hook state shape, and a neighboring hook with the same async behavior.
2. Model the complete state explicitly: data plus relevant loading, loaded, error, empty, or not-found flags.
3. Expose a focused result object with state and stable commands such as `reload`, `refetch`, setters, or mutations.
4. Start side effects in `useEffect` and prevent stale requests from updating state.
5. Clean up every resource created by an effect.
6. Keep derived view data memoized only when identity stability or computation cost matters.

## Async lifecycle

- Use `AbortController` when the service accepts a signal and cancellation is meaningful.
- Otherwise use the established `isMounted`/`isDisposed` flag or monotonically increasing request id.
- Check freshness before every state update after an `await` or promise callback.
- Reset the state fields affected by a changed identifier, URL, query, or page input.
- Keep previous data during background reload only when the current feature already distinguishes initial loading from loading-more.
- Convert `unknown` failures to a user-facing Russian fallback through a focused helper.

## Effects and callbacks

- Include every reactive value used by an effect unless it is intentionally stored in a ref.
- Dispose `autorun`, abort requests, clear timers and intervals, and remove DOM listeners in cleanup.
- Prefix intentionally unawaited promises with `void`.
- Use `useCallback` for commands returned by a hook or passed to dependency-sensitive children.
- Use `useMemo` for stable query objects and derived view models that otherwise retrigger effects.
- Do not use memoization as a blanket style rule.

## Boundaries

- Let services own HTTP and DTO mapping.
- Let hooks own asynchronous orchestration and page state.
- Let UI components render the returned contract and invoke commands.
- Promote a page hook to `shared/hooks` only when multiple features use the same workflow.
- Use `$frontend-mobx-state` when the source of truth is a global store rather than hook-local state.

## Validation

- Check rapid identifier/query changes, unmount during request, retry/refetch, empty data, and failure state.
- Run `npm run lint` and `npm run build`.
