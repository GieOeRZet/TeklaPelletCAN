"""Przyciski (potwierdzenie alarmu, podajnik, dmuchawa, diagnostyka)."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TeklaCoordinator
from .api import TeklaError
from .const import DOMAIN
from .entity import TeklaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TeklaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TeklaButton(coordinator, i) for i in coordinator.data.values() if i["domain"] == "button")


class TeklaButton(TeklaEntity, ButtonEntity):
    def __init__(self, coordinator: TeklaCoordinator, item: dict) -> None:
        super().__init__(coordinator, item)
        if item["id"].startswith(("snap", "raport")):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    async def async_press(self) -> None:
        try:
            await self.coordinator.client.call("button", "press", {"entity_id": self._id})
        except TeklaError as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
