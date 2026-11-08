#include "alarms.h"

namespace tpc {

const char* alarm_name(uint16_t code) {
    for (unsigned i = 0; i < kAlarmNameCount; i++)
        if (kAlarmNames[i].code == code) return kAlarmNames[i].name;
    return "";
}

}  // namespace tpc
