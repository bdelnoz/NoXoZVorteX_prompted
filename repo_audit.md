# Audit du dépôt NoXoZVorteX_prompted

## 1) Inventaire des fichiers (par domaine/fonction)

### Backend / cœur applicatif (Python)
- `analyse_conversations_merged.py`
- `config.py`
- `extractors.py`
- `prompt_executor.py`
- `result_formatter.py`
- `utils.py`
- `install.py`
- `help.py`

### Frontend
- Aucun fichier front-end (pas de HTML/CSS/JS).

### Data / exemples
- `data_example/example_claude_json.json`
- `data_example/example_chatgpt_json.json`
- `data_example/example_lechat_json.json`

### Prompts / templates
- `prompts/prompt_example_child_safety_prompt.txt`
- `prompts/prompt_example_security_prompt.txt`
- `prompts/prompt_example_full_security_analysis_prompt.txt`

### Scripts (CLI / outils)
- Tous les scripts sont en Python (voir section Backend).
- Aucun script `.sh`.

### Documentation
- `README.md`
- `TRY_THIS_FIRST.txt`
- `help_advanced.txt`
- `LICENSE`

### Configuration
- `config.py`
- `.gitignore`

### Infra / CI / déploiement
- Aucun fichier dédié (pas de Dockerfile, CI, etc.).

### Tests
- Aucun dossier/fichier de tests.

## 2) Fichiers clés par domaine et usage

### Backend / cœur applicatif
- `analyse_conversations_merged.py` : point d’entrée CLI. Charge les exports JSON, détecte les doublons, découpe les conversations, exécute les prompts via l’API Mistral (ou simulation), puis sauvegarde les résultats en CSV/JSON/TXT/Markdown.
- `prompt_executor.py` : gestion des prompts (chargement, formatage), exécution des requêtes API Mistral avec retry, traitement d’une conversation pour produire un résultat.
- `extractors.py` : détection du format JSON (ChatGPT/LeChat/Claude) et extraction des messages.
- `result_formatter.py` : sérialisation des résultats dans plusieurs formats (CSV/JSON/TXT/Markdown).
- `utils.py` : logging, nettoyage du texte, comptage approximatif des tokens, génération de noms de sorties.
- `config.py` : constantes (version, modèle, limites, dépendances, etc.) et récupération de la clé API.
- `install.py` : création du venv, vérification/installation des dépendances et nettoyage de fichiers.
- `help.py` : aide CLI, aide avancée et changelog.

### Data / exemples
- `data_example/*.json` : fichiers d’exemples pour ChatGPT, LeChat et Claude.

### Prompts / templates
- `prompts/*.txt` : exemples de prompts utilisés par le moteur.

### Documentation
- `TRY_THIS_FIRST.txt` : commande d’exemple rapide.
- `help_advanced.txt` : aide CLI détaillée (long format).
- `README.md` : description minimale du dépôt.
- `LICENSE` : licence du projet.

### Configuration
- `config.py` : paramètres du runtime (API, modèles, limites, etc.).
- `.gitignore` : exclusions Git.

## 3) Structure globale du projet

### Points d’entrée
- `analyse_conversations_merged.py` est le point d’entrée principal (CLI). Il orchestre l’ensemble du flux :
  1. Lecture des arguments et validation.
  2. Chargement des JSON et détection de format.
  3. Déduplication et découpage des conversations.
  4. Exécution du prompt (API Mistral ou mode simulation).
  5. Sauvegarde des résultats (CSV/JSON/TXT/Markdown).

### Modules principaux
- **Extraction & normalisation** : `extractors.py`.
- **Exécution de prompts** : `prompt_executor.py`.
- **Formatage des résultats** : `result_formatter.py`.
- **Utilitaires** : `utils.py`.
- **Configuration** : `config.py`.

