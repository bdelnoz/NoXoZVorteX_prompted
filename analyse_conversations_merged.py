#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Nom du script: analyse_conversations_merged.py
Auteur: Bruno DELNOZ - bruno.delnoz@protonmail.com
Version: v3.0.1 - CORRECTION EXÉCUTION
Date: 2025-10-26

Script principal - Moteur d'exécution de prompts personnalisés
"""

import os
import sys
import argparse
import json
import csv
import glob
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Imports des modules locaux
from config import (
    VERSION, INPUT_FILE, MAX_WORKERS, MODEL, MAX_TOKENS,
    ENV_DIR, obtenir_api_key
)
from utils import ecrire_log, compter_tokens
from extractors import extraire_messages, detecter_format_json
from install import (
    verifier_prerequis_complet, verifier_dependances, installer_dependances,
    supprimer_fichier
)
from help import afficher_aide, afficher_aide_avancee, afficher_changelog


def ensure_directory(directory: str) -> Path:
    """
    Assure qu'un répertoire existe, le crée si nécessaire.

    Args:
        directory: Chemin du répertoire

    Returns:
        Path: Objet Path du répertoire créé
    """
    dir_path = Path(directory).resolve()
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def generer_hash_conversation(conv: Dict, format_conv: str) -> str:
    """Génère un hash unique pour détecter les doublons."""
    signature_parts = []

    titre = conv.get("title", conv.get("name", ""))
    if titre:
        signature_parts.append(f"title:{titre}")

    conv_id = conv.get("id", conv.get("uuid", conv.get("conversation_id", "")))
    if conv_id:
        signature_parts.append(f"id:{conv_id}")

    created = conv.get("create_time", conv.get("created_at", conv.get("createdAt", "")))
    if created:
        signature_parts.append(f"created:{created}")

    if format_conv == "chatgpt":
        mapping = conv.get("mapping", {})
        nb_messages = len([m for m in mapping.values() if m.get("message")])
    elif format_conv == "lechat":
        messages = conv.get("messages", conv.get("exchanges", []))
        nb_messages = len(messages)
    elif format_conv == "claude":
        messages = conv.get("chat_messages", [])
        nb_messages = len(messages)
    else:
        nb_messages = 0

    signature_parts.append(f"msgs:{nb_messages}")

    signature = "|".join(signature_parts)
    return hashlib.sha256(signature.encode('utf-8')).hexdigest()


def detecter_doublons(toutes_conversations: List[Dict]) -> Dict[str, Any]:
    """Détecte les conversations en doublon."""
    hash_map = {}
    doublons = []
    conversations_uniques = []

    for idx, conv in enumerate(toutes_conversations):
        format_conv = conv.get('_format', 'unknown')
        conv_hash = generer_hash_conversation(conv, format_conv)

        if conv_hash in hash_map:
            original_idx = hash_map[conv_hash]
            original_conv = toutes_conversations[original_idx]

            doublons.append({
                'original': {
                    'index': original_idx,
                    'titre': original_conv.get('title', original_conv.get('name', 'Sans titre')),
                    'fichier': original_conv.get('_source_file', 'inconnu'),
                    'format': original_conv.get('_format', 'unknown')
                },
                'doublon': {
                    'index': idx,
                    'titre': conv.get('title', conv.get('name', 'Sans titre')),
                    'fichier': conv.get('_source_file', 'inconnu'),
                    'format': conv.get('_format', 'unknown')
                },
                'hash': conv_hash
            })
        else:
            hash_map[conv_hash] = idx
            conversations_uniques.append(conv)

    return {
        'conversations_uniques': conversations_uniques,
        'doublons': doublons,
        'nb_total': len(toutes_conversations),
        'nb_uniques': len(conversations_uniques),
        'nb_doublons': len(doublons)
    }


def charger_fichiers(fichiers_a_traiter: List[str], format_source: str) -> tuple:
    """Charge et analyse les fichiers JSON."""
    toutes_conversations = []
    stats_chargement = {'chatgpt': 0, 'lechat': 0, 'claude': 0, 'unknown': 0, 'erreurs': 0}

    print("📂 Chargement des fichiers...")
    for fichier in fichiers_a_traiter:
        try:
            with open(fichier, "r", encoding="utf-8") as f:
                data = json.load(f)

            if format_source == "auto":
                format_detecte = detecter_format_json(data, fichier)
            else:
                format_detecte = format_source

            stats_chargement[format_detecte] = stats_chargement.get(format_detecte, 0) + 1

            if format_detecte == "chatgpt":
                if isinstance(data, list):
                    for conv in data:
                        conv['_source_file'] = os.path.basename(fichier)
                        conv['_format'] = 'chatgpt'
                        toutes_conversations.append(conv)
                    print(f"   ✅ ChatGPT: {os.path.basename(fichier)} ({len(data)} conversations)")

            elif format_detecte == "lechat":
                if isinstance(data, list):
                    titre = os.path.splitext(os.path.basename(fichier))[0]
                    import re
                    titre = re.sub(r'^chat-', '', titre)
                    titre = re.sub(r'^AI_exportation_', '', titre)
                    titre = re.sub(r'_conversations$', '', titre)
                    conv = {
                        "title": titre or "Conversation LeChat",
                        "messages": data,
                        "_source_file": os.path.basename(fichier),
                        "_format": "lechat"
                    }
                    toutes_conversations.append(conv)
                    print(f"   ✅ LeChat: {os.path.basename(fichier)} ({len(data)} messages)")
                elif isinstance(data, dict):
                    titre = data.get("title", os.path.splitext(os.path.basename(fichier))[0])
                    data['title'] = titre
                    data['_source_file'] = os.path.basename(fichier)
                    data['_format'] = 'lechat'
                    toutes_conversations.append(data)
                    nb_msg = len(data.get('messages', data.get('exchanges', [])))
                    print(f"   ✅ LeChat: {os.path.basename(fichier)} ({nb_msg} messages)")

            elif format_detecte == "claude":
                if isinstance(data, list):
                    for conv in data:
                        conv['_source_file'] = os.path.basename(fichier)
                        conv['_format'] = 'claude'
                        if 'title' not in conv and 'name' not in conv:
                            conv['title'] = f"Claude - {conv.get('uuid', 'Sans titre')[:8]}"
                        toutes_conversations.append(conv)
                    print(f"   ✅ Claude: {os.path.basename(fichier)} ({len(data)} conversations)")
                elif isinstance(data, dict):
                    data['_source_file'] = os.path.basename(fichier)
                    data['_format'] = 'claude'
                    if 'title' not in data and 'name' not in data:
                        data['title'] = f"Claude - {data.get('uuid', 'Sans titre')[:8]}"
                    toutes_conversations.append(data)
                    print(f"   ✅ Claude: {os.path.basename(fichier)} (1 conversation)")

            else:
                print(f"   ⚠️ Format inconnu: {os.path.basename(fichier)}")
                stats_chargement['unknown'] = stats_chargement.get('unknown', 0) + 1

        except json.JSONDecodeError as e:
            print(f"   ❌ Erreur JSON: {os.path.basename(fichier)}")
            ecrire_log(f"Erreur JSON {fichier}: {e}", "ERROR")
            stats_chargement['erreurs'] += 1
        except Exception as e:
            print(f"   ❌ Erreur: {os.path.basename(fichier)}")
            ecrire_log(f"Erreur {fichier}: {e}", "ERROR")
            stats_chargement['erreurs'] += 1

    return toutes_conversations, stats_chargement


def decouper_conversation(conversation: Dict[str, Any], messages: List[str]) -> List[Dict[str, Any]]:
    """Découpe une conversation si > MAX_TOKENS."""
    import uuid

    titre = conversation.get("title", "Sans titre")

    if not messages:
        return [{"title": titre, "messages": [], "partie": "1/1"}]

    texte_complet = "\n".join(messages)
    token_count = compter_tokens(texte_complet)

    if token_count <= MAX_TOKENS:
        return [{
            "title": titre,
            "messages": messages,
            "partie": "1/1",
            "titre_original": titre
        }]

    conv_id = str(uuid.uuid4())
    moitie = len(messages) // 2

    return [
        {
            "title": f"{titre} (Partie 1/2)",
            "messages": messages[:moitie],
            "conversation_id": conv_id,
            "partie": "1/2",
            "titre_original": titre
        },
        {
            "title": f"{titre} (Partie 2/2)",
            "messages": messages[moitie:],
            "conversation_id": conv_id,
            "partie": "2/2",
            "titre_original": titre
        }
    ]


def main() -> None:
    """Fonction principale."""
    temps_debut = time.time()

    if len(sys.argv) == 1:
        afficher_aide()
        return

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', action='store_true')
    parser.add_argument('--help-adv', action='store_true')
    parser.add_argument('--exec', action='store_true')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--chatgpt', action='store_true', default=False)
    parser.add_argument('--lechat', action='store_true', default=False)
    parser.add_argument('--claude', action='store_true', default=False)
    parser.add_argument('--aiall', '--auto', action='store_true', default=False)
    parser.add_argument('--simulate', action='store_true', default=False)
    parser.add_argument('--only-split', action='store_true', default=False)
    parser.add_argument('--not-split', action='store_true', default=False)
    parser.add_argument('--cnbr', type=int)
    parser.add_argument('--fichier', '-F', type=str, nargs='*', default=[INPUT_FILE])
    parser.add_argument('--model', '-m', type=str, default=MODEL)
    parser.add_argument('--workers', '-w', type=int, default=MAX_WORKERS)
    parser.add_argument('--delay', '-d', type=float, default=0.5)
    parser.add_argument('--prerequis', action='store_true')
    parser.add_argument('--changelog', action='store_true')
    parser.add_argument('--recursive', action='store_true', default=False)

    # Nouveaux arguments v3.0
    parser.add_argument('--prompt-file', '-p', type=str)
    parser.add_argument('--prompt-list', action='store_true')
    parser.add_argument('--prompt-text', '-pt', type=str)
    parser.add_argument('--format', choices=['csv', 'json', 'txt', 'markdown'], default='csv')
    parser.add_argument('--output', '-o', type=str)
    parser.add_argument('--target-logs', type=str, default='./')
    parser.add_argument('--target-results', type=str, default='./')

    args = parser.parse_args()

    # Gestion des commandes simples
    if args.help:
        afficher_aide()
        return

    if args.help_adv:
        afficher_aide_avancee()
        return

    if args.changelog:
        afficher_changelog()
        return

    if args.prerequis:
        verifier_prerequis_complet()
        return

    if args.install:
        installer_dependances()
        return

    if args.prompt_list:
        from prompt_executor import PromptLoader
        loader = PromptLoader()
        prompts = loader.list_prompts()
        if prompts:
            print("\n📋 Prompts disponibles:\n")
            for i, p in enumerate(prompts, 1):
                print(f"   {i}. {p}")
            print()
        else:
            print("\n⚠️  Aucun prompt trouvé dans le dossier 'prompts/'\n")
        return

    if not args.exec:
        print("❌ Utilisez --exec pour lancer l'analyse.")
        print("💡 Utilisez --help ou --help-adv pour plus d'informations.")
        return

    # Vérification du prompt
    if not args.prompt_file and not args.prompt_text:
        print("❌ Vous devez spécifier un prompt:")
        print("   --prompt-file <nom_du_prompt>")
        print("   OU")
        print("   --prompt-text \"votre prompt\"")
        print("\n💡 Utilisez --prompt-list pour voir les prompts disponibles")
        return

    # Créer les répertoires de sortie
    logs_dir = ensure_directory(args.target_logs)
    results_dir = ensure_directory(args.target_results)

    # Initialiser le log dans le bon répertoire
    log_filename = f"log.prompt_executor.{VERSION}.log"
    log_path = logs_dir / log_filename

    # Mettre à jour la config
    import config
    config.LOG_FILE = str(log_path)

    print(f"\n📁 Configuration des répertoires:")
    print(f"   📋 Logs     : {logs_dir}")
    print(f"   📊 Résultats: {results_dir}\n")

    # Vérification des dépendances
    api_key = None
    if not args.simulate:
        manquantes = verifier_dependances()
        if manquantes:
            print("❌ Dépendances manquantes.")
            print(f"   Activez le venv: source {ENV_DIR}/bin/activate")
            sys.exit(1)
        api_key = obtenir_api_key()

    # Charger le prompt
    from prompt_executor import PromptLoader
    loader = PromptLoader()

    if args.prompt_text:
        prompt_template = args.prompt_text
        print(f"📝 Utilisation d'un prompt direct\n")
    else:
        prompt_template = loader.load_prompt(args.prompt_file)
        if not prompt_template:
            print(f"❌ Prompt '{args.prompt_file}' introuvable")
            print("💡 Utilisez --prompt-list pour voir les prompts disponibles")
            return
        print(f"📝 Prompt chargé: {args.prompt_file}\n")

    # Déterminer le format
    if args.aiall:
        format_source = "auto"
    elif args.claude:
        format_source = "claude"
    elif args.chatgpt:
        format_source = "chatgpt"
    elif args.lechat:
        format_source = "lechat"
    else:
        format_source = "auto"

    # Recherche des fichiers
    fichier_patterns = args.fichier if isinstance(args.fichier, list) else [args.fichier]
    fichiers_a_traiter = []

    for pattern in fichier_patterns:
        if args.recursive and '**' not in pattern:
            if os.path.isdir(pattern):
                pattern = os.path.join(pattern, '**', '*.json')
            elif '*' in pattern:
                base_dir = os.path.dirname(pattern) or '.'
                filename = os.path.basename(pattern)
                pattern = os.path.join(base_dir, '**', filename)
            else:
                base_dir = os.path.dirname(pattern) or '.'
                filename = os.path.basename(pattern)
                if filename:
                    pattern = os.path.join(base_dir, '**', filename)
                else:
                    pattern = os.path.join(pattern, '**', '*.json')

        if '**' in pattern or args.recursive:
            fichiers_trouves = glob.glob(pattern, recursive=True)
        else:
            fichiers_trouves = glob.glob(pattern)

        if fichiers_trouves:
            fichiers_a_traiter.extend(fichiers_trouves)

    if not fichiers_a_traiter:
        print(f"❌ Aucun fichier trouvé")
        return

    fichiers_a_traiter = sorted(list(set(fichiers_a_traiter)))

    print("╔" + "═" * 78 + "╗")
    print("║  AI Conversation Prompt Executor v3.0.1                          ║")
    print("╚" + "═" * 78 + "╝")
    print(f"📁 Fichiers: {len(fichiers_a_traiter)}")
    print(f"🤖 Modèle: {args.model}")
    print(f"⚡ Workers: {args.workers}")
    print(f"🔄 Format: {format_source.upper()}")
    if args.simulate:
        print("🧪 Mode: SIMULATION")
    print()

    # Chargement
    toutes_conversations, stats_chargement = charger_fichiers(fichiers_a_traiter, format_source)

    if not toutes_conversations:
        print("\n❌ Aucune conversation trouvée.")
        return

    print(f"\n{'─' * 70}")
    print(f"📊 Total chargé: {len(toutes_conversations)} conversations")
    print(f"{'─' * 70}\n")

    # Détection doublons
    print("🔍 Détection des doublons...")
    rapport_doublons = detecter_doublons(toutes_conversations)

    if rapport_doublons['nb_doublons'] > 0:
        print(f"⚠️  {rapport_doublons['nb_doublons']} doublon(s) détecté(s) et exclu(s)")
    else:
        print("✅ Aucun doublon détecté")

    toutes_conversations = rapport_doublons['conversations_uniques']
    print()

    # ========================================================================
    # PARTIE AJOUTÉE - EXÉCUTION RÉELLE
    # ========================================================================

    # Extraction et découpage des messages
    print("📝 Extraction des messages...")
    conversations_a_traiter = []

    for conv in toutes_conversations:
        format_conv = conv.get('_format', 'unknown')
        messages = extraire_messages(conv, format_conv)

        if not messages:
            continue

        # Découpage si nécessaire
        conversations_decoupees = decouper_conversation(conv, messages)
        for conv_decoupee in conversations_decoupees:
            # Préserver les métadonnées
            conv_decoupee['_source_file'] = conv.get('_source_file', 'inconnu')
            conv_decoupee['_format'] = format_conv
            conversations_a_traiter.append(conv_decoupee)

    print(f"✅ {len(conversations_a_traiter)} conversations prêtes (après découpage)\n")

    # Filtrage si demandé
    if args.cnbr is not None:
        if 0 < args.cnbr <= len(conversations_a_traiter):
            conversations_a_traiter = [conversations_a_traiter[args.cnbr - 1]]
            print(f"🎯 Analyse uniquement conversation #{args.cnbr}\n")
        else:
            print(f"❌ --cnbr {args.cnbr} hors limites (1-{len(conversations_a_traiter)})")
            return

    if args.only_split:
        conversations_a_traiter = [c for c in conversations_a_traiter if '/' in c.get('partie', '')]
        print(f"✂️  Filtrage: {len(conversations_a_traiter)} conversations splittées\n")

    if args.not_split:
        conversations_a_traiter = [c for c in conversations_a_traiter if c.get('partie', '') == '1/1']
        print(f"✅ Filtrage: {len(conversations_a_traiter)} conversations non-splittées\n")

    if not conversations_a_traiter:
        print("❌ Aucune conversation à traiter après filtrage.")
        return

    # Initialisation de l'exécuteur
    from prompt_executor import PromptExecutor, process_conversation_with_prompt

    executor = None
    if not args.simulate:
        executor = PromptExecutor(
            api_key=api_key,
            model=args.model
        )
    else:
        # Mode simulation: créer un executor factice
        class SimulateExecutor:
            def __init__(self):
                self.model = args.model
        executor = SimulateExecutor()

    # Exécution parallèle
    print(f"🚀 Démarrage de l'analyse ({args.workers} workers)...\n")
    resultats = []

    try:
        from tqdm import tqdm
    except ImportError:
        print("⚠️  Module tqdm non disponible, progression sans barre visuelle")
        tqdm = None

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}

        for conv in conversations_a_traiter:
            messages = conv.get('messages', [])
            future = pool.submit(
                process_conversation_with_prompt,
                conv,
                messages,
                prompt_template,
                executor,
                args.simulate,
                args.delay
            )
            futures[future] = conv.get('titre', 'Sans titre')

        # Barre de progression
        if tqdm:
            with tqdm(total=len(futures), desc="Analyse", unit="conv") as pbar:
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        resultats.append(result)
                        pbar.update(1)
                    except Exception as e:
                        titre = futures[future]
                        ecrire_log(f"Erreur traitement '{titre}': {e}", "ERROR")
                        print(f"\n⚠️  Erreur: {titre}")
                        pbar.update(1)
        else:
            # Sans tqdm
            completed = 0
            for future in as_completed(futures):
                try:
                    result = future.result()
                    resultats.append(result)
                    completed += 1
                    if completed % 10 == 0:
                        print(f"   Progression: {completed}/{len(futures)}")
                except Exception as e:
                    titre = futures[future]
                    ecrire_log(f"Erreur traitement '{titre}': {e}", "ERROR")
                    print(f"⚠️  Erreur: {titre}")
                    completed += 1

    # Sauvegarde des résultats
    print(f"\n💾 Sauvegarde des résultats...")

    from result_formatter import ResultFormatter
    formatter = ResultFormatter()

    # Générer nom de fichier de sortie
    if args.output:
        output_base = args.output
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_name = args.prompt_file if args.prompt_file else "custom"
        output_base = f"results_{prompt_name}_{timestamp}"

    # Ajouter l'extension selon le format
    if not any(output_base.endswith(ext) for ext in ['.csv', '.json', '.txt', '.md', '.markdown']):
        if args.format == 'csv':
            output_file = f"{output_base}.csv"
        elif args.format == 'json':
            output_file = f"{output_base}.json"
        elif args.format == 'txt':
            output_file = f"{output_base}.txt"
        elif args.format == 'markdown':
            output_file = f"{output_base}.md"
    else:
        output_file = output_base

    output_path = results_dir / output_file

    # Sauvegarder selon le format
    success = False
    if args.format == 'csv':
        success = formatter.save_csv(resultats, str(output_path))
    elif args.format == 'json':
        success = formatter.save_json(resultats, str(output_path))
    elif args.format == 'txt':
        success = formatter.save_txt(resultats, str(output_path))
    elif args.format == 'markdown':
        success = formatter.save_markdown(resultats, str(output_path))

    if success:
        print(f"✅ Résultats sauvegardés: {output_path}")
        print(f"   📊 Format: {args.format.upper()}")
        file_size = os.path.getsize(output_path)
        print(f"   📁 Taille: {file_size:,} octets")
    else:
        print(f"❌ Erreur lors de la sauvegarde")

    # Statistiques finales
    temps_total = time.time() - temps_debut
    success_count = sum(1 for r in resultats if r.get('success', False))
    error_count = len(resultats) - success_count

    print(f"\n{'═' * 70}")
    print(f"📊 RAPPORT FINAL")
    print(f"{'═' * 70}")
    print(f"⏱️  Temps total: {temps_total:.2f}s")
    print(f"✅ Succès: {success_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📊 Total traité: {len(resultats)}")
    if len(resultats) > 0:
        print(f"📈 Taux de succès: {(success_count/len(resultats)*100):.1f}%")
    print(f"{'═' * 70}\n")

    ecrire_log(f"Analyse terminée: {success_count} succès, {error_count} erreurs", "INFO")


if __name__ == "__main__":
    # Relance automatique dans le venv si nécessaire
    venv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ENV_DIR)
    is_in_venv = hasattr(sys, 'real_prefix') or (sys.prefix != sys.base_prefix) or (venv_path in sys.executable)

    should_relaunch = (
        os.path.exists(venv_path) and
        not is_in_venv and
        '--install' not in sys.argv and
        '--help' not in sys.argv and
        '--help-adv' not in sys.argv and
        len(sys.argv) > 1
    )

    if should_relaunch:
        python_path = os.path.join(venv_path, "bin", "python3")
        if os.path.exists(python_path):
            try:
                os.execv(python_path, [python_path] + sys.argv)
            except Exception as e:
                print(f"⚠️  Avertissement: Échec relance venv: {e}")

    main()
