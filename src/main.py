from __future__ import annotations

import argparse
import json

from .config import BLOG_TARGET_WORDS
from .models import BlogRequest
from .workflow import run_blog_agent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automated SEO blog writer agent")
    parser.add_argument("--topic", required=True, help="Blog topic")
    parser.add_argument("--tone", default="authoritative", help="Writing tone")
    parser.add_argument("--audience", default="marketing professionals", help="Target audience")
    parser.add_argument("--target-words", type=int, default=BLOG_TARGET_WORDS, help="Target word count")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    req = BlogRequest(
        topic=args.topic,
        tone=args.tone,
        audience=args.audience,
        target_words=args.target_words,
    )
    result = run_blog_agent(req)
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()
