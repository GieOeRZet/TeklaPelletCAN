#pragma once
// Katalog encji identyczny z ESPHome PelletCAN (rejestry/encje.csv): nazwy, domeny, jednostki.
#include <string>

namespace tpc {

struct Entity {
    const char* domain;    // sensor, binary_sensor, text_sensor, select, switch, button
    const char* id;        // identyfikator ESPHome (np. boiler_temp)
    const char* name;      // nazwa wyświetlana (np. "Kociol temperatura")
    const char* unit;
    const char* dclass;
    const char* source;    // id punktu silnika (odczyty.csv); "" = jeszcze nieprzeniesiona
};

extern const Entity kEntities[];
extern const unsigned kEntityCount;

// "Kociol temperatura" -> "kociol_temperatura" (małe litery, bez znaków diakrytycznych ASCII, _ zamiast reszty).
std::string slugify(const std::string& s);

// Domena HA dla domeny ESPHome (text_sensor -> sensor).
const char* ha_domain(const char* esphome_domain);

// entity_id w HA: <domena>.<prefiks>_<slug nazwy>
std::string entity_id(const Entity& e, const std::string& prefix);

}  // namespace tpc
