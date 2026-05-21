import logging
import os
import subprocess
import time

import requests

from agent.config import settings

logger = logging.getLogger(__name__)


def is_ollama_ready() -> bool:
    try:
        response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=3)
        return response.ok
    except requests.RequestException:
        return False


def start_ollama() -> None:
    if is_ollama_ready():
        logger.info("Ollama is already running.")
        return

    logger.info("Starting Ollama server.")
    kwargs = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS

    try:
        subprocess.Popen(["ollama", "serve"], **kwargs)
    except FileNotFoundError as exc:
        raise RuntimeError("Ollama command was not found. Confirm Ollama is installed and on PATH.") from exc

    deadline = time.monotonic() + settings.ollama_startup_wait_seconds
    while time.monotonic() < deadline:
        if is_ollama_ready():
            logger.info("Ollama is ready.")
            return
        time.sleep(2)

    raise RuntimeError(
        f"Ollama did not become ready within {settings.ollama_startup_wait_seconds} seconds."
    )


def stop_ollama() -> None:
    if not settings.stop_ollama_after_report:
        logger.info("Skipping Ollama shutdown because STOP_OLLAMA_AFTER_REPORT is false.")
        return

    logger.info("Stopping Ollama to free RAM.")
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/IM", "ollama.exe", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    subprocess.run(
        ["pkill", "-f", "ollama serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
