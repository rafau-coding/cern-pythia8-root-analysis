# Opis funkcji i struktur zdefiniowanych w projekcie (`functionalities.md`)

Poniżej przedstawiono pełne zestawienie wszystkich funkcji, metod oraz struktur pomocniczych opracowanych w ramach projektu, z podziałem na języki programowania oraz poszczególne pliki źródłowe.

---

## 1. Język C++17 (programy kompilowane oraz makro ROOT)

### 1.1. Plik [`generate_events.cc`](../generate_events.cc)
Program odpowiedzialny za symulację zderzeń $pp$ przy $\sqrt{s} = 13.6\text{ TeV}$ w generatorze Pythia 8 oraz zapis cząstek stanu końcowego do pliku `events.root`.

- **`int main(int argc, char* argv[])`**
  - **Argumenty wejściowe**:
    - `argc`, `argv`: opcjonalne argumenty linii poleceń:
      1. `argv[1]` – liczba zdarzeń do wygenerowania (`nEvents`, domyślnie `100000`),
      2. `argv[2]` – nazwa pliku wyjściowego ROOT (`outFileName`, domyślnie `"events.root"`).
  - **Działanie**:
    1. Konfiguracja obiektu `Pythia8::Pythia` dla wiązek protonowych (`idA = 2212`, `idB = 2212`) przy energii w układzie środka masy $\sqrt{s} = 13\,600\text{ GeV}$ w trybie *Minimum Bias* (`SoftQCD:all = on`) ze stałym ziarnem generatora liczb pseudolosowych (`Random:seed = 12345`).
    2. Utworzenie pliku wyjściowego `TFile` oraz drzewa `TTree` o nazwie `"Events"` z pięcioma gałęziami wektorowymi: `pdgId`, `isCharged`, `pt`, `eta`, `phi`.
    3. Generowanie kolejnych zdarzeń w pętli poprzez wywołanie `pythia.next()`, iteracja po wszystkich wyprodukowanych cząstkach, odrzucenie cząstek pośrednich (`if (!p.isFinal()) continue;`) oraz zapis właściwości kinematycznych cząstek stanu końcowego do drzewa `TTree`.
    4. Wypisanie statystyk końcowych (`pythia.stat()`) oraz zamknięcie pliku `.root`.

---

### 1.2. Plik [`analyze_events.cc`](../analyze_events.cc)
Program odczytujący drzewo `"Events"` z pliku `events.root`, klasyfikujący cząstki według kodu PDG i ładunku elektrycznego oraz zapisujący wymagane histogramy w pliku `analysis.root`.

#### Struktura **`CategoryHists`**
Struktura grupująca cztery wymagane histogramy (`hN`, `hPt`, `hEta`, `hPhi`) oraz licznik cząstek w bieżącym zdarzeniu (`countInEvent`) dla pojedynczej kategorii cząstek (`ch`, `all`, `pip`, `pim`, `Kp`, `Km`, `p`, `pbar`). Zdefiniowano w niej następujące metody:

- **`void CategoryHists::init(const std::string& suffix, const std::string& label)`**
  - **Zadanie**: Inicjalizacja czterech histogramów `TH1D` dla danej kategorii o nazwach `hN_<suffix>`, `hPt_<suffix>`, `hEta_<suffix>` oraz `hPhi_<suffix>`, ustawienie ich tytułów, podpisów osi oraz zakresów i liczby binów zgodnych ze specyfikacją zadania:
    - $N$: $400$ binów w zakresie $[0, 400]$,
    - $p_T$: $100$ binów w zakresie $[0, 10]\text{ GeV}$,
    - $\eta$: $100$ binów w zakresie $[-5, 5]$,
    - $\phi$: $64$ biny w zakresie $[0, \pi]\text{ rad}$.
    Dodatkowo metoda aktywuje obliczanie niepewności statystycznych (`Sumw2()`).
- **`void CategoryHists::resetEventCounter()`**
  - **Zadanie**: Wyzerowanie licznika cząstek danej kategorii (`countInEvent = 0`) przed rozpoczęciem analizy kolejnego zdarzenia.
- **`void CategoryHists::fillParticle(double pt, double eta, double phi)`**
  - **Zadanie**: Metoda wywoływana dla każdej cząstki zaklasyfikowanej do danej kategorii. Zwiększa licznik krotności `countInEvent` o $1$ oraz wypełnia histogramy kinematyczne: `hPt->Fill(pt)`, `hEta->Fill(eta)` oraz `hPhi->Fill(std::abs(phi))`.
- **`void CategoryHists::fillEventMultiplicity()`**
  - **Zadanie**: Metoda wywoływana jednokrotnie na koniec każdego zdarzenia – wpisuje łączną liczbę cząstek danej kategorii zaobserwowanych w danym zdarzeniu (`countInEvent`) do histogramu krotności `hN`.
