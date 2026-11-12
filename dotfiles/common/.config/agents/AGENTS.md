# Global Agent Rules

## Communication

- Respond to the user in Traditional Chinese (Taiwan).
- Use clear, simple, and concise language.
- Be direct and avoid unnecessary explanations or repetition.
- Keep technical terms, code, and identifiers in English.
- Never use the em dash character (U+2014); use a plain hyphen (-) instead.
- Use ASCII parentheses `(` and `)` in both Chinese and English; never use fullwidth parentheses (U+FF08 and U+FF09).
- Write formal reports, academic writing, and technical reports in English unless otherwise specified.
- Use Traditional Chinese when discussing or explaining reports to the user.

## Development

- Understand relevant code before making changes.
- Follow existing project conventions and architecture.
- Prefer simple, readable, and maintainable solutions.
- Avoid unnecessary abstractions, complexity, and dependencies.
- Keep changes focused on the requested task.
- Do not modify unrelated files.

## Python

- For new Python projects, default to `uv` for environments and dependencies, Ruff for linting and formatting, and pytest for tests unless instructed otherwise.
- Preserve existing project tooling, supported Python versions, and configuration. Do not migrate tools or add dependencies solely to match these defaults.
- Annotate all new or modified function parameters and return values, including `-> None` where appropriate. Avoid unrelated annotation-only changes.
- Use modern typing syntax supported by the project's Python version. Avoid `Any`, type suppressions, and unnecessary casts unless justified.
- Use the project's existing type checker; consider Pyrefly for new projects without one. Ruff and pytest do not replace type checking.
- Keep tool configuration in `pyproject.toml` when practical, respecting existing configuration files. Keep test, lint, and type-check dependencies out of runtime dependencies.
- Test observable behavior and relevant edge cases. For bug fixes, reproduce the failure first and add a regression test when appropriate; avoid tests that merely mirror implementation details.
- Run tools through the project environment. For projects using these defaults, use `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pytest`, plus the configured type-check command. Follow existing project commands when they differ.

## Verification

- Run relevant tests, linters, and type checkers after making changes.
- Do not claim tests passed unless they were actually executed.
- Clearly report verification results and any unresolved issues.

## Git

- Follow Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Write commit messages in English using the imperative mood.
- Keep commit subjects concise, preferably under 72 characters.
- Keep commits focused on a single logical change.
- Never commit, push, or rewrite Git history without explicit permission.

## Safety

- Ask before destructive or irreversible operations.
- Never expose or commit secrets or credentials.
- Never overwrite or discard existing user changes without permission.
