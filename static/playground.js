/* Progressive enhancement for <spork-playground>. */
"use strict";

const PROTOCOL_VERSION = 1;
const EVALUATION_TIMEOUT_MS = 5_000;
const STARTUP_TIMEOUT_MS = 30_000;
const SOURCE_LIMIT_BYTES = 64 * 1024;
const TRANSCRIPT_LIMIT_CHARS = 256 * 1024;
const TRANSCRIPT_LIMIT_ENTRIES = 100;
const encoder = new TextEncoder();

class SporkPlayground extends HTMLElement {
  constructor() {
    super();
    this.worker = null;
    this.workerGeneration = 0;
    this.nextRequestId = 1;
    this.pendingRequestId = null;
    this.ready = false;
    this.evaluating = false;
    this.startupTimer = null;
    this.evaluationTimer = null;
    this.transcriptChars = 0;

    this.source = this.querySelector("[data-playground-source]");
    this.runButton = this.querySelector("[data-playground-run]");
    this.stopButton = this.querySelector("[data-playground-stop]");
    this.resetButton = this.querySelector("[data-playground-reset]");
    this.clearButton = this.querySelector("[data-playground-clear]");
    this.retryButton = this.querySelector("[data-playground-retry]");
    this.status = this.querySelector("[data-playground-status]");
    this.transcript = this.querySelector("[data-playground-transcript]");
  }

