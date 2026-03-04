#!/usr/bin/env python3
"""
Two-pass generational research runner for Pearl News.
Pass 1: reasoning with /think (or <think>); save to .reasoning.md.
Pass 2: YAML-only with /no_think; save to artifacts/research/<layer>/ with provenance.

Usage:
  python scripts/research/run_research.py --prompt-id psychology [--paste path/to/raw.txt]
  python scripts/research/run_research.py --prompt-id pain_points --paste artifacts/research/raw/feed_2026-03-04.txt
  python scripts/research/run_research.py --prompt-id event_impact --paste -   # read stdin

Requires: Ollama running with Qwen3-14B-GGUF (or set OLLAMA_MODEL).
  pip install requests pyyaml (optional, for YAML parse check)
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Repo root (script lives in scripts/research/)
REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS_ROOT = REPO_ROOT / "research" / "prompts"
ARTIFACTS_ROOT = REPO_ROOT / "artifacts" / "research"

PROMPT_ID_TO_LAYER = {
    "psychology": "psychology",
    "pain_points": "pain_points",
    "event_impact": "world_events",
}

DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:14b")


def load_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read().strip()


SYSTEM_FILE_BY_PROMPT_ID = {
    "psychology": "psych_pulse_researcher",
    "pain_points": "econ_script_analyst",
    "event_impact": "identity_conflict_researcher",
}


def load_prompt(kind: str, prompt_id: str) -> str:
    """Load system or task prompt. kind in ('system', 'task', 'yaml_instruction')."""
    if kind == "system":
        name = SYSTEM_FILE_BY_PROMPT_ID.get(prompt_id, prompt_id)
        p = PROMPTS_ROOT / "system" / f"{name}.txt"
    elif kind == "yaml_instruction":
        p = PROMPTS_ROOT / "tasks" / f"{prompt_id}_yaml_instruction.txt"
    else:
        p = PROMPTS_ROOT / "tasks" / f"{prompt_id}_task.txt"
    if not p.exists():
        raise FileNotFoundError(f"Prompt file not found: {p}")
    return load_text(p)


def call_ollama(prompt: str, model: str, use_think: bool, temperature: float = 0.6) -> str:
    """Call Ollama generate API. use_think=True appends /think to prompt."""
    try:
        import requests
    except ImportError:
        print("Install requests: pip install requests", file=sys.stderr)
        sys.exit(1)
    if use_think:
        prompt = prompt.rstrip() + "\n\n/think"
    url = os.environ.get("OLLAMA_HOST", "http://localhost:11434") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    r = requests.post(url, json=payload, timeout=300)
    r.raise_for_status()
    return r.json().get("response", "")


def extract_analysis_summary(reasoning: str, max_chars: int = 12000) -> str:
    """Take first substantive part for YAML pass; strip <think> if present."""
    text = reasoning
    think_match = re.search(r"<think>(.*?)</think>", text, re.DOTALL | re.IGNORECASE)
    if think_match:
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE).strip()
    text = text.strip()
    if len(text) > max_chars:
        text = text[: max_chars - 80] + "\n\n[... truncated for YAML pass ...]"
    return text


def write_yaml_with_provenance(out_path: Path, yaml_body: str, prompt_id: str, model: str) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d")
    header = f"""# provenance
run_date: {now}
model: {model}
prompt_id: {prompt_id}
source: yaml_pass

"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write(yaml_body)
        if not yaml_body.endswith("\n"):
            f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Two-pass Qwen3 generational research")
    parser.add_argument("--prompt-id", required=True, choices=list(PROMPT_ID_TO_LAYER), help="Dimension: psychology, pain_points, event_impact")
    parser.add_argument("--paste", default=None, help="Path to raw data file, or '-' for stdin")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Ollama model name")
    parser.add_argument("--skip-yaml-pass", action="store_true", help="Only run reasoning pass")
    parser.add_argument("--out-dir", default=None, help="Override artifacts/research subdir")
    args = parser.parse_args()

    prompt_id = args.prompt_id
    layer = PROMPT_ID_TO_LAYER[prompt_id]
    out_dir = Path(args.out_dir) if args.out_dir else ARTIFACTS_ROOT / layer
    out_dir.mkdir(parents=True, exist_ok=True)

    raw_data = ""
    if args.paste:
        if args.paste == "-":
            raw_data = sys.stdin.read()
        else:
            raw_data = load_text(Path(args.paste))

    system = load_prompt("system", prompt_id)
    task = load_prompt("task", prompt_id)
    task = task.replace("{{RAW_DATA}}", raw_data or "(no paste provided)")
    prompt_pass1 = f"{system}\n\n---\n\n{task}"

    print("Pass 1 (reasoning with /think)...", file=sys.stderr)
    response1 = call_ollama(prompt_pass1, args.model, use_think=True, temperature=0.6)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    reasoning_path = out_dir / f"{ts}_reasoning.md"
    with open(reasoning_path, "w", encoding="utf-8") as f:
        f.write(response1)
    print(f"Wrote {reasoning_path}", file=sys.stderr)

    if args.skip_yaml_pass:
        return

    analysis_summary = extract_analysis_summary(response1)
    yaml_instruction = load_prompt("yaml_instruction", prompt_id)
    yaml_instruction = yaml_instruction.replace("{{ANALYSIS_SUMMARY}}", analysis_summary)
    prompt_pass2 = f"Output only valid YAML. No thinking, no markdown fences.\n\n{yaml_instruction}"

    print("Pass 2 (YAML only, /no_think)...", file=sys.stderr)
    response2 = call_ollama(prompt_pass2, args.model, use_think=False, temperature=0.4)
    yaml_path = out_dir / f"{ts}.yaml"
    write_yaml_with_provenance(yaml_path, response2.strip(), prompt_id, args.model)
    print(f"Wrote {yaml_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
