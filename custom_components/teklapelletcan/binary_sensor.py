"""Sensory binarne."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TeklaCoordinator
from .const import DOMAIN
from .entity import TeklaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TeklaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(TeklaBinary(coordinator, i) for i in coordinator.data.values() if i["domain"] == "binary_sensor")


class TeklaBinary(TeklaEntity, BinarySensorEntity):
    def __init__(self, coordinator: TeklaCoordinator, item: dict) -> None:
        super().__init__(coordinator, item)
        dc = item["attributes"].get("device_class")
        if dc:
            try:
                self._attr_device_class = BinarySensorDeviceClass(dc)
            except ValueError:
                pass

    @property
    def is_on(self) -> bool | None:
        s = self._state
        return None if s is None else s == "on"
