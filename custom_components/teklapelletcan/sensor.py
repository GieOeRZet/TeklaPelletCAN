"""Sensory (liczbowe i tekstowe)."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import TeklaCoordinator
from .const import DOMAIN
from .entity import TeklaEntity


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: TeklaCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        TeklaSensor(coordinator, i) for i in coordinator.data.values() if i["domain"] in ("sensor", "text_sensor")
    )


class TeklaSensor(TeklaEntity, SensorEntity):
    def __init__(self, coordinator: TeklaCoordinator, item: dict) -> None:
        super().__init__(coordinator, item)
        attrs = item["attributes"]
        self._numeric = item["domain"] == "sensor" and bool(attrs.get("unit_of_measurement") or attrs.get("device_class"))
        if attrs.get("unit_of_measurement"):
            self._attr_native_unit_of_measurement = attrs["unit_of_measurement"]
        if attrs.get("device_class"):
            try:
                self._attr_device_class = SensorDeviceClass(attrs["device_class"])
            except ValueError:
                pass
        if item["id"] in ("sdo_last", "diag_rep", "snap_txt", "conf_txt", "stat_txt", "fw_ver", "sig_txt"):
            self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        s = self._state
        if s is None:
            return None
        if self._numeric:
            try:
                return float(s)
            except ValueError:
                return None
        return s
