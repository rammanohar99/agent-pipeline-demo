# Running the pipeline yourself

This guide sets up the Builder → Reviewer → Merger pipeline on your own fork, running locally with
[OpenHands Agent Canvas](https://github.com/OpenHands/OpenHands) in Docker and Claude Code as the agent.

**You need:**

- Docker Desktop (or Docker Engine)
- A Claude Pro/Max subscription **or** an Anthropic API key
- The [GitHub CLI](https://cli.github.com/) (`gh`), logged in, for creating labels and issues
- Python 3.10+ to run the setup scripts (the runner itself uses only the standard library)

## 1. Fork or copy the repo

Fork this repo (or push a copy), then point the runner at it. In [`automation/run_agent.py`](../automation/run_agent.py):

```python
REPO = "your-user/agent-pipeline-demo"
```

Create the six labels and some work for the Builder:

```bash
R=your-user/agent-pipeline-demo
gh label create agent:todo        --repo $R --color 0e8a16 --description "Issue ready for the Builder agent"
gh label create agent:in-progress --repo $R --color fbca04 --description "Builder agent is working on this issue"
gh label create agent:review      --repo $R --color 1d76db --description "PR waiting for the Reviewer agent"
gh label create agent:changes     --repo $R --color d93f0b --description "Reviewer requested changes; Builder fixes"
gh label create agent:approved    --repo $R --color 5319e7 --description "Reviewer approved; Merger merges when green"
gh label create agent:human       --repo $R --color b60205 --description "Agents gave up; needs a human"

gh issue create --repo $R --title "Add word_count(text)" --label agent:todo \
  --body "Add word_count(text: str) -> int: number of whitespace-separated words, 0 for blank input."
```

> **Windows PowerShell 5.1** strips double quotes from arguments passed to native programs like `gh`.
> Put issue bodies in a file and use `--body-file`, or run these commands from Git Bash.

## 2. Start Agent Canvas

```bash
mkdir -p ~/projects ~/.openhands
docker run -d --name agent-canvas \
  -p 127.0.0.1:8000:8000 \
  -e AGENT_CANVAS_ALLOW_LAN_SESSION_KEY=true \
  -v "$HOME/.openhands:/home/openhands/.openhands" \
  -v "$HOME/projects:/projects" \
  ghcr.io/openhands/agent-canvas:1.32.0
```

Open <http://localhost:8000/canvas> and complete onboarding:

1. **Choose your agent:** pick **Claude Code**.
2. **Credentials:**
   - *With a subscription:* run `claude setup-token` on your machine and paste the `sk-ant-oat...` token into
     `CLAUDE_CODE_OAUTH_TOKEN`. Leave the API key and base URL blank, because a base URL breaks OAuth tokens.
   - *With API credits:* fill in `ANTHROPIC_API_KEY` instead.
3. Send a test message such as "hi" to confirm the agent replies.

## 3. Give the agents GitHub access

Create a [fine-grained personal access token](https://github.com/settings/personal-access-tokens/new)
scoped to **only this repository**:

| Permission | Access |
|---|---|
| Contents | Read and write |
| Pull requests | Read and write |
| Issues | Read and write |
| Actions | Read-only |
| Commit statuses | Read-only |

In Canvas, go to **Settings → Secrets** and save it with the name **`GITHUB_TOKEN`**. The runner attaches
every saved secret to each agent conversation.

## 4. Do a dry run by hand

Before scheduling anything, run each role once from your machine against the Canvas API and check the result
on GitHub after each step:

```bash
export AGENT_SERVER_URL=http://127.0.0.1:8000
export OH_SESSION_API_KEYS_0=$(docker exec agent-canvas cat /home/openhands/.openhands/agent-canvas/api-key.txt)

python automation/run_agent.py builder    # expect: a PR labelled agent:review
python automation/run_agent.py reviewer   # expect: a review ending in "Verdict: ..."
python automation/run_agent.py merger     # expect: the PR merged (if approved and CI is green)
```

Each run appears as a conversation in the Canvas sidebar, so you can watch the agent work.

## 5. Schedule it

Each role becomes a **custom automation** that runs the uploaded runner. All requests below go to the Canvas
automation API with your session key:

```bash
KEY=$OH_SESSION_API_KEYS_0
API=http://127.0.0.1:8000/api/automation/v1
```

**Upload the runner and prompts** as a tarball:

```bash
git archive --format=tar.gz -o runner.tar.gz HEAD automation/run_agent.py .agents/prompts
curl -s -H "X-Session-API-Key: $KEY" -H "Content-Type: application/gzip" \
  -X POST "$API/uploads?name=pipeline-runner" --data-binary @runner.tar.gz
# -> note the "tarball_path", e.g. oh-internal://uploads/<id>
```

**Find your Claude Code agent profile id:**

```bash
curl -s -H "X-Session-API-Key: $KEY" http://127.0.0.1:8000/api/agent-profiles
# -> "active_agent_profile_id"
```

**Create one automation per role.** They start inactive. Swap in the role and cron for each one:

```bash
curl -s -H "X-Session-API-Key: $KEY" -H "Content-Type: application/json" -X POST "$API" -d '{
  "name": "PR pipeline - Builder",
  "tarball_path": "oh-internal://uploads/<id>",
  "entrypoint": "python3 automation/run_agent.py builder",
  "agent_profile_id": "<profile-id>",
  "trigger": {"type": "cron", "schedule": "*/30 * * * *", "timezone": "Asia/Kolkata"},
  "timeout": 1800,
  "state": "INACTIVE"
}'
```

| Role | `entrypoint` argument | Suggested `schedule` |
|---|---|---|
| Builder | `builder` | `*/30 * * * *` |
| Reviewer | `reviewer` | `5,20,35,50 * * * *` |
| Merger | `merger` | `10,25,40,55 * * * *` |

**Test each automation once**, then activate it:

```bash
curl -s -H "X-Session-API-Key: $KEY" -H "Content-Type: application/json" -X POST "$API/<automation-id>/dispatch" -d '{}'
curl -s -H "X-Session-API-Key: $KEY" -H "Content-Type: application/json" -X PATCH "$API/<automation-id>" -d '{"state": "ACTIVE"}'
```

Runs and their conversations show up on the **Automations** page in Canvas. Set `"state": "INACTIVE"` to pause.

> **Changed a prompt or the runner?** The automations run the uploaded tarball, not the repo. Upload a new
> tarball and update each automation's `tarball_path`.

## Why custom automations, not "prompt" automations?

Canvas also offers a simpler *prompt automation* (paste a prompt, pick a schedule). Its generated script
always launches the built-in **OpenHands agent** with your LLM settings and ignores the selected agent profile.
That works with an LLM API key, but not with Claude Code on a subscription. It also installs the full SDK on
every run, which can take several minutes. The custom runner starts Claude Code directly and starts in seconds.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Conversation fails with `ACP error: Authentication required` | Claude Code started without its credentials | Make sure `CLAUDE_CODE_OAUTH_TOKEN` (or `ANTHROPIC_API_KEY`) is saved under **Settings → Secrets**. The runner forwards every saved secret. |
| `RuntimeError: GITHUB_TOKEN is not saved` | No GitHub secret | Add `GITHUB_TOKEN` in **Settings → Secrets** (step 3). |
| CI fails at `pip install -e` with *Multiple top-level packages discovered* | setuptools found `automation/` next to `textkit/` | Keep `[tool.setuptools] packages = ["textkit"]` in `pyproject.toml`. |
| A run stays `RUNNING` for hours, then completes | The host slept, which freezes Docker | Expected on a laptop. Host Canvas on an always-on machine for 24/7 runs. |
| Runner crashes printing output on Windows (`UnicodeEncodeError`) | Console encoding is cp1252 | Already handled. The runner switches stdout to UTF-8. |
| Merger keeps skipping a PR | CI still running, failed, or review is older than the latest commit | Check the PR's checks and labels. The Merger sends failed PRs back with `agent:changes`. |

## Security notes

- Scope the GitHub token to this one repository. The agents can push branches and merge PRs.
- Only collaborators can apply labels, so strangers can't queue work by opening issues. Don't add an issue
  template that auto-applies `agent:todo`, because that would let anyone trigger the Builder.
- The Builder reads PR comments when fixing changes. On a public repo, anyone can comment, so a malicious
  comment could try to steer the agent. For anything beyond a playground, restrict the Builder to comments
  from the `[Reviewer agent]` and stop at `agent:approved` for a human to merge.
