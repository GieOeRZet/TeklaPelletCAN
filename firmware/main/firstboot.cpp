#include "firstboot.h"

// volatile + used: kompilator nie może założyć wartości pól (są zmieniane w pliku binarnym po zbudowaniu).
__attribute__((used, section(".data.tpc_firstboot")))
volatile FirstBoot g_firstboot = {
    {'T', 'P', 'C', '-', 'F', 'I', 'R', 'S', 'T', 'B', 'O', 'O', 'T', '-', 'v', '1'}, 0, 1, {0, 0}, {0}, {0}, {0}, {0}, {0}, {0}, {0}, {0, 0, 0, 0}};
