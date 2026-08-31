# spork.sh

The source for the public Spork website at [spork.sh](https://spork.sh). It is a source-only Spork project deployed to GitHub Pages—not a Python distribution—and the canonical production consumer of [`spork-site`](https://github.com/spork-it/spork-site).

The site also publishes the reviewed shell installer at `https://spork.sh/install`. The short `/get/` page provides the direct installation path and links to the complete getting-started guide. `site.spork` calculates the installer SHA-256 while rendering that detailed guide and emits the matching `https://spork.sh/install.sha256` verification file.

The site combines:

- a Spork-authored application shell, navigation, layouts, and reusable components;
- structural Markdown documentation under `content/`;
- metadata-derived hierarchical navigation, breadcrumbs, heading permalinks, page tables of contents, and hierarchy-scoped previous/next links;
- a deterministic browser-side documentation search index;
- generated `sitemap.xml` and `robots.txt` output;
- a system-aware, user-selectable light/dark theme;
- deterministic static asset discovery and builds; and
- full-rebuild development serving with browser reload.

## Work locally

Install the compatible project toolchain and dependencies once:

```bash
spork sync
```

Then validate or serve the site from any directory beneath the project root:

```bash
spork check
spork test
spork site check
spork site routes
spork site serve --open
```

A production build writes to `public/`:

```bash
spork site build
python tools/verify_docs.py
python tools/verify_site.py
```

`verify_docs.py` executes Spork and Python fences by default and syntax-checks shell fences. A deliberately partial or environment-dependent example must carry an adjacent `<!-- verify-docs: compile=fragment -->` or `<!-- verify-docs: skip=reason -->` marker; unclassified failures stop CI. `verify_site.py` checks all generated internal links, form actions, assets, fragments, and HTML IDs.

Documentation pages declare `section`, `group`, `project`, and `order` front matter. Pages below a navigation group may also declare an arbitrarily deep `nav-path`; every path level has one centrally validated label, order, and landing route. `src/spork_sh/docs.spork` enables structural Markdown tables, validates metadata, derives the navigation tree and breadcrumbs, decorates structural headings, checks source links and fragments, and emits `/docs/search.json`. Package labels come from one immutable documented-version map in that namespace. The split language, standard-library, and tooling references under `content/docs/reference/` are canonical for the Spork 0.6.0 language, built-in APIs, and project CLI. Package guides and contracts live under `content/docs/packages/`; maintained editor and example walkthroughs live under `content/docs/editors/` and `content/docs/examples/`.

Development serving builds isolated temporary generations. It switches traffic only after a complete successful rebuild, retains the last successful generation after an error, and injects browser reload support only into served HTML. Generated production files are not modified by the reload client.

## Deployment

`.github/workflows/pages.yml` validates and builds every change targeting `main`. A push to `main` uploads `public/` as a GitHub Pages artifact and deploys it through the protected `github-pages` environment. Pull requests run the same checks without publishing.

The custom domain is retained in `static/CNAME` and copied into every production generation. GitHub Pages must be configured to publish through **GitHub Actions** with `spork.sh` as the custom domain.

No wheel or source distribution is built for this repository. Its only release artifact is the complete static site.

## Project structure

```text
spork.sh/
├── .github/workflows/pages.yml
├── spork.it
├── content/
│   ├── index.md
│   ├── 404.md
│   ├── get/
│   └── docs/
├── src/spork_sh/
│   ├── docs.spork
│   └── site.spork
├── static/
│   ├── CNAME
│   ├── docs-search.js
│   ├── favicon.svg
│   ├── install
│   ├── site.css
│   └── theme.js
├── tools/
│   ├── verify_docs.py
│   └── verify_site.py
└── tests/
    ├── install_test.sh
    └── spork_sh/
        ├── docs_test.spork
        └── site_test.spork
```

`spork-sh.site:make-site` is loaded directly from source by the `spork site` command provider declared by the installed `spork-site` dependency. The project does not need an ahead-of-time Python build, a bespoke website executable, or Python package publication.
