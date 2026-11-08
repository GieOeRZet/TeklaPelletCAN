// Narzędzie testowe: czyta pakiet zapytania mDNS (hex na stdin) i wypisuje odpowiedź responderu (hex). Użyte w tests/test_mdns.py.
#include <cstdio>
#include <iostream>
#include <string>
#include <vector>
#include "../components/core/mdns.h"

int main(int argc, char** argv) {
    tpc::MdnsConfig c;
    c.host = "teklapelletcan-a1b2c3"; c.instance = "TeklaPelletCAN A1B2C3"; c.port = 80;
    c.ipv4 = (192u << 24) | (168u << 16) | (10u << 8) | 250u;
    c.txt = {"id=A1B2C3D4E5F6", "fw=0.2.0", "api=1"};
    std::string hex; std::getline(std::cin, hex);
    std::vector<uint8_t> q;
    for (size_t i = 0; i + 1 < hex.size(); i += 2) q.push_back((uint8_t)std::stoi(hex.substr(i, 2), nullptr, 16));
    auto r = argc > 1 && std::string(argv[1]) == "announce" ? tpc::mdns_announce(c) : tpc::mdns_respond(c, q.data(), q.size());
    for (auto b : r) printf("%02x", b);
    printf("\n");
    return 0;
}
