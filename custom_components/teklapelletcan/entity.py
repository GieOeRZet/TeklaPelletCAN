"""Wspólna baza encji."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TeklaCoordinator
from .const import DOMAIN


_STANDARD_ATTRS = {"friendly_name", "unit_of_measurement", "device_class"}


class TeklaEntity(CoordinatorEntity[TeklaCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator: TeklaCoordinator, item: dict) -> None:
        super().__init__(coordinator)
        self._id = item["id"]
        self._attr_name = item["attributes"]["friendly_name"]
        self._attr_unique_id = f"{coordinator.device_id}_{self._id}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            name=coordinator.device_name,
            manufacturer="TeklaPelletCAN",
            model="ESP32-C6 + MCP2515 (CAN)",
            sw_version=coordinator.info.get("fw"),
        )

    @property
    def _item(self) -> dict | None:
        return self.coordinator.data.get(self._id) if self.coordinator.data else None

    @property
    def _state(self) -> str | None:
        item = self._item
        if not item or item.get("state") in (None, "unknown", "unavailable"):
            return None
        return item["state"]

    @property
    def extra_state_attributes(self) -> dict:
        # Id punktu z urzadzenia (ten sam co w rejestry/*.csv i w /api/v1/points) – zeby karty Lovelace
        # mogly mapowac punkt -> encje bez zgadywania po nazwie (np. teklapelletcan-modern-card). Dodatkowe
        # atrybuty z urzadzenia (np. wpisy historii alarmow ah_0..ah_19 na encji alarm_history) przechodza
        # tutaj tez, zywo przy kazdej aktualizacji - zamiast upychac wiele wartosci w jeden tekst do parsowania.
        out = {"tpc_id": self._id}
        item = self._item
        if item:
            for k, v in item.get("attributes", {}).items():
                if k not in _STANDARD_ATTRS:
                    out[k] = v
        return out
