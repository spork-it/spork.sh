---
title: Namespaces and modules
description: Require Spork namespaces, import Python modules, and use dotted access.
section: reference
group: language
project: spork-lang
order: 170
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

Namespaces map Spork names to source modules and control compile-time and runtime dependencies. Use `:require` for Spork namespaces and `:import` for Python modules.

## Namespace Declaration

```spork
(ns my.app.core
  (:require
    [my.utils :refer [helper-fn]]
    [external.lib :refer :all])
  (:import
    [spork.pds :as pds]
    [array :as arr]
    [os.path :as osp]
    [collections :refer [defaultdict Counter]]
    [math :refer [sin cos]]))
```

## Require Options (for Spork namespaces)

Use `:require` only for Spork namespaces. It loads compile-time macros as well as runtime definitions. Python modules are rejected by `:require`; load them with `:import`.

<!-- verify-docs: skip=namespace-fragments -->
```spork
; Alias the namespace; this makes short.foo available
[some.long.module :as short]

; Specific imports into current namespace
[module :refer [fn1 fn2]]

; Import all public symbols
[module :refer :all]
```

Attempting to require a Python module is a compile-time error:

<!-- verify-docs: expect-error=SyntaxError -->
```spork
(ns invalid.require
  (:require [json :as j]))
```

## Import Options (for Python modules)

Use `:import` for Python modules. This makes the dependency's origin explicit and avoids compile-time macro loading. Python modules cannot be loaded with `:require`.

```spork
; Inside (ns ...) use (:import ...)
(ns my.app
  (:import
    [os]                              ; import os
    [json :as j]                      ; import json as j
    [pathlib :refer [Path]]           ; from pathlib import Path
    [collections :refer [defaultdict Counter]]  ; from collections import ...
    [math :refer [sin :as s cos]]     ; from math import sin as s, cos
    [os.path :as osp]))               ; import os.path as osp

; Access with dot notation
(print (os.getcwd))
(print (j.dumps (dict [["a" 1]])))
(print (s 0.5))
```

## Importing Macros

Macros use the same `:require` syntax as regular definitions; the compiler determines which referred symbols are macros. There is no separate macro-import form.

```spork
(ns my.app
  (:require [my.macros :refer [my-macro]]
            [other.lib :as lib :refer [foo]]))

; A referred macro is called without qualification
(my-macro some args)

; An alias provides qualified access
(lib.some-macro arg)

; :refer :all imports all public macros and definitions
(ns another.app
  (:require [my.macros :refer :all]))
```

## Dotted Access

Dotted symbols are the canonical spelling for qualified namespace calls, Python module calls, class methods, and methods on named objects. Unlike Clojure, Spork uses dots rather than slashes for qualified names.

```spork
(ns my.app
  (:require [std.string :as str])
  (:import [math :as m]
           [array :as arr]))

(str.join ", " ["a" "b" "c"])  ; => "a, b, c"
(m.sqrt 16)                     ; => 4.0
(arr.array "i" [1 2 3])         ; Python standard-library array

(def values (list [3 1 2]))
(values.sort)
(vec values)                       ; => [1 2 3]
```

A dotted symbol compiles as one Python attribute chain, so `client.session.get` works for nested attributes as long as the chain begins with a symbol. Qualified macros must also use this spelling, such as `(lib.some-macro arg)`; leading-dot method syntax is a runtime call and does not macro-expand.