### Flux de données (résumé)
- Entrée : exports JSON (ChatGPT/LeChat/Claude) -> `analyse_conversations_merged.py` -> `extractors.py`.
- Transformation : assemblage du texte + découpage par tokens -> `prompt_executor.py`.
- Sortie : résultats via `result_formatter.py`.

### Dépendances majeures (Python)
- `requests` (appels API Mistral), `tqdm` (progression), `tiktoken` (comptage tokens), `argparse`, `concurrent.futures`.

## 4) API
- Aucune API interne exposée (pas de FastAPI/Flask/Express). Le projet consomme l’API Mistral via HTTP.

## 5) Scripts `.sh`
- Aucun.

## 6) Scripts `.py` (usage + imports)

### `analyse_conversations_merged.py`
- Usage : CLI principal (analyse, extraction, exécution de prompts).
- Imports notables : `argparse`, `json`, `csv`, `glob`, `hashlib`, `concurrent.futures`, modules locaux (`config`, `utils`, `extractors`, `install`, `help`, `prompt_executor`, `result_formatter`).

### `prompt_executor.py`
- Usage : chargement/formatage des prompts, exécution API Mistral, traitement conversation.
- Imports notables : `requests`, `random`, `time`, `pathlib`, `typing`.

### `extractors.py`
- Usage : détecte le format JSON (ChatGPT/LeChat/Claude) et extrait les messages.
- Imports notables : `typing`, `utils.ecrire_log`.

### `result_formatter.py`
- Usage : écrit les résultats dans plusieurs formats (CSV/JSON/TXT/Markdown).
- Imports notables : `csv`, `json`, `datetime`, `pathlib`.

### `utils.py`
- Usage : logging, nettoyage texte, tokens, génération noms de sortie.
- Imports notables : `re`, `datetime`, `tiktoken` (optionnel).

### `config.py`
- Usage : constantes globales + récupération clé API.
- Imports notables : `os`.

### `install.py`
- Usage : vérification prérequis, création venv, installation dépendances.
- Imports notables : `subprocess`, `venv`, `shutil`.

### `help.py`
- Usage : affichage aide standard/avancée.
- Imports notables : `pathlib`, `config`.

## 7) Duplications, conflits potentiels, obsolescence
- **Versions incohérentes** : `analyse_conversations_merged.py` annonce v3.0.1 alors que `config.py` est en v2.7.0 (risque de confusion sur les logs et paramètres).
- **Redondance `ensure_directory`** : fonction similaire dans `analyse_conversations_merged.py` et `prompt_executor.py`.
- **Dépendances divergentes** : `install.py` déclare des dépendances de fallback (`mistletoe`, `anthropic`, `python-dotenv`) non listées dans `config.py`.
- **Docs minimales** : `README.md` ne décrit pas l’usage, ce qui peut être perçu comme obsolète/incomplet.

## 8) Tableau synthétique des fichiers

| Chemin | Usage |
| --- | --- |
| `analyse_conversations_merged.py` | CLI principal d’analyse et d’exécution de prompts. |
| `config.py` | Configuration globale (versions, API, limites). |
| `extractors.py` | Détection de format JSON + extraction de messages. |
| `prompt_executor.py` | Chargement/formatage de prompts et exécution API. |
| `result_formatter.py` | Export des résultats (CSV/JSON/TXT/Markdown). |
| `utils.py` | Utilitaires (log, nettoyage, tokens, noms). |
| `install.py` | Installation dépendances + venv. |
| `help.py` | Aide CLI standard/avancée. |
| `data_example/*.json` | Exemples de données (ChatGPT/LeChat/Claude). |
| `prompts/*.txt` | Exemples de prompts. |
| `README.md` | Description minimale. |
| `TRY_THIS_FIRST.txt` | Exemple de commande rapide. |
| `help_advanced.txt` | Aide CLI détaillée. |
| `.gitignore` | Exclusions Git. |
| `LICENSE` | Licence. |

## 9) Tableau des endpoints
- Non applicable (aucune API exposée).
