import os
import logging
import httpx
from sqlalchemy import select
from database import AsyncSessionLocal

logger = logging.getLogger(__name__)

DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_LLM_BASE_URL = "http://localhost:11434"
DEFAULT_LLM_MODEL = "qwen2.5:7b"
DEFAULT_LLM_API_KEY = ""


async def get_llm_config() -> dict:
    config = {
        "provider": os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER),
        "base_url": os.getenv("LLM_BASE_URL", DEFAULT_LLM_BASE_URL),
        "model": os.getenv("LLM_MODEL", DEFAULT_LLM_MODEL),
        "api_key": os.getenv("LLM_API_KEY", DEFAULT_LLM_API_KEY),
    }
    try:
        from models.system_config import SystemConfig
        async with AsyncSessionLocal() as db:
            for key in ["llm_provider", "llm_base_url", "llm_model", "llm_api_key"]:
                result = await db.execute(
                    select(SystemConfig.value).where(SystemConfig.key == key)
                )
                row = result.scalar_one_or_none()
                if row:
                    config[key.replace("llm_", "")] = row
    except Exception:
        pass
    return config


async def call_llm(prompt: str, system_prompt: str = "") -> str:
    cfg = await get_llm_config()
    if cfg["provider"] == "ollama":
        return await _call_ollama(cfg, prompt, system_prompt)
    else:
        return await _call_openai_compatible(cfg, prompt, system_prompt)


async def _call_ollama(cfg: dict, prompt: str, system_prompt: str) -> str:
    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{cfg['base_url']}/api/generate",
            json={
                "model": cfg["model"],
                "prompt": full_prompt,
                "stream": False,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "").strip()


async def _call_openai_compatible(cfg: dict, prompt: str, system_prompt: str) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    headers = {"Content-Type": "application/json"}
    if cfg["api_key"]:
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    base = cfg["base_url"].rstrip("/")
    url = f"{base}/chat/completions"

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            url,
            headers=headers,
            json={
                "model": cfg["model"],
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 2000,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
