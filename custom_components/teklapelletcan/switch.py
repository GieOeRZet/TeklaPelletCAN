"""Przełączniki: włącz/wyłącz kocioł, restart urządzenia."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TeklaCoordinator
from .api import TeklaError
from .const import DOMAIN
from .entity import TeklaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TeklaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TeklaSwitch(coordinator, i) for i in coordinator.data.values() if i["domain"] == "switch")


class TeklaSwitch(TeklaEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        s = self._state
        return None if s is None else s == "on"

    async def _set(self, service: str) -> None:
        try:
            await self.coordinator.client.call("switch", service, {"entity_id": self._id})
        except TeklaError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs) -> None:
        await self._set("turn_on")

    async def async_turn_off(self, **kwargs) -> None:
        await self._set("turn_off")
