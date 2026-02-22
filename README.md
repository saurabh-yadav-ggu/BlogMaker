# Automated SEO Blog Writer Agent

A production-oriented AI blog writer that uses:

- **Gemini** for planning + writing
- **LangChain** for prompt/model orchestration
- **LangGraph** ("langram") for deterministic workflow execution
- **Nano Banana** for image generation

## Workflow

1. Research keywords + intent
2. Build SEO outline
3. Generate draft markdown
4. Score draft SEO quality
5. Generate image prompts
6. Create images via Nano Banana
7. Return final blog package JSON

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.main --topic "How AI agents improve content marketing"
```

## Environment Variables

- `GEMINI_API_KEY` (required)
- `GEMINI_MODEL` (default: `gemini-1.5-pro`)
- `NANO_BANANA_API_KEY` (required for image generation)
- `NANO_BANANA_BASE_URL` (default: `https://api.nanobanana.ai/v1`)
- `BLOG_TARGET_WORDS` (default: `1600`)

## Why this version is cleaner

- Stronger config parsing/validation
- Safer JSON handling from LLM responses
- Strict typed workflow state
- Better slug generation and defaults
- Graceful image-generation failure handling
