# Test Audit

## Tests unitaires
- Commande: `python -m unittest discover`
- Résultat:
```
----------------------------------------------------------------------
Ran 0 tests in 0.000s

OK
```

## Test global (smoke test CLI)
- Commande: `python analyse_conversations_merged.py --help`
- Résultat:
```
╔═══════════════════════════════════════════════════════════════╗
║  AI Conversation Prompt Executor v2.7.0                     ║
╚═══════════════════════════════════════════════════════════════╝

Version: v2.7.0
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
  --model, -m MODEL   Modèle Mistral (défaut: pixtral-large-latest)
  --workers, -w N     Workers parallèles (défaut: 5)
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
   python analyse_conversations_merged.py --exec \
     --aiall --fichier *.json \
     --prompt-file resume

3. Organisation complète:
   python analyse_conversations_merged.py --exec \
     --prompt-file security_analysis \
     --fichier data/*.json \
     --target-logs ./logs \
     --target-results ./results \
     --format markdown

4. Mode simulation (test sans API):
   python analyse_conversations_merged.py --exec \
     --simulate --prompt-file test \
     --fichier export.json

💡 Pour plus de détails et d'exemples: --help-adv
📚 Documentation complète: voir STRUCTURE.md
```
