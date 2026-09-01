# spork.sh

This repository contains the source for [spork.sh](https://spork.sh), the homepage and canonical live documentation for Spork, a Lisp hosted on CPython.

The site documents the language, standard library, project tooling, editors, examples, and the associated `spork-lang`, `spork-runtime`, `spork-pds`, `spork-state`, and `spork-site` packages. It also publishes the installer at [`/install`](https://spork.sh/install) and its generated checksum.

The website is an ordinary source-only Spork project built with [`spork-site`](https://github.com/spork-it/spork-site). It is deployed to GitHub Pages and is not a Python distribution. During deployment, CI builds the browser playground runtime from a digest-locked `spork-pds` source distribution and the published `spork-runtime` and `spork-lang` wheels; the generated blob is staged directly into the Pages artifact and is not committed under `static/`.

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

Ordinary local site builds intentionally omit the generated WebAssembly package blob. Test the complete playground from a Pages artifact or deployed build.

## Build the browser runtime

The Pages workflow installs the exact tools declared by `tools/playground-lock.json` and runs:

```bash
python -m pip install \
  "pyodide-build==0.39.0" \
  "setuptools==84.0.0" \
  "wheel==0.48.0"
pyodide xbuildenv install 314.0.6
pyodide xbuildenv install-emscripten
python tools/build_playground_runtime.py
spork site build
cp -R build/playground-runtime/assets/playground-runtime public/
python tools/verify_playground_assets.py
```

The builder downloads hash-locked published artifacts, cross-compiles `spork-pds`, and writes the deterministic bundle beneath ignored `build/`. CI stages that directory into `public/` before verifying and uploading the complete Pages artifact.

## Deployment

`.github/workflows/pages.yml` validates pull requests and deploys pushes to `main`. The custom domain is retained through `static/CNAME`.
