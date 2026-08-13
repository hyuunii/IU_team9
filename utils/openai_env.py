"""Helpers for safely loading OpenAI-related environment variables."""
import os

OPENAI_ENV_KEYS = (
    "OPENAI_API_KEY",
    "OPENAI_ORG_ID",
    "OPENAI_ORGANIZATION",
    "OPENAI_PROJECT",
    "OPENAI_BASE_URL",
)

DASH_CHARS = (
    chr(0x2010),
    chr(0x2011),
    chr(0x2012),
    chr(0x2013),
    chr(0x2014),
    chr(0x2015),
    chr(0x2212),
)


def normalize_openai_env() -> str | None:
    """OpenAI SDK headers must be ASCII-only. Clean common copy/paste dash mistakes."""
    error = None
    for key in OPENAI_ENV_KEYS:
        value = os.getenv(key)
        if not value:
            continue
        cleaned = value.strip().strip('"').strip("'")
        for dash in DASH_CHARS:
            cleaned = cleaned.replace(dash, "-")
        os.environ[key] = cleaned
        if any(ord(ch) > 127 for ch in cleaned):
            error = f"{key} 값에 영문/숫자/기호가 아닌 문자가 섞여 있어요."
    return error
