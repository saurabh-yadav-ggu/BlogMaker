from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from .llm import generate_json, generate_text
from .models import BlogRequest, BlogState, FinalBlogPackage
from .nano_banana import NanoBananaClient
from .seo import estimate_seo_score


def research_node(state: BlogState) -> BlogState:
    data = generate_json(
        "You are an expert SEO strategist.",
        (
            "Create keyword research for this topic. Return keys: "
            "search_intent, primary_keywords, secondary_keywords, faq_questions. "
            f"Topic: {state.request.topic}. Audience: {state.request.audience}."
        ),
    )
    state.research = data
    return state


def outline_node(state: BlogState) -> BlogState:
    data = generate_json(
        "You design SEO blog outlines that rank.",
        (
            "Create an outline with keys: title, slug, meta_description, h2_sections. "
            "Each h2 section should contain heading and bullet_points. "
            f"Use this research context: {state.research}"
        ),
    )
    state.outline = data
    return state


def draft_node(state: BlogState) -> BlogState:
    markdown = generate_text(
        "You are a senior content writer. Output markdown only.",
        (
            "Write a complete, SEO-optimized blog post with clear headings, "
            "internal-link placeholders, a short intro, and strong CTA conclusion. "
            f"Target words: {state.request.target_words}. Tone: {state.request.tone}. "
            f"Topic: {state.request.topic}. Outline: {state.outline}."
        ),
    )
    state.draft = {
        "title": state.outline.get("title", state.request.topic.title()),
        "slug": state.outline.get("slug", state.request.topic.lower().replace(" ", "-")),
        "meta_description": state.outline.get("meta_description", ""),
        "markdown": markdown,
        "keywords": state.research.get("primary_keywords", []) + state.research.get("secondary_keywords", []),
    }
    return state


def seo_node(state: BlogState) -> BlogState:
    score = estimate_seo_score(
        title=state.draft.get("title", ""),
        meta_description=state.draft.get("meta_description", ""),
        markdown=state.draft.get("markdown", ""),
        keywords=state.draft.get("keywords", []),
    )
    state.seo = {"score": score, "status": "pass" if score >= 70 else "needs_improvement"}
    return state


def image_prompt_node(state: BlogState) -> BlogState:
    prompts = generate_json(
        "You are a creative director for blog visuals.",
        (
            "Return JSON with key 'prompts' as an array of 2-3 prompts for article images. "
            f"Blog title: {state.draft.get('title', state.request.topic)}. "
            f"Main keywords: {state.draft.get('keywords', [])[:5]}."
        ),
    )
    state.image_prompts = prompts.get("prompts", [])
    return state


def image_generation_node(state: BlogState) -> BlogState:
    client = NanoBananaClient()
    generated: list[dict[str, Any]] = []

    for idx, prompt in enumerate(state.image_prompts):
        try:
            result = client.generate_image(prompt=prompt)
            generated.append(
                {
                    "slot": "hero" if idx == 0 else f"inline_{idx}",
                    "prompt": prompt,
                    "url": result.get("url") or result.get("image_url"),
                    "provider": "nano_banana",
                }
            )
        except Exception as exc:  # noqa: BLE001
            state.errors.append(f"Image generation failed for prompt {idx + 1}: {exc}")
            generated.append(
                {
                    "slot": "hero" if idx == 0 else f"inline_{idx}",
                    "prompt": prompt,
                    "url": None,
                    "provider": "nano_banana",
                    "error": str(exc),
                }
            )

    state.images = generated
    return state


def assemble_node(state: BlogState) -> BlogState:
    return state


def build_graph():
    graph = StateGraph(BlogState)
    graph.add_node("research", research_node)
    graph.add_node("outline", outline_node)
    graph.add_node("draft", draft_node)
    graph.add_node("seo", seo_node)
    graph.add_node("image_prompt", image_prompt_node)
    graph.add_node("image_generation", image_generation_node)
    graph.add_node("assemble", assemble_node)

    graph.set_entry_point("research")
    graph.add_edge("research", "outline")
    graph.add_edge("outline", "draft")
    graph.add_edge("draft", "seo")
    graph.add_edge("seo", "image_prompt")
    graph.add_edge("image_prompt", "image_generation")
    graph.add_edge("image_generation", "assemble")
    graph.add_edge("assemble", END)

    return graph.compile()


def run_blog_agent(request: BlogRequest) -> FinalBlogPackage:
    app = build_graph()
    state = BlogState(request=request)
    result = app.invoke(state)

    return FinalBlogPackage(
        title=result["draft"]["title"],
        slug=result["draft"]["slug"],
        meta_description=result["draft"]["meta_description"],
        markdown=result["draft"]["markdown"],
        keywords=result["draft"]["keywords"],
        seo_score=result["seo"]["score"],
        images=result["images"],
        debug={
            "research": result["research"],
            "outline": result["outline"],
            "errors": result.get("errors", []),
        },
    )
