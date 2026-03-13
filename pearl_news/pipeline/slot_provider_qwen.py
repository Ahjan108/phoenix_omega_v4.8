"""
Qwen Slot Provider — Fills slot contracts using Qwen via OpenAI-compatible API.

Usage:
    provider = QwenSlotProvider(config)
    provider.process_all_pending(slots_root)

Config from environment or llm_expansion.yaml:
    QWEN_BASE_URL, QWEN_API_KEY, QWEN_MODEL

The provider:
- Reads pending slot contracts
- Calls Qwen to fill only required_slots
- Writes completed contracts
- Assembler consumes file exactly like local/file mode
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None

from pearl_news.pipeline.slot_provider_base import SlotProviderBase

logger = logging.getLogger(__name__)


def _read_repo_text_file(repo_root: Path, relative_path: str) -> str:
    path = repo_root / relative_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _load_qwen_api_key_from_file(repo_root: Path | None = None) -> str:
    """Load Qwen API key from docs/qwen_api_key.txt if present.

    Accepts plain tokens or lines like:
    Api key= "sk-..."
    """
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    raw = _read_repo_text_file(repo_root, "docs/qwen_api_key.txt")
    if not raw:
        return ""
    patterns = [
        r'Api\s*key\s*=\s*"([^"]+)"',
        r"Api\s*key\s*=\s*'([^']+)'",
        r"Api\s*key\s*=\s*([^\s]+)",
        r"\b(sk-[A-Za-z0-9._-]+)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return re.sub(r"^-+(?=sk-)", "", value)
    value = raw.strip().strip('"').strip("'")
    return re.sub(r"^-+(?=sk-)", "", value)


def _load_qwen_base_url_from_file(repo_root: Path | None = None) -> str:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    raw = _read_repo_text_file(repo_root, "docs/qwen_api_base_url.txt")
    if not raw:
        return ""
    match = re.search(r"(https?://[^\s\"']+)", raw)
    if match:
        return match.group(1).strip()
    return raw.strip().strip('"').strip("'")


def _load_qwen_model_from_file(repo_root: Path | None = None) -> str:
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    raw = _read_repo_text_file(repo_root, "docs/qwen_model.txt")
    if not raw:
        return ""
    if "=" in raw:
        raw = raw.split("=", 1)[1].strip()
    return raw.strip().strip('"').strip("'")


def _load_config(config_root: Path | None = None) -> dict[str, Any]:
    """Load Qwen config from yaml + env overrides."""
    data: dict[str, Any] = {}
    repo_root = Path(__file__).resolve().parents[2]

    if config_root:
        path = config_root / "llm_expansion.yaml"
        if path.exists() and yaml:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

    if os.environ.get("QWEN_BASE_URL"):
        data["base_url"] = os.environ.get("QWEN_BASE_URL", "").strip()
    else:
        file_base_url = _load_qwen_base_url_from_file(repo_root)
        if file_base_url:
            data["base_url"] = file_base_url

    if os.environ.get("QWEN_API_KEY") is not None:
        data["api_key"] = (os.environ.get("QWEN_API_KEY") or "").strip()
    else:
        file_key = _load_qwen_api_key_from_file(repo_root)
        if file_key:
            data["api_key"] = file_key

    if os.environ.get("QWEN_MODEL"):
        data["model"] = os.environ.get("QWEN_MODEL", "").strip()
    else:
        file_model = _load_qwen_model_from_file(repo_root)
        if file_model:
            data["model"] = file_model

    api_key = str(data.get("api_key") or "").strip()
    base_url = str(data.get("base_url") or "").strip()
    if api_key and (not base_url or "localhost" in base_url or "127.0.0.1" in base_url):
        data["base_url"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    if api_key and not str(data.get("model") or "").strip():
        data["model"] = "qwen-plus"
    if os.environ.get("QWEN_BASE_URL") and data.get("enabled") is not True:
        data["enabled"] = True

    return data


def _create_openai_client(config: dict[str, Any]) -> Any | None:
    """Create OpenAI client for Qwen endpoint."""
    base_url = (config.get("base_url") or "").strip()
    api_key = (config.get("api_key") or "lm-studio").strip()
    timeout = float(config.get("timeout") or 360)

    if not base_url:
        return None

    from openai import OpenAI

    try:
        from httpx import Timeout as HttpxTimeout
        http_timeout = HttpxTimeout(timeout)
    except Exception:
        http_timeout = timeout

    return OpenAI(base_url=base_url, api_key=api_key, timeout=http_timeout)


def _sanitize_model_output(raw: str | None) -> str | None:
    """Clean up model output: remove think blocks, code fences."""
    if not raw:
        return None
    text = raw.strip()
    text = re.sub(r"^\s*<think>\s*</think>\s*", "", text, flags=re.DOTALL)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    if text.startswith("```"):
        lines = text.split("\n")
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text.strip() or None


def _chat_once(
    *,
    client: Any,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    disable_thinking: bool,
) -> str | None:
    """Single chat completion call with fallback to direct HTTP."""
    raw = None
    extra_body = {"enable_thinking": False} if disable_thinking else {}

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=0.8,
            presence_penalty=1.5,
            max_tokens=max_tokens,
            **({"extra_body": extra_body} if extra_body else {}),
        )
        choice = resp.choices[0] if resp.choices else None
        if choice and getattr(choice, "message", None):
            raw = (choice.message.content or "").strip()
    except Exception as e:
        logger.warning("OpenAI client chat failed; trying direct HTTP fallback: %s", e)

    if not raw:
        try:
            base_url = str(getattr(client, "base_url", "")).rstrip("/")
            if not base_url:
                return None
            url = f"{base_url}/chat/completions"
            payload: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "top_p": 0.8,
                "presence_penalty": 1.5,
                "max_tokens": max_tokens,
            }
            if disable_thinking:
                payload["enable_thinking"] = False
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {getattr(client, 'api_key', 'lm-studio')}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8", errors="ignore"))
            raw = (
                (((data.get("choices") or [{}])[0].get("message") or {}).get("content"))
                or ""
            ).strip()
        except Exception as e:
            logger.warning("Direct HTTP fallback failed: %s", e)
            return None

    return _sanitize_model_output(raw)


def _build_slot_prompt(
    slot_name: str,
    contract: dict[str, Any],
    context: dict[str, Any] | None,
) -> str:
    """Build prompt for filling a single slot."""
    template_id = contract.get("template_id") or "hard_news_spiritual_response"
    topic = contract.get("topic") or "general"
    teacher_name = contract.get("teacher_name") or "Forum Participant"
    source_title = contract.get("source_title") or ""
    source_url = contract.get("source_url") or ""

    det_ctx = contract.get("deterministic_context") or {}
    ordered_sections = det_ctx.get("ordered_sections") or []

    slot_info = None
    for section in ordered_sections:
        if section.get("slot") == slot_name:
            slot_info = section
            break

    slot_description = ""
    if slot_info:
        slot_description = f"""
