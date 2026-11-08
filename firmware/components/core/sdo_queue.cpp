#include "sdo_queue.h"

namespace tpc {

void SdoQueue::push(const SdoJob& job) {
    if (job.write) {
        // zapisy przed odczytami, ale za wcześniejszymi zapisami
        auto it = q_.begin();
        while (it != q_.end() && it->write) ++it;
        q_.insert(it, job);
    } else {
        q_.push_back(job);
    }
}

void SdoQueue::start(uint32_t now) {
    CanFrame f = cur_.write ? sdo_write_request(node_, cur_.index, cur_.sub, cur_.value, cur_.size)
                            : sdo_read_request(node_, cur_.index, cur_.sub);
    sent_ms_ = now;
    if (f.id == 0 || !send_(f)) {
        // nie wysłano (zajęty bufor) – spróbuj w następnym tiku, liczy się jako podejście
        sent_ms_ = now - timeout_ms_;
    }
}

void SdoQueue::finish(const SdoResult& r) {
    busy_ = false;
    if (done_) done_(r);
}

void SdoQueue::tick(uint32_t now) {
    if (!busy_) {
        if (q_.empty()) return;
        cur_ = q_.front();
        q_.pop_front();
        busy_ = true;
        tries_ = 0;
        start(now);
        return;
    }
    if (now - sent_ms_ >= timeout_ms_) {
        if (tries_ < retries_) {
            tries_++;
            start(now);
        } else {
            SdoResult r;
            r.job = cur_;
            r.outcome = SdoOutcome::Timeout;
            finish(r);
        }
    }
}

void SdoQueue::on_frame(const CanFrame& f, uint32_t) {
    if (!busy_) return;
    SdoReply p = sdo_parse_reply(node_, f);
    if (p.status == SdoStatus::BadFrame) return;
    if (p.index != cur_.index || p.sub != cur_.sub) return;  // odpowiedź na inne zapytanie
    SdoResult r;
    r.job = cur_;
    if (p.status == SdoStatus::Abort) {
        r.outcome = SdoOutcome::Abort;
        r.abort_code = p.abort_code;
    } else if (p.is_write_ack == cur_.write) {
        r.outcome = SdoOutcome::Ok;
        r.value = p.value;
        r.size = p.size;
    } else {
        return;
    }
    finish(r);
}

}  // namespace tpc
