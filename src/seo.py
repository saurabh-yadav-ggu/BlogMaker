from __future__ import annotations


def keyword_density(markdown: str, keyword: str) -> float:
    words = markdown.lower().split()
    if not words:
        return 0.0
    count = sum(1 for w in words if keyword.lower() in w)
    return (count / len(words)) * 100


def estimate_seo_score(title: str, meta_description: str, markdown: str, keywords: list[str]) -> float:
    score = 0.0

    if 45 <= len(title) <= 65:
        score += 20
    if 120 <= len(meta_description) <= 160:
        score += 20
    if markdown.count("## ") >= 4:
        score += 20

    for kw in keywords[:3]:
        density = keyword_density(markdown, kw)
        if 0.4 <= density <= 2.5:
            score += 13.3

    return round(min(score, 100.0), 2)