Slot section info:
- Section: {slot_info.get('section', '')}
- Slot: {slot_info.get('slot', '')}
- Source: {slot_info.get('source', '')}
- Instructions: {slot_info.get('instructions', '')}
"""

    return f"""/no_think
You are filling a single slot for a Pearl News article.

TEMPLATE: {template_id}
TOPIC: {topic}
TEACHER: {teacher_name}

SOURCE NEWS:
Title: {source_title}
URL: {source_url}
Published: {contract.get('source_published_at', '')}

SLOT TO FILL: {slot_name}
{slot_description}
CONSTRAINTS:
{chr(10).join('- ' + c for c in (contract.get('writer_notes') or {}).get('constraints', []))}

Write ONLY the content for the "{slot_name}" slot.
Output just the slot content as a single paragraph (2-4 sentences).
Do not include the slot name, labels, or any preamble.
"""


def _build_system_prompt() -> str:
    """System prompt for slot filling."""
    return """You are a Pearl News slot filler. You fill individual article slots with concise, factual content.

Rules:
- Output ONLY the requested slot content
- Keep each slot to 2-4 sentences
- Use facts from the provided source
- Match the teacher's voice and tradition
- Do not invent facts beyond the source
- Do not include HTML tags unless the slot specifically requires them"""


class QwenSlotProvider(SlotProviderBase):
    """Qwen-based slot provider using OpenAI-compatible API."""

    provider_name: str = "qwen"

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        config_root: Path | None = None,
    ):
        if config is None:
            config = _load_config(config_root)
        super().__init__(config)
        self._client = None
        self._client_initialized = False

    def _get_client(self) -> Any | None:
        """Lazy-init OpenAI client."""
        if not self._client_initialized:
            self._client = _create_openai_client(self.config)
            self._client_initialized = True
        return self._client

    def _preflight_check(self) -> tuple[bool, str | None]:
        """Quick health check before processing."""
        client = self._get_client()
        if client is None:
            return False, "no_client_configured"

        model = self.config.get("model") or "qwen3-14b"
        disable_thinking = self.config.get("disable_thinking", True)
        max_seconds = float(self.config.get("preflight_max_seconds") or 45)

        started = time.monotonic()
        reply = _chat_once(
            client=client,
            model=model,
            messages=[
                {"role": "system", "content": "Reply only READY"},
                {"role": "user", "content": "/no_think\nreply only READY"},
            ],
            temperature=0.1,
            max_tokens=12,
            disable_thinking=disable_thinking,
        )
        elapsed = time.monotonic() - started

        if not reply:
            return False, "preflight_no_response"
        if reply.strip() != "READY":
            return False, f"preflight_bad_reply:{reply[:80]}"
        if elapsed > max_seconds:
            return False, f"preflight_too_slow:{elapsed:.1f}s"

        return True, None

    def fill_slots(
        self,
        contract: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """Fill required slots using Qwen."""
        client = self._get_client()
        if client is None:
            raise RuntimeError("Qwen client not configured (check QWEN_BASE_URL)")

        model = self.config.get("model") or "qwen3-14b"
        temperature = float(self.config.get("temperature") or 0.5)
        max_tokens = int(self.config.get("max_tokens") or 512)
        disable_thinking = self.config.get("disable_thinking", True)

        required_slots = contract.get("required_slots") or {}
        if not isinstance(required_slots, dict):
            raise ValueError("Contract has no required_slots dict")

        system_prompt = _build_system_prompt()
        filled: dict[str, str] = {}

        for slot_name in required_slots.keys():
            if str(required_slots.get(slot_name) or "").strip():
                filled[slot_name] = required_slots[slot_name]
                logger.debug("Slot %s already filled, skipping", slot_name)
                continue

            user_prompt = _build_slot_prompt(slot_name, contract, context)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            logger.info("Filling slot %s for %s", slot_name, contract.get("article_id"))

            result = _chat_once(
                client=client,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                disable_thinking=disable_thinking,
            )

            if result:
                filled[slot_name] = result
                logger.debug("Filled %s: %d chars", slot_name, len(result))
            else:
                logger.warning("Failed to fill slot %s", slot_name)
                filled[slot_name] = ""

        return filled

    def process_contract(
        self,
        pending_path: Path,
        slots_root: Path,
        context: dict[str, Any] | None = None,
    ) -> tuple[Path, list[str]]:
        """Override to add preflight check on first call."""
        ok, err = self._preflight_check()
        if not ok:
            raise RuntimeError(f"Qwen preflight failed: {err}")

        return super().process_contract(pending_path, slots_root, context)


def main() -> int:
    """CLI entry point for Qwen slot provider."""
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(
        description="Fill pending slot contracts using Qwen"
    )
    parser.add_argument(
        "--slots-dir",
        required=True,
        help="Root directory with pending/ and completed/ subdirs",
    )
    parser.add_argument(
        "--config-root",
        default="",
        help="Config directory (default: pearl_news/config)",
    )
    parser.add_argument(
        "--contract",
        default="",
        help="Process single contract file instead of all pending",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    config_root = Path(args.config_root) if args.config_root else repo_root / "pearl_news" / "config"
    slots_root = Path(args.slots_dir)

    provider = QwenSlotProvider(config_root=config_root)

    if args.contract:
        contract_path = Path(args.contract)
        try:
            completed_path, errors = provider.process_contract(contract_path, slots_root)
            print(f"Completed: {completed_path}")
            if errors:
                print(f"Errors: {errors}")
                return 1
            return 0
        except Exception as e:
            print(f"Failed: {e}")
            return 1

    results = provider.process_all_pending(slots_root)
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count

    print(f"\nProcessed {len(results)} contracts: {success_count} success, {fail_count} failed")

    for r in results:
        status = "OK" if r["success"] else "FAIL"
        print(f"  [{status}] {r['article_id']}")
        if r["errors"]:
            for e in r["errors"]:
                print(f"       - {e}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
