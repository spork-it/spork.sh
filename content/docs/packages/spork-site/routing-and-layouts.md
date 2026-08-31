---
title: Routing and layouts
description: Build components and layouts as ordinary functions and generate conflict-checked clean routes.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 654
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

Components and layouts are ordinary functions returning node-like values.

**Namespaces:** require `spork-site.routing` as `routing` and refer `element`, `fragment`, and `markup` from `spork-site.core`.

```spork
(defn document-layout [document]
  (markup
    ($html {:lang "en"}
      ($head
        ($meta {:charset "utf-8"})
        ($meta {:name "viewport"
                :content "width=device-width, initial-scale=1"})
        ($title (:title document))
        ($link {:rel "stylesheet" :href "/site.css"}))
      ($body
        ($main {:class "prose"}
          ($h1 (:title document))
          (:content document))))))

(def content-pages
  (routing.pages-for posts document-layout))
```

`pages-for` is equivalent to an eager generated route expression:

<!-- verify-docs: compile=preceding-definition -->
```spork
(for [document posts]
  (routing.page (:route document)
                (document-layout document)))
```

`routing.page` marks structural content for HTML serialization during build planning; ordinary text and attribute values are escaped. Use `routing.output-file` for already serialized text or bytes such as `robots.txt`, XML, or JSON.

Duplicate canonical routes, page/asset collisions, and file/directory output conflicts fail before output is cleaned or written.
