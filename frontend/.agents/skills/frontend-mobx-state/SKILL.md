---
name: frontend-mobx-state
description: Implement or change application-wide MobX stores, store actions and getters, initialization hooks, and React subscriber hooks built with `autorun`. Use in `src/app/store/` and app-level hooks when state must be shared across routes. Do not use for page-local form, loading, popup, or request state.
---

# Maintain Global MobX State

## Workflow

1. Confirm the state is truly shared across routes or distant components; otherwise keep it local to a hook/component.
2. Inspect the closest store and every subscriber or initializer that consumes it.
3. Add observable state, focused mutation methods, and derived getters to the owning class.
4. Export one singleton instance following the existing store pattern.
5. Expose store data to React through an app hook using `autorun` and local React state.
6. Dispose the reaction and any pending resources during cleanup.

## Store pattern

- Place stores in `src/app/store/` and name classes `<Domain>Store`.
- Call `makeAutoObservable(this)` in the constructor.
- Keep state normalized for its lookup pattern; use a private `Map` when data is keyed by normalized identifiers.
- Normalize identifiers in one private/module helper and reuse it for set/get/has/clear operations.
- Mutate observable state through store methods instead of directly from JSX.
- Use getters for cheap derived state and query methods for keyed collections.
- Export `const <name>Store = new <Name>Store()` as the shared instance.

## React bridge

- Initialize React state from the current store value.
- Create `autorun` inside `useEffect`, copy the observed fields into local React state, and call `dispose()` in cleanup.
- Return plain React values and stable callbacks from the subscriber hook.
- Put application startup loading/subscription in `src/app/hooks/` and invoke it from `App` or `AppLayout` according to its scope.
- Prevent duplicate initial requests with store `has*` queries, pending identifier sets, or the existing readiness flags.

## Guardrails

- Do not add `mobx-react-lite`, `observer`, a MobX Context provider, Redux, or another global-state mechanism during a feature task.
- Do not mirror all page-local state globally.
- Keep HTTP in services and orchestration in init/subscriber hooks; a store should not become an API client.
- Clear user-scoped global data during logout or identity change when its current contract requires it.

## Validation

- Check initial value, observable update, duplicate initialization, identifier normalization, and cleanup after unmount.
- Run `npm run lint` and `npm run build`.
