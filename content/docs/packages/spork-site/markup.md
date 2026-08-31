---
title: Markup
description: Use locally scoped $tag forms while components, conditions, data access, and iteration remain ordinary Spork.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 658
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

`markup` only gives special meaning to lists headed by a `$`-prefixed symbol. Components, conditionals, calls, data access, and iteration remain ordinary Spork.

**Namespace:** refer `element`, `fragment`, and `markup` from `spork-site.core`; examples also use `site` as its alias.

```spork
(defn post-card [post]
  (markup
    ($article {:class "post"}
      ($h2 ($a {:href (:route post)} (:title post)))
      ($p (:summary post)))))

(defn homepage [posts]
  (markup
    ($main {:class ["content" nil]}
      ($h1 "Spork")
      (for [post posts]
        (post-card post)))))
```

The macro lowers to public `element` and `fragment` bindings, so refer those names with `markup`. A qualified macro call also works:

```spork
(site.markup
  ($spork-playground {:source "(+ 1 2)"}))
```
