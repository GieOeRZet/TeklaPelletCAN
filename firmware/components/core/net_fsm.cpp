#include "net_fsm.h"

namespace tpc {

void NetFsm::begin(bool has_credentials, uint32_t now) {
    state_ = has_credentials ? NetState::Connecting : NetState::Provisioning;
    since_ms_ = now;
    connected_ = false;
}

void NetFsm::on_sta_connected(uint32_t now) {
    connected_ = true;
    connected_ms_ = now;
}

void NetFsm::on_sta_disconnected(uint32_t now) {
    connected_ = false;
    if (state_ == NetState::Online) {
        state_ = NetState::Connecting;  // krótka próba bez AP
        since_ms_ = now;
    }
}

void NetFsm::on_new_credentials(bool had_previous, uint32_t now) {
    state_ = NetState::Trial;
    since_ms_ = now;
    had_previous_ = had_previous;
    connected_ = false;
}

void NetFsm::on_factory_reset(uint32_t now) {
    state_ = NetState::Provisioning;
    since_ms_ = now;
    connected_ = false;
}

NetOutput NetFsm::tick(uint32_t now) {
    NetOutput o;
    const uint32_t in_state = now - since_ms_;
    const bool stable = connected_ && (now - connected_ms_) >= cfg_.stable_ms;

    switch (state_) {
        case NetState::Provisioning:
            break;
        case NetState::Connecting:
            if (connected_) { state_ = NetState::Online; since_ms_ = now; }
            else if (in_state >= cfg_.connect_timeout_ms) { state_ = NetState::Fallback; since_ms_ = now; }
            break;
        case NetState::Online:
            break;
        case NetState::Fallback:
            if (stable) { state_ = NetState::Online; since_ms_ = now; }
            break;
        case NetState::Trial:
            if (connected_) {
                pending_ok_ = true;
                // AP zostaje jeszcze na czas, w którym portal pokaże adres IP.
                if (stable) { state_ = NetState::Online; since_ms_ = now; }
            } else if (in_state >= cfg_.trial_timeout_ms) {
                pending_fail_ = true;
                revert_ = had_previous_;
                state_ = had_previous_ ? NetState::Connecting : NetState::Provisioning;
                since_ms_ = now;
            }
            break;
    }

    switch (state_) {
        case NetState::Provisioning: o.ap_on = true;  o.sta_on = false; break;
        case NetState::Connecting:   o.ap_on = false; o.sta_on = true;  break;
        case NetState::Online:       o.ap_on = false; o.sta_on = true;  break;
        case NetState::Fallback:     o.ap_on = true;  o.sta_on = true;  break;
        case NetState::Trial:        o.ap_on = true;  o.sta_on = true;  break;
    }
    o.trial_ok = pending_ok_;
    o.trial_failed = pending_fail_;
    o.use_previous_credentials = revert_;
    pending_ok_ = pending_fail_ = revert_ = false;
    return o;
}

}  // namespace tpc
