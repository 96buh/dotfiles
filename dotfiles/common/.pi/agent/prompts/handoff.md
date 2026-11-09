---
description: Summarize this task for another agent or a later session
argument-hint: "[focus]"
---
Prepare a concise handoff in Traditional Chinese. Additional focus: ${@:-the current task}.

Include the user's objective and constraints, completed changes and their paths,
important decisions, exact verification commands and observed results, unresolved
issues, and the next concrete steps. Distinguish this task's changes from pre-existing
user changes. State whether changes are committed or pushed. Do not claim unrun tests
passed, include secrets, or modify files; return the handoff directly in the response.
