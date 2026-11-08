#pragma once
#include <cstdint>

namespace tpc {

struct AlarmName { uint16_t code; const char* name; };

extern const AlarmName kAlarmNames[];   // wygenerowane z rejestry/alarmy-kody.csv
extern const unsigned kAlarmNameCount;

// Nazwa alarmu dla kodu albo "" gdy nieznany.
const char* alarm_name(uint16_t code);

}  // namespace tpc
