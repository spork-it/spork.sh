---
title: Lexical syntax
description: Understand whitespace, comments, delimiters, atomic literals, symbols, and identifier normalization.
section: reference
group: language
project: spork-lang
order: 100
package-version: "0.6.3"
changefreq: monthly
priority: 0.7
---

Spork source is a sequence of forms. The tokenizer separates atoms and delimiters, and the reader turns them into lists, collection literals, symbols, keywords, and scalar values. Prefix forms that change how the reader interprets the next form are documented together in [reader macros](/docs/reference/language/reader-macros/).

## Whitespace and comments

Spaces, tabs, carriage returns, and newlines separate forms. Newlines do not terminate statements; balanced delimiters determine where a form ends. Unlike in some Lisps, a comma is not whitespace and should not separate forms.

A semicolon begins a line comment outside a string. The reader ignores everything from that semicolon through the end of the line. One and two semicolons behave identically; `;;` is only a source-style convention for longer comments.

```spork
; One complete form may span lines
(def total
  (+ 10
     20))

;; A comment may follow a form
total ; => 30
```

## Delimiters and collection forms

| Syntax | Reader result | Typical use |
| --- | --- | --- |
| `(form ...)` | list form | Calls, special forms, and macro forms |
| `[value ...]` | vector literal | Persistent vectors, bindings, and parameter patterns |
| `{key value ...}` | map literal | Persistent maps; requires an even number of forms |
| `#{value ...}` | set literal | Persistent sets |
| `"text"` | string atom | Python string value |

The meaning of a list depends on its first form and compilation context. Collection runtime behavior is covered under [data structures](/docs/reference/language/data-structures/); binding and call contexts are covered under [forms and control flow](/docs/reference/language/forms-and-control-flow/) and [functions](/docs/reference/language/functions/).

Mismatched or missing closing delimiters are syntax errors. Delimiters inside strings do not end the surrounding form.

## Scalar literals

```spork
; Decimal and hexadecimal integers
42
-17
0x2a
-0x2a

; Floating-point values contain a decimal point
3.14
-0.5
1.0e3

; Strings may contain escapes or span source lines
"hello"
"line 1\nline 2"
"tab:\tvalue"

; These map directly to Python values
true        ; Python True
false       ; Python False
nil         ; Python None
```

Ordinary strings recognize `\n` and `\t`; a backslash before another character includes that character without the backslash. A backslash immediately followed by a newline continues the string without including that newline. Regex literals have separate raw-pattern behavior documented under [`#r"..."`](/docs/reference/language/reader-macros/#regex-literal).

## Keywords

A nonempty atom beginning with `:` is a `Keyword`. Keywords evaluate to themselves, retain hyphens in their names, and can be called as map lookup functions.

```spork
:name
:my-key

(:name {:name "Alice"})                ; => "Alice"
(:missing {:a 1})                       ; => nil
(:missing {:a 1} "default")             ; => "default"
```

The lone token `:` is a symbol, not a keyword.

## Symbols and identifier normalization

Any atom that is not a scalar literal or keyword is read as a symbol. A quoted symbol retains its source spelling. When a symbol is compiled as a Python name, Spork normalizes Lisp punctuation for Python compatibility:

| Spork symbol | Python name | Rule |
| --- | --- | --- |
| `my-variable` | `my_variable` | Hyphens become underscores |
| `valid?` | `valid_q` | A trailing question mark becomes `_q` |
| `swap!` | `swap_bang` | A trailing exclamation mark becomes `_bang` |
| `math.sin` | `math.sin` | Dots remain attribute or namespace access |
| `foo.bar.baz` | `foo.bar.baz` | Dotted access may have several segments |
| `+` | `_plus_` | Operator symbols have dedicated normalized names |

Punctuation inside a name is normalized as well. Because normalization is not one-to-one, source spellings such as `my-variable` and `my_variable` collide when used as names in the same scope.

Dotted-symbol call and import behavior is defined under [namespaces and modules](/docs/reference/language/namespaces/#dotted-access).

## Reader prefixes

Quote, quasiquote, unquote, decoration, anonymous-function, slice, discard, tagged-literal, and read-time-evaluation prefixes are all defined on the [reader macro reference](/docs/reference/language/reader-macros/). Keeping those transformations on one page separates token and literal rules from syntax that constructs or rewrites forms.

`#{...}` is a persistent set literal rather than a reader-macro transformation. Likewise, `*{...}` is keyword-argument call syntax and is documented under [keyword arguments](/docs/reference/language/functions/#keyword-arguments).
