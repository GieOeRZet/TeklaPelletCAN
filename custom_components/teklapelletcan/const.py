"""Stałe integracji TeklaPelletCAN."""
DOMAIN = "teklapelletcan"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_TOKEN = "token"
CONF_NAME = "name"
DEFAULT_PORT = 80
DEFAULT_NAME = "Tekla"
SCAN_INTERVAL_S = 2

# Akcje (usługi) – identyczne jak w ESPHome PelletCAN; karta woła je jako <węzeł>_<akcja>.
ACTIONS = [
    "unlock", "set_setpoint", "set_boiler_mode", "set_param", "set_schedule", "set_output", "set_output_pct",
    "test_refresh", "test_reset", "alarm_refresh", "param_refresh", "schedule_refresh", "sdo_read", "sdo_scan",
    "sdo_scan_stop", "sdo_write", "sdo_poll_add", "sdo_poll_clear",
]
SELECT_OPTIONS = ["Off", "Eko", "Harmonogram", "Komfort"]
