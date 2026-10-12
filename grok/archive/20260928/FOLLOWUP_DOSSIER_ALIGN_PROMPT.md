# Follow-up: align DOSSIER.md to current inspect

CWD /Users/daniele_palagi/Desktop/phantom_cloud (trusted).

AGENTS.md exists at the checkout root. grok inspect 1.0.41 reports Project Instructions (1), path Agents.md (~244 tokens), trusted yes. Do not create new agents, skills, or hooks.

## Edit only `.grok/DOSSIER.md`

1. Repo layout: delete or replace the line that says AGENTS.md is not in this workdir. State that project instructions are `AGENTS.md` at the checkout root (inspect may show `Agents.md`).

2. Grok CLI section: keep "AGENTS.md is present; inspect project instructions > 0". Remove the inspect bullet that still says instructions loaded 0 / no AGENTS.md. Replace with:
   - Project trusted: yes
   - Project instructions: 1 (AGENTS.md / Agents.md, ~244 tokens)
   - MCP: phantom-cloud-engine (sse) from project config
   - Project agent: phantom-surgery
   - Project skill: phantom-matrix (present; model invocation disabled)
   - Hooks: none from this project (Vercel plugin is user-global)
   - [privacy] warning is from ~/.grok/config.toml, not this project file

3. Do not narrate test archives. Evidence index stays as names only.

Do not edit AGENTS.md, the skill body, the agent, config.toml, or engine files. Do not delete the skill.

## Stop

Re-read DOSSIER.md. No sentence may claim AGENTS.md is absent. Do not commit.
