#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'extraction de messages
Gère l'extraction des messages depuis différents formats (ChatGPT, LeChat, Claude)
"""

from typing import List, Dict, Any
from utils import ecrire_log


def detecter_format_json(data: Any, fichier: str) -> str:
    """Détecte automatiquement le format du fichier JSON."""
    try:
        if isinstance(data, list):
            if len(data) > 0 and isinstance(data[0], dict):
                premier = data[0]
                if 'mapping' in premier and 'title' in premier:
                    ecrire_log(f"Format détecté: ChatGPT pour {fichier}", "INFO")
                    return 'chatgpt'
                if 'role' in premier and 'content' in premier:
                    ecrire_log(f"Format détecté: LeChat pour {fichier}", "INFO")
                    return 'lechat'
                if 'uuid' in premier and 'chat_messages' in premier:
                    ecrire_log(f"Format détecté: Claude pour {fichier}", "INFO")
                    return 'claude'

        if isinstance(data, dict):
            if 'messages' in data or 'exchanges' in data:
                ecrire_log(f"Format détecté: LeChat (dict) pour {fichier}", "INFO")
                return 'lechat'
            if 'uuid' in data and 'chat_messages' in data:
                ecrire_log(f"Format détecté: Claude pour {fichier}", "INFO")
                return 'claude'

        ecrire_log(f"Format inconnu pour {fichier}", "WARNING")
        return 'unknown'

    except Exception as e:
        ecrire_log(f"Erreur détection format {fichier}: {e}", "ERROR")
        return 'unknown'


def extraire_messages_chatgpt(conversation: Dict[str, Any]) -> List[str]:
    """Extrait les messages d'une conversation ChatGPT."""
    messages = []
    if "mapping" not in conversation:
        return messages

    mapping = conversation["mapping"]
    for node_id, node_data in mapping.items():
        if not isinstance(node_data, dict):
            continue
        message_data = node_data.get("message")
        if not message_data or not isinstance(message_data, dict):
            continue
        author = message_data.get("author", {})
        role = author.get("role", "")
        if role not in ["user", "assistant"]:
            continue
        content = message_data.get("content", {})
        if not isinstance(content, dict):
            continue
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            continue
        for part in parts:
            if isinstance(part, str) and part.strip():
                messages.append(part.strip())

    return messages


def extraire_messages_lechat(conversation: Dict[str, Any]) -> List[str]:
    """Extrait les messages d'une conversation LeChat (Mistral)."""
    messages = []
    
    if isinstance(conversation, list):
        for msg in conversation:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role", "")
            if role not in ["user", "assistant"]:
                continue

            text_parts = []
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                text_parts.append(content.strip())

            content_chunks = msg.get("contentChunks", [])
            if isinstance(content_chunks, list):
                for chunk in content_chunks:
                    if isinstance(chunk, dict) and "text" in chunk:
                        text = chunk["text"]
                        if isinstance(text, str) and text.strip():
                            text_parts.append(text.strip())

            full_text = "\n".join(text_parts)
            if full_text.strip():
                messages.append(full_text.strip())
        return messages

    msg_list = conversation.get("messages", [])
    if isinstance(msg_list, list):
        for msg in msg_list:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role", "")
            if role not in ["user", "assistant"]:
                continue

            text_parts = []
            content = msg.get("content", "")
            if isinstance(content, str) and content.strip():
                text_parts.append(content.strip())

            content_chunks = msg.get("contentChunks", [])
            if isinstance(content_chunks, list):
                for chunk in content_chunks:
                    if isinstance(chunk, dict) and "text" in chunk:
                        text = chunk["text"]
                        if isinstance(text, str) and text.strip():
                            text_parts.append(text.strip())

            full_text = "\n".join(text_parts)
            if full_text.strip():
                messages.append(full_text.strip())
        return messages

    exchanges = conversation.get("exchanges", [])
    if isinstance(exchanges, list):
        for exchange in exchanges:
            if not isinstance(exchange, dict):
                continue
            user_msg = exchange.get("user", "")
            if isinstance(user_msg, str) and user_msg.strip():
                messages.append(user_msg.strip())
            elif isinstance(user_msg, dict):
                content = user_msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    messages.append(content.strip())
            ass_msg = exchange.get("assistant", "")
            if isinstance(ass_msg, str) and ass_msg.strip():
                messages.append(ass_msg.strip())
            elif isinstance(ass_msg, dict):
                content = ass_msg.get("content", "")
                if isinstance(content, str) and content.strip():
                    messages.append(content.strip())

    return messages


def extraire_messages_claude(conversation: Dict[str, Any]) -> List[str]:
    """Extrait les messages d'une conversation Claude."""
    messages = []
    chat_messages = conversation.get("chat_messages", [])

    if not isinstance(chat_messages, list):
        return messages

    for msg in chat_messages:
        if not isinstance(msg, dict):
            continue
        sender = msg.get("sender", "")
        text = msg.get("text", "")
        if sender in ["human", "assistant"] and isinstance(text, str) and text.strip():
            messages.append(text.strip())

    return messages


def extraire_messages(conversation: Dict[str, Any], format_source: str = "auto") -> List[str]:
    """Extrait les messages selon le format."""
    if format_source == "auto":
        format_source = detecter_format_json(conversation, "conversation")

    if format_source == "lechat":
        return extraire_messages_lechat(conversation)
    elif format_source == "claude":
        return extraire_messages_claude(conversation)
    else:
        return extraire_messages_chatgpt(conversation)