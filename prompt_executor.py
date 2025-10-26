#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'exécution de prompts personnalisés
Gère le chargement, formatage et exécution des prompts via l'API Mistral
"""

import os
import time
import random
import re
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path


def ensure_directory(directory: str) -> Path:
    """
    Assure qu'un répertoire existe, le crée si nécessaire.
    
    Args:
        directory: Chemin du répertoire
    
    Returns:
        Path: Objet Path du répertoire créé
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


class PromptLoader:
    """Charge et gère les fichiers de prompts."""
    
    def __init__(self, prompt_dir: str = "prompts"):
        self.prompt_dir = Path(prompt_dir)
        self.prompt_dir.mkdir(exist_ok=True)
    
    def list_prompts(self) -> List[str]:
        """Liste tous les prompts disponibles."""
        if not self.prompt_dir.exists():
            return []
        
        prompts = []
        for file in self.prompt_dir.glob("prompt_*.txt"):
            # Enlever le préfixe "prompt_" et l'extension ".txt"
            prompt_name = file.stem.replace("prompt_", "")
            prompts.append(prompt_name)
        return sorted(prompts)
    
    def load_prompt(self, prompt_name: str) -> Optional[str]:
        """Charge un fichier prompt."""
        # Ajouter automatiquement le préfixe si absent
        if not prompt_name.startswith("prompt_"):
            prompt_name = f"prompt_{prompt_name}"
        
        prompt_path = self.prompt_dir / f"{prompt_name}.txt"
        
        if not prompt_path.exists():
            return None
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Erreur lecture prompt {prompt_name}: {e}")
            return None
    
    def load_prompt_from_file(self, file_path: str) -> Optional[str]:
        """Charge un prompt depuis un chemin de fichier."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Erreur lecture {file_path}: {e}")
            return None


class PromptFormatter:
    """Formate les prompts avec les variables de conversation."""
    
    @staticmethod
    def format_prompt(
        template: str,
        conversation: Dict[str, Any],
        messages: List[str]
    ) -> str:
        """
        Remplace les variables dans le template de prompt.
        
        Variables disponibles:
        - {CONVERSATION_TEXT}: Texte complet
        - {TITLE}: Titre
        - {MESSAGE_COUNT}: Nombre de messages
        - {TOKEN_COUNT}: Nombre de tokens
        - {FORMAT}: Format source
        - {FILE}: Fichier source
        """
        conversation_text = "\n\n".join(messages)
        
        variables = {
            'CONVERSATION_TEXT': conversation_text,
            'TITLE': conversation.get('title', 'Sans titre'),
            'MESSAGE_COUNT': str(len(messages)),
            'TOKEN_COUNT': str(conversation.get('token_count', 0)),
            'FORMAT': conversation.get('_format', 'unknown').upper(),
            'FILE': conversation.get('_source_file', 'inconnu')
        }
        
        # Remplacement des variables
        formatted = template
        for key, value in variables.items():
            formatted = formatted.replace(f"{{{key}}}", value)
        
        return formatted
    
    @staticmethod
    def parse_system_user(prompt: str) -> tuple:
        """
        Sépare le prompt en parties SYSTEM et USER si présent.
        
        Syntaxe:
        ---SYSTEM---
        Consignes système
        ---USER---
        Prompt utilisateur
        """
        if '---SYSTEM---' in prompt and '---USER---' in prompt:
            parts = prompt.split('---SYSTEM---', 1)[1]
            system_part, user_part = parts.split('---USER---', 1)
            return system_part.strip(), user_part.strip()
        
        # Par défaut: tout est user prompt
        return None, prompt.strip()


class PromptExecutor:
    """Exécute les prompts via l'API."""
    
    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.mistral.ai/v1/chat/completions",
        model: str = "pixtral-large-latest"
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.model = model
    
    def execute_prompt(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 16000,
        simulate: bool = False
    ) -> Dict[str, Any]:
        """
        Exécute un prompt via l'API.
        
        Returns:
            {
                'success': bool,
                'response': str,
                'error': str (si échec)
            }
        """
        if simulate:
            time.sleep(random.uniform(0.1, 0.3))
            return {
                'success': True,
                'response': '[SIMULATION] Réponse simulée du modèle',
                'simulate': True
            }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = []
        
        # Ajouter system prompt si présent
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Ajouter user prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                return {
                    'success': True,
                    'response': content,
                    'model': self.model,
                    'tokens_used': result.get('usage', {})
                }
            
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response else "Unknown"
                
                if attempt < max_retries - 1 and (status_code == 429 or status_code >= 500):
                    wait_time = 5 * (2 ** attempt) if status_code == 429 else (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                
                return {
                    'success': False,
                    'error': f"HTTP {status_code}: {str(e)}"
                }
            
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                
                return {
                    'success': False,
                    'error': "Timeout après plusieurs tentatives"
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': f"{type(e).__name__}: {str(e)}"
                }
        
        return {
            'success': False,
            'error': "Échec après tous les retry"
        }


def process_conversation_with_prompt(
    conversation: Dict[str, Any],
    messages: List[str],
    prompt_template: str,
    executor: PromptExecutor,
    simulate: bool = False,
    delay: float = 0.5
) -> Dict[str, Any]:
    """
    Traite une conversation avec un prompt personnalisé.
    
    Returns:
        {
            'conversation_id': str,
            'titre': str,
            'response': str,
            'success': bool,
            'error': str (si échec),
            'token_count': int,
            'partie': str
        }
    """
    titre = conversation.get("title", "Sans titre")
    
    base_result = {
        "conversation_id": conversation.get("conversation_id", ""),
        "titre_original": conversation.get("titre_original", titre),
        "titre": titre,
        "partie": conversation.get("partie", "1/1"),
        "_source_file": conversation.get("_source_file", "inconnu"),
        "_format": conversation.get("_format", "unknown")
    }
    
    if not messages:
        return {
            **base_result,
            "success": False,
            "response": "",
            "error": "Aucun message",
            "token_count": 0
        }
    
    # Calculer tokens
    from utils import compter_tokens
    conversation_text = "\n".join(messages)
    token_count = compter_tokens(conversation_text)
    
    # Ajouter token_count à conversation pour le formatter
    conversation['token_count'] = token_count
    
    # Formater le prompt
    formatter = PromptFormatter()
    formatted_prompt = formatter.format_prompt(prompt_template, conversation, messages)
    
    # Séparer system/user si présent
    system_prompt, user_prompt = formatter.parse_system_user(formatted_prompt)
    
    # Délai entre requêtes
    if not simulate:
        time.sleep(delay)
    
    # Exécuter le prompt
    result = executor.execute_prompt(
        user_prompt,
        system_prompt=system_prompt,
        simulate=simulate
    )
    
    return {
        **base_result,
        "success": result['success'],
        "response": result.get('response', ''),
        "error": result.get('error', ''),
        "token_count": token_count,
        "model_used": result.get('model', ''),
        "tokens_used": result.get('tokens_used', {})
    }


# ============================================
# FONCTIONS UTILITAIRES
# ============================================

def create_default_prompts(prompt_dir: str = "prompts"):
    """Crée des exemples de prompts par défaut."""
    prompt_path = Path(prompt_dir)
    prompt_path.mkdir(exist_ok=True)
    
    default_prompts = {
        "prompt_resume.txt": """Tu es un expert en résumé de conversations.

Analyse cette conversation et fournis un résumé structuré.

Conversation:
{CONVERSATION_TEXT}

Format attendu:
1. Résumé en 3 points clés
2. Sujets principaux abordés
3. Conclusions ou décisions importantes

Sois concis et factuel.""",
        
        "prompt_extract_topics.txt": """Tu es un analyste de contenu.

Extrait les sujets principaux de cette conversation.

Conversation:
{CONVERSATION_TEXT}

Liste uniquement les sujets, un par ligne, sans numérotation.""",
        
        "prompt_questions.txt": """Tu es un assistant d'analyse.

Identifie dans cette conversation:
1. Les questions posées par l'utilisateur
2. Les questions qui nécessitent un suivi

Conversation:
{CONVERSATION_TEXT}

Format: liste à puces."""
    }
    
    created = []
    for filename, content in default_prompts.items():
        file_path = prompt_path / filename
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            created.append(filename)
    
    return created
