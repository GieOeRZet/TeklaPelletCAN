#pragma once
// Kodowanie wartości rejestrów kotła (U16, sub 1) – zgodnie z rejestry/README.md.
#include <cstdint>

namespace tpc {

enum class Encoding : uint8_t {
    Plain,     // raw = wartość
    PlainS16,  // raw = wartość jako int16 (U16 w kodzie uzupełnień do 2)
    TenthsS16, // raw = wartość * 10 jako int16
    FlagByte,  // raw = 256 + wartość (młodszy bajt = wartość, bit 8 = flaga)
    Tenths,    // raw = wartość * 10
    FlagTenths,// raw = 256 + wartość * 10 (wartość 0..25.5)
    Switch,    // 256 = wył., 257 = wł.
    EnumList,  // raw = 256 + indeks
    Mask24,    // maska godzin (bit i = godzina i)
    UnixTime,  // sekundy Unix
};

// Wynik dekodowania: wartość fizyczna jako double. ok=false gdy raw niezgodny z kodowaniem.
struct Decoded {
    bool ok = false;
    double value = 0;
};

Decoded decode(Encoding enc, uint32_t raw);

// Koduje wartość fizyczną do raw. ok=false gdy poza zakresem kodowania.
struct Encoded {
    bool ok = false;
    uint32_t raw = 0;
};

Encoded encode(Encoding enc, double value);

}  // namespace tpc
