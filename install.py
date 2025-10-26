#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'installation et vérification
Gère l'installation des dépendances et la vérification des prérequis
"""

import os
import sys
import shutil
import subprocess
import venv
from typing import List, Dict

# Assurez-vous que les imports locaux sont disponibles ou gérez-les
try:
    from config import ENV_DIR, DEPENDANCES
    from utils import ecrire_log
except ImportError:
    # Fallback minimal si l'import initial échoue
    ENV_DIR = ".venv_analyse"
    # Les dépendances listées dans le fichier config.py
    DEPENDANCES = ["requests", "tqdm", "tiktoken", "mistletoe", "anthropic", "python-dotenv"]
    def ecrire_log(*args, **kwargs):
        pass


# Mapping des noms de packages pip vers leurs noms d'import
PACKAGE_IMPORT_MAP: Dict[str, str] = {
    'tiktoken': 'tiktoken',
    'mistletoe': 'mistletoe',
    'anthropic': 'anthropic',
    'python-dotenv': 'dotenv',
    'tqdm': 'tqdm',
    'requests': 'requests', # Ajouté pour être complet
}


def get_import_name(package_name: str) -> str:
    """Retourne le nom d'import correspondant au nom du package pip."""
    return PACKAGE_IMPORT_MAP.get(package_name, package_name)


def verifier_prerequis_systeme() -> bool:
    """Vérifie les prérequis système (Python3, droits)."""
    ecrire_log("Vérification prérequis système", "INFO")
    print("🔍 Vérification prérequis système...")
    pre_ok = True
    if not shutil.which("python3"):
        print("❌ Python3 non trouvé")
        pre_ok = False
    if not os.geteuid() == 0:
        print("⚠️ Pas sudo, mais script gère si besoin pour install")
    print("✅ Prérequis système OK" if pre_ok else "❌ Prérequis système manquants")
    return pre_ok


def verifier_dependances() -> List[str]:
    """
    Vérifie les dépendances. Retourne une liste des dépendances manquantes.
    Si le venv n'existe pas, toutes les dépendances sont considérées comme manquantes.
    """
    venv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), ENV_DIR)

    if not os.path.exists(venv_path):
        # Si le venv n'existe pas, on considère qu'aucun package n'est installé.
        return list(DEPENDANCES)

    manquantes = []
    python_path = os.path.join(venv_path, "bin", "python3")

    if not os.path.exists(python_path):
        # Le venv existe mais pas l'exécutable, problème d'environnement/création.
        return list(DEPENDANCES)

    # Si on est dans le venv, on vérifie les packages
    print(f"🔍 Vérification des packages dans {ENV_DIR}...")
    for dep in DEPENDANCES:
        import_name = get_import_name(dep)
        try:
            # Tente de vérifier DANS le venv
            # On utilise le python du venv pour vérifier l'import
            result = subprocess.run(
                [python_path, "-c", f"import {import_name}"],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                manquantes.append(dep)
        except Exception:
            manquantes.append(dep)

    return manquantes


def verifier_prerequis_complet() -> None:
    """Vérifie tous les prérequis complets et affiche le résultat."""
    verifier_prerequis_systeme()
    manquantes = verifier_dependances()

    if manquantes:
        if len(manquantes) == len(DEPENDANCES):
            # Le venv n'est pas prêt ou est vide
            print(f"\n❌ Le venv ({ENV_DIR}) n'est pas prêt.")
        else:
            # Quelques packages manquent (cas rare)
            print(f"\n❌ Dépendances manquantes : {', '.join(manquantes)}.")

        # Message d'action clair
        print(f"   Veuillez lancer l'installation avec : `./analyse_conversations_merged.py --install`")
    else:
        print("\n✅ Toutes les dépendances sont installées et l'environnement est prêt.")


def installer_dependances() -> bool:
    """Installe les dépendances avec une boucle de robustesse."""
    ecrire_log("Installation dépendances", "INFO")

    if not os.path.exists(ENV_DIR):
        print(f"📦 Création de l'environnement virtuel...")
        try:
            venv.create(ENV_DIR, with_pip=True, symlinks=True)
            print("✅ Environnement créé.")
        except Exception as e:
            print(f"❌ Erreur de création du venv: {e}")
            return False

    pip_path = os.path.join(ENV_DIR, "bin", "pip")
    if not os.path.exists(pip_path):
        print("❌ pip introuvable dans le venv.")
        return False

    # Amélioration 1: Mise à jour/Installation de pip lui-même
    try:
        print("⚙️ Mise à jour de pip...")
        subprocess.run(
            [pip_path, "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
            text=True
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Échec de la mise à jour de pip: {e.stderr.strip()}")
        return False

    # Amélioration 2: Boucle d'installation robuste
    max_tentatives = 3
    for tentative in range(1, max_tentatives + 1):
        manquantes = verifier_dependances()

        if not manquantes:
            print("✅ Toutes les dépendances sont installées.")
            return True

        if tentative > 1:
            print(f"🔄 Tentative {tentative}/{max_tentatives}: Ré-installation des packages manquants...")
        else:
            print(f"📥 Installation de {len(manquantes)} package(s): {', '.join(manquantes)}")

        try:
            result = subprocess.run(
                [pip_path, "install", "-q"] + manquantes,
                check=True,
                capture_output=True,
                text=True
            )

            # Vérification après cette tentative
            encore_manquantes = verifier_dependances()
            if not encore_manquantes:
                print("✅ Installation terminée avec succès.")
                return True

            if tentative < max_tentatives:
                continue

            # Si c'est la dernière tentative et qu'il y a toujours des manquants
            print(f"❌ Après {max_tentatives} tentatives, des packages sont toujours manquants: {', '.join(encore_manquantes)}")
            return False

        except subprocess.CalledProcessError as e:
            print(f"❌ Échec de l'installation lors de la tentative {tentative}: {e.stderr.strip()}")
            if tentative == max_tentatives:
                return False
        except Exception as e:
            print(f"❌ Erreur inattendue lors de l'installation: {e}")
            return False

    return False

def supprimer_fichier(fichier: str, backup: bool = True) -> bool:
    """Supprime fichier avec backup horodaté si demandé."""
    from datetime import datetime

    if not os.path.exists(fichier):
        print(f"⚠️ Fichier {fichier} non trouvé")
        return False
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{fichier}.backup.{timestamp}"
        shutil.copy2(fichier, backup_file)
        print(f"💾 Backup: {backup_file}")
    os.remove(fichier)
    print(f"🗑️ Supprimé: {fichier}")
    ecrire_log(f"Supprimé {fichier} (backup: {backup_file if backup else 'non'})", "INFO")
    return True
