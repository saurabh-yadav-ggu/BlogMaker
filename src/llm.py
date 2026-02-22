from __future__ import annotations

import json
from json import JSONDecodeError

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import get_settings


def _model() -> ChatGoogleGenerativeAI:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY is required.")
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.3,
    )


def generate_json(system: str, user: str) -> dict:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system
                + "\nReturn only valid JSON without markdown fences."
                + "\nIf unsure, return an empty JSON object.",
            ),
            ("user", user),
        ]
    )
    raw = (prompt | _model() | StrOutputParser()).invoke({}).strip()
    try:
        return json.loads(raw)
    except JSONDecodeError as exc:
        raise ValueError(f"Model did not return valid JSON: {raw[:250]}") from exc


def generate_text(system: str, user: str) -> str:
    prompt = ChatPromptTemplate.from_messages([("system", system), ("user", user)])
    return (prompt | _model() | StrOutputParser()).invoke({}).strip()
