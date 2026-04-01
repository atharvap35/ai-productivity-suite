# AI Internal Productivity Suite

Local Streamlit app demonstrating AI workflows for Operations, Sales, Marketing/GTM, and Finance.

## Setup

```bash
cd ai-productivity-suite
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set `OPENAI_API_KEY` in your environment, or use a project **`.env`** file (see `.env.example`).

**Ollama (local LLM):** run Ollama, pull a model (e.g. `llama3.2`), then set:

- `OPENAI_BASE_URL=http://localhost:11434/v1`
- `OPENAI_API_KEY=ollama` (placeholder; Ollama ignores the value for local calls)
- `OPENAI_MODEL=<name of the model you pulled>`

## Git repository

From this folder (`ai-productivity-suite`), after [Git for Windows](https://git-scm.com/download/win) is installed, either run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/init-git.ps1
```

or manually:

```powershell
git init
git add -A
git commit -m "Initial commit: AI Internal Productivity Suite"
```

`.env` and `.streamlit/secrets.toml` are listed in `.gitignore` and will not be committed.

**Note:** If you use Cursor’s integrated terminal, restart it after installing Git so `PATH` picks up `git.exe`.

## Run

```bash
streamlit run app.py
```

## Project layout

- `app.py` — home page
- `pages/` — multipage workflows per team
- `modules/` — LLM client, prompts, evaluator
- `data/` — golden CSV test cases
- `utils/` — helpers

## Build steps

1. Project structure (this step)
2. LLM client
3. Prompts
4. Operations page
5. Other pages
6. Evaluation module
7. UI polish
