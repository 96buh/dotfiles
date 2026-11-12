# Assemble a minimal submission

- Put every final hand-in artifact, such as a ZIP, PDF, or required standalone
  file, under <assignment-root>/submissions/. Create this directory when preparing
  a submission if it does not exist. Use another destination only if the user
  explicitly requests it.
- Follow the course's required artifact names and internal directory layout.
  The outer submissions/ destination does not mean the archive should contain a
  submissions/ prefix, or that the development tree must be copied unchanged.
- Build an explicit inclusion list from the assignment requirements and actual
  reproduction dependencies. Include only required documents and the smallest
  complete set of code, configuration, dependencies, and resources needed to
  execute the solution and reproduce the requested results.
- Include required reports, exact setup/run instructions or dependency manifests
  when needed, necessary inputs, and required model weights or result files.
  For large external data or models, include permitted retrieval instructions
  or scripts when that meets the course rules. Do not bundle an entire virtual
  environment, installed dependency tree, dataset, or experiment history by default.
- Exclude agent-created validation unit tests, smoke tests, mocks, fixtures,
  debug scripts, benchmark probes, test reports, work notes, caches, editor/OS
  metadata, version-control metadata, previous submissions, and incidental logs.
  Preserve any files explicitly required by the course, including supplied tests
  or a test implementation that is itself an assigned deliverable. If an explicit
  user exclusion conflicts with a required deliverable, explain the conflict.
- Include a test helper as runtime code only if it truly belongs to the required
  solution; ordinarily remove that development dependency by moving necessary
  functionality into a clear solution module. Never make reproduction depend on
  an excluded local validation script or absolute workspace path.
- Keep required evaluation logs, figures, checkpoints, and results when the
  assignment requires them. Decide by purpose and dependency, not extension.
- Do not zip the whole working folder, rely solely on .gitignore, or use tracked
  files alone to select the submission. Required new or untracked solution files
  must be included; tracked development artifacts may still need exclusion.
- Stage the package in a temporary location outside submissions/. Preserve the
  working repository and earlier submissions. Avoid replacing an existing user
  artifact unless requested; choose a clear unused filename when naming is
  flexible. Keep submissions/ for completed hand-in artifacts, not staging files
  or agent-generated checklists.
- Inspect the final archive's actual file list against the inclusion list.
  Extract it to a fresh temporary directory and, when feasible, run the minimal
  documented reproduction command using its submitted files. Check that required
  resources are present, paths work, and source-workspace files are not borrowed.
- Run developer-only tests outside the final archive if needed. Do not insert
  tests into the hand-in package just to perform this check. Check for regenerated
  caches after verification and verify starter files remain unchanged.
- Prepare, upload, or submit only what the user requested. Creating a local
  hand-in archive does not authorize submitting it to a course platform.
