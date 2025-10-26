#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de formatage des résultats
Gère la sortie dans différents formats (CSV, JSON, TXT, Markdown)
"""

import csv
import json
import os
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path


class ResultFormatter:
    """Formate et sauvegarde les résultats dans différents formats."""
    
    @staticmethod
    def save_csv(
        results: List[Dict[str, Any]],
        output_file: str,
        include_metadata: bool = True
    ) -> bool:
        """
        Sauvegarde les résultats au format CSV.
        
        Args:
            results: Liste des résultats
            output_file: Chemin du fichier de sortie
            include_metadata: Inclure les métadonnées (fichier source, format, etc.)
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                fieldnames = [
                    "conversation_id",
                    "titre_original",
                    "titre",
                    "partie",
                    "response",
                    "success",
                    "error",
                    "token_count"
                ]
                
                if include_metadata:
                    fieldnames.extend([
                        "fichier_source",
                        "format",
                        "model_used"
                    ])
                
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    extrasaction='ignore'
                )
                writer.writeheader()
                
                # Préparer les données
                for r in results:
                    if 'fichier_source' not in r:
                        r['fichier_source'] = r.get('_source_file', 'inconnu')
                    if 'format' not in r:
                        r['format'] = r.get('_format', 'unknown')
                
                writer.writerows(results)
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur sauvegarde CSV: {e}")
            return False
    
    @staticmethod
    def save_json(
        results: List[Dict[str, Any]],
        output_file: str,
        pretty: bool = True
    ) -> bool:
        """
        Sauvegarde les résultats au format JSON.
        
        Args:
            results: Liste des résultats
            output_file: Chemin du fichier de sortie
            pretty: Formater avec indentation
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(results, f, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur sauvegarde JSON: {e}")
            return False
    
    @staticmethod
    def save_txt(
        results: List[Dict[str, Any]],
        output_file: str,
        separator: str = "\n" + "="*80 + "\n"
    ) -> bool:
        """
        Sauvegarde les résultats au format TXT simple.
        
        Args:
            results: Liste des résultats
            output_file: Chemin du fichier de sortie
            separator: Séparateur entre conversations
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # En-tête
                f.write("╔" + "═" * 78 + "╗\n")
                f.write("║" + " " * 20 + "RÉSULTATS D'ANALYSE" + " " * 39 + "║\n")
                f.write("╚" + "═" * 78 + "╝\n\n")
                
                f.write(f"Date: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
                f.write(f"Nombre de conversations: {len(results)}\n")
                f.write(f"{'─' * 80}\n\n")
                
                # Résultats
                for idx, result in enumerate(results, 1):
                    titre = result.get('titre', 'Sans titre')
                    success = result.get('success', False)
                    response = result.get('response', '')
                    error = result.get('error', '')
                    
                    f.write(f"[{idx}] {titre}\n")
                    f.write(f"{'─' * 80}\n")
                    
                    if success:
                        f.write(f"{response}\n")
                    else:
                        f.write(f"❌ ERREUR: {error}\n")
                    
                    f.write(separator)
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur sauvegarde TXT: {e}")
            return False
    
    @staticmethod
    def save_markdown(
        results: List[Dict[str, Any]],
        output_file: str,
        include_toc: bool = True
    ) -> bool:
        """
        Sauvegarde les résultats au format Markdown.
        
        Args:
            results: Liste des résultats
            output_file: Chemin du fichier de sortie
            include_toc: Inclure une table des matières
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                # En-tête
                f.write("# Résultats d'analyse de conversations\n\n")
                f.write(f"**Date**: {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}  \n")
                f.write(f"**Nombre de conversations**: {len(results)}  \n\n")
                
                # Statistiques rapides
                success_count = sum(1 for r in results if r.get('success', False))
                error_count = len(results) - success_count
                
                f.write("## 📊 Statistiques\n\n")
                f.write(f"- ✅ Succès: {success_count}\n")
                f.write(f"- ❌ Erreurs: {error_count}\n\n")
                f.write("---\n\n")
                
                # Table des matières
                if include_toc:
                    f.write("## 📑 Table des matières\n\n")
                    for idx, result in enumerate(results, 1):
                        titre = result.get('titre', 'Sans titre')
                        anchor = titre.lower().replace(' ', '-')
                        anchor = ''.join(c for c in anchor if c.isalnum() or c == '-')
                        f.write(f"{idx}. [{titre}](#{anchor})\n")
                    f.write("\n---\n\n")
                
                # Résultats détaillés
                for idx, result in enumerate(results, 1):
                    titre = result.get('titre', 'Sans titre')
                    success = result.get('success', False)
                    response = result.get('response', '')
                    error = result.get('error', '')
                    token_count = result.get('token_count', 0)
                    source_file = result.get('_source_file', 'inconnu')
                    format_type = result.get('_format', 'unknown')
                    
                    f.write(f"## {idx}. {titre}\n\n")
                    
                    # Métadonnées
                    f.write(f"**Source**: {source_file}  \n")
                    f.write(f"**Format**: {format_type.upper()}  \n")
                    f.write(f"**Tokens**: {token_count:,}  \n")
                    f.write(f"**Statut**: {'✅ Succès' if success else '❌ Erreur'}  \n\n")
                    
                    # Contenu
                    if success:
                        f.write(f"{response}\n\n")
                    else:
                        f.write(f"**Erreur**: {error}\n\n")
                    
                    f.write("---\n\n")
            
            return True
        
        except Exception as e:
            print(f"❌ Erreur sauvegarde Markdown: {e}")
            return False
