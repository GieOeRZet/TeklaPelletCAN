#!/usr/bin/env bash
# Uruchamiany wewnątrz emulatora (reactivecircus/android-emulator-runner): instaluje APK, robi zrzuty i test dymny przez CDP.
set -u
APK="$1"; OUT="$2"; mkdir -p "$OUT"
adb install -r -g "$APK" | tee "$OUT/install.txt"
adb logcat -c
adb shell am start -W -n pl.gieoerzet.teklapelletcan/.MainActivity | tee "$OUT/start.txt"
sleep 8
adb exec-out screencap -p > "$OUT/00_po_uruchomieniu.png"
PID=$(adb shell pidof pl.gieoerzet.teklapelletcan | tr -d '\r')
echo "pid=$PID" | tee "$OUT/pid.txt"
adb forward tcp:9222 localabstract:webview_devtools_remote_$PID
cd "$(dirname "$0")" && (npm ls ws >/dev/null 2>&1 || npm i --no-save ws >/dev/null 2>&1)
node cdp_smoke.js "$OUT" 2>&1 | tee "$OUT/wynik.txt"
RC=${PIPESTATUS[0]}
adb logcat -d -v time '*:W' | grep -E "pl.gieoerzet|chromium|AndroidRuntime|FATAL|tpc" | tail -150 > "$OUT/logcat.txt"
echo "rc=$RC" >> "$OUT/wynik.txt"
exit 0
