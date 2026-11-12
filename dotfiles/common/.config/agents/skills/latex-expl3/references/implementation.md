# Expansion, state, and public interfaces

## Preserve tokens deliberately

- `N` takes one control-sequence token; `n` takes an unexpanded argument.
  A variable passed inside an `n` argument remains a variable token.
- Use a documented `V` variant to retrieve a variable's value, `v` when the
  variable is named by constructed text, and `c` for a constructed csname.
  Prefer direct `N` access when the control sequence is already known.
- Use `e` expansion only when the API needs expandable content evaluated now.
  Do not fully expand arbitrary user text containing formatting commands.
- Check the installed interface manual for base functions and available
  variants. Generate a missing variant once with `\cs_generate_variant:Nn`,
  using a signature compatible with the base function.
- `\tl_set:Nn` preserves input, `\tl_set:NV` copies the current value of another
  token-list variable, and `\tl_set_eq:NN` copies its current meaning. The latter
  does not establish a live reference that tracks future assignments.

## Scope and reentrancy

Use local assignments for temporary options and global assignments only when
state must survive the current group. An `l_` or `g_` name communicates intent;
the assignment function determines actual scope.

Group per-call options if they should not affect later calls. Do not end that
group before using its result, and do not group away definitions or persistent
settings. Shared scratch variables can be overwritten by nested helper calls;
pass values or use appropriately scoped owned variables when this matters.

## Keys and wrappers

Choose `.tl_set:N`, `.bool_set:N`, `.dim_set:N`, or `.choice:` according to the
value's meaning. Define defaults intentionally and provide useful diagnostics
with `\msg_new:nnn` and appropriate error/warning calls. Decide whether unknown
keys should error or be forwarded; do not silently discard misspellings.

For package/class options, follow the existing option interface.
On kernels supporting it, `\ProcessKeyOptions` is a kernel interface; older
targets may use `l3keys2e` and `\ProcessKeysOptions`. Check the supported format
date before choosing. Public document-command interfaces are also in modern
kernels; do not add `xparse` without a compatibility reason.

### Minimal package example

This example keeps package defaults but scopes each command's overrides. Rename
the module and command for the project; it is not a required template.

```tex
\NeedsTeXFormat{LaTeX2e}[2022-06-01]
\ProvidesExplPackage{skilldemo}{2026-11-12}{0.1}{Scoped options example}
\tl_new:N \l__skilldemo_title_tl
\bool_new:N \l__skilldemo_bold_bool
\keys_define:nn { skilldemo }
  {
    title .tl_set:N = \l__skilldemo_title_tl,
    title .initial:n = Untitled,
    bold .bool_set:N = \l__skilldemo_bold_bool,
    bold .initial:n = false,
    bold .default:n = true,
  }
\ProcessKeyOptions [ skilldemo ]
\cs_new_protected:Npn \__skilldemo_print:n #1
  {
    \group_begin:
      \keys_set:nn { skilldemo } {#1}
      \bool_if:NT \l__skilldemo_bold_bool { \bfseries }
      \tl_use:N \l__skilldemo_title_tl
    \group_end:
  }
\NewDocumentCommand \DemoTitle { O{} }
  { \__skilldemo_print:n {#1} }
\ExplSyntaxOff
\endinput
```

## Integration boundaries

In Beamer themes or tcolorbox abstractions, keep their documented key and hook
systems at the boundary. Use expl3 for internal logic, not to replace working
ecosystem interfaces. Prefer documented LaTeX hooks over patching private macros.
Preserve moving-argument, PDF-string, and fragile-content behavior when those
are part of the existing command's contract.
