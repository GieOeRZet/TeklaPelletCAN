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


async def _finish_pair_flow(hass: HomeAssistant, flow_id: str, password: str = "qwerty123", name: str = "Tekla", card: str = "none"):
    """Konczy parowanie: krok auth (haslo) + krok card (wybor karty) -> CREATE_ENTRY."""
    # symuluje normalna instalacje, gdzie komponent "frontend" jest zaladowany (tu pomijany dla szybkosci testow)
    hass.data.setdefault("frontend_extra_module_url", set())
    r = await hass.config_entries.flow.async_configure(
        flow_id, {"password": password, "password_confirm": password, "name": name}
    )
    assert r["type"] is FlowResultType.FORM and r["step_id"] == "card"
    return await hass.config_entries.flow.async_configure(r["flow_id"], {"card": card})


async def test_config_flow_pairs_and_creates_entry(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    # literówka w powtórzeniu hasła -> błąd i ponowny formularz (urządzenie nie dostaje złego hasła)
    bad = await hass.config_entries.flow.async_configure(
        r["flow_id"], {"password": "qwerty123", "password_confirm": "qwerty124", "name": "Tekla"}
    )
    assert bad["type"] is FlowResultType.FORM and bad["errors"]["base"] == "password_mismatch"
    r = await _finish_pair_flow(hass, r["flow_id"])
    assert r["type"] is FlowResultType.CREATE_ENTRY
    assert r["data"]["token"] and r["data"]["host"] == host
    assert r["data"]["card"] == "none"
    assert r["result"].unique_id == "A1B2C3D4E5F6"


async def test_same_device_cannot_be_added_twice(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    await _finish_pair_flow(hass, r["flow_id"])
    r2 = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    r2 = await hass.config_entries.flow.async_configure(r2["flow_id"], {"host": host, "port": port})
    assert r2["type"] is FlowResultType.ABORT and r2["reason"] == "already_configured"


async def test_wrong_password_rejected(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    await _finish_pair_flow(hass, r["flow_id"])
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
    r = await _finish_pair_flow(hass, r["flow_id"])
    await hass.async_block_till_done()
    return r["result"]


async def test_card_choice_modern_adds_only_modern_resource(hass: HomeAssistant, sim):
    # integracja nie wstrzykuje zadnej karty "domyslnie" - tylko ta wybrana w kreatorze (tu: modern)
    host, port = sim
    r = await _pair_flow(hass, host, port)
    r = await _finish_pair_flow(hass, r["flow_id"], card="modern")
    await hass.async_block_till_done()
    assert r["data"]["card"] == "modern"
    extra_urls = hass.data["frontend_extra_module_url"]
    assert any(u.endswith("teklapelletcan-modern-card.js") for u in extra_urls)
    assert not any(u.endswith("teklapelletcan-card.js") and "modern" not in u for u in extra_urls)


async def test_card_choice_none_adds_no_resource(hass: HomeAssistant, sim):
    host, port = sim
    r = await _pair_flow(hass, host, port)
    await _finish_pair_flow(hass, r["flow_id"], card="none")
    await hass.async_block_till_done()
    extra_urls = hass.data.get("frontend_extra_module_url", set())
    assert not any("teklapelletcan" in u for u in extra_urls)


async def test_options_flow_changes_card_choice(hass: HomeAssistant, entry):
    # fixture "entry" parowana z card="none" (domyslne) - w opcjach zmieniamy na "classic"
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM and result["step_id"] == "init"
    result = await hass.config_entries.options.async_configure(result["flow_id"], {"card": "classic"})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    extra_urls = hass.data["frontend_extra_module_url"]
    assert any(u.endswith("/pelletcan-card.js") for u in extra_urls)
    assert any(u.endswith("/teklapelletcan-card.js") for u in extra_urls)


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
    # historia alarmow: skonsolidowana w 1 encje (dawniej 20 osobnych ah_0..ah_19) - wpisy jako atrybuty
    hist = hass.states.get("sensor.tekla_historia_alarmow")
    assert hist is not None and hist.attributes["ah_1"].startswith("kod 140")
    # palnik - nastawy serwisowe: skonsolidowane w 2 encje wg poziomu (dawniej 22 osobne p_*)
    p1 = hass.states.get("sensor.tekla_palnik_nastawy_serwisowe_poziom_1")
    assert p1 is not None and p1.attributes["p_prefeed"] == "60"
    # CO1 konfiguracja krzywej pogodowej: skonsolidowane w 2 encje wg poziomu (dawniej 19 osobnych co1_*)
    co1 = hass.states.get("sensor.tekla_co1_konfiguracja_krzywej_pogodowej_poziom_1")
    assert co1 is not None and co1.attributes["co1_tmax"] == "30"
    # Kociol konfiguracja: skonsolidowane w 3 encje wg poziomu (dawniej 17 osobnych, w tym k_*)
    kk = hass.states.get("sensor.tekla_kociol_konfiguracja_poziom_2")
    assert kk is not None and kk.attributes["k_nominal"] == "60"
    # Palnik krzywe dmuchawy i spalin: skonsolidowane w 1 encje (dawniej 10 osobnych fan_mod_*/exh_c*)
    pk = hass.states.get("sensor.tekla_palnik_krzywe_dmuchawy_i_spalin_poziom_1")
    assert pk is not None and pk.attributes["exh_c3"] == "30"
    # CWU konfiguracja: skonsolidowane w 2 encje wg poziomu (dawniej 8 osobnych)
    cwuk = hass.states.get("sensor.tekla_cwu_konfiguracja_poziom_0")
    assert cwuk is not None and cwuk.attributes["cwu_legion"] == "30"
    # Alarmy ustawienia: skonsolidowane w 1 encje (dawniej 3 osobne)
    alk = hass.states.get("sensor.tekla_alarmy_ustawienia_poziom_1")
    assert alk is not None and alk.attributes["alarm_snd"] == "30"
    # liczba encji: wszystkie z katalogu poza CO2 przy jednym obiegu (spadek z 165: konsolidacja
    # nastaw serwisowych - patrz AttrGroup w engine.cpp)
    ours = [s for s in hass.states.async_all() if s.entity_id.split(".")[1].startswith("tekla_")]
    assert len(ours) >= 90


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


async def test_forgotten_password_can_be_changed_from_ha(hass: HomeAssistant, entry):
    """Zapomniane hasło: HA (ma token) zmienia je usługą; nowy klient paruje się już nowym hasłem."""
    from custom_components.teklapelletcan.api import TeklaAuthError, TeklaClient
    from homeassistant.helpers.aiohttp_client import async_get_clientsession

    await hass.services.async_call(DOMAIN, "set_device_password", {"password": "nowe-haslo"}, blocking=True)
    c = TeklaClient(async_get_clientsession(hass), entry.data["host"], entry.data["port"])
    with pytest.raises(TeklaAuthError):
        await c.pair("qwerty123", "ktos-inny", "x")
    assert (await c.pair("nowe-haslo", "ktos-inny", "x"))["token"]
    # HA nadal działa dotychczasowym tokenem
    await hass.services.async_call(DOMAIN, "tekla_unlock", {"pin": 900}, blocking=True)
