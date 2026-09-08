from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


APP_DIR = Path.home() / ".game_troll_buster"
CONFIG_PATH = APP_DIR / "config.json"
LOG_DIR = APP_DIR / "chat_logs"


DEFAULTS: dict[str, Any] = {
    "delay_min": 15,
    "delay_max": 90,
    "max_replies": 250,
    "auto_stop_hours": 12,
    "store_logs": True,
    "theme": "Cyber Dark",
    "eliza_mode": "Classic ELIZA",
    "show_timestamps": False,
    "confirm_before_enable": False,
    "contact_configs": {},
}


def ensure_dirs() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict[str, Any]:
    ensure_dirs()
    data = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(stored, dict):
                data.update(stored)
        except Exception:
            pass
    return data


def save_config(data: dict[str, Any]) -> None:
    ensure_dirs()
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _safe_name(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value).strip(" .")
    return cleaned[:80] or "unknown_contact"


def chat_log_path(steam_id: str, name: str) -> Path:
    ensure_dirs()
    return LOG_DIR / f"{_safe_name(name)}_{_safe_name(steam_id)}.txt"


def append_chat_log(
    steam_id: str,
    name: str,
    direction: str,
    text: str,
    show_timestamp: bool = False,
) -> Path:
    """Append one message in a human-readable chat transcript format."""
    ensure_dirs()
    path = chat_log_path(steam_id, name)
    label = "Troll" if direction == "in" else "ELIZA"
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with path.open("a", encoding="utf-8", newline="\n") as f:
        if path.stat().st_size == 0:
            f.write("Game Troll Buster - Chat Transcript\n")
            f.write(f"Contact: {name}\n")
            f.write(f"Steam ID: {steam_id}\n")
            f.write("=" * 72 + "\n\n")

        if show_timestamp:
            f.write(f"[{stamp}] [{label}]: {text}\n\n")
        else:
            f.write(f"[{label}]: {text}\n\n")

    return path
