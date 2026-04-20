<!--
Document : INSTALL.md
Auteur : Bruno DELNOZ
Email : bruno.delnoz@protonmail.com
Version : v1.0.0
Date : 2026-04-20 11:33
-->
# INSTALL

## Scope
This guide explains how to set up and validate the repository environment without modifying any existing script logic.

## 1) System prerequisites
- Linux/macOS shell environment (or equivalent).
- Python `>= 3.8` available as `python3`.
- Network access for package installation and Mistral API calls.

Check Python:

```bash
python3 --version
```

## 2) Clone and enter repository
```bash
git clone <repository-url>
cd NoXoZVorteX_prompted
```

## 3) Recommended virtual environment
The project uses `.venv_analyse` by default.

Create/refresh environment through project command:

```bash
python analyse_conversations_merged.py --install
```

This action:
- creates `.venv_analyse` if missing,
- upgrades `pip`,
- installs missing dependencies declared in `config.py`.

## 4) Activate virtual environment (optional but recommended)
```bash
source .venv_analyse/bin/activate
```

## 5) API key configuration
Real execution requires:

```bash
export MISTRAL_API_KEY='your_api_key_here'
```

Without this variable, runtime execution (`--exec` without `--simulate`) fails by design.

## 6) Verify prerequisites
Run:

```bash
python analyse_conversations_merged.py --prerequis
```

Expected behavior:
- system prerequisites are checked,
- missing packages (if any) are listed,
- an explicit install instruction is provided when required.

## 7) Quick smoke test (simulation)
You can validate end-to-end flow without API calls:

```bash
python analyse_conversations_merged.py --exec \
  --simulate \
  --aiall \
  --fichier ./data_example/*.json \
  --prompt-file example_security_prompt \
  --target-logs ./logs \
  --target-results ./results \
  --format markdown
```

## 8) Troubleshooting basics
- **`Prompt '<name>' introuvable`**: ensure prompt file exists as `prompts/prompt_<name>.txt`.
- **No files found**: validate `--fichier` glob and use `--recursive` when needed.
- **Dependency errors**: run `--install` then reactivate `.venv_analyse`.
- **Rate limits**: reduce `--workers` and increase `--delay`.
