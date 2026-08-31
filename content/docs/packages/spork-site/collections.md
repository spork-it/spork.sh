---
title: Document collections
description: Filter, sort, and limit discovered documents with eager ordinary Spork values.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 653
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

Collections use ordinary Spork predicates and callable keys rather than a query language.

**Namespace:** require `spork-site.collections` with an alias such as `collections`.

```spork
(defn published? [document]
  (not (is (:draft document) true)))

(def posts
  (collections.collection
    documents
    * :where published?
      :sort-by :date
      :order :desc
      :limit 20))
```

`collection`, `filter-documents`, and `sort-documents` eagerly return persistent vectors. Standard functions such as `filter`, `group-by`, `take`, and eager `(for ...)` expressions remain available for further composition.
