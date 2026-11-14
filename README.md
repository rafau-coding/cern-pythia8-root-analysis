# Symulacja i analiza rozkładów cząstek dla zderzeń $pp$ @ $\sqrt{s} = 13.6\text{ TeV}$ (Pythia 8 + ROOT 6)

Kompletny, w pełni reprodukowalny potok przetwarzania (pipeline) obejmujący generację zdarzeń proton–proton przy energii $\sqrt{s} = 13.6\text{ TeV}$ (tryb *Minimum Bias / SoftQCD*) w generatorze **Pythia 8**, analizę cząstek stanu końcowego w **C++17 / ROOT 6**, wizualizację wyników oraz automatyczne przygotowanie prezentacji PDF.

---

## Zawartość repozytorium (zestaw oddawanych plików)

Zgodnie ze specyfikacją zadania w repozytorium znajdują się następujące elementy:

1. **Program i skrypt uruchamiający generator Pythia 8**:
   - [`generate_events.cc`](./generate_events.cc) – program w C++17 generujący $100\,000$ zdarzeń $pp$ przy $\sqrt{s} = 13.6\text{ TeV}$ (`Beams:eCM = 13600`, `SoftQCD:all = on`, stałe ziarno losowe `Random:seed = 12345`), filtrujący wyłącznie cząstki w stanie końcowym (`p.isFinal()`) i zapisujący je do drzewa `TTree` (`events.root`).
   - [`run_pipeline.sh`](./run_pipeline.sh) – skrypt powłoki automatyzujący kompilację i uruchomienie całego potoku.
2. **Program w C++/ROOT tworzący plik `analysis.root`**:
   - [`analyze_events.cc`](./analyze_events.cc) – program w C++17 / ROOT 6 wyznaczający rozkłady krotności ($N$), pędu poprzecznego ($p_T$), pseudorapidity ($\eta$) oraz kąta azymutalnego ($\phi$) dla wszystkich cząstek naładowanych (`ch` / `all`), pionów ($\pi^+, \pi^-$), kaonów ($K^+, K^-$) i protonów ($p, \bar{p}$).
3. **Makro rysujące w ROOT**:
   - [`draw_plots.C`](./draw_plots.C) – makro ROOT otwierające plik `analysis.root`, rysujące histogramy na oddzielnych canvasach (zarówno indywidualnych dla każdej kategorii, jak i zbiorczych z legendą) oraz eksportujące je do formatów **PNG** i **PDF** w katalogu `plots/`.
4. **Plik wynikowy ROOT**:
   - `analysis.root` – plik zawierający wszystkie wymagane histogramy (`hN_*`, `hPt_*`, `hEta_*`, `hPhi_*`).
5. **Prezentacja w PDF zawierająca wszystkie uzyskane wykresy**:
   - `prezentacja.pdf` – prezentacja generowana skryptem [`build_presentation.py`](./build_presentation.py) na podstawie wyeksportowanych wykresów z katalogu `plots/`.
6. **Dodatkowa dokumentacja projektu (katalog [`docs/`](./docs/))**:
   - [`docs/libraries.md`](./docs/libraries.md) – szczegółowy opis wszystkich bibliotek wykorzystanych w projekcie (Pythia 8, ROOT 6, STL C++17, Python) wraz z omówieniem wywołanych gotowych klas i funkcji.
   - [`docs/functionalities.md`](./docs/functionalities.md) – opis wszystkich funkcji, metod i struktur zdefiniowanych w projekcie, w podziale na języki programowania i pliki źródłowe.
   - [`docs/theoretical_overview.md`](./docs/theoretical_overview.md) – wprowadzenie teoretyczne wyjaśniające fizykę zderzeń $pp$, strukturę danych w generatorze Pythia 8 oraz znaczenie poszczególnych zmiennych ($N$, $p_T$, $\eta$, $\phi$) i kodów PDG.

---

## Struktura katalogów projektu

```text
├── .github/                  # Konfiguracja GitHub Actions (workflow CI/CD)
├── docs/                     # Dodatkowa dokumentacja opisowa
│   ├── functionalities.md
│   ├── libraries.md
│   └── theoretical_overview.md
├── plots/                    # Wygenerowane wykresy wynikowe (.png oraz .pdf)
├── .gitattributes            # Konfiguracja końców linii i atrybutów repozytorium
├── .gitignore                # Lista plików ignorowanych przez Git
├── Makefile                  # Automatyzacja kompilacji programów C++
├── README.md                 # Główna dokumentacja projektu i instrukcja uruchomienia
├── analysis.root             # Wymagany plik wynikowy z histogramami
├── analyze_events.cc         # Kod źródłowy C++/ROOT analizujący zdarzenia
├── build_presentation.py     # Skrypt Python generujący prezentację PDF
├── draw_plots.C              # Makro ROOT rysujące i eksportujące wykresy
├── generate_events.cc        # Kod źródłowy C++ generujący zdarzenia w Pythia 8
├── prezentacja.pdf           # Gotowa prezentacja wynikowa
└── run_pipeline.sh           # Skrypt bash uruchamiający cały potok krok po kroku
```

