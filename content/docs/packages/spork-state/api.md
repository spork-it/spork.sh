---
title: spork-state API
description: Atom construction, reads, updates, compare-and-set, watches, subscriptions, validators, and exports.
section: package
group: packages
nav-path: [packages, spork-state]
project: spork-state
order: 642
package-version: "0.2.1"
changefreq: monthly
priority: 0.7
---

Import the public API from the package root:

```python
from spork_state import Atom, atom, deref, swap
```

```spork
(ns example.state
  (:require [spork-state :as state]))
```

The implementation namespace `spork-state.core` remains available for direct use.

## `Atom`

### Construction

Python:

```text
Atom(value, *, validator=None)
atom(value, validator=None)
```

Spork:

```spork
(atom value)
(atom value validator)
```

A validator is a callable receiving a candidate value. It must return a truthy value. A false result raises `ValueError("Validator rejected reference state")`; an exception raised by the validator propagates unchanged. The initial value is validated during construction.

### Reading

| Python | Spork | Result |
| --- | --- | --- |
| `reference.value` | `(deref reference)` | Current value snapshot. |
| `reference.deref()` | `(deref reference)` | Current value snapshot. |

`value` is a read-only Python property. Atom synchronization does not make a mutable object stored inside the atom safe to mutate.

### Unconditional updates

| Python | Spork | Result |
| --- | --- | --- |
| `reference.reset(value)` | `(reset! reference value)` | New value. |
| `reference.reset_vals(value)` | `(reset-vals! reference value)` | `(old, new)` pair. |
| `reference.swap(fn, *args)` | `(swap! reference fn & args)` | New value. |
| `reference.swap_vals(fn, *args)` | `(swap-vals! reference fn & args)` | `(old, new)` pair. |

`swap` invokes `fn(current_value, *args)` exactly once under the atom's reentrant lock. If the function or validator raises, no value is committed and no watch runs.

The Python facade also exports `reset`, `reset_vals`, `swap`, and `swap_vals` functional forms. Non-bang functional forms are available to Spork as well.

### Compare-and-set

Python:

```python
reference.compare_and_set(expected, new_value)
compare_and_set(reference, expected, new_value)
```

Spork:

```spork
(compare-and-set! reference expected new-value)
```

Returns `true` only when the current value **is the exact `expected` object**. Equality is not considered. A successful replacement is validated before commit.

A successful compare-and-set to the identical object returns `true` but does not notify watches because no identity transition occurred.

### Watches

Python:

```python
reference.add_watch(key, callback)
reference.remove_watch(key)
```

Spork:

```spork
(add-watch! reference key callback)
(remove-watch! reference key)
```

A watch callback has the signature:

```text
callback(key, reference, old_value, new_value)
```

`add_watch` associates one callback with a hashable key and returns the atom. Reusing a key replaces its callback without changing that key's dictionary position. `remove_watch` returns the removed callback, or `None`/`nil`.

After a commit, the atom takes a watch snapshot while locked, releases the lock, then calls the snapshot synchronously in registration order. Registration changes during notification apply to later transitions. A callback exception propagates and prevents subsequent callbacks in that notification from running; the state remains committed.

No watch runs when old and new are the same object.

### Subscriptions

Python:

```python
unsubscribe = reference.subscribe(callback, fire_immediately=False)
```

Spork:

```spork
(def unsubscribe
  (subscribe reference callback *{:fire-immediately false}))
```

Subscription callbacks receive `(old_value, new_value)`. The returned zero-argument unsubscribe function is idempotent. With `fire_immediately=True`, the callback first receives `(current_value, current_value)`.

Subscriptions are convenience wrappers over keyed watches and have the same synchronous error behavior.

### Validators

| Python | Spork | Result |
| --- | --- | --- |
| `reference.validator` | `(get-validator reference)` | Current validator or `None`/`nil`. |
| `reference.get_validator()` | `(get-validator reference)` | Current validator or `None`/`nil`. |
| `reference.set_validator(fn)` | `(set-validator! reference fn)` | The atom. |

Installing a validator checks it against the current value before installation. Passing `None`/`nil` removes validation.

## Python exports

```text
Atom
VALIDATION_ERROR_MESSAGE
atom, is_atom, deref
reset, reset_vals, swap, swap_vals, compare_and_set
add_watch, remove_watch, subscribe
get_validator, set_validator
```

The build generates `py.typed` and generic stubs from the annotated Spork implementation, so `Atom[int]` and inferred operation results are available to static type checkers without hand-written Python declarations.
