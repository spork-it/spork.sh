---
title: Using atoms
description: Create, update, validate, watch, and subscribe to state from Python and Spork.
section: package
group: packages
nav-path: [packages, spork-state]
project: spork-state
order: 641
package-version: "0.2.1"
changefreq: monthly
priority: 0.7
---

Use `Atom` when one reference needs synchronized updates, pre-commit validation, and synchronous change observation. The Python and Spork API sections operate on the same implementation.

## Python API

```python
from spork_state import Atom

counter = Atom(0, validator=lambda value: value >= 0)

unsubscribe = counter.subscribe(
    lambda old, new: print(f"{old} -> {new}"),
    fire_immediately=True,
)

counter.swap(lambda value, amount: value + amount, 3)
assert counter.value == 3
assert counter.compare_and_set(counter.value, 4)

unsubscribe()
```

Functional equivalents (`atom`, `deref`, `swap`, `reset`, and others) are also exported.

## Spork API

```spork
(ns example.counter
  (:require [spork-state :as state]))

(def counter (state.atom 0 (fn [value] (>= value 0))))

(state.add-watch! counter :log
  (fn [key reference old-value new-value]
    (print old-value "->" new-value)))

(state.swap! counter (fn [value amount] (+ value amount)) 3)
(assert (= (state.deref counter) 3))
```

The core Spork functions are `atom`, `atom?`, `deref`, `swap!`, `swap-vals!`, `reset!`, `reset-vals!`, `compare-and-set!`, `add-watch!`, `remove-watch!`, `get-validator`, and `set-validator!`.

## Guarantees

- `swap`, `reset`, validator replacement, and compare-and-set are linearizable.
- A swap function runs exactly once while the atom's reentrant lock is held.
- Validators run before commit. Rejection leaves the old value unchanged.
- Watches run synchronously after commit, outside the lock, in registration order.
- A watch exception propagates but never rolls back committed state.
- Compare-and-set and change notification use object identity, not equality.
- Reading an atom is safe; mutating a mutable value obtained from it is not synchronized. Prefer immutable values.

See the [API reference](/docs/packages/spork-state/api/) and [design semantics](/docs/packages/spork-state/design/) for concurrency details.
