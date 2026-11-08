#pragma once
// Kolejka zapytań SDO: jedno zapytanie w locie, limit czasu, ponowienia.
// Czas z zewnątrz (ms); wysyłanie ramek przez funkcję `send`.
#include <cstdint>
#include <deque>
#include <functional>
#include "can_frame.h"
#include "sdo.h"

namespace tpc {

struct SdoJob {
    bool write = false;
    uint16_t index = 0;
    uint8_t sub = 1;
    uint32_t value = 0;  // zapis
    uint8_t size = 2;    // zapis: 1/2/4
    uint32_t tag = 0;    // dowolny znacznik wywołującego (np. klucz punktu)
};

enum class SdoOutcome : uint8_t { Ok, Abort, Timeout };

struct SdoResult {
    SdoJob job;
    SdoOutcome outcome = SdoOutcome::Timeout;
    uint32_t value = 0;        // odczyt: wartość
    uint8_t size = 0;
    uint32_t abort_code = 0;
};

class SdoQueue {
public:
    using SendFn = std::function<bool(const CanFrame&)>;
    using DoneFn = std::function<void(const SdoResult&)>;

    SdoQueue(uint8_t node, SendFn send, DoneFn done, uint32_t timeout_ms = 200, uint8_t retries = 2)
        : node_(node), send_(std::move(send)), done_(std::move(done)),
          timeout_ms_(timeout_ms), retries_(retries) {}

    // Dodaje zadanie. Zapisy trafiają przed odczyty (priorytet).
    void push(const SdoJob& job);
    size_t pending() const { return q_.size() + (busy_ ? 1 : 0); }

    // Odebrana ramka CAN (dowolna) – kolejka sama odfiltruje cudze.
    void on_frame(const CanFrame& f, uint32_t now_ms);

    // Wywoływać często (co kilka ms): wysyła następne zadanie, obsługuje limit czasu.
    void tick(uint32_t now_ms);

private:
    void start(uint32_t now_ms);
    void finish(const SdoResult& r);

    uint8_t node_;
    SendFn send_;
    DoneFn done_;
    uint32_t timeout_ms_;
    uint8_t retries_;
    std::deque<SdoJob> q_;
    bool busy_ = false;
    SdoJob cur_;
    uint8_t tries_ = 0;
    uint32_t sent_ms_ = 0;
};

}  // namespace tpc
