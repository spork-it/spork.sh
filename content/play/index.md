---
title: Play with Spork
description: Compile and run Spork locally in your browser with CPython and WebAssembly.
changefreq: monthly
priority: 0.9
---

<spork-playground data-worker-url="/playground-worker.js?v=0.1.1">
  <header class="playground-toolbar">
    <div class="playground-title">
      <h1>Spork playground</h1>
      <p class="playground-status" data-playground-status data-state="loading" role="status" aria-live="polite">JavaScript is required to start the browser runtime.</p>
    </div>
    <div class="playground-controls" aria-label="Playground controls">
      <button class="playground-run" type="button" data-playground-run disabled>run <span>⌘↵</span></button>
      <button type="button" data-playground-stop disabled>stop</button>
      <button type="button" data-playground-reset>reset runtime</button>
      <button type="button" data-playground-retry hidden>retry loading</button>
    </div>
  </header>
  <div class="playground-workspace">
    <section class="playground-panel playground-editor" aria-labelledby="playground-editor-title">
      <div class="playground-panel-heading">
        <h2 id="playground-editor-title"><label for="playground-source">editor</label></h2>
        <span>Ctrl/⌘ + Enter to run</span>
      </div>
      <div class="playground-code-editor">
        <pre class="playground-highlight" data-playground-highlight aria-hidden="true"><code></code></pre>
        <textarea id="playground-source" data-playground-source wrap="off" spellcheck="false" autocapitalize="off" autocomplete="off" aria-describedby="playground-session-note">(defn square [n]&#10;  (* n n))&#10;&#10;(vec (map square [1 2 3 4 5]))</textarea>
      </div>
    </section>
    <section class="playground-panel playground-output" aria-labelledby="playground-output-title">
      <div class="playground-panel-heading">
        <h2 id="playground-output-title">output</h2>
        <button type="button" data-playground-clear disabled>clear</button>
      </div>
      <div class="playground-transcript" data-playground-transcript role="log" aria-live="polite" aria-relevant="additions" tabindex="0"></div>
    </section>
  </div>
  <p id="playground-session-note" class="visually-hidden">Definitions remain available between runs. Resetting or stopping the runtime clears them.</p>
  <noscript><p class="playground-fallback">Enable JavaScript to use the playground, or <a href="/get/">install Spork</a> to run this source locally.</p></noscript>
</spork-playground>

<details class="playground-about">
  <summary>about this playground and its browser runtime</summary>
  <div>
    <p>The real Spork compiler, runtime, and persistent collections run locally inside browser-hosted CPython and WebAssembly. Your source is not sent to a Spork evaluation server.</p>
    <p>Definitions remain available between runs. Stop, timeout, reset, page reload, or a worker failure starts a fresh interpreter and clears them.</p>
    <p>The first visit downloads CPython and WebAssembly and can take several seconds. The playground is intended for short experiments and does not provide project files, project commands, subprocesses, nREPL, persistent sessions, or arbitrary package installation.</p>
    <p>Code runs in a Web Worker to keep evaluation off the page's main thread. A worker is not a hard security or memory sandbox. Do not run untrusted source.</p>
  </div>
</details>
