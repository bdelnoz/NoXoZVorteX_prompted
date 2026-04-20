<!--
Document : README.md
Auteur : Bruno DELNOZ
Email : bruno.delnoz@protonmail.com
Version : v1.0.0
Date : 2026-04-20 11:33
-->
# NoXoZVorteX_prompted

## Overview
`NoXoZVorteX_prompted` is a Python-based CLI toolchain designed to run customizable prompt analyses on exported AI conversations.

The project focuses on:
- loading conversation exports from multiple vendors,
- extracting and normalizing message content,
- applying a reusable prompt template,
- executing analysis through the Mistral Chat Completions API,
- writing structured results in multiple output formats.

## Main entrypoint
The primary executable is:

```bash
python analyse_conversations_merged.py
```

If no argument is provided, the script displays help by default.

## Supported source formats
The tool can ingest:
- ChatGPT exports,
- LeChat/Mistral exports,
- Claude exports,
- mixed inputs with auto-detection (`--aiall` / `--auto`).

Automatic format detection is implemented in `extractors.py`.

## Core features
- Prompt-file based execution (`--prompt-file`) with templates from `./prompts`.
- Inline prompt execution (`--prompt-text`).
- Prompt inventory listing (`--prompt-list`).
- Recursive file discovery (`--recursive`) and glob support on `--fichier`.
- Duplicate conversation detection based on a deterministic signature.
- Automatic conversation splitting when token count exceeds `MAX_TOKENS`.
- Parallel processing using configurable workers (`--workers`).
- Optional dry-run mode (`--simulate`) with no external API call.
- Configurable output directory layout for logs/results.
- Output serialization to CSV, JSON, TXT, or Markdown.

## CLI options summary
### Control and lifecycle
- `--help`, `--help-adv`
- `--exec`
- `--install`
- `--prerequis`
- `--changelog`

### Input selection
- `--chatgpt`, `--lechat`, `--claude`, `--aiall` / `--auto`
- `--fichier`, `-F`
- `--recursive`
- `--cnbr`
- `--only-split`
- `--not-split`

### Prompt management
- `--prompt-file`, `-p`
- `--prompt-text`, `-pt`
- `--prompt-list`

### Execution tuning
- `--model`, `-m`
- `--workers`, `-w`
- `--delay`, `-d`
- `--simulate`

### Output and storage
- `--format` (`csv|json|txt|markdown`)
- `--output`, `-o`
- `--target-logs`
- `--target-results`

## Built-in prompt examples
The repository currently ships these prompt templates:
- `prompt_example_security_prompt.txt`
- `prompt_example_full_security_analysis_prompt.txt`
- `prompt_example_child_safety_prompt.txt`

## Execution requirements
- Python 3.8+
- A configured virtual environment (`.venv_analyse`) recommended
- Dependencies from `config.py` (`requests`, `tqdm`, `tiktoken`)
- `MISTRAL_API_KEY` environment variable for real API execution

## Typical workflow
```bash
# 1) Verify prerequisites
python analyse_conversations_merged.py --prerequis

# 2) Install dependencies (if needed)
python analyse_conversations_merged.py --install

# 3) List prompt templates
python analyse_conversations_merged.py --prompt-list

# 4) Run analysis
python analyse_conversations_merged.py --exec \
  --aiall \
  --fichier ./data_example/*.json \
  --prompt-file example_security_prompt \
  --target-logs ./logs \
  --target-results ./results \
  --format markdown
```

## Repository layout
- `analyse_conversations_merged.py`: main orchestration script.
- `prompt_executor.py`: prompt loading/formatting and API execution.
- `extractors.py`: source-format detection and message extraction.
- `result_formatter.py`: result persistence formatters.
- `install.py`: prerequisite checks and dependency installation.
- `help.py` + `help_advanced.txt`: CLI help system.
- `config.py`: constants, defaults, and API key retrieval.
- `prompts/`: reusable prompt templates.
- `data_example/`: sample input JSON files.

## Documentation index
- `README.md`: product and usage overview.
- `INSTALL.md`: installation and environment setup.
- `WHY.md`: project intent and design rationale.
- `CHANGELOG.md`: documentation update history.
