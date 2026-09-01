---
title: std.string
description: String joining, splitting, trimming, searching, replacing, padding, and line handling.
section: reference
group: standard-library
project: spork-lang
order: 480
package-version: "0.6.1"
changefreq: monthly
priority: 0.7
---

The `std.string` namespace wraps common Python string operations with Spork-friendly names and argument order. Require it explicitly; ordinary Python string methods remain available through direct interoperability.

**Usage:** `(ns my-file (:require [std.string :as str]))`

## `str.join`
Joins a collection of strings with `sep`. Non-string elements raise Python's `TypeError`.
```spork
(str.join ", " ["a" "b" "c"])      ; => "a, b, c"
(str.join "-" ["1" "2" "3"])       ; => "1-2-3"
(str.join "" ["a" "b" "c"])        ; => "abc"
(str.join "\n" ["line1" "line2"])  ; => "line1\nline2"
```

## `str.split`
Splits a string on an explicit separator and returns a persistent vector. Unlike Python's zero-argument `str.split`, the separator is required.
```spork
(str.split "a,b,c" ",")           ; => ["a" "b" "c"]
(str.split "hello world" " ")     ; => ["hello" "world"]
(str.split "a-b-c-d" "-")         ; => ["a" "b" "c" "d"]
```

## `str.trim` / `str.ltrim` / `str.rtrim`
Remove leading and/or trailing whitespace. These functions do not take a custom character set.
```spork
(str.trim "  hello  ")            ; => "hello"
(str.trim "\n\thello\n\t")        ; => "hello"
(str.ltrim "  hello  ")           ; => "hello  "
(str.rtrim "  hello  ")           ; => "  hello"
```

## `str.upper` / `str.lower`
Case conversion.
```spork
(str.upper "hello")               ; => "HELLO"
(str.upper "Hello World")         ; => "HELLO WORLD"
(str.lower "HELLO")               ; => "hello"
(str.lower "Hello World")         ; => "hello world"
```

## `str.capitalize` / `str.title`
Capitalization.
```spork
(str.capitalize "hello world")    ; => "Hello world"
(str.capitalize "HELLO")          ; => "Hello"
(str.title "hello world")         ; => "Hello World"
(str.title "the quick brown fox") ; => "The Quick Brown Fox"
```

## `str.starts-with?` / `str.ends-with?`
Prefix/suffix checks.
```spork
(str.starts-with? "hello" "he")   ; => true
(str.starts-with? "hello" "lo")   ; => false
(str.ends-with? "hello" "lo")     ; => true
(str.ends-with? "hello" "he")     ; => false
```

## `str.includes?`
Substring check.
```spork
(str.includes? "hello" "ell")     ; => true
(str.includes? "hello" "xyz")     ; => false
(str.includes? "hello" "")        ; => true
```

## `str.blank?`
Checks if nil, empty, or whitespace only.
```spork
(str.blank? nil)                  ; => true
(str.blank? "")                   ; => true
(str.blank? "   ")                ; => true
(str.blank? "\n\t")               ; => true
(str.blank? "hi")                 ; => false
(str.blank? "  hi  ")             ; => false
```

## `str.replace` / `str.replace-first`
String replacement.
```spork
(str.replace "abab" "a" "x")      ; => "xbxb"
(str.replace "hello" "l" "L")     ; => "heLLo"
(str.replace-first "abab" "a" "x"); => "xbab"
(str.replace-first "hello" "l" "L") ; => "heLlo"
```

## `str.reverse`
Reverses a string.
```spork
(str.reverse "hello")             ; => "olleh"
(str.reverse "abc")               ; => "cba"
(str.reverse "")                  ; => ""
```

## `str.repeat`
Repeats string n times.
```spork
(str.repeat "ab" 3)               ; => "ababab"
(str.repeat "-" 10)               ; => "----------"
(str.repeat "x" 0)                ; => ""
```

## `str.substring-count`
Counts non-overlapping occurrences of a substring.
```spork
(str.substring-count "abab" "ab") ; => 2
(str.substring-count "aaa" "a")   ; => 3
(str.substring-count "aaa" "aa")  ; => 1
(str.substring-count "hello" "l") ; => 2
(str.substring-count "hello" "x") ; => 0
```

## `str.index-of` / `str.last-index-of`
Find substring position.
```spork
(str.index-of "hello" "l")        ; => 2
(str.index-of "hello" "x")        ; => nil
(str.index-of "hello" "lo")       ; => 3
(str.last-index-of "hello" "l")   ; => 3
(str.last-index-of "abcabc" "bc") ; => 4
```

## `str.substring`
Extracts a substring using Python slice semantics: the start is inclusive, the end is exclusive, negative indices are accepted, and out-of-range bounds are clamped.
```spork
(str.substring "hello" 1 4)       ; => "ell"
(str.substring "hello" 0 2)       ; => "he"
(str.substring "hello" 2 5)       ; => "llo"
```

## `str.char-at`
Returns the one-character slice from `idx` to `idx + 1`. It is intended for nonnegative indices; an out-of-range index returns `""` rather than raising `IndexError`.
```spork
(str.char-at "hello" 0)           ; => "h"
(str.char-at "hello" 1)           ; => "e"
(str.char-at "hello" 4)           ; => "o"
(str.char-at "hello" 9)           ; => ""
```

## `str.length`
String length.
```spork
(str.length "hello")              ; => 5
(str.length "")                   ; => 0
(str.length "日本語")              ; => 3
```

## `str.pad-left` / `str.pad-right` / `str.center`
Pad to at least the requested width. The padding argument must be exactly one character; strings already at least as wide are unchanged.
```spork
(str.pad-left "hi" 5 " ")         ; => "   hi"
(str.pad-left "42" 5 "0")         ; => "00042"
(str.pad-right "hi" 5 " ")        ; => "hi   "
(str.pad-right "hi" 5 ".")        ; => "hi..."
(str.center "hi" 6 "-")           ; => "--hi--"
(str.center "x" 5 " ")            ; => "  x  "
```

## `str.lines`
Splits at line boundaries, removes the line endings, and returns a vector. A trailing line break does not add a final empty string.
```spork
(str.lines "a\nb\nc")             ; => ["a" "b" "c"]
(str.lines "line1\nline2\nline3") ; => ["line1" "line2" "line3"]
(str.lines "single")              ; => ["single"]
(str.lines "a\n")                  ; => ["a"]
```