- **`void CategoryHists::write()`**
  - **Zadanie**: Zapis wszystkich czterech histogramów (`hN`, `hPt`, `hEta`, `hPhi`) danej kategorii do otwartego pliku wynikowego `analysis.root`.

#### Funkcja główna:
- **`int main(int argc, char* argv[])`**
  - **Argumenty wejściowe**:
    - `argv[1]` – ścieżka do pliku wejściowego z drzewem zdarzeń (domyślnie `"events.root"`),
    - `argv[2]` – ścieżka do pliku wyjściowego z histogramami (domyślnie `"analysis.root"`).
  - **Działanie**:
    1. Otwarcie pliku `events.root` i powiązanie wskaźników wektorowych z gałęziami drzewa `"Events"`.
    2. Utworzenie pliku `analysis.root` i inicjalizacja obiektów `CategoryHists` dla wszystkich kategorii (`ch` / `all`, `pip`, `pim`, `Kp`, `Km`, `p`, `pbar`).
    3. Iteracja po wszystkich zdarzeniach i cząstkach:
       - dla cząstek spełniających warunek `isCharged != 0` aktualizowane są kategorie wszystkich cząstek naładowanych (`cat_ch` oraz `cat_all`),
       - za pomocą instrukcji `switch (id)` identyfikowany jest kod PDG ($\pm 211$, $\pm 321$, $\pm 2212$) i wypełniane są odpowiednie histogramy gatunkowe.
    4. Po przetworzeniu wszystkich cząstek w danym zdarzeniu aktualizowane są histogramy krotności `hN_*`, a po zakończeniu pętli po zdarzeniach wszystkie histogramy zapisywane są na dysk.

---

### 1.3. Plik [`draw_plots.C`](../draw_plots.C)
Makro środowiska ROOT 6 rysujące histogramy z pliku `analysis.root` i eksportujące je do plików `.png` oraz `.pdf`.

#### Struktury pomocnicze:
- **`struct SpeciesInfo`** – przechowuje metadane wizualne dla każdego gatunku cząstek:
  - `suffix` (np. `"pip"`),
  - `label` (etykieta w notacji `TLatex` pakietu ROOT, np. `"#pi^{+}"`),
  - `color` (kod koloru linii w pakiecie ROOT, np. `kRed+1`),
  - `lineStyle` (styl linii: ciągła `1` dla cząstek, przerywana `2` dla antycząstek).
- **`struct ObservableInfo`** – przechowuje ustawienia wykresu dla każdej z czterech analizowanych wielkości fizycznych (`hN`, `hPt`, `hEta`, `hPhi`):
  - `prefix` (prefiks nazwy histogramu),
  - `title` (tytuł główny wykresu),
  - `xTitle` oraz `yTitle` (podpisy osi X i Y zgodne ze specyfikacją zadania: `Multiplicity N`, `p_{T} [GeV]`, `#eta`, `#phi [rad]`),
  - `logY` (flaga określająca zastosowanie skali logarytmicznej na osi Y).

#### Funkcja główna makra:
- **`void draw_plots(const char* inFileName = "analysis.root", const char* outDir = "plots")`**
  - **Argumenty wejściowe**:
    - `inFileName` – nazwa pliku wejściowego z histogramami (domyślnie `"analysis.root"`),
    - `outDir` – katalog wyjściowy przeznaczony na wygenerowane wykresy (domyślnie `"plots"`).
  - **Działanie**:
    1. Konfiguracja globalnego stylu graficznego `gStyle` oraz utworzenie katalogu wyjściowego `plots/`.
    2. **Część 1 (wykresy indywidualne)**: w podwójnej pętli po wszystkich czterech obserwablach (`hN`, `hPt`, `hEta`, `hPhi`) i siedmiu kategoriach cząstek (`ch`, `pip`, `pim`, `Kp`, `Km`, `p`, `pbar`) tworzony jest osobny obiekt `TCanvas`, formatowane są osie, dodawana jest legenda i zapisywanych jest $28$ wykresów w formatach `.png` oraz `.pdf` (np. `plots/hPt_pip.png`, `plots/hPt_pip.pdf`).
    3. **Część 2 (wykresy zbiorcze/porównawcze)**: dla każdej z czterech obserwabli tworzony jest wspólny obiekt `TCanvas`, na który nakładane są rozkłady wszystkich siedmiu kategorii cząstek (`"HIST SAME"`), dodawana jest zbiorcza legenda `TLegend`, a wynik zapisywany jest do plików `summary_hN`, `summary_hPt`, `summary_hEta`, `summary_hPhi` w formatach `.png` i `.pdf`.

