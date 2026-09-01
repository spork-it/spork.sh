/* Browser-hosted Spork runtime. All Python work stays in this worker. */
"use strict";

const PROTOCOL_VERSION = 1;
const RUNTIME_MANIFEST_URL = "/playground-runtime/runtime.json";
const SOURCE_LIMIT_BYTES = 64 * 1024;
const encoder = new TextEncoder();

let ready = false;
let initializing = false;
let evaluateSource = null;

function post(type, value = {}) {
  self.postMessage({ version: PROTOCOL_VERSION, type, ...value });
}

function errorText(error) {
  if (error instanceof Error) {
    return error.message || error.name;
  }
  return String(error);
}

function requireObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error(`${label} is not an object`);
  }
  return value;
}

function validateRuntime(value) {
  const runtime = requireObject(value, "runtime manifest");
  const pyodide = requireObject(runtime.pyodide, "runtime.pyodide");
  const bundle = requireObject(runtime.bundle, "runtime.bundle");
  const packages = requireObject(runtime.packages, "runtime.packages");
  if (runtime.format !== 1) {
    throw new Error(`Unsupported runtime format ${runtime.format}`);
  }
  for (const [label, item] of [
    ["pyodide.version", pyodide.version],
    ["pyodide.indexURL", pyodide.indexURL],
    ["bundle.url", bundle.url],
    ["bundle.sha256", bundle.sha256],
  ]) {
    if (typeof item !== "string" || !item) {
      throw new Error(`${label} is missing`);
    }
  }
  if (!Number.isSafeInteger(bundle.bytes) || bundle.bytes <= 0) {
    throw new Error("bundle.bytes is invalid");
  }
  if (!/^[0-9a-f]{64}$/.test(bundle.sha256)) {
    throw new Error("bundle.sha256 is invalid");
  }
  const expectedIndexPath = `/pyodide/v${pyodide.version}/full/`;
  const indexURL = new URL(pyodide.indexURL);
  if (
    indexURL.protocol !== "https:" ||
    indexURL.hostname !== "cdn.jsdelivr.net" ||
    indexURL.pathname !== expectedIndexPath
  ) {
    throw new Error("Pyodide URL does not match the pinned jsDelivr release");
  }
  const bundleURL = new URL(bundle.url, self.location.href);
  if (bundleURL.origin !== self.location.origin) {
    throw new Error("The Spork bundle must be same-origin");
  }
  for (const name of ["spork-lang", "spork-runtime", "spork-pds"]) {
    if (typeof packages[name] !== "string" || !packages[name]) {
      throw new Error(`runtime package ${name} is missing`);
    }
  }
  return runtime;
}

async function fetchJSON(url) {
  const response = await fetch(url, { cache: "no-cache" });
  if (!response.ok) {
    throw new Error(`Cannot load ${url}: HTTP ${response.status}`);
  }
  return response.json();
}

async function fetchBundle(runtime) {
  const response = await fetch(runtime.bundle.url, { cache: "force-cache" });
  if (!response.ok) {
    throw new Error(`Cannot load Spork runtime: HTTP ${response.status}`);
  }
  const buffer = await response.arrayBuffer();
  if (buffer.byteLength !== runtime.bundle.bytes) {
    throw new Error(
      `Spork runtime size mismatch: expected ${runtime.bundle.bytes}, got ${buffer.byteLength}`,
    );
  }
  const digest = await crypto.subtle.digest("SHA-256", buffer);
  const actual = Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, "0"),
  ).join("");
  if (actual !== runtime.bundle.sha256) {
    throw new Error("Spork runtime SHA-256 verification failed");
  }
  return new Uint8Array(buffer);
}

