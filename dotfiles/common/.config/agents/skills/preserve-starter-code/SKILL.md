---
name: preserve-starter-code
description: >-
  Implement, debug, review, and package programming coursework under an explicit
  requirement to keep supplied starter files unchanged. Use when the user invokes
  this skill or requests preserving starter code, including resumed work and
  minimal reproducible submissions; not ordinary coursework or TODO completion
  without that preservation requirement.
---

# Preserve Starter Code

Keep original starter files unchanged. Build the smallest clear implementation
that fits their supported interfaces, maintain an organized workspace, and
prepare only required, reproducible deliverables. Apply these constraints across
the active task, including implementation, debugging, testing, and packaging.

## Scope

The no-edit rule is established by an explicit invocation of this skill or the
user's preservation requirement. Do not infer it merely from the presence of
starter files, TODOs, slides, or an autograder. Once established, assignment
instructions to fill TODOs do not silently waive that rule; obtain the user's
specific exception when needed.

## 1. Discover the workspace and its contract

- Treat the user-designated working folder as the assignment root. If launched
  inside a subfolder, use explicit context and nearby assignment files to identify
  the root; do not assume the Git root or current code folder is the hand-in root.
- Inspect the actual layout before creating directories. A layout such as
  code/, hw_slides.pdf, report/, submissions/ is an example, not a mandatory
  template. Reuse existing code and report locations and meaningful conventions.
- Read the assignment specification, relevant slides and README, repository
  instructions, provided checks, and affected code. Identify required documents,
  supported extension points, grading commands, permitted submission paths, and
  the minimum procedure needed to reproduce the requested results.
- Distinguish supplied starter files, user-authored solution code, reports, data,
  required results, local validation tools, and previous submissions. Existing
  files are not automatically all starter code; establish provenance from the
  specification, known history, or user context. If an existing code file's
  provenance is unclear, preserve it until the needed editing scope is resolved.
- Record the initial inventory and existing changes in conversation or temporary
  storage outside the deliverable. Inspect Git status and existing staged and
  unstaged diffs; account for relevant untracked and ignored files. Do not assume
  HEAD is the original starter. Preserve pre-existing user modifications.
- Retain before-hashes or before-copies of protected starter files outside the
  submission tree so their final state can be checked. Do not create an extra
  tracking document in the project just to record this inventory.
- Briefly explain the intended changes and where new implementation files belong.
  Proceed with authorized additions and solution edits without seeking approval
  for routine design choices.

## 2. Keep starter code immutable

- Do not edit, rename, move, delete, replace, or reformat any supplied starter
  file. Preserve its contents, paths, public interfaces, configuration, and
  execution contract. This includes TODO bodies, placeholder implementations,
  instructor tests, grading scripts, and dependency manifests in the starter.
- Add new implementation files only where the assignment permits them. Connect
  them through existing supported imports, configuration options, CLI options,
  subclassing hooks, or other documented extension points, without editing
  protected files.
- Do not treat an assignment instruction to fill a TODO, an apparent starter bug,
  or convenience as permission to override the user's no-edit rule.
- Do not bypass the rule through an edited starter copy, runtime monkeypatching,
  import tricks, or altered replacements generated during packaging. A separate
  editable copy of the starter also requires explicit user authorization.
- If the required solution cannot integrate without changing protected code,
  identify the exact file or interface and the smallest necessary exception.
  Explain the conflict and ask for that specific scope unless it has already
  been authorized. Continue independent work that does not depend on the answer.
- When the user explicitly permits editing particular files or TODO regions,
  limit changes to that scope and retain all other protections. Do not restore
  an older official version over the user's existing work.

## 3. Maintain a simple, structured repository

- Place new code beside related implementation or in a small solution module or
  package suited to the existing design. Keep responsibilities clear and imports
  predictable; avoid scattering scripts across the assignment root.
- Separate reusable implementation, necessary execution or evaluation entry
  points, and report materials when their responsibilities warrant it. Prefer
  the current project's organization over imposing a new directory convention.
- Use simple modules and functions before introducing additional layers,
  frameworks, factories, or configuration systems. Do not redesign the starter
  or add infrastructure for hypothetical future assignments.
- Preserve required signatures, command-line arguments, data formats, output
  formats, and grading behavior. Adding files must not silently change the
  command that the course expects.
- Match existing coding and dependency conventions. Do not migrate tooling,
  upgrade dependencies, format the whole project, or add CI without task need.
  If new dependencies are necessary, respect course limits and describe their
  minimal reproducible setup without editing protected manifests.
- Keep plans, task tracking, work logs, reasoning notes, and test transcripts
  in conversation or outside the deliverable. Do not add agent-only PLAN.md,
  PROGRESS.md, WORK_LOG.md, or AGENTS.md files unless explicitly requested.
- Keep temporary probes, one-off scripts, debug dumps, caches, and build output
  outside protected source directories where supported. Reuse an appropriate
  existing development area, or external temporary storage, instead of creating
  a new agent directory by default.

## 4. Validate during development

- Run relevant existing checks and the assignment's execution command. Add
  focused validation only when it addresses a meaningful correctness risk.
- Use agent-created unit tests, smoke tests, mocks, fixtures, and debugging
  helpers locally when useful. Keep them in a suitable development location or
  temporary storage, and exclude them from the hand-in package by default.
- Preserve instructor checks and pre-existing user tests. Never weaken a check
  or change expected results to make an implementation pass.
- Report commands that cannot run and why. Do not claim that a result was
  reproduced when its environment, data, hardware, or runtime was unavailable.
- Check protected starter files against their initial state after changes and
  validation. Review new and edited solution files for unnecessary complexity,
  temporary debug prints, abandoned experiments, and unrelated modifications.
- Remove only confirmed task-created disposable artifacts, using exact inspected
  paths. Never use blanket git clean, git reset --hard, or recursive removal of
  unknown, pre-existing, untracked, or ignored files for cleanliness.
- Keep useful local tests and user material when appropriate; excluding a file
  from submission does not authorize deleting it from the working repository.

## 5. Assemble a minimal submission when requested

Read [submission.md](references/submission.md) only when preparing hand-in
artifacts. It covers the `submissions/` destination, inclusion rules, preservation
of earlier artifacts, and fresh-extraction reproduction checks. Implementation
alone does not authorize packaging, upload, or submission.

## Final response

Respond concisely in the user's language. State what was implemented, where new
files belong, whether starter files stayed unchanged, and the validation results
and limits. When packaging was requested, link to the final artifacts in
submissions/ and summarize their required contents and minimal reproduction
command. Keep progress and change summaries in the conversation, not extra
documents in the submission.
