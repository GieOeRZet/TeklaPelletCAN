"""Stałe integracji TeklaPelletCAN."""
DOMAIN = "teklapelletcan"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"
CONF_NAME = "name"
CONF_CARD = "card"
DEFAULT_PORT = 80
DEFAULT_NAME = "Tekla"
DEFAULT_CARD = "none"
SCAN_INTERVAL_S = 2

# Wybor karty w kreatorze konfiguracji – integracja nie wstrzykuje karty automatycznie,
# dopiero na podstawie jawnego wyboru (jedno repo = jeden wpis HACS, karty sa plikami
# wewnatrz integracji, nie osobnymi wpisami HACS).
CARD_CHOICES = ["none", "classic", "modern", "both"]

# Akcje (usługi) – identyczne jak w ESPHome PelletCAN; karta woła je jako <węzeł>_<akcja>.
ACTIONS = [
    "unlock", "set_setpoint", "set_boiler_mode", "set_param", "set_schedule", "set_output", "set_output_pct",
    "test_refresh", "test_reset", "alarm_refresh", "param_refresh", "schedule_refresh", "sdo_read", "sdo_scan",
    "sdo_scan_stop", "sdo_write", "sdo_poll_add", "sdo_poll_clear",
]
SELECT_OPTIONS = ["Off", "Eko", "Harmonogram", "Komfort"]
