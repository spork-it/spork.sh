---
title: Feeds and sitemaps
description: Generate deterministic XML sitemaps, RSS feeds, and Atom feeds from route-bearing document maps.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 657
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

Sitemap entries are any route-bearing maps. `:lastmod`, `:changefreq`, and `:priority` are optional, and `:sitemap false` excludes an entry.

**Namespaces:** require `spork-site.sitemap` as `sitemap` and `spork-site.feeds` as `feeds`.

```spork
(def sitemap-output
  (sitemap.sitemap "https://example.com" posts))
```

RSS and Atom consume the same document maps. Entries require `:title`, `:route`, and one of `:updated`, `:date`, or `:published`. Drafts and entries with `:feed false` are excluded.

```spork
(def feed-config
  {:title "Example Blog"
   :description "News from Example"
   :url "https://example.com"
   :author "Example Authors"})

(def rss-output (feeds.rss feed-config posts))
(def atom-output (feeds.atom feed-config posts))
```

Feed timestamps derive from content dates, never the wall clock, so repeated builds are byte-for-byte stable. Empty feeds require an explicit `:updated` value.
