# Agent pipeline rules

This repo is worked on by three automated agents that coordinate **only through GitHub labels**.
Every agent loads this file; follow it exactly.

## Labels (the state machine)

| Label | Meaning | Owner |
|---|---|---|
| `agent:todo` | Issue ready to be implemented | Builder picks it up |
| `agent:in-progress` | Builder is working on it (issue) | Builder |
| `agent:review` | PR waiting for review | Reviewer |
| `agent:changes` | Reviewer requested changes | Builder fixes |
| `agent:approved` | Reviewer approved | Merger |
| `agent:human` | Agents gave up; a human must look | Nobody (agents skip it) |

Rules for every agent:
- Use the GitHub REST API (or `gh` if installed) with the `GITHUB_TOKEN` environment variable.
- Only touch issues/PRs carrying the labels you own. Never touch anything labelled `agent:human`.
- Handle **at most one** item per run, then stop. If there is nothing to do, stop immediately
  without making changes (runs cost subscription usage).
- Always move the label forward (remove the old one, add the new one) as the last step,
  so a crashed run leaves the item where it was.
- Start every comment you post with your role in bold, e.g. `**[Reviewer agent]**`.

## Code rules

- Python 3.10+, standard library only. Public functions get type hints and a one-line docstring.
- Every change ships with pytest tests in `tests/`. `ruff check .` and `pytest -q` must pass.
- Export new public functions from `textkit/__init__.py`.
- Keep PRs small: one issue per PR, branch name `agent/issue-<number>`,
  PR body contains `Closes #<number>`.
