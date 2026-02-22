from __future__ import annotations

import json

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from .config import GEMINI_API_KEY, GEMINI_MODEL


def _model() -> ChatGoogleGenerativeAI:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is required.")
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GEMINI_API_KEY,
        temperature=0.35,
    )


def generate_json(system: str, user: str) -> dict:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system + "\nRespond strictly as valid JSON."),
            ("user", user),
        ]
    )
    chain = prompt | _model() | StrOutputParser()
    raw = chain.invoke({})
    return json.loads(raw)


def generate_text(system: str, user: str) -> str:
    prompt = ChatPromptTemplate.from_messages([("system", system), ("user", user)])
    chain = prompt | _model() | StrOutputParser()
    return chain.invoke({})
