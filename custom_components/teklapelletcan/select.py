"""Wybory trybu pracy obiegów CO i CWU."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TeklaCoordinator
from .api import TeklaError
from .const import DOMAIN, SELECT_OPTIONS
from .entity import TeklaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TeklaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TeklaSelect(coordinator, i)
        for i in coordinator.data.values()
        if i["domain"] == "select" and (i["id"] != "co2_mode_sel" or coordinator.info.get("two_circuits"))
    )


class TeklaSelect(TeklaEntity, SelectEntity):
    _attr_options = SELECT_OPTIONS

    @property
    def current_option(self) -> str | None:
        s = self._state
        return s if s in SELECT_OPTIONS else None

    async def async_select_option(self, option: str) -> None:
        try:
            await self.coordinator.client.call("select", "select_option", {"entity_id": self._id, "option": option})
        except TeklaError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
