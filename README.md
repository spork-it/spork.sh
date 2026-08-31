# spork.sh

This repository contains the source for [spork.sh](https://spork.sh), the homepage and canonical live documentation for Spork, a Lisp hosted on CPython.

The site documents the language, standard library, project tooling, editors, examples, and the associated `spork-lang`, `spork-runtime`, `spork-pds`, `spork-state`, and `spork-site` packages. It also publishes the installer at [`/install`](https://spork.sh/install) and its generated checksum.

The website is an ordinary source-only Spork project built with [`spork-site`](https://github.com/spork-it/spork-site). It is deployed to GitHub Pages and is not a Python distribution.

## Work locally

Synchronize the project environment:

```bash
spork sync
```

Validate or serve the site:

```bash
spork check
spork test
python tools/verify_docs.py
spork site check
spork site serve --open
```

Build and verify the static output:

```bash
spork site build
python tools/verify_site.py
```

## Deployment

`.github/workflows/pages.yml` validates pull requests and deploys pushes to `main`. The custom domain is retained through `static/CNAME`.
