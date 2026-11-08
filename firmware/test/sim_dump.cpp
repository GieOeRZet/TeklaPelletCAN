// Symulator: uruchamia silnik z atrapą kotła i zrzuca stany (format HA) do pliku – dla testów karty w przeglądarce.
#include <cstdio>
#include <cstdlib>
#include "fake_boiler.h"
#include "../components/core/reads.h"

int main(int argc, char** argv) {
    const char* out = argc > 1 ? argv[1] : "states.json";
    FakeBoiler b;
    populate_demo(b);
    const uint8_t dev[6] = {1, 2, 3, 4, 5, 6};
    EngineConfig cfg; cfg.boot_delay_ms = 100;
    Engine e(cfg, [&](const CanFrame& f) { return b.on_can(f); }, dev);
    uint32_t t = 0;
    for (; t < 90000; t += 2) {
        e.tick(t);
        auto fr = b.to_engine; b.to_engine.clear();
        for (auto& f : fr) e.on_frame(f, t);
    }
    FILE* f = fopen(out, "w");
    std::string j = e.states_json("tekla", t);
    fwrite(j.data(), 1, j.size(), f);
    fclose(f);
    printf("zapisano %s (%zu B)\n", out, j.size());
    return 0;
}
