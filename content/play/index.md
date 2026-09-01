---
title: Play with Spork
description: Compile and run Spork locally in your browser with CPython and WebAssembly.
changefreq: monthly
priority: 0.9
---

The playground runs the real Spork compiler, runtime, and persistent collections inside browser-hosted CPython. Your source stays in this browser; there is no Spork evaluation server.

<spork-playground data-worker-url="/playground-worker.js?v=0.1.0">
  <div class="playground-editor">
    <div class="playground-editor-heading">
      <label for="playground-source">Spork source</label>
      <span>Ctrl/⌘ + Enter to run</span>
    </div>
    <textarea id="playground-source" data-playground-source spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="playground-session-note">(defn square [n]&#10;  (* n n))&#10;&#10;(vec (map square [1 2 3 4 5]))</textarea>
  </div>
  <div class="playground-controls" aria-label="Playground controls">
    <button type="button" data-playground-run disabled>run</button>
    <button type="button" data-playground-stop disabled>stop</button>
    <button type="button" data-playground-reset>reset runtime</button>
    <button type="button" data-playground-clear disabled>clear output</button>
    <button type="button" data-playground-retry hidden>retry loading</button>
  </div>
  <p class="playground-status" data-playground-status data-state="loading" role="status" aria-live="polite">JavaScript is required to start the browser runtime.</p>
  <div class="playground-transcript" data-playground-transcript aria-label="Playground output" tabindex="0"></div>
  <noscript><p class="playground-fallback">Enable JavaScript to use the playground, or <a href="/get/">install Spork</a> to run this source locally.</p></noscript>
</spork-playground>

<p id="playground-session-note" class="playground-note">Definitions remain available between runs. Stop, timeout, Reset, page reload, or a worker failure starts a fresh interpreter and clears them.</p>

## Browser runtime boundaries

The first visit downloads CPython and WebAssembly and can take several seconds. The Spork package archive is small, but the browser runtime uses substantially more network data and memory.

The playground is intended for short experiments. It does not provide project files, project commands, subprocesses, nREPL, persistent sessions, or arbitrary package installation. Python standard-library behavior can also differ under WebAssembly.

Code executes locally in a Web Worker, which keeps ordinary evaluation off the page's main thread. A worker is not a hard security or memory sandbox: deliberately hostile code can still consume browser resources or use worker network APIs. Do not use the playground to run untrusted source.
