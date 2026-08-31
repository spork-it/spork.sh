---
title: Atom design and concurrency
description: Commit linearization, reentrant locking, validation, notification, identity, and free-threaded behavior.
section: package
group: packages
nav-path: [packages, spork-state]
project: spork-state
order: 643
package-version: "0.2.1"
changefreq: monthly
priority: 0.7
---

This page specifies how `Atom` commits updates, validates values, and notifies observers under concurrency. It describes the guarantees applications may rely on rather than only the current implementation shape.

## State machine

An atom owns four pieces of mutable implementation state:

1. the current value;
2. an optional validator;
3. a keyed, insertion-ordered watch dictionary;
4. a `threading.RLock` protecting all three.

Every value-changing operation follows the same commit protocol:

1. acquire the lock;
2. read the old value;
3. compute the candidate when applicable;
4. validate the candidate;
5. store the candidate;
6. snapshot watches;
7. release the lock;
8. notify the snapshot if old and new differ by identity.

The linearization point is the value assignment in step 5. Reads linearize while holding the same lock.

## Why an `RLock`

A swap function can safely inspect the same atom with `deref`; a plain non-reentrant lock would deadlock. A swap function should still be brief and should not perform another state-changing operation on the same atom: a nested commit can be overwritten by the outer swap's eventual commit and produces confusing notification order.

Unlike a compare-and-retry implementation, the update function runs exactly once. This gives predictable exception and side-effect behavior at the cost of serializing update computation for one atom.

## Validation

Validation occurs while locked and before assignment. Rejection, including an exception from the validator, preserves the old value and skips notification. Constructor validation occurs before the initial value is exposed.

Validator replacement is also synchronized. A new validator must accept the current value before it is installed, so the atom cannot enter a state that violates its active validator.

Validators should be deterministic and should not mutate the atom they validate.

## Notification

Watches are deliberately outside the lock:

- slow callbacks do not prevent readers or later writers from acquiring the atom;
- callbacks can safely read or update the atom;
- callback code cannot extend the update's critical section.

Notification is synchronous: the updating caller does not return until all selected watches return. A thrown exception is visible to that caller, but the value was already committed and is never rolled back. Since notification uses a snapshot, a callback may add or remove watches without modifying the current iteration.

Concurrent commits can cause watch callbacks for different transitions to overlap or complete out of order after their respective locks are released. Each callback still receives the exact old/new transition for its own commit. Consumers requiring serialized side effects should serialize them in the callback or place events onto a queue.

## Identity semantics

Compare-and-set follows Clojure atom semantics and compares the current and expected values by object identity (`is`). Watches use the same identity notion of a transition. Consequently:

- equal but distinct immutable or persistent values are transitions;
- resetting to the exact current object does not notify;
- a successful compare-and-set to the same object returns true without notification.

Callers should retain the value obtained from `deref`/`.value` when attempting compare-and-set.

## Mutable values

The atom protects replacement of its value, not arbitrary mutation inside that value. For example, mutating a stored Python list bypasses validation, synchronization, and watches. Prefer Spork persistent data structures, frozen dataclasses, tuples, or other immutable values.

## Free-threaded Python

Correctness does not depend on the CPython global interpreter lock. All atom metadata and transitions are protected explicitly, and callbacks run only after protected state has been snapshotted. CI exercises the same contract on Python 3.14t with the GIL disabled.
