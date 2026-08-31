---
title: Spork
description: A Lisp hosted on CPython, with direct Python interoperability, persistent collections, macros, and project tools.
changefreq: weekly
priority: 1.0
---
Imports go through Python's loader, and imported classes, exceptions, iterators, async values, and extension modules remain ordinary Python objects. There is no FFI layer or parallel package ecosystem.
