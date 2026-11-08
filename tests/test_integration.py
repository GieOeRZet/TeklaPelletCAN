"""Testy integracji HA na prawdziwym symulatorze urządzenia."""
import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.teklapelletcan.const import DOMAIN


async def _pair_flow(hass: HomeAssistant, host: str, port: int, password: str = "qwerty123"):
    r = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert r["type"] is FlowResultType.FORM and r["step_id"] == "user"
    r = await hass.config_entries.flow.async_configure(r["flow_id"], {"host": host, "port": port})
    assert r["type"] is FlowResultType.FORM and r["step_id"] == "auth"
    return r


async def test_config_flow_pairs_and_creates_entry(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    r = await hass.config_entries.flow.async_configure(r["flow_id"], {"password": "qwerty123", "name": "Tekla"})
    assert r["type"] is FlowResultType.CREATE_ENTRY
    assert r["data"]["token"] and r["data"]["host"] == host
    assert r["result"].unique_id == "A1B2C3D4E5F6"


async def test_same_device_cannot_be_added_twice(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    await hass.config_entries.flow.async_configure(r["flow_id"], {"password": "qwerty123", "name": "Tekla"})
    r2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    r2 = await hass.config_entries.flow.async_configure(r2["flow_id"], {"host": host, "port": port})
    assert r2["type"] is FlowResultType.ABORT and r2["reason"] == "already_configured"


async def test_wrong_password_rejected(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    await hass.config_entries.flow.async_configure(r["flow_id"], {"password": "qwerty123", "name": "Tekla"})
    # drugi HA (inny client_id) próbuje sparować ze złym hasłem – nowe urządzenie z hasłem ustawionym
    from custom_components.teklapelletcan.api import TeklaAuthError, TeklaClient
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    client = TeklaClient(async_get_clientsession(hass), host, port)
    with pytest.raises(TeklaAuthError):
        await client.pair("zle-haslo", "inny-ha", "Drugi HA")
    ok = await client.pair("qwerty123", "inny-ha", "Drugi HA")   # kilka HA może używać jednego urządzenia
    assert ok["token"] and ok["already_paired"] is False


@pytest.fixture
async def entry(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    r = await hass.config_entries.flow.async_configure(r["flow_id"], {"password": "qwerty123", "name": "Tekla"})
    await hass.async_block_till_done()
    return r["result"]


async def test_entities_have_esphome_compatible_ids_and_values(hass: HomeAssistant, entry):
    # te same entity_id co w ESPHome PelletCAN, więc oryginalna karta wykrywa je bez zmian
    st = hass.states.get("sensor.tekla_kociol_temperatura")
    assert st is not None and float(st.state) == pytest.approx(78.4)
    assert st.attributes["unit_of_measurement"] == "°C"
    assert hass.states.get("sensor.tekla_palnik_stan").state == "Modulacja"
    assert hass.states.get("binary_sensor.tekla_kociol_wlaczony").state == "on"
    assert hass.states.get("select.tekla_cwu_tryb_ustaw").state == "Komfort"
    assert hass.states.get("switch.tekla_kociol_wlacz_wylacz") is not None
    assert hass.states.get("button.tekla_potwierdz_alarm") is not None
    assert hass.states.get("sensor.tekla_alarm_wpis_2") is not None
    # liczba encji: wszystkie z katalogu poza CO2 przy jednym obiegu
    ours = [s for s in hass.states.async_all() if s.entity_id.split(".")[1].startswith("tekla_")]
    assert len(ours) >= 185


async def test_services_have_card_compatible_names_and_write(hass: HomeAssistant, entry):
    assert hass.services.has_service(DOMAIN, "tekla_set_param")
    await hass.services.async_call(DOMAIN, "tekla_unlock", {"pin": 900}, blocking=True)
    await hass.services.async_call(DOMAIN, "tekla_set_setpoint", {"which": 4, "value": 73}, blocking=True)
    import asyncio

    for _ in range(40):
        await asyncio.sleep(0.25)
        coordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_refresh()
        if hass.states.get("sensor.tekla_kociol_zadana_reczna").state in ("73", "73.0"):
            break
    assert hass.states.get("sensor.tekla_kociol_zadana_reczna").state in ("73", "73.0")
    assert hass.states.get("sensor.tekla_poziom_dostepu").state in ("1", "1.0")


async def test_out_of_range_write_raises(hass: HomeAssistant, entry):
    from homeassistant.exceptions import HomeAssistantError

    with pytest.raises(HomeAssistantError):
        await hass.services.async_call(DOMAIN, "tekla_set_setpoint", {"which": 4, "value": 99}, blocking=True)


async def test_button_and_select_work(hass: HomeAssistant, entry):
    await hass.services.async_call("button", "press", {"entity_id": "button.tekla_dmuchawa_automat"}, blocking=True)
    await hass.services.async_call(
        "select", "select_option", {"entity_id": "select.tekla_cwu_tryb_ustaw", "option": "Eko"}, blocking=True
    )
