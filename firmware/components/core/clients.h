#pragma once
// Sparowani klienci (HA, aplikacje, przeglądarki): tokeny, hasło urządzenia, blokada duplikatów.
#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace tpc {

struct ClientInfo {
    std::string id;      // identyfikator klienta (dla HA: installation_uuid, dla przeglądarki: losowy z localStorage)
    std::string name;
    std::string token;   // na urządzeniu przechowywany jako hash; w pamięci testowej jawnie
};

enum class PairResult : uint8_t { Ok, BadPassword, BadRequest };

// Magazyn: implementacja pamięciowa (testy) i NVS (urządzenie) wspólny interfejs.
class ClientStore {
public:
    virtual ~ClientStore() = default;
    virtual bool has_password() const = 0;
    virtual bool set_password(const std::string& pw) = 0;
    virtual bool check_password(const std::string& pw) const = 0;
    virtual bool valid_token(const std::string& token) const = 0;
    virtual std::vector<ClientInfo> list() const = 0;
    virtual bool put(const ClientInfo& c) = 0;          // dodaje lub zastępuje klienta o tym samym id
    virtual bool remove(const std::string& id) = 0;
};

class MemoryClientStore : public ClientStore {
public:
    bool has_password() const override { return !pw_.empty(); }
    bool set_password(const std::string& pw) override { pw_ = pw; return true; }
    bool check_password(const std::string& pw) const override { return !pw_.empty() && pw == pw_; }
    bool valid_token(const std::string& t) const override {
        if (t.empty()) return false;
        for (auto& c : clients_) if (c.token == t) return true;
        return false;
    }
    std::vector<ClientInfo> list() const override { return clients_; }
    bool put(const ClientInfo& c) override {
        for (auto& x : clients_) if (x.id == c.id) { x = c; return true; }
        clients_.push_back(c);
        return true;
    }
    bool remove(const std::string& id) override {
        for (size_t i = 0; i < clients_.size(); i++) if (clients_[i].id == id) { clients_.erase(clients_.begin() + i); return true; }
        return false;
    }

private:
    std::string pw_;
    std::vector<ClientInfo> clients_;
};

}  // namespace tpc
