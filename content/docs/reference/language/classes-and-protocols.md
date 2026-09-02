---
title: Classes and protocols
description: Define Python-compatible classes and protocol-based polymorphism.
section: reference
group: language
project: spork-lang
order: 160
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Spork classes compile to Python classes, while protocols provide explicit runtime dispatch over participating types. This page defines their declarations, methods, fields, properties, and extension forms.

## Classes

### Basic Class Definition

`defclass` takes a class name, an optional vector of base classes, and a body of methods, fields, or class-level definitions. An empty base vector (`[]`) declares no explicit base class.

```spork
(defclass Point []
  (defn __init__ [self x y]
    (set! self.x x)
    (set! self.y y))

  (defn distance [self other]
    (let [dx (- other.x self.x)
          dy (- other.y self.y)]
      (** (+ (* dx dx) (* dy dy)) 0.5))))
```

### Inheritance

```spork
(defclass ColorPoint [Point]
  (defn __init__ [self x y color]
    (.__init__ (super) x y)  ; (super).__init__(x, y)
    (set! self.color color)))
```

### Decorators

Decorator metadata appears after `defn` or `defclass` and before the function or class name. External Python decorators must be imported; Python built-ins such as `staticmethod` and `classmethod` are already available.

```spork
(ns example.classes
  (:import [dataclasses :refer [dataclass]]))

(defclass ^dataclass Person []
  (field name str)
  (field age int 0))

(defclass Counter []
  (defn ^staticmethod create []
    (Counter))

  (defn ^classmethod from-value [cls value]
    (let [c (cls)]
      (set! c.value value)
      c)))
```

### Class Fields

Inside any class, `(field name type)` emits an annotated field without a default, while `(field name type default)` includes a default. This is especially useful for dataclasses. `field` is a Spork class form; it does not need to be imported from `dataclasses`.

```spork
(ns example.config
  (:import [dataclasses :refer [dataclass]]))

(defclass ^dataclass Config []
  (field host str "localhost")
  (field port int 8080)
  (field debug bool false))
```


## Protocols

Protocols provide polymorphic dispatch similar to Clojure protocols or type classes.

### Defining Protocols

```spork
(defprotocol IShape
  "Protocol for geometric shapes."
  (area [self])
  (perimeter [self]))

; Structural protocol (duck typing based on methods)
(defprotocol ^structural ICloseable
  (close [self]))
```

### Extending Types

```spork
; Extend a type to implement a protocol
(extend-type Circle
  IShape
  (area [self] (* 3.14 self.radius self.radius))
  (perimeter [self] (* 2 3.14 self.radius)))

; Extend multiple types for one protocol
(extend-protocol IShape
  Rectangle
  (area [self] (* self.width self.height))
  (perimeter [self] (* 2 (+ self.width self.height)))

  Square
  (area [self] (* self.side self.side))
  (perimeter [self] (* 4 self.side)))
```

### Using Protocols

```spork
; Call protocol methods
(area my-circle)
(perimeter my-rectangle)

; Explicit extensions also register the type with the protocol ABC
(isinstance my-object IShape)
```
