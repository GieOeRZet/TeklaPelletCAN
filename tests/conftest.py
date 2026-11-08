"""Fixtures: prawdziwy symulator urządzenia (Engine + Api z firmware, skompilowany na hoście) jako proces."""
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"

ROOT = Path(__file__).resolve().parent.parent
SIM = Path(os.environ.get("SIM_SERVER", ROOT / "build-host" / "sim_server"))


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations, socket_enabled):
    """Włącza własne integracje i gniazda (symulator urządzenia działa na localhost)."""
    yield


@pytest.fixture
def sim():
    """Uruchamia sim_server; zwraca (host, port). Czeka, aż silnik przeczyta dane z atrapy kotła."""
    if not SIM.exists():
        pytest.skip(f"brak {SIM} – zbuduj: cmake -S firmware/test -B build-host && cmake --build build-host")
    port = _free_port()
    proc = subprocess.Popen([str(SIM), str(port), str(ROOT / "web")], stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/info", timeout=0.5).read()
                break
            except Exception:
                time.sleep(0.1)
        # czekamy, aż silnik przeczyta stany z atrapy kotła (pierwszy pełny cykl ok. 15-20 s)
        import json

        for _ in range(240):
            try:
                st = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/api/v1/states?prefix=tekla", timeout=1))
                got = {x["id"]: x["state"] for x in st["states"]}
                if all(got.get(k) not in (None, "unknown") for k in ("burner_state_text", "boiler_on", "co_mode_text", "cwu_mode_text")):
                    break
            except Exception:
                pass
            time.sleep(0.25)
        yield "127.0.0.1", port
    finally:
        proc.terminate()
        proc.wait(timeout=5)
