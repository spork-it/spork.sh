---
title: GitHub stars
description: Profile network calls and rank API results with a macro, matching, and sorted-for.
section: example
group: examples
project: spork-lang
order: 830
package-version: "0.6.0"
changefreq: monthly
priority: 0.6
---

This project makes unauthenticated GitHub API requests. It requires network access, is subject to rate limits, and prints values that change over time.

## Manifest

```spork
;; Spork Project Manifest
;; See https://spork.sh/docs/reference/tooling/ for manifest documentation

{:name "stars"
 :version "0.1.0"

 ;; Dependencies (pip-style specifications)
 :dependencies ["requests>=2.32,<3"]

 ;; Source code locations
 :source-paths ["src"]

 ;; Entry point for 'spork run'
 :main "stars.core:main"}
```

## Source

<!-- verify-docs: skip=external-network-dependency -->
```spork
(ns stars.core
  (:import
    [requests]
    [time :as t]))

;; Simple profiling macro using Python's time.perf_counter
(defmacro profile [label & body]
  `(let [start# (t.perf_counter)
         result# (do ~@body)
         end# (t.perf_counter)
         elapsed# (- end# start#)]
     (print (+ ~label " took " (str elapsed#) "s"))
     result#))

;; Fetch the star count for a given GitHub repo full name
(defn ^int fetch-stars [^str full-name]
  (let [resp (requests.get (+ "https://api.github.com/repos/" full-name)
                           *{:timeout 10})]
    (match resp.status_code
      200 (get (resp.json) "stargazers_count")
      404 0                                     ; missing repo → 0 stars
      _   (throw (RuntimeError "GitHub API error")))))

;; Get top repos by star count
(defn top-repos [names]
  ;; Return a persistent sorted collection of maps
  (sorted-for [full-name names]
    {:name full-name
     :stars (fetch-stars full-name)}
    :key :stars :reverse true))

(defn main []
  (let [repos ["pallets/flask"
               "django/django"
               "tiangolo/fastapi"
               "psf/requests"]
        ranked (profile "GitHub fetch" (top-repos repos))]
    (doseq [row ranked]
      (let [{:keys [name stars]} row]
        (print stars "-" name)))))

;; Example output (timing and star counts vary):
; GitHub fetch took 0.1801389280008152s
; 92823 - tiangolo/fastapi
; 86079 - django/django
; 70890 - pallets/flask
; 53551 - psf/requests
```

Run it from the project directory:

```bash
spork sync
spork run
```

The example combines [macros](/docs/reference/language/macros/), [pattern matching](/docs/reference/language/pattern-matching/), and [sorted iteration](/docs/reference/language/forms-and-control-flow/#sorted-for-expression).
