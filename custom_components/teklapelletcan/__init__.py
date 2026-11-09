"""Integracja TeklaPelletCAN: kocioł Tekla/Estyma przez własne urządzenie ESP32 + CAN."""
from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path
from typing import Any

import voluptuous as vol
from homeassistant.components import frontend
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import slugify

from .api import TeklaAuthError, TeklaClient, TeklaError
from .const import (
    ACTIONS,
    CONF_CARD,
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_TOKEN,
    DEFAULT_CARD,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
    SCAN_INTERVAL_S,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.BUTTON, Platform.SWITCH, Platform.SELECT]
CARD_URL = f"/{DOMAIN}_static/pelletcan-card.js"
NEW_CARD_URL = f"/{DOMAIN}_static/teklapelletcan-card.js"
MODERN_CARD_URL = f"/{DOMAIN}_static/teklapelletcan-modern-card.js"
CARDS_ADDED_KEY = "_cards_added"
# klasyczna zaleza od silnika tekla-panel-card zarejestrowanego przez pelletcan-card.js (zwykly <script>,
# nie import ES) – musi byc wczytany PRZED wrapperem, wiec kolejnosc w tej liscie ma znaczenie.
CARD_URLS = {
    "classic": [CARD_URL, NEW_CARD_URL],
    "modern": [MODERN_CARD_URL],
}
CARD_URLS["both"] = CARD_URLS["classic"] + CARD_URLS["modern"]


class TeklaCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Pobiera stany wszystkich encji z urządzenia."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: TeklaClient) -> None:
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=SCAN_INTERVAL_S))
        self.entry = entry
        self.client = client
        self.device_id: str = entry.unique_id or entry.entry_id
        self.device_name: str = entry.data.get(CONF_NAME, DEFAULT_NAME)
        self.node: str = slugify(entry.title) or "tekla_estyma"
        self.info: dict = {}

    async def _async_update_data(self) -> dict[str, dict]:
        try:
            self.info = await self.client.info()
            items = await self.client.states(slugify(self.device_name))
        except TeklaAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except TeklaError as err:
            raise UpdateFailed(str(err)) from err
        return {i["id"]: i for i in items}


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Udostępnia pliki kart pod /teklapelletcan_static/ – samo ich wstrzyknięcie do dashboardu
    zależy od wyboru w kreatorze konfiguracji (patrz _async_apply_card_choice), integracja niczego
    nie narzuca automatycznie."""
    www = Path(__file__).parent / "www"
    if www.is_dir():
        await hass.http.async_register_static_paths([StaticPathConfig(f"/{DOMAIN}_static", str(www), False)])
    return True


def _async_apply_card_choice(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Wstrzykuje zasoby karty wybranej w kreatorze (lub pozniej w opcjach), raz na proces HA."""
    choice = entry.options.get(CONF_CARD, entry.data.get(CONF_CARD, DEFAULT_CARD))
    urls = CARD_URLS.get(choice, [])
    if not urls:
        return
    added: set[str] = hass.data.setdefault(DOMAIN, {}).setdefault(CARDS_ADDED_KEY, set())
    try:
        for url in urls:
            if url in added:
                continue
            frontend.add_extra_js_url(hass, url)
            added.add(url)
    except KeyError:   # frontend niezaładowany (np. instalacja bez interfejsu) – kartę można dodać ręcznie jako zasób
        _LOGGER.debug("frontend niedostępny, karta nie została dodana automatycznie")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    client = TeklaClient(
        async_get_clientsession(hass), entry.data[CONF_HOST], entry.data.get(CONF_PORT, DEFAULT_PORT), entry.data[CONF_TOKEN]
    )
    coordinator = TeklaCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    _async_apply_card_choice(hass, entry)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    # Akcje o nazwach jak w ESPHome PelletCAN: <węzeł>_<akcja> (np. tekla_estyma_set_param) – woła je karta.
    def _handler(action: str):
        async def _call(call: ServiceCall) -> None:
            try:
                await client.call(DOMAIN, f"{coordinator.node}_{action}", dict(call.data))
            except TeklaError as err:
                raise HomeAssistantError(f"{action}: {err}") from err
            await coordinator.async_request_refresh()

        return _call

    for action in ACTIONS:
        hass.services.async_register(
            DOMAIN, f"{coordinator.node}_{action}", _handler(action), schema=vol.Schema({}, extra=vol.ALLOW_EXTRA)
        )
    async def _set_password(call: ServiceCall) -> None:
        """Zmiana hasła urządzenia z HA (token tego HA) – ratunek, gdy hasło zostało zapomniane."""
        try:
            await client.set_password(call.data["password"], call.data.get("confirm", call.data["password"]), auth=True)
        except TeklaError as err:
            raise HomeAssistantError(f"zmiana hasla: {err}") from err

    hass.services.async_register(
        DOMAIN,
        "set_device_password",
        _set_password,
        schema=vol.Schema({vol.Required("password"): vol.All(str, vol.Length(min=4)), vol.Optional("confirm"): str}),
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Wybór karty zmieniony w opcjach integracji – dokłada nowe zasoby (nie usuwa starych: frontend
    nie ma do tego API, więc zmiana wyboru na "none" wymaga ręcznego usunięcia zasobu w Ustawieniach)."""
    _async_apply_card_choice(hass, entry)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    coordinator: TeklaCoordinator = hass.data[DOMAIN][entry.entry_id]
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        for action in ACTIONS:
            hass.services.async_remove(DOMAIN, f"{coordinator.node}_{action}")
        hass.services.async_remove(DOMAIN, "set_device_password")
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok
