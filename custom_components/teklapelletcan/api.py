"""Klient API urządzenia TeklaPelletCAN (REST)."""
from __future__ import annotations

from typing import Any

import aiohttp


class TeklaError(Exception):
    """Błąd komunikacji z urządzeniem."""


class TeklaAuthError(TeklaError):
    """Brak/nieważny token albo złe hasło."""


class TeklaSetupRequired(TeklaError):
    """Urządzenie nie ma jeszcze hasła (pierwsza konfiguracja)."""


class TeklaClient:
    def __init__(self, session: aiohttp.ClientSession, host: str, port: int = 80, token: str = "") -> None:
        self._s = session
        self._base = f"http://{host}:{port}"
        self.token = token

    async def _request(self, method: str, path: str, body: dict | None = None, auth: bool = True) -> Any:
        headers = {}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        try:
            async with self._s.request(
                method, self._base + path, json=body, headers=headers, timeout=aiohttp.ClientTimeout(total=8)
            ) as r:
                data = await r.json(content_type=None)
                if r.status == 401:
                    raise TeklaAuthError(data.get("error", "unauthorized"))
                if r.status == 403 and data.get("error") == "setup_required":
                    raise TeklaSetupRequired()
                if r.status >= 400:
                    raise TeklaError(data.get("result") or data.get("error") or f"HTTP {r.status}")
                return data
        except (aiohttp.ClientError, TimeoutError) as err:
            raise TeklaError(str(err)) from err

    async def info(self) -> dict:
        return await self._request("GET", "/api/v1/info", auth=False)

    async def states(self, prefix: str) -> list[dict]:
        data = await self._request("GET", f"/api/v1/states?prefix={prefix}", auth=False)
        return data["states"]

    async def set_password(self, password: str, confirm: str | None = None, auth: bool = False) -> None:
        """Ustawia hasło (pierwsza konfiguracja) albo zmienia je (auth=True, token sparowanego klienta)."""
        body = {"password": password}
        if confirm is not None:
            body["confirm"] = confirm
        await self._request("POST", "/api/v1/password", body, auth=auth)

    async def pair(self, password: str, client_id: str, name: str) -> dict:
        return await self._request(
            "POST", "/api/v1/pair", {"password": password, "client_id": client_id, "name": name}, auth=False
        )

    async def call(self, domain: str, service: str, data: dict | None = None) -> dict:
        return await self._request("POST", "/api/v1/call", {"domain": domain, "service": service, "data": data or {}})
