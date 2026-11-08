#pragma once
// Awaryjne przełączenie anteny: gdy wybrana antena zewnętrzna (U.FL) nie pozwala połączyć się z siecią,
// po tym samym czasie, po którym włączyłby się awaryjny AP, przełączamy na antenę wewnętrzną i łączymy ponownie.
// Czysta logika (czas z zewnątrz), testowana na hoście; sterowanie GPIO jest w warstwie ESP.
#include <cstdint>
#include "net_fsm.h"

namespace tpc {

struct AntennaOut {
    bool external = false;     // którą antenę ustawić teraz
    bool changed = false;      // true tylko w chwili przełączenia (warstwa ESP przełącza GPIO i łączy ponownie)
};

class AntennaFailover {
public:
    explicit AntennaFailover(bool configured_external) : configured_(configured_external), ext_(configured_external) {}

    // Wywoływać okresowo ze stanem automatu sieci.
    AntennaOut tick(NetState st) {
        AntennaOut o;
        if (ext_ && st == NetState::Fallback) {       // wcześniej brak połączenia przez cały czas oczekiwania
            ext_ = false;
            auto_ = true;
            o.changed = true;
        }
        o.external = ext_;
        return o;
    }

    bool using_external() const { return ext_; }
    bool auto_fallback() const { return auto_; }       // true = przełączono awaryjnie (do restartu)
    bool configured_external() const { return configured_; }

private:
    bool configured_, ext_, auto_ = false;
};

}  // namespace tpc
