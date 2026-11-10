# Global Agent Rules

## Communication

- Respond to the user in Traditional Chinese (Taiwan).
- Use clear, simple, and concise language.
- Be direct and avoid unnecessary explanations or repetition.
- Keep technical terms, code, and identifiers in English.
- Never use the em dash character (U+2014); use a plain hyphen (-) instead.
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

- Prefer `uv` for new Python projects; preserve the environment and dependency tools used by existing projects.
- Use type hints for all function parameters and return values.
- Prefer modern Python typing syntax compatible with the project's Python version.
- Use the project's existing type checker; consider Pyrefly for new projects without one.
- Avoid `Any`, type suppressions, and unnecessary casts unless justified.
- Follow existing project formatting and linting configurations.
- Use the project's existing Python test framework; prefer pytest for new projects without one.
- Run tests through the project's environment, such as `uv run pytest`.

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
