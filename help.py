#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'aide
Affiche l'aide standard, avancée et le changelog
"""

import os
from pathlib import Path
from config import VERSION, MAX_TOKENS, MAX_WORKERS, MODEL


def afficher_aide() -> None:
    """Affiche l'aide standard du script."""
    aide = f"""
╔═══════════════════════════════════════════════════════════════╗
║  AI Conversation Prompt Executor {VERSION}                     ║
╚═══════════════════════════════════════════════════════════════╝

Version: {VERSION}
Auteur: Bruno DELNOZ

## DESCRIPTION
Moteur d'exécution de prompts personnalisés sur conversations AI.
Supporte ChatGPT, Claude et LeChat/Mistral.

## CONFIGURATION API
export MISTRAL_API_KEY='votre_clé_api'

## OPTIONS PRINCIPALES
  --help              Affiche cette aide
  --help-adv          Affiche l'aide avancée complète ⭐
  --exec              Lance l'analyse
  --install           Installe les dépendances
  --prerequis         Vérifie les prérequis
  --changelog         Affiche le changelog

## FORMATS SUPPORTÉS
  --chatgpt           Format d'export ChatGPT
  --lechat            Format d'export LeChat (Mistral)
  --claude            Format d'export Claude
  --aiall, --auto     Auto-détection de TOUS les formats

## PROMPTS ⭐ NOUVEAU
  --prompt-file FILE  Fichier prompt à utiliser (dans prompts/)
  --prompt-list       Liste tous les prompts disponibles
  --prompt-text TEXT  Prompt direct en ligne de commande

## SOURCES DE DONNÉES
  --fichier, -F FILE  Fichier(s) JSON (supporte *.json)
  --recursive         Recherche récursive dans sous-dossiers

## OPTIONS D'EXÉCUTION
  --model, -m MODEL   Modèle Mistral (défaut: {MODEL})
  --workers, -w N     Workers parallèles (défaut: {MAX_WORKERS})
  --simulate          Mode simulation (pas d'appel API)

## ORGANISATION DES FICHIERS ⭐ NOUVEAU
  --target-logs DIR   Dossier pour les logs (défaut: ./)
  --target-results    Dossier pour les résultats (défaut: ./)
  --format FORMAT     csv, json, txt, markdown (défaut: csv)
  --output, -o FILE   Nom du fichier de sortie personnalisé

## EXEMPLES RAPIDES

1. Lister les prompts disponibles:
   python analyse_conversations_merged.py --prompt-list

2. Analyse simple avec prompt:
   python analyse_conversations_merged.py --exec \\
     --aiall --fichier *.json \\
     --prompt-file resume

3. Organisation complète:
   python analyse_conversations_merged.py --exec \\
     --prompt-file security_analysis \\
     --fichier data/*.json \\
     --target-logs ./logs \\
     --target-results ./results \\
     --format markdown

4. Mode simulation (test sans API):
   python analyse_conversations_merged.py --exec \\
     --simulate --prompt-file test \\
     --fichier export.json

💡 Pour plus de détails et d'exemples: --help-adv
📚 Documentation complète: voir STRUCTURE.md
"""
    print(aide)


def afficher_aide_avancee() -> None:
    """Affiche l'aide avancée complète depuis help_advanced.txt."""
    help_file = Path("help_advanced.txt")
    
    if help_file.exists():
        try:
            with open(help_file, 'r', encoding='utf-8') as f:
                contenu = f.read()
            print(contenu)
        except Exception as e:
            print(f"❌ Erreur lecture help_advanced.txt: {e}")
            afficher_aide_avancee_integree()
    else:
        print(f"⚠️  Fichier help_advanced.txt introuvable")
        print(f"💡 Création du fichier avec le contenu par défaut...\n")
        creer_help_advanced_defaut()
        afficher_aide_avancee_integree()


def afficher_aide_avancee_integree() -> None:
    """Affiche l'aide avancée intégrée si le fichier n'existe pas."""
    aide_avancee = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║             AI CONVERSATION PROMPT EXECUTOR - AIDE AVANCÉE                    ║
║                           Version {VERSION}                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════════════════════════
📋 TABLE DES MATIÈRES
═══════════════════════════════════════════════════════════════════════════════

1. Arguments détaillés
2. Gestion des prompts
3. Variables disponibles
4. Formats de sortie
5. Exemples avancés
6. Troubleshooting

