#pragma once
// Automat sieci: kiedy ESP ma wystawiać własny punkt dostępu (AP), a kiedy łączyć się z Wi-Fi (STA).
// Czysta logika (bez ESP-IDF); czas podawany z zewnątrz w ms.
#include <cstdint>

namespace tpc {

enum class NetState : uint8_t {
    Provisioning,  // brak zapisanej sieci: tylko AP + portal
    Connecting,    // są dane sieci: próba połączenia (AP wyłączony)
    Online,        // połączono (AP wyłączony)
    Fallback,      // nie można połączyć: AP + portal włączone, dalej próby STA w tle
    Trial,         // użytkownik wpisał nowe dane w portalu: AP zostaje, test połączenia
};

struct NetConfig {
    uint32_t connect_timeout_ms = 30000;   // tyle czekamy na połączenie, zanim włączymy AP
    uint32_t lost_grace_ms = 30000;        // po utracie sieci: próby bez AP
    uint32_t stable_ms = 10000;            // tyle musi trwać połączenie, by wyłączyć AP
    uint32_t trial_timeout_ms = 30000;     // test nowych danych z portalu
};

struct NetOutput {
    bool ap_on = false;
    bool sta_on = false;
    bool use_previous_credentials = false;  // po nieudanym teście wróć do poprzednich danych
    bool trial_failed = false;              // jednorazowo: portal ma pokazać błąd
    bool trial_ok = false;                  // jednorazowo: portal ma pokazać adres IP
};

class NetFsm {
public:
    explicit NetFsm(NetConfig cfg = {}) : cfg_(cfg) {}

    // Start: has_credentials = czy w NVS są dane sieci.
    void begin(bool has_credentials, uint32_t now_ms);

    // Zdarzenia z warstwy Wi-Fi.
    void on_sta_connected(uint32_t now_ms);
    void on_sta_disconnected(uint32_t now_ms);

    // Użytkownik zapisał nowe dane w portalu (wersja próbna).
    void on_new_credentials(bool had_previous, uint32_t now_ms);

    // Reset fabryczny (usunięte dane sieci).
    void on_factory_reset(uint32_t now_ms);

    // Wywoływać okresowo. Zwraca aktualne żądania dla warstwy Wi-Fi.
    NetOutput tick(uint32_t now_ms);

    NetState state() const { return state_; }

private:
    NetConfig cfg_;
    NetState state_ = NetState::Provisioning;
    uint32_t since_ms_ = 0;       // początek bieżącego stanu
    uint32_t connected_ms_ = 0;   // od kiedy trwa połączenie
    bool connected_ = false;
    bool had_previous_ = false;
    bool pending_ok_ = false, pending_fail_ = false, revert_ = false;
};

}  // namespace tpc
