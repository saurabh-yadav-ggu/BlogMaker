# Automated SEO Blog Writer Agent

This project implements an automated blog-writing AI agent that:

- Uses **Gemini** as the LLM for strategy + writing.
- Uses **Nano Banana** as the image generation provider.
- Uses **LangChain** for prompt/model orchestration.
- Uses **LangGraph** ("langram" workflow graph) to build a deterministic multi-step pipeline.

## Workflow

1. **Research**: Expand a topic into search intent, audience, and semantic keyword clusters.
2. **Outline**: Create an SEO-driven H1/H2/H3 structure.
3. **Draft**: Produce a complete long-form article in Markdown with metadata.
4. **SEO Audit**: Validate keyword placement, title/meta lengths, and heading quality.
5. **Image Prompting**: Create prompts for hero + inline images.
6. **Image Generation**: Generate images with Nano Banana and return URLs.
7. **Assemble**: Return a final blog package.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.main --topic "How AI agents improve content marketing"
```

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | API key for Google Gemini |
| `GEMINI_MODEL` | Optional Gemini model, defaults to `gemini-1.5-pro` |
| `NANO_BANANA_API_KEY` | API key for Nano Banana |
| `NANO_BANANA_BASE_URL` | API base URL for Nano Banana |
| `BLOG_TARGET_WORDS` | Optional target length, defaults to `1600` |

## Example Output

The CLI returns a JSON package containing:

- `title`
- `slug`
- `meta_description`
- `markdown`
- `keywords`
- `seo_score`
- `images` (hero + inline image URLs)

## Notes

- If Nano Banana is unavailable, the workflow still returns the blog with image prompts and error details.
- You can plug this agent into a scheduler to auto-publish at fixed intervals.
