from __future__ import annotations

import os

import requests


def generate_book_summary(book: dict) -> str | None:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    base_url = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta").rstrip("/")

    if not api_key:
        return None

    prompt = (
        "Write a clear, factual summary of approximately 500 words for this book. "
        "Return plain text only.\n"
        f"ISBN: {book['ISBN']}\n"
        f"Title: {book['title']}\n"
        f"Author: {book['Author']}\n"
        f"Description: {book['description']}\n"
        f"Genre: {book['genre']}\n"
    )

    url = f"{base_url}/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are a concise book summarizer. "
                            "Return plain text only.\n\n"
                            + prompt
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
        },
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None

        text_fragments = [part.get("text", "") for part in parts if isinstance(part.get("text"), str)]
        combined = "\n".join(fragment for fragment in text_fragments if fragment.strip())
        return combined.strip() if combined.strip() else None
    except Exception:
        return None