  connectedCallback() {
    if (
      !this.source ||
      !this.runButton ||
      !this.stopButton ||
      !this.resetButton ||
      !this.clearButton ||
      !this.retryButton ||
      !this.status ||
      !this.transcript
    ) {
      return;
    }
    this.runButton.addEventListener("click", () => this.run());
    this.stopButton.addEventListener("click", () => this.stop());
    this.resetButton.addEventListener("click", () => this.reset());
    this.clearButton.addEventListener("click", () => this.clearTranscript());
    this.retryButton.addEventListener("click", () => this.restart("retry"));
    this.source.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
        event.preventDefault();
        this.run();
      }
    });
    this.classList.add("is-enhanced");
    this.restart("initial");
  }

  disconnectedCallback() {
    this.clearTimers();
    this.worker?.terminate();
    this.worker = null;
  }

  clearTimers() {
    if (this.startupTimer !== null) {
      clearTimeout(this.startupTimer);
      this.startupTimer = null;
    }
    if (this.evaluationTimer !== null) {
      clearTimeout(this.evaluationTimer);
      this.evaluationTimer = null;
    }
  }

  setStatus(text, state) {
    this.status.textContent = text;
    this.status.dataset.state = state;
  }

  updateControls() {
    this.runButton.disabled = !this.ready || this.evaluating;
    this.stopButton.disabled = !this.evaluating;
    this.resetButton.disabled = false;
    this.clearButton.disabled = this.transcript.childElementCount === 0;
  }

  restart(reason) {
    this.clearTimers();
    this.worker?.terminate();
    this.worker = null;
    this.workerGeneration += 1;
    this.pendingRequestId = null;
    this.ready = false;
    this.evaluating = false;
    this.retryButton.hidden = true;
    this.setStatus(
      reason === "initial" ? "loading browser runtime…" : "restarting browser runtime…",
      "loading",
    );
    this.updateControls();

    const generation = this.workerGeneration;
    const workerURL = this.getAttribute("data-worker-url") || "/playground-worker.js";
    let worker;
    try {
      worker = new Worker(workerURL, { type: "module" });
    } catch (error) {
      this.failStartup(error instanceof Error ? error.message : String(error));
      return;
    }
    this.worker = worker;
    worker.onmessage = (event) => {
      if (generation === this.workerGeneration) {
        this.handleMessage(event.data);
      }
    };
    worker.onerror = (event) => {
      if (generation === this.workerGeneration) {
        event.preventDefault();
        this.failStartup(event.message || "The playground worker failed");
      }
    };
    this.startupTimer = setTimeout(() => {
      if (generation === this.workerGeneration && !this.ready) {
        this.worker?.terminate();
        this.worker = null;
        this.failStartup("The browser runtime did not load within 30 seconds");
      }
    }, STARTUP_TIMEOUT_MS);
    worker.postMessage({ version: PROTOCOL_VERSION, type: "initialize" });
  }

  handleMessage(message) {
    if (!message || message.version !== PROTOCOL_VERSION) {
      this.failStartup("The playground worker returned an unsupported response");
      return;
    }
    if (message.type === "status") {
      const labels = {
        "loading-runtime": "checking the Spork runtime…",
        "loading-pyodide": "loading CPython and WebAssembly…",
        "loading-spork": "loading the Spork compiler…",
      };
      this.setStatus(labels[message.state] || "loading browser runtime…", "loading");
      return;
    }
    if (message.type === "ready") {
      if (this.startupTimer !== null) {
        clearTimeout(this.startupTimer);
        this.startupTimer = null;
      }
      this.ready = true;
      this.evaluating = false;
      const version = message.versions?.["spork-lang"];
      this.setStatus(version ? `ready · Spork ${version}` : "ready", "ready");
      this.updateControls();
      return;
    }
    if (message.type === "fatal") {
      this.failStartup(message.error || "The browser runtime failed to load");
      return;
    }
    if (message.type === "result") {
      this.handleResult(message);
    }
  }

  failStartup(error) {
    this.clearTimers();
    this.worker?.terminate();
    this.worker = null;
    this.ready = false;
    this.evaluating = false;
    this.pendingRequestId = null;
    this.setStatus(`runtime unavailable · ${error}`, "error");
    this.retryButton.hidden = false;
    this.updateControls();
  }

  run() {
    if (!this.ready || this.evaluating || !this.worker) {
      return;
    }
    const source = this.source.value;
    if (!source.trim()) {
      this.setStatus("enter a Spork form to run", "ready");
      return;
    }
    if (encoder.encode(source).byteLength > SOURCE_LIMIT_BYTES) {
      this.appendEntry("error", "Source exceeds the 64 KiB playground limit.");
      return;
    }

    const id = this.nextRequestId++;
    this.pendingRequestId = id;
    this.evaluating = true;
    this.setStatus("evaluating…", "evaluating");
    this.appendEntry("source", source);
    this.updateControls();
    this.worker.postMessage({
      version: PROTOCOL_VERSION,
      type: "eval",
      id,
      source,
    });
    const generation = this.workerGeneration;
    this.evaluationTimer = setTimeout(() => {
      if (
        generation === this.workerGeneration &&
        this.pendingRequestId === id &&
        this.evaluating
      ) {
        this.appendEntry(
          "timeout",
          "Evaluation exceeded 5 seconds. The runtime was restarted and session state was cleared.",
        );
        this.restart("timeout");
      }
    }, EVALUATION_TIMEOUT_MS);
  }

  handleResult(message) {
    if (!this.evaluating || message.id !== this.pendingRequestId) {
      return;
    }
    if (this.evaluationTimer !== null) {
      clearTimeout(this.evaluationTimer);
      this.evaluationTimer = null;
    }
    this.pendingRequestId = null;
    this.evaluating = false;
    const result = message.result || {};

    if (result.stdout) {
      this.appendEntry("stdout", result.stdout);
    }
    if (result.stderr) {
      this.appendEntry("stderr", result.stderr);
    }
    if (result.kind === "value" && Object.hasOwn(result, "value")) {
      this.appendEntry("value", result.value);
    } else if (result.kind === "error") {
      const label = result.errorType ? `${result.errorType}: ` : "";
      this.appendEntry("error", `${label}${result.error || "Unknown evaluation error"}`, {
        traceback: result.traceback,
      });
    } else if (result.kind === "incomplete") {
      this.appendEntry("incomplete", "The form is incomplete.");
    } else if (!result.stdout && !result.stderr) {
      this.appendEntry("empty", "definition accepted");
    }

    this.setStatus(`ready · namespace ${result.namespace || "user"}`, "ready");
    this.updateControls();
  }

  stop() {
    if (!this.evaluating) {
      return;
    }
    this.appendEntry(
      "timeout",
      "Evaluation stopped. The runtime was restarted and session state was cleared.",
    );
    this.restart("stop");
  }

  reset() {
    this.appendEntry("system", "Runtime reset. Session state was cleared.");
    this.restart("reset");
  }

  clearTranscript() {
    this.transcript.replaceChildren();
    this.transcriptChars = 0;
    this.updateControls();
  }

  appendEntry(kind, text, options = {}) {
    const entry = document.createElement("article");
    entry.className = `playground-entry playground-entry-${kind}`;
    const label = document.createElement("p");
    label.className = "playground-entry-label";
    const labels = {
      source: "source",
      stdout: "output",
      stderr: "stderr",
      value: "value",
      error: "error",
      incomplete: "incomplete",
      empty: "result",
      timeout: "runtime restarted",
      system: "runtime",
    };
    label.textContent = labels[kind] || kind;
    const body = document.createElement("pre");
    body.textContent = String(text);
    entry.append(label, body);

    if (options.traceback) {
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = "traceback";
      const traceback = document.createElement("pre");
      traceback.textContent = String(options.traceback);
      details.append(summary, traceback);
      entry.append(details);
    }

    const size = entry.textContent.length;
    entry.dataset.characters = String(size);
    this.transcript.append(entry);
    this.transcriptChars += size;
    while (
      this.transcript.childElementCount > TRANSCRIPT_LIMIT_ENTRIES ||
      this.transcriptChars > TRANSCRIPT_LIMIT_CHARS
    ) {
      const first = this.transcript.firstElementChild;
      if (!first) {
        break;
      }
      this.transcriptChars -= Number(first.dataset.characters || 0);
      first.remove();
    }
    this.transcript.scrollTop = this.transcript.scrollHeight;
    this.updateControls();
  }
}

if (!customElements.get("spork-playground")) {
  customElements.define("spork-playground", SporkPlayground);
}
