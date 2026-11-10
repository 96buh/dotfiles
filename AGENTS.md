# Repository Guidelines

## Project Structure

- `flake.nix`, `flake.lock`, and `macos/` define nix-darwin, Home Manager, packages, and account settings.
- `dotfiles/common/`, `dotfiles/macos/`, and `dotfiles/linux/` mirror home-directory paths. Mac-specific files override common files during Nix deployment.
- `dotfiles/settings/` contains preferences merged into writable application configs; these files are not directly linked.
- `scripts/` contains deployment and TOML merge utilities. Remote TeX preview sources live in `dotfiles/common/tools/remote-tex-preview/`.
- Shared agent instructions and skills live under `dotfiles/common/.config/agents/`. Preserve vendored licenses and assets.
- `packages/cachyos/` contains reference package lists. Local notes in `docs/` are Git-ignored.

## Build and Development Commands

Run from the repository root:

```sh
sudo darwin-rebuild build --flake .#macbookpro
./scripts/deploy-linux --check
```

The first builds the macOS configuration without activation; the second previews Linux links and validates Codex preferences. Activate deliberately with `sudo darwin-rebuild switch --flake .#macbookpro` or `./scripts/deploy-linux`.

Register new source files with Git before building: Git-backed flakes omit untracked files. Neovim configuration is maintained in a separate repository.

## Coding Style

Follow nearby conventions: two-space Nix indentation, four-space Python indentation, and quoted Bash expansions. Use Python type hints and prefer `uv` for script dependencies. Check Python with:

```sh
ruff check scripts/apply-codex-settings.py --config dotfiles/common/.config/ruff/ruff.toml
bash -n scripts/deploy-linux
```

Keep scripts focused; avoid introducing duplicate deployment logic or reformatting unrelated files.

## Verification

No test suite is maintained in this repository. Run relevant build, lint, syntax,
and deployment preview commands, plus `git diff --check`. Validate risky changes
in temporary directories and report untested platform behavior explicitly.

## Commits and Pull Requests

Prefer Conventional Commits with concise English imperative subjects, such as `fix: preserve unmanaged TOML settings`. Keep changes focused. PRs should describe behavior, affected platforms, verification, and migration steps; link relevant issues. Include screenshots only for visual changes.

## Configuration Safety

Never commit credentials or machine-local overrides. Keep Codex's runtime config writable; edit `dotfiles/settings/codex.toml` for managed preferences. Back up conflicting home files rather than using Stow `--adopt`. Preserve unrelated user changes and obtain explicit authorization before committing or pushing.
