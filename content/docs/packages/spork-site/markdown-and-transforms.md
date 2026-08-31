---
title: Markdown, highlighting, and transforms
description: Convert CommonMark into shared immutable nodes, apply structural highlighting, and transform trees post-order.
section: package
group: packages
nav-path: [packages, spork-site]
project: spork-site
order: 659
package-version: "0.1.1"
changefreq: monthly
priority: 0.7
---

`spork-site` keeps parsed Markdown in the same immutable node model as authored markup. This page covers syntax highlighting, parser configuration, and post-order structural transformations.

**Namespaces:** require `spork-site.core` as `site`; file-loading options belong to `spork-site.content`.

## Syntax highlighting

Fenced Markdown code gets a `language-*` class during Markdown conversion. Content loading applies Pygments by default and retains the shared structure:

```spork
(def highlighted
  (site.highlight-syntax
    (site.render-markdown "```spork\n(+ 1 2)\n```")))
```

The result remains `Element("pre")` containing `Element("code")`; only Pygments' trusted, escaped span markup is represented as `RawHtml`. Unknown lexer names leave the original code block unchanged.

## Markdown and transformations

`spork-site.markdown` parses CommonMark into `Fragment`, `Element`, `Text`, and explicit `RawHtml` values, never an opaque HTML string:

```spork
(def ast (site.parse-markdown source))
(def nodes (site.markdown-ast-to-nodes ast))
(def content (site.render-markdown source))
```

With the default parser, inline and block HTML tokens become explicit `RawHtml` nodes. Surrounding text remains escaped `Text`. Use `(site.make-markdown-parser false)` to disable Markdown raw HTML.

The parser is a `markdown-it-py` `MarkdownIt` instance, so a site may enable supported extensions explicitly. For example, this enables structural pipe tables rather than treating their source as plain paragraph text:

```spork
(def parser (site.make-markdown-parser))
(parser.enable "table")
(def content (site.render-markdown-with parser source))
```

Pass the same parser as `:parser` to `content.load-markdown` or `content.load-documents` when loading files. Extensions still convert into the shared node model; they do not introduce an opaque HTML-rendering path.

`transform` walks a node tree depth-first and invokes a function post-order after transformed children have been installed in a fresh immutable parent:

```spork
(defn mark-heading [node]
  (if (and (isinstance node site.Element)
           (contains? #{"h1" "h2" "h3" "h4" "h5" "h6"} node.tag))
    (site.Element node.tag
                  (assoc node.attrs "data-heading" true)
                  node.children)
    node))

(def transformed (site.transform content mark-heading))
```

A transform may return a node, `nil` to remove it, a deterministic sequence to splice through a fragment, or a printable scalar to create a `Text` node.
