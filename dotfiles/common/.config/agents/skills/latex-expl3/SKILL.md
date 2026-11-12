---
name: latex-expl3
description: Write, refactor, and debug LaTeX packages, classes, themes, reusable macros, and key-value interfaces using expl3. Use for nontrivial macro logic, expansion, and state management; not ordinary document prose, equations, or simple one-off snippets.
---

# LaTeX expl3

Prefer expl3 for substantial internal logic. Preserve existing public APIs,
supported engines, and minimum LaTeX versions unless a change is requested.
Keep ordinary document markup and simple wrappers in familiar LaTeX syntax.

## Before editing

- Identify the source of truth: edit `.dtx` sources rather than generated
  `.sty` or `.cls` files when the project uses docstrip.
- Inspect the module prefix, public commands, option processing, load order,
  grouping, and existing build commands before selecting an implementation.
- For bugs, reproduce the user's document failure with the actual engine and
  relevant packages, reducing it only enough to isolate the cause.

## Implementation rules

- Use a consistent module prefix. Private helpers use `\__module_action:n`;
  owned variables use names such as `\l__module_title_tl` and
  `\g__module_registry_prop`. Declare variables once, outside repeated calls.
- Use `\ExplSyntaxOn` / `\ExplSyntaxOff` where needed. Ordinary spaces are
  ignored under expl3 syntax; do not silently change text or key names.
- Separate public commands from helpers. Use `\NewDocumentCommand` for new
  public interfaces; renew an existing command only intentionally.
- Choose `\cs_new:Npn` for expandable computation and
  `\cs_new_protected:Npn` for assignments, typesetting, or other side effects.
  Do not promise expandability merely because a function is short.
- Match argument signatures and expansion to actual inputs. Read
  [implementation.md](references/implementation.md) when manipulating token
  lists, generating variants, defining keys, or changing state and grouping.
- Prefer typed expl3 data structures and `l3keys` over ad-hoc parsing.
  Use documented interfaces of dependencies, not another module's internals.
- Preserve user tokens unless the API explicitly expands them. Make local
  versus persistent state intentional, especially with repeated or nested calls.

## Verification and delivery

Follow [validation.md](references/validation.md) for compiler checks, regression
cases, and when to use l3build. Verify behavior, not just successful compilation.
For visual changes, inspect the resulting PDF using available rendering tools.

Report public-interface changes, engine/version assumptions, commands actually
run, and remaining limitations. Do not install a TeX distribution, enable shell
escape, or regenerate reference outputs merely to make a check pass.

## Authoritative references

Use `texdoc interface3` for installed expl3 APIs and `texdoc clsguide` for
package/class interfaces. If local documentation is unavailable, consult the
[LaTeX documentation index](https://www.latex-project.org/help/documentation/)
and [l3kernel interface manual](https://mirrors.ctan.org/macros/latex/required/l3kernel/interface3.pdf).
Verify unfamiliar variants and engine restrictions rather than inventing APIs.
