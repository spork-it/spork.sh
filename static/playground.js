/* Progressive enhancement for <spork-playground>. */
"use strict";

const PROTOCOL_VERSION = 1;
const EVALUATION_TIMEOUT_MS = 5_000;
const STARTUP_TIMEOUT_MS = 30_000;
const SOURCE_LIMIT_BYTES = 64 * 1024;
const TRANSCRIPT_LIMIT_CHARS = 256 * 1024;
const TRANSCRIPT_LIMIT_ENTRIES = 100;
const encoder = new TextEncoder();

const SPECIAL_FORMS = new Set([
  "and", "case", "catch", "cond", "def", "defmacro", "defn", "do", "else",
  "finally", "fn", "for", "if", "import", "let", "loop", "match", "ns", "or",
  "quote", "recur", "require", "set!", "throw", "try", "var", "when", "while",
]);
const BUILTINS = new Set([
  "*", "+", "-", "/", "<", "<=", "=", ">", ">=", "assoc", "conj", "cons",
  "contains?", "count", "dissoc", "empty?", "filter", "first", "fmt", "get",
  "into", "keys", "map", "next", "not", "nth", "print", "println", "reduce",
  "rest", "seq", "str", "update", "vals", "vec", "vector", "zipmap",
]);
const LITERALS = new Set(["false", "nil", "true"]);
const NUMBER_TOKEN = /^[+-]?(?:0[xX][0-9a-fA-F]+|0[bB][01]+|0[oO][0-7]+|(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)$/;

function appendToken(parent, text, kind = "") {
  if (!kind) {
    parent.append(document.createTextNode(text));
    return;
  }
  const token = document.createElement("span");
  token.className = `tok-${kind}`;
  token.textContent = text;
  parent.append(token);
}

function tokenKind(token) {
  if (SPECIAL_FORMS.has(token)) return "form";
  if (BUILTINS.has(token)) return "builtin";
  if (LITERALS.has(token)) return "literal";
  if (NUMBER_TOKEN.test(token)) return "number";
  if (token.startsWith(":")) return "keyword";
  if (token.startsWith("\\")) return "string";
  return "";
}

function highlightSpork(source, target) {
  const fragment = document.createDocumentFragment();
  let index = 0;
  while (index < source.length) {
    const character = source[index];

    if (/\s/.test(character) || character === ",") {
      let end = index + 1;
      while (end < source.length && (/\s/.test(source[end]) || source[end] === ",")) {
        end += 1;
      }
      appendToken(fragment, source.slice(index, end));
      index = end;
      continue;
    }

    if (character === ";") {
      let end = source.indexOf("\n", index);
      if (end === -1) end = source.length;
      appendToken(fragment, source.slice(index, end), "comment");
      index = end;
      continue;
    }

    if (character === '"' || (character === "#" && source[index + 1] === '"')) {
      let end = index + (character === "#" ? 2 : 1);
      let escaped = false;
      while (end < source.length) {
        const current = source[end++];
        if (current === '"' && !escaped) break;
        if (current === "\\" && !escaped) {
          escaped = true;
        } else {
          escaped = false;
        }
      }
      appendToken(fragment, source.slice(index, end), character === "#" ? "regex" : "string");
      index = end;
      continue;
    }

    if ("()[]{}".includes(character)) {
      appendToken(fragment, character, "delimiter");
      index += 1;
      continue;
    }

    if ("'`~@^".includes(character) || (character === "#" && "_{(".includes(source[index + 1] || ""))) {
      const length = (character === "~" && source[index + 1] === "@") || character === "#" ? 2 : 1;
      appendToken(fragment, source.slice(index, index + length), "reader");
      index += length;
      continue;
    }

    let end = index + 1;
    while (
      end < source.length &&
      !/\s/.test(source[end]) &&
      !"()[]{}\";'`~@^,".includes(source[end])
    ) {
      end += 1;
    }
    const token = source.slice(index, end);
    appendToken(fragment, token, tokenKind(token));
    index = end;
  }
  target.replaceChildren(fragment);
}

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
    this.highlight = this.querySelector("[data-playground-highlight]");
    this.highlightCode = this.highlight?.querySelector("code");
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
      !this.highlight ||
      !this.highlightCode ||
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
    this.source.addEventListener("input", () => this.renderHighlight());
    this.source.addEventListener("scroll", () => this.syncHighlightScroll());
    this.source.addEventListener("keydown", (event) => this.handleEditorKeydown(event));
    this.classList.add("is-enhanced");
    this.renderHighlight();
    this.restart("initial");
  }

  disconnectedCallback() {
    this.clearTimers();
    this.worker?.terminate();
    this.worker = null;
  }

  handleEditorKeydown(event) {
    if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
      event.preventDefault();
      this.run();
      return;
    }
    if (event.key === "Tab" && !event.shiftKey && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();
      this.source.setRangeText(
        "  ",
        this.source.selectionStart,
        this.source.selectionEnd,
        "end",
      );
      this.renderHighlight();
    }
  }

  renderHighlight() {
    highlightSpork(this.source.value, this.highlightCode);
    this.syncHighlightScroll();
  }

  syncHighlightScroll() {
    this.highlight.scrollTop = this.source.scrollTop;
    this.highlight.scrollLeft = this.source.scrollLeft;
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
      stdout: "output",
      stderr: "stderr",
      value: "value",
      error: "error",
      incomplete: "incomplete",
      timeout: "runtime restarted",
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
