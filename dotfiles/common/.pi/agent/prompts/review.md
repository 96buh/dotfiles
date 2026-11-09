---
description: Review current Git changes without modifying files
argument-hint: "[focus]"
---
Review the current repository's staged and unstaged changes, including relevant
untracked files. Focus on ${@:-correctness, regressions, error handling, and missing tests}.

Read the changed code and its relevant callers. Report actionable findings first,
ordered by severity, with file paths and line numbers. Explain the concrete trigger
and impact. If there are no findings, say so and mention remaining verification gaps.
Do not edit, stage, commit, or push files. Respond in Traditional Chinese.
