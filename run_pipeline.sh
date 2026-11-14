#!/usr/bin/env bash
set -euo pipefail

NEVENTS=${1:-100000}
EVENTS_FILE="events.root"
ANALYSIS_FILE="analysis.root"
PLOTS_DIR="plots"

echo "=== [1/4] Kompilacja programow C++17 (Pythia 8 + ROOT 6) ==="
make all

echo "=== [2/4] Generacja ${NEVENTS} zdarzen pp @ sqrt(s) = 13.6 TeV ==="
./generate_events "${NEVENTS}" "${EVENTS_FILE}"

echo "=== [3/4] Analiza zdarzen i tworzenie pliku ${ANALYSIS_FILE} ==="
./analyze_events "${EVENTS_FILE}" "${ANALYSIS_FILE}"

echo "=== [4/4] Generowanie wykresow PNG i PDF (draw_plots.C) ==="
root -b -q "draw_plots.C(\"${ANALYSIS_FILE}\", \"${PLOTS_DIR}\")"

echo "=== Gotowe! Wyniki zapisano w ${ANALYSIS_FILE} oraz katalogu ${PLOTS_DIR}/ ==="