---

## Szczegóły fizyczne i techniczne

### Mapowanie PDG oraz kategorie cząstek
Analizie poddawane są **wyłącznie cząstki w stanie końcowym** (`pythia.event[i].isFinal() == true`):
- **`ch` / `all` (All charged)**: wszystkie cząstki końcowe o ładunku elektrycznym $\neq 0$ (`isCharged() == true`),
- **`pip` ($\pi^+$)**: $\text{PDG ID} = +211$,
- **`pim` ($\pi^-$)**: $\text{PDG ID} = -211$,
- **`Kp` ($K^+$)**: $\text{PDG ID} = +321$,
- **`Km` ($K^-$)**: $\text{PDG ID} = -321$,
- **`p` ($p$)**: $\text{PDG ID} = +2212$,
- **`pbar` ($\bar{p}$)**: $\text{PDG ID} = -2212$.

### Zakresy i binowanie histogramów
| Wielkość | Prefiks histogramu | Zakres osi X | Liczba binów | Podpis osi X |
| :--- | :--- | :--- | :--- | :--- |
| Krotność na zdarzenie ($N$) | `hN_*` | $0 - 400$ | $400$ | `Multiplicity N` |
| Pęd poprzeczny ($p_T$) | `hPt_*` | $0 - 10\text{ GeV}$ | $100$ | `p_{T} [GeV]` |
| Pseudorapidity ($\eta$) | `hEta_*` | $-5\text{ do }5$ | $100$ | `\eta` (`#eta`) |
| Kąt azymutalny ($\phi$) | `hPhi_*` | $0 - \pi\text{ rad}$ | $64$ | `\phi [rad]` (`#phi [rad]`) |

---

## Wymagania techniczne

- Kompilator obsługujący standard **C++17** (`g++` lub `clang++`)
- **ROOT 6** (`root-config` oraz `root` dostępne w zmiennej środowiskowej `PATH`)
- **Pythia 8** (`pythia8-config` dostępne w zmiennej środowiskowej `PATH`)
- Opcjonalnie: **Python 3** z bibliotekami `matplotlib` oraz `pillow` (w celu zbudowania pliku `prezentacja.pdf`)

---

## Instrukcja kompilacji i uruchomienia

### Sposób 1: Automatyczne uruchomienie potoku (skrypt `run_pipeline.sh` lub `Makefile`)

W środowisku Linux / macOS / WSL2 z zainstalowanym pakietem ROOT 6 oraz Pythia 8 należy wykonać polecenia:

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh 100000
```

Skrypt realizuje kolejno następujące kroki:
1. Kompilację programów `generate_events` oraz `analyze_events` (`make all`),
2. Generację $100\,000$ zdarzeń $pp$ @ $\sqrt{s} = 13.6\text{ TeV}$ do pliku `events.root`,
3. Przeprowadzenie analizy i zapis histogramów do pliku `analysis.root`,
4. Uruchomienie makra `root -b -q 'draw_plots.C("analysis.root", "plots")'`, zapisującego wykresy PNG i PDF w katalogu `plots/`.

W celu wygenerowania prezentacji PDF ze wszystkimi wykresami należy wykonać:

```bash
python3 build_presentation.py plots prezentacja.pdf
```

### Sposób 2: Ręczna kompilacja i uruchomienie krok po kroku

```bash
g++ -std=c++17 -O2 -Wall -Wextra generate_events.cc -o generate_events \
    $(pythia8-config --cflags) $(root-config --cflags) \
    $(pythia8-config --libs) $(root-config --libs)

g++ -std=c++17 -O2 -Wall -Wextra analyze_events.cc -o analyze_events \
    $(root-config --cflags) $(root-config --libs)

./generate_events 100000 events.root

./analyze_events events.root analysis.root

root -b -q 'draw_plots.C("analysis.root", "plots")'

python3 build_presentation.py plots prezentacja.pdf
```

### Sposób 3: Automatyczna reprodukcja przez GitHub Actions

Repozytorium zawiera skonfigurowany przepływ pracy [`.github/workflows/pipeline.yml`](./.github/workflows/pipeline.yml). Po przesłaniu kodu na serwer GitHub (`git push`):
1. Środowisko uruchomieniowe `ubuntu-latest` instaluje pakiety `root` (ROOT 6) oraz `pythia8` (Pythia 8.3) z kanału `conda-forge`,
2. Kompilowane i uruchamiane są programy `generate_events` ($100\,000$ zdarzeń) oraz `analyze_events`,
3. Wykonywane jest makro `draw_plots.C` w środowisku ROOT 6 oraz budowany jest plik `prezentacja.pdf`,
4. Wygenerowane pliki `analysis.root`, `plots/*.png`, `plots/*.pdf` oraz `prezentacja.pdf` są automatycznie dołączane do gałęzi repozytorium GitHub oraz udostępniane jako artefakt (`analysis-results`).
