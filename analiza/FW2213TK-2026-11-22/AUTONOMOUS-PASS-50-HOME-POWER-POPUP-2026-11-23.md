# PASS 50 — okno "power" (kafelek prawy dol ekranu glownego) zalezne od konfiguracji

Render: `screens/render_HOME_power_popup_by_config.png` (cztery konfiguracje: PID 0x2105 Heating configuration / 0x2106 Hot water / 0x2107 Buffer / 0x2108 Solar).
- Zawsze: przelacznik "Kociol" (on/off) + przycisk OK.
- Wiersze trybow zaleznie od konfiguracji: "Ogrzewanie 1..N" (suwak 4-pozycyjny: off / eco / harmonogram / komfort), "Woda uzytkowa" (suwak 4-poz.). Konfig (1,0,0,0): tylko Ogrzewanie 1; (0,1,0,0): tylko Woda uzytkowa; (2,1,0,0) i (4,1,1,1): lista ogranicza sie do 3 widocznych wierszy (Ogrzewanie 1, 2, Woda) — przy 4 obwodach NIE widac 3. i 4. (przewijanie lub limit — do zbadania).
- Bufor i Solar w oknie nie maja wlasnych wierszy w badanych konfiguracjach.
- Do zbadania: skutki zmian (PID / ramki CAN) po suwaku, przelaczniku i OK.
