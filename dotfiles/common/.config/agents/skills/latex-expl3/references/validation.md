# Verification for LaTeX macro changes

## Compile the real use case

Use the project's documented command and engine. In a minimal fixture, typical
commands are:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -lualatex -interaction=nonstopmode -halt-on-error main.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

Choose the applicable command, not all three automatically. Chinese documents,
fonts, bibliography tools, minted, and Beamer may require the project's actual
configuration. Never silently switch engines to avoid a failure. Keep temporary
fixtures and compiler output outside managed dotfile trees.

Check the exit status and log for undefined control sequences, bad argument
signatures, missing resources, key errors, and relevant layout warnings. A PDF
left from an earlier successful build does not prove the latest build succeeded.

## Exercise the contract

Pick cases relevant to the change:

- Defaults and overridden values, empty input, and supported starred/optional forms.
- Literal tokens versus a token-list variable, with only the intended expansion.
- Repeated calls with different options to detect leaked local state.
- Nested calls when the implementation shares scratch state.
- Invalid keys/values producing the intended diagnostic.
- Package options and command options separately, including load-order behavior.
- Moving arguments or PDF bookmarks if the command supports them.

For the `skilldemo` example, load it with `title=Default`, call
`\DemoTitle[title=Override,bold]`, then `\DemoTitle` again. The second call must
use `Default`, and bold must not leak. Also try `title={A,B}` and a formatting
command in the title; successful token parsing alone does not prove correct output.

## Existing regression infrastructure

If the project already uses l3build, run `l3build check` with its configured
engines. Use log-based `.lvt`/`.tlg` cases for expansion, diagnostics, and state.
Inspect expected-log differences before accepting them; `l3build save` updates
the baseline and is not a fix for a failing test. Do not introduce an entire
l3build setup for a small one-off macro unless sustained regression coverage is
needed. See the [official l3build project](https://github.com/latex3/l3build).

Log comparisons do not establish visual correctness. For layout or theme
changes, inspect a representative rendered PDF with available tools. If the
engine, dependencies, or renderer are unavailable, state what remains unverified.
