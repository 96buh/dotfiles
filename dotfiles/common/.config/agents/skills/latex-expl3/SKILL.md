---
name: latex-expl3
description: Use this skill when writing or refactoring LaTeX packages, classes, themes, reusable macros, key-value interfaces, or complex LaTeX command logic. Do not use it for ordinary document text or simple one-off LaTeX snippets.
---

# LaTeX expl3 Skill

When helping with LaTeX package/class/theme development, prefer modern LaTeX3 `expl3` style for internal implementation.

Use `expl3` especially for:

- package or class internals
- reusable macro systems
- key-value options
- conditional logic
- token list, sequence, clist, prop, int, bool, dim, skip variables
- robust wrapper commands
- Beamer themes, document classes, style files, and tcolorbox abstractions

Do not force `expl3` for:

- normal LaTeX document content
- simple equations
- simple figure/table snippets
- short one-off macros where LaTeX2e is clearer

## Style rules

Use:

```tex
\ExplSyntaxOn
...
\ExplSyntaxOff
```

Prefer `\NewDocumentCommand`, `\RenewDocumentCommand`, and `\ProvideDocumentCommand` for user-facing commands.

Separate public commands from internal implementation:

```tex
\NewDocumentCommand \MyCommand { m }
  {
    \mytheme_do_something:n { #1 }
  }

\cs_new_protected:Npn \mytheme_do_something:n #1
  {
    ...
  }
```

Use a clear module prefix, such as:

```tex
mytheme_
mystyle_
myclass_
```

Use proper variable naming:

```tex
\tl_new:N   \l_mytheme_title_tl
\seq_new:N  \l_mytheme_items_seq
\bool_new:N \l_mytheme_enabled_bool
\dim_new:N  \l_mytheme_margin_dim
\prop_new:N \l_mytheme_color_prop
```

For key-value options, prefer `l3keys`:

```tex
\keys_define:nn { mytheme }
  {
    title .tl_set:N = \l_mytheme_title_tl,
    enabled .bool_set:N = \l_mytheme_enabled_bool,
    margin .dim_set:N = \l_mytheme_margin_dim,
  }
```

For package/class options, prefer a maintainable key-value interface instead of many ad-hoc booleans.

## Output expectations

When generating LaTeX package/class code:

1. Use `expl3` for internal logic.
2. Keep user-facing commands LaTeX-friendly.
3. Add short comments only where they clarify structure.
4. Avoid overly clever low-level TeX unless necessary.
5. Prefer maintainability over extreme compactness.
