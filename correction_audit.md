# Corrections à appliquer (basées sur l’audit)

## Priorité haute
1. **Aligner les versions** : harmoniser `config.py` (v2.7.0) avec `analyse_conversations_merged.py` (v3.0.1) pour éviter la confusion et garantir la cohérence des logs.
2. **Unifier les dépendances** : faire converger `DEPENDANCES` de `config.py` avec la liste utilisée dans `install.py` (éviter les écarts).
3. **Documenter l’usage** : enrichir `README.md` avec installation, exemples, variables d’environnement et formats supportés.

## Priorité moyenne
4. **Factoriser `ensure_directory`** : déplacer la fonction vers `utils.py` et l’utiliser partout pour éviter la duplication.
5. **Clarifier les fichiers d’exemple** : préciser dans la documentation leur rôle (tests manuels, format attendu).

## Priorité basse
6. **Ajouter une section “Troubleshooting”** dans `README.md` pour erreurs courantes (clé API manquante, venv non activé, etc.).
7. **Ajouter un squelette de tests** (smoke test CLI) pour fiabiliser les exécutions futures.