---

## 2. Język Python 3 (automatyczny generator prezentacji PDF)

### 2.1. Plik [`build_presentation.py`](../build_presentation.py)
Skrypt składający wyeksportowane ze środowiska ROOT wykresy w 11-slajdową prezentację `prezentacja.pdf`.

- **`trim_whitespace(png_path, pad=20)`**
  - **Zadanie**: Automatyczne wykrywanie granic obszaru rysowania na obrazie `.png` (poprzez porównanie pikseli z białym tłem za pomocą `ImageChops.difference`) oraz przycinanie nadmiarowych białych marginesów strony (np. wynikających z rozmiaru arkusza `MediaBox` w plikach PDF), z zachowaniem równomiernego odstępu `pad` wokół wykresu.
- **`ensure_png_from_pdf(plots_dir)`**
  - **Zadanie**: Weryfikacja obecności oraz aktualności plików `.png` w katalogu `plots_dir`. W przypadku gdy plików `.png` brakuje lub pliki `.pdf` zostały zaktualizowane (np. po ponownym uruchomieniu makra ROOT), funkcja automatycznie konwertuje każdy plik `.pdf` do formatu `.png` o wysokiej rozdzielczości (z wykorzystaniem biblioteki `PyMuPDF`, natywnego interfejsu `Windows.Data.Pdf` w systemie Windows lub narzędzia `pdftoppm -cropbox` w systemie Linux), a następnie wywołuje `trim_whitespace` dla każdego obrazu.
- **`add_header(fig, title, subtitle="")`**
  - **Zadanie**: Narysowanie w górnej części slajdu (`fig`) ciemnoniebieskiego paska nagłówkowego i umieszczenie na nim tytułu głównego oraz podtytułu slajdu.
- **`add_footer(fig, page_num, total_pages)`**
  - **Zadanie**: Narysowanie w dolnej części slajdu paska stopki zawierającego tytuł projektu po lewej stronie oraz numerację slajdów (`Slajd X / 11`) po prawej stronie.
- **`draw_image_on_axes(ax, img_path, title="")`**
  - **Zadanie**: Wczytanie pliku graficznego PNG ze ścieżki `img_path` i wyświetlenie go w zadanym panelu (`ax`) slajdu wraz z tytułem pomocniczym. W przypadku braku pliku wyświetlany jest komunikat diagnostyczny.
- **`build_presentation(plots_dir="plots", out_pdf="prezentacja.pdf")`**
  - **Zadanie**: Główna funkcja generująca dokument PDF przy użyciu klasy `PdfPages`. Tworzone są kolejno:
    - **Slajd 1**: Strona tytułowa projektu,
    - **Slajd 2**: Opis metodologii, parametrów generatora Pythia 8, kodów PDG i zakresów histogramów,
    - **Slajd 3**: Zestawienie $2 \times 2$ wykresów zbiorczych (`summary_hN`, `summary_hPt`, `summary_hEta`, `summary_hPhi`),
    - **Slajdy 4–10**: Zestawienia $2 \times 2$ czterech rozkładów ($N, p_T, \eta, \phi$) osobno dla każdej z siedmiu kategorii cząstek (`ch`, `pip`, `pim`, `Kp`, `Km`, `p`, `pbar`),
    - **Slajd 11**: Podsumowanie i wnioski z analizy danych oparte na statystykach widocznych na wygenerowanych wykresach.

---

## 3. Skrypty powłoki i automatyzacji (Bash / Make)

### 3.1. Plik [`run_pipeline.sh`](../run_pipeline.sh) (Bash)
Skrypt uruchamiający cały potok przetwarzania jednym poleceniem:
1. Kompilacja obu programów C++ za pomocą polecenia `make all`,
2. Uruchomienie programu `./generate_events` dla zadanej liczby zdarzeń (domyślnie `100000`),
3. Uruchomienie programu `./analyze_events`, generującego plik `analysis.root`,
4. Wywołanie w trybie wsadowym (`-b -q`) makra `root -b -q 'draw_plots.C("analysis.root", "plots")'`.

### 3.2. Plik [`Makefile`](../Makefile) (GNU Make)
Plik definiujący reguły kompilacji i konsolidacji (linkowania):
- **`all`**: kompilacja plików wykonywalnych `generate_events` oraz `analyze_events` z flagami `-std=c++17 -O2 -Wall -Wextra`, z automatycznym pobraniem ścieżek nagłówków i bibliotek z narzędzi `root-config` oraz `pythia8-config`.
- **`run`**: wykonanie pełnego cyklu generacji, analizy i rysowania wykresów.
- **`clean`**: usunięcie plików binarnych oraz tymczasowego pliku `events.root`.