async function initialize() {
  initializing = true;
  const started = performance.now();
  post("status", { state: "loading-runtime" });
  const runtime = validateRuntime(await fetchJSON(RUNTIME_MANIFEST_URL));

  post("status", { state: "loading-pyodide" });
  const pyodideModule = await import(`${runtime.pyodide.indexURL}pyodide.mjs`);
  if (typeof pyodideModule.loadPyodide !== "function") {
    throw new Error("Pinned Pyodide module did not export loadPyodide");
  }
  const pyodide = await pyodideModule.loadPyodide({
    indexURL: runtime.pyodide.indexURL,
  });
  const pyodideLoaded = performance.now();

  post("status", { state: "loading-spork" });
  const archive = await fetchBundle(runtime);
  const archivePath = "/tmp/spork-playground.zip";
  pyodide.FS.writeFile(archivePath, archive);
  try {
    pyodide.runPython(`
import json as _playground_json
import sys as _playground_sys
import zipfile as _playground_zipfile

with _playground_zipfile.ZipFile('/tmp/spork-playground.zip') as _playground_bundle:
    for _playground_member in _playground_bundle.infolist():
        _playground_parts = _playground_member.filename.split('/')
        if (_playground_member.filename.startswith('/') or
                '..' in _playground_parts):
            raise RuntimeError('Unsafe path in Spork playground bundle')
    _playground_bundle.extractall('/spork-playground')
_playground_sys.path.insert(0, '/spork-playground')

from spork_playground_bridge import evaluate as _spork_playground_evaluate
from spork_playground_bridge import runtime_info as _spork_playground_runtime_info
`);
  } finally {
    pyodide.FS.unlink(archivePath);
  }

  evaluateSource = pyodide.globals.get("_spork_playground_evaluate");
  const runtimeInfoFunction = pyodide.globals.get("_spork_playground_runtime_info");
  let runtimeInfo;
  try {
    runtimeInfo = JSON.parse(runtimeInfoFunction());
  } finally {
    runtimeInfoFunction.destroy();
  }
  for (const [name, version] of Object.entries(runtime.packages)) {
    if (runtimeInfo.packages[name] !== version) {
      throw new Error(
        `Loaded ${name} ${runtimeInfo.packages[name]}, expected ${version}`,
      );
    }
  }
  if (!/spork_pds\.cpython-\d+-wasm32-emscripten\.so$/.test(runtimeInfo.extension)) {
    throw new Error(`Unexpected spork-pds extension: ${runtimeInfo.extension}`);
  }

  ready = true;
  initializing = false;
  const finished = performance.now();
  post("ready", {
    versions: {
      ...runtimeInfo.packages,
      pyodide: runtime.pyodide.version,
    },
    timing: {
      pyodideMs: Math.round(pyodideLoaded - started),
      sporkMs: Math.round(finished - pyodideLoaded),
      totalMs: Math.round(finished - started),
    },
  });
}

function evaluate(message) {
  if (!ready || evaluateSource === null) {
    throw new Error("Spork runtime is not ready");
  }
  if (!Number.isSafeInteger(message.id)) {
    throw new Error("Evaluation request ID is invalid");
  }
  if (typeof message.source !== "string") {
    throw new Error("Evaluation source must be a string");
  }
  if (encoder.encode(message.source).byteLength > SOURCE_LIMIT_BYTES) {
    post("result", {
      id: message.id,
      result: {
        kind: "error",
        errorType: "SourceLimitError",
        error: `Source exceeds the ${SOURCE_LIMIT_BYTES}-byte playground limit`,
        stdout: "",
        stderr: "",
        namespace: "user",
        truncated: [],
      },
    });
    return;
  }
  const result = JSON.parse(evaluateSource(message.source));
  post("result", { id: message.id, result });
}

self.onmessage = (event) => {
  const message = event.data;
  if (!message || message.version !== PROTOCOL_VERSION) {
    post("fatal", { phase: "protocol", error: "Unsupported worker protocol" });
    return;
  }
  if (message.type === "initialize") {
    if (ready || initializing) {
      return;
    }
    initialize().catch((error) => {
      initializing = false;
      post("fatal", { phase: "initialize", error: errorText(error) });
    });
    return;
  }
  if (message.type === "eval") {
    try {
      evaluate(message);
    } catch (error) {
      post("result", {
        id: message.id,
        result: {
          kind: "error",
          errorType: "PlaygroundBridgeError",
          error: errorText(error),
          stdout: "",
          stderr: "",
          namespace: "user",
          truncated: [],
        },
      });
    }
  }
};

self.onunhandledrejection = (event) => {
  event.preventDefault();
  post("fatal", { phase: "worker", error: errorText(event.reason) });
};
