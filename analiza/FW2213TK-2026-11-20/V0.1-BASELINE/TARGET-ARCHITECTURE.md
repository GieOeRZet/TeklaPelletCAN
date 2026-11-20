# Target Architecture — ESP32 / Home Assistant / PC Emulator

One canonical model should drive all targets:

                 CAN + parameter model
                         |
              +----------+----------+
              |          |          |
            ESP32        HA       Emulator
             TWAI      dynamic       PC
                       UI

## ESP32
can_hal
can_protocol
parameter_store
configuration_engine
alarm_engine
scheduler
ui_state_model
ha_api

## Home Assistant
Generate the card from schema:
- available screens
- zones
- parameters
- enum labels
- units
- read-only/editable state
- alarms
- schedules
- statistics

Configuration must change the generated UI automatically.

## Emulator
Base viewport 480x272.
Same canonical state model as ESP32.
Scenario runner and screenshot regression.

Example:
{
  "language": "PL",
  "access": 3,
  "params": {"0x10E": 2, "0x10F": 1, "0x10D": 2},
  "actions": ["home", "tap:CO1", "back", "tap:MENU"]
}

1:1 means matching externally observable behaviour:
screens, labels, values/scales, access rules, buttons, navigation, alarms/status, CAN effects, visibility/editability and, where required, pixel geometry/assets.