═══════════════════════════════════════════════════════════════════════════════
1. ARGUMENTS DÉTAILLÉS
═══════════════════════════════════════════════════════════════════════════════

## Arguments principaux
  --help              Aide standard (rapide)
  --help-adv          Cette aide (complète)
  --exec              Exécute le traitement
  --install           Installe les dépendances dans .venv_analyse
  --prerequis         Vérifie Python >= 3.8, droits, modules
  --changelog         Historique des versions

## Formats source
  --chatgpt           Force format ChatGPT
  --lechat            Force format LeChat/Mistral  
  --claude            Force format Claude
  --aiall / --auto    Auto-détection (recommandé)

## Prompts (OBLIGATOIRE avec --exec)
  --prompt-file FILE  Charge prompts/prompt_FILE.txt
                      Exemples: resume, security_analysis, child_safety_analysis
  --prompt-list       Liste tous les prompts/ disponibles
  --prompt-text TEXT  Prompt direct sans fichier

## Sources de données
  --fichier, -F       Un ou plusieurs fichiers JSON
                      Supporte wildcards: *.json, data/*.json
  --recursive         Recherche récursive dans sous-dossiers
                      Combiné avec --fichier pour chercher partout

## Filtres
  --cnbr N            Analyse uniquement la conversation N
  --only-split        Uniquement conversations > {MAX_TOKENS} tokens
  --not-split         Uniquement conversations ≤ {MAX_TOKENS} tokens

## Exécution
  --model, -m MODEL   Modèle Mistral (défaut: {MODEL})
  --workers, -w N     Workers parallèles (défaut: {MAX_WORKERS})
  --delay, -d SEC     Délai entre requêtes (défaut: 0.5s)
  --simulate          Mode dry-run (pas d'appel API)

## Organisation des fichiers
  --target-logs DIR   Dossier logs (créé auto si absent)
  --target-results    Dossier résultats (créé auto si absent)
  --format FORMAT     csv | json | txt | markdown
  --output, -o FILE   Nom personnalisé du fichier de sortie

═══════════════════════════════════════════════════════════════════════════════
2. GESTION DES PROMPTS
═══════════════════════════════════════════════════════════════════════════════

## Structure d'un prompt

Les prompts sont des fichiers texte dans prompts/ avec le préfixe prompt_

Exemple: prompts/prompt_resume.txt

### Format simple:
```
Tu es un expert en [DOMAINE].

Analyse cette conversation et [OBJECTIF].

Conversation:
{{CONVERSATION_TEXT}}

Format de sortie:
[Instructions]
```

### Format avancé (SYSTEM/USER):
```
---SYSTEM---
Tu es un expert en [DOMAINE] avec [EXPÉRIENCE].
Tes compétences: [LISTE]

---USER---
# ANALYSE DE [TYPE]

## CONTEXTE
- Titre: {TITLE}
- Messages: {MESSAGE_COUNT}
- Tokens: {TOKEN_COUNT}
- Format: {FORMAT}
- Fichier: {FILE}

## MISSION
[Instructions détaillées]

Conversation:
{CONVERSATION_TEXT}
```

## Variables disponibles

Dans vos prompts, utilisez ces variables entre accolades:

- {CONVERSATION_TEXT}  - Texte complet de la conversation
- {TITLE}              - Titre de la conversation
- {MESSAGE_COUNT}      - Nombre de messages
- {TOKEN_COUNT}        - Nombre de tokens
- {FORMAT}             - Format source (CHATGPT/LECHAT/CLAUDE)
- {FILE}               - Nom du fichier source

## Prompts fournis par défaut

- prompt_resume.txt              - Résumé en 3 points
- prompt_extract_topics.txt      - Liste des sujets
- prompt_questions.txt           - Questions posées
- prompt_security_analysis.txt   - Analyse de sécurité complète
- prompt_child_safety_analysis.txt - Sécurité contenu enfants

═══════════════════════════════════════════════════════════════════════════════
3. FORMATS DE SORTIE
═══════════════════════════════════════════════════════════════════════════════

## CSV (par défaut)
Colonnes: conversation_id, titre, partie, response, success, error,
          token_count, fichier_source, format, model_used

Avantages: Excel/LibreOffice compatible, facile à filtrer

## JSON
Structure hiérarchique avec tous les champs
Avantages: Facile à parser, typage préservé

## TXT
Format lisible avec séparateurs visuels
Avantages: Lecture directe, aucun outil nécessaire

## Markdown
Format avec table des matières, métadonnées, statistiques
Avantages: GitHub preview, export PDF/HTML

═══════════════════════════════════════════════════════════════════════════════
4. EXEMPLES AVANCÉS
═══════════════════════════════════════════════════════════════════════════════

## Exemple 1: Workflow complet de sécurité
```bash
# 1. Installation
python analyse_conversations_merged.py --install

# 2. Vérification
python analyse_conversations_merged.py --prerequis

# 3. Liste des prompts
python analyse_conversations_merged.py --prompt-list

# 4. Analyse de sécurité sur tous les JSON
export MISTRAL_API_KEY='votre_clé'
python analyse_conversations_merged.py --exec \\
  --aiall --recursive \\
  --fichier ./data/ \\
  --prompt-file security_analysis \\
  --target-logs ./logs/security \\
  --target-results ./reports/security \\
  --format markdown \\
  --workers 10
```

## Exemple 2: Test rapide avec simulation
```bash
python analyse_conversations_merged.py --exec \\
  --simulate \\
  --prompt-file resume \\
  --fichier test.json \\
  --format json
```

## Exemple 3: Analyse d'un fichier spécifique
```bash
python analyse_conversations_merged.py --exec \\
  --chatgpt \\
  --fichier export_20251026.json \\
  --prompt-file extract_topics \\
  --output topics_report.txt \\
  --format txt
```

## Exemple 4: Multi-fichiers avec filtrage
```bash
# Uniquement les longues conversations
python analyse_conversations_merged.py --exec \\
  --aiall \\
  --fichier data/*.json \\
  --only-split \\
  --prompt-file security_analysis \\
  --target-results ./results/long_conversations
```

## Exemple 5: Prompt direct sans fichier
```bash
python analyse_conversations_merged.py --exec \\
  --aiall --fichier *.json \\
  --prompt-text "Liste les 5 sujets principaux de cette conversation"
```

## Exemple 6: Organisation professionnelle
```bash
# Structure recommandée:
# projet/
# ├── data/           (vos exports)
# ├── logs/           (logs générés)
# ├── results/        (résultats)
# └── prompts/        (vos prompts)

python analyse_conversations_merged.py --exec \\
  --recursive --aiall \\
  --fichier ./data/ \\
  --prompt-file custom_analysis \\
  --target-logs ./logs/$(date +%Y%m%d) \\
  --target-results ./results/$(date +%Y%m%d) \\
  --format markdown \\
  --workers 15
```

═══════════════════════════════════════════════════════════════════════════════
5. TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

## Problème: "Aucun prompt spécifié"
Solution: Utilisez --prompt-file <nom> ou --prompt-text "..."

## Problème: "Prompt introuvable"
Solutions:
- Vérifiez que le fichier existe: prompts/prompt_<nom>.txt
- Utilisez --prompt-list pour voir les prompts disponibles
- Le préfixe prompt_ est automatique: --prompt-file resume suffit

## Problème: "Dépendances manquantes"
Solutions:
1. Lancez: python analyse_conversations_merged.py --install
2. Activez le venv: source .venv_analyse/bin/activate
3. Relancez votre commande

## Problème: "API key non définie"
Solution: export MISTRAL_API_KEY='votre_clé'

## Problème: "Format inconnu"
Solutions:
- Utilisez --aiall pour auto-détection
- Vérifiez la structure de votre JSON
- Consultez les logs dans --target-logs

## Problème: "Erreur HTTP 429 (rate limit)"
Solutions:
- Augmentez --delay: --delay 1.0
- Réduisez --workers: --workers 3
- Attendez quelques minutes

## Problème: Conversations trop longues
Le script découpe automatiquement les conversations > {MAX_TOKENS} tokens
en 2 parties. Vous pouvez:
- Filtrer avec --only-split ou --not-split
- Voir les conversations splittées dans le rapport final

═══════════════════════════════════════════════════════════════════════════════
6. BONNES PRATIQUES
═══════════════════════════════════════════════════════════════════════════════

## Organisation des fichiers
```
mon_projet/
├── data/                      # Vos exports JSON
│   ├── chatgpt/
│   ├── claude/
│   └── lechat/
├── prompts/                   # Vos prompts personnalisés
│   ├── prompt_resume.txt
│   └── prompt_custom.txt
├── logs/                      # Logs (auto-créé)
│   └── 2025-10-26/
└── results/                   # Résultats (auto-créé)
    └── 2025-10-26/
```

## Nommage des prompts
- Toujours préfixer: prompt_<nom>.txt
- Utiliser snake_case: prompt_security_analysis.txt
- Être descriptif: prompt_extract_technical_skills.txt

## Sécurité API
- Ne jamais commiter MISTRAL_API_KEY
- Utiliser des variables d'environnement
- Tester avec --simulate d'abord

## Performance
- Commencer avec --workers 5
- Augmenter progressivement selon votre machine
- Utiliser --only-split pour traiter les longues conversations séparément

## Workflow recommandé
1. --install (une seule fois)
2. --prerequis (vérification)
3. --prompt-list (voir les prompts)
4. --simulate (test sans API)
5. --exec (exécution réelle)

═══════════════════════════════════════════════════════════════════════════════
📞 SUPPORT
═══════════════════════════════════════════════════════════════════════════════

Auteur: Bruno DELNOZ
Email: bruno.delnoz@protonmail.com
Version: {VERSION}

Documentation complète: voir STRUCTURE.md
Changelog: --changelog

═══════════════════════════════════════════════════════════════════════════════
"""
    print(aide_avancee)


def creer_help_advanced_defaut() -> None:
    """Crée le fichier help_advanced.txt avec le contenu par défaut."""
    help_file = Path("help_advanced.txt")
    
    contenu = """╔═══════════════════════════════════════════════════════════════════════════════╗
║             AI CONVERSATION PROMPT EXECUTOR - AIDE AVANCÉE                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

Ce fichier peut être édité pour personnaliser l'aide avancée.
Voir help.py pour le contenu par défaut complet.

Pour régénérer ce fichier: supprimez-le et relancez --help-adv
"""
    
    try:
        with open(help_file, 'w', encoding='utf-8') as f:
            f.write(contenu)
        print(f"✅ Fichier {help_file} créé avec succès\n")
    except Exception as e:
        print(f"❌ Erreur création {help_file}: {e}\n")


def afficher_changelog() -> None:
    """Affiche le changelog complet."""
    print(f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                           CHANGELOG COMPLET                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

v3.0.0 (2025-10-26) - REFONTE MAJEURE
  ★ Système de prompts personnalisables (prompt_*.txt)
  ★ Suppression du mode --local (uniquement API maintenant)
  ★ --prompt-file: fichiers prompts dans prompts/
  ★ --prompt-list: liste tous les prompts disponibles
  ★ --prompt-text: prompt direct en ligne de commande
  ★ --help-adv: aide avancée complète depuis help_advanced.txt
  ★ --target-logs: dossier personnalisé pour les logs
  ★ --target-results: dossier personnalisé pour les résultats
  ★ --format: csv, json, txt, markdown
  ★ Détection et élimination automatique des doublons
  ★ Variables dans les prompts: {{CONVERSATION_TEXT}}, {{TITLE}}, etc.
  ★ Support SYSTEM/USER prompt avec ---SYSTEM--- / ---USER---
  ★ Création automatique des dossiers (mkdir -p équivalent)
  ★ Module prompt_executor.py: gestion complète des prompts
  ★ Module result_formatter.py: formats de sortie multiples
  ★ Architecture simplifiée: 8 fichiers au lieu de 12
  ★ Documentation STRUCTURE.md complète

v2.7.5 (2025-10-22):
  - Fix erreur import verifier_prerequis
  - Correction logique finale

v2.7.0 (2025-10-19):
  - Génération automatique fichier TXT avec tous les sujets
  - Rapport ultra-complet des opérations
  - Indicateur split visuel (✂️/✅)
  - Temps d'exécution + performance
  - Espace disque total utilisé

v2.6.0 (2025-10-19):
  - Rapport complet des opérations
  - Statistiques détaillées split vs non-split
  - Tableau récapitulatif des fichiers

v2.5.0 (2025-10-19):
  - Auto-détection multi-formats
  - Support ChatGPT/LeChat/Claude simultané
  - Focus IA renforcé (score x3)
  - 35+ domaines de compétences
  - Logging complet avec rotation

v2.4.0 (2025-10-19):
  - AUTO-DÉTECTION MULTI-FORMATS
  - --aiall: traite tous les formats

v2.3.0 (2025-10-18):
  - Priorité maximale sur compétences IA/ML
  - Détection exhaustive IA
  - Catégorisation automatique

═══════════════════════════════════════════════════════════════════════════════
""")
