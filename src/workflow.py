from __future__ import annotations

import re
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from .llm import generate_json, generate_text
from .models import BlogRequest, FinalBlogPackage
from .nano_banana import NanoBananaClient
from .seo import estimate_seo_score


class WorkflowState(TypedDict):
    request: BlogRequest
    research: dict[str, Any]
    outline: dict[str, Any]
    draft: dict[str, Any]
    seo: dict[str, Any]
    image_prompts: list[str]
    images: list[dict[str, Any]]
    errors: list[str]


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", text).strip().lower()
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug or "blog-post"


def research_node(state: WorkflowState) -> WorkflowState:
    request = state["request"]
    state["research"] = generate_json(
        "You are an expert SEO strategist.",
        (
            "Create keyword research for this topic. Return keys: "
            "search_intent, primary_keywords, secondary_keywords, faq_questions. "
            f"Topic: {request.topic}. Audience: {request.audience}."
        ),
    )
    return state


def outline_node(state: WorkflowState) -> WorkflowState:
    state["outline"] = generate_json(
        "You design SEO blog outlines that rank.",
        (
            "Create an outline with keys: title, slug, meta_description, h2_sections. "
            "Each h2 section should contain heading and bullet_points. "
            f"Use this research context: {state['research']}"
        ),
    )
    return state


def draft_node(state: WorkflowState) -> WorkflowState:
    request = state["request"]
    outline = state["outline"]
    research = state["research"]

    markdown = generate_text(
        "You are a senior content writer. Output markdown only.",
        (
            "Write a complete, SEO-optimized blog post with clear headings, "
            "internal-link placeholders, a short intro, and strong CTA conclusion. "
            f"Target words: {request.target_words}. Tone: {request.tone}. "
            f"Topic: {request.topic}. Outline: {outline}."
        ),
    )

    title = str(outline.get("title") or request.topic.title())
    slug = str(outline.get("slug") or _slugify(title))
    meta_description = str(outline.get("meta_description") or "")

    primary = research.get("primary_keywords", []) if isinstance(research, dict) else []
    secondary = research.get("secondary_keywords", []) if isinstance(research, dict) else []
    keywords = [*primary, *secondary]

    state["draft"] = {
        "title": title,
        "slug": slug,
        "meta_description": meta_description,
        "markdown": markdown,
        "keywords": [str(k) for k in keywords if str(k).strip()],
    }
    return state


def seo_node(state: WorkflowState) -> WorkflowState:
    draft = state["draft"]
    score = estimate_seo_score(
        title=draft.get("title", ""),
        meta_description=draft.get("meta_description", ""),
        markdown=draft.get("markdown", ""),
        keywords=draft.get("keywords", []),
    )
    state["seo"] = {"score": score, "status": "pass" if score >= 70 else "needs_improvement"}
    return state


def image_prompt_node(state: WorkflowState) -> WorkflowState:
    draft = state["draft"]
    prompts_payload = generate_json(
        "You are a creative director for blog visuals.",
        (
            "Return JSON with key 'prompts' as an array of 2-3 prompts for article images. "
            f"Blog title: {draft.get('title', state['request'].topic)}. "
            f"Main keywords: {draft.get('keywords', [])[:5]}."
        ),
    )
    prompts = prompts_payload.get("prompts", []) if isinstance(prompts_payload, dict) else []
    state["image_prompts"] = [str(p).strip() for p in prompts if str(p).strip()][:3]
    return state


def image_generation_node(state: WorkflowState) -> WorkflowState:
    generated: list[dict[str, Any]] = []
    prompts = state["image_prompts"]
    if not prompts:
        state["images"] = generated
        return state

    client = NanoBananaClient()
    for idx, prompt in enumerate(prompts):
        slot = "hero" if idx == 0 else f"inline_{idx}"
        try:
            result = client.generate_image(prompt=prompt)
            generated.append(
                {
                    "slot": slot,
                    "prompt": prompt,
                    "url": result.get("url") or result.get("image_url"),
                    "provider": "nano_banana",
                }
            )
        except Exception as exc:  # noqa: BLE001
            state["errors"].append(f"Image generation failed for '{slot}': {exc}")
            generated.append(
                {
                    "slot": slot,
                    "prompt": prompt,
                    "url": None,
                    "provider": "nano_banana",
                    "error": str(exc),
                }
            )

    state["images"] = generated
    return state


def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("research", research_node)
    graph.add_node("outline", outline_node)
    graph.add_node("draft", draft_node)
    graph.add_node("seo", seo_node)
    graph.add_node("image_prompt", image_prompt_node)
    graph.add_node("image_generation", image_generation_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "outline")
    graph.add_edge("outline", "draft")
    graph.add_edge("draft", "seo")
    graph.add_edge("seo", "image_prompt")
    graph.add_edge("image_prompt", "image_generation")
    graph.add_edge("image_generation", END)

    return graph.compile()


def run_blog_agent(request: BlogRequest) -> FinalBlogPackage:
    initial: WorkflowState = {
        "request": request,
        "research": {},
        "outline": {},
        "draft": {},
        "seo": {},
        "image_prompts": [],
        "images": [],
        "errors": [],
    }

    result = build_graph().invoke(initial)
    draft = result["draft"]
    return FinalBlogPackage(
        title=draft["title"],
        slug=draft["slug"],
        meta_description=draft["meta_description"],
        markdown=draft["markdown"],
        keywords=draft["keywords"],
        seo_score=float(result["seo"].get("score", 0.0)),
        images=result["images"],
        debug={
            "research": result["research"],
            "outline": result["outline"],
            "errors": result["errors"],
        },
    )
