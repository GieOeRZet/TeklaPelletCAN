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
def auto_enable_custom_integrations(enable_custom_integrations):
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
        time.sleep(7)  # czas na pierwszy cykl odczytu
        yield "127.0.0.1", port
    finally:
        proc.terminate()
        proc.wait(timeout=5)
