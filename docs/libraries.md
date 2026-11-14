# Opis bibliotek i gotowych funkcji wykorzystanych w projekcie (`libraries.md`)

W projekcie wykorzystano biblioteki standardowe języka **C++17**, specjalistyczne pakiety fizyki wysokich energii (**Pythia 8** oraz **ROOT 6**), a także biblioteki języka **Python 3** (służące do wygenerowania prezentacji PDF). Poniżej przedstawiono szczegółowe zestawienie wszystkich bibliotek oraz wywołanych z nich gotowych klas, metod i funkcji.

---

## 1. Biblioteki C++ – Generator zdarzeń: **Pythia 8**

### `"Pythia8/Pythia.h"`
Główny plik nagłówkowy generatora zdarzeń Monte Carlo **Pythia 8**, przeznaczonego do symulacji zderzeń cząstek elementarnych przy wysokich energiach.

#### Wykorzystane klasy i obiekty:
- **`Pythia8::Pythia`** – główna klasa sterująca symulacją (inicjalizacja wiązek, wybór procesów fizycznych, generowanie kolejnych zderzeń oraz podsumowanie statystyczne).
- **`pythia.event`** (obiekt klasy `Pythia8::Event`) – kontener przechowujący listę wszystkich cząstek wyprodukowanych w bieżącym zdarzeniu (zarówno początkowych, pośrednich, jak i końcowych).
- **`Pythia8::Particle`** (element zwracany przez `pythia.event[i]`) – obiekt reprezentujący pojedynczą cząstkę w zapisie zdarzenia.

#### Wykorzystane gotowe metody z pakietu Pythia 8:
- **`pythia.readString(const std::string& line)`** – przekazuje tekstową komendę konfiguracyjną do silnika Pythia 8 (np. `"Beams:idA = 2212"`, `"Beams:eCM = 13600."`, `"SoftQCD:all = on"`, `"Random:setSeed = on"`).
- **`pythia.init()`** – inicjalizuje generator na podstawie wczytanych parametrów (oblicza przekroje czynne, inicjuje strukturę partonową protonów itp.). Zwraca wartość `true` w przypadku powodzenia lub `false` w razie błędu.
- **`pythia.next()`** – generuje jedno pełne zdarzenie (pojedyncze zderzenie proton–proton) i wypełnia tablicę `pythia.event`. Zwraca `true`, jeśli zdarzenie zostało poprawnie wygenerowane.
- **`pythia.stat()`** – wypisuje na standardowe wyjście tabelę podsumowującą przebieg symulacji (liczbę wygenerowanych zdarzeń, przekroje czynne w milibarnach oraz ewentualne ostrzeżenia i błędy).
- **`pythia.event.size()`** – zwraca całkowitą liczbę cząstek zapisanych w historii bieżącego zdarzenia.
- **`p.isFinal()`** – metoda klasy `Particle` zwracająca `true`, jeśli cząstka znajduje się w **stanie końcowym** (tj. nie uległa dalszemu rozpadowi ani fragmentacji i dociera do detektora).
- **`p.id()`** – zwraca kod identyfikacyjny cząstki zgodny ze standardem **PDG** (*Particle Data Group*), np. `211` dla $\pi^+$, `-211` dla $\pi^-$, `2212` dla protonu.
- **`p.isCharged()`** – zwraca `true`, jeśli cząstka posiada niezerowy ładunek elektryczny ($Q \neq 0$).
- **`p.pT()`** – oblicza i zwraca pęd poprzeczny cząstki $p_T = \sqrt{p_x^2 + p_y^2}$ wyrażony w $\text{GeV}/c$.
- **`p.eta()`** – oblicza i zwraca pseudopospieszność (*pseudorapidity*) cząstki $\eta = -\ln\tan(\theta/2)$.
- **`p.phi()`** – oblicza i zwraca kąt azymutalny cząstki $\phi = \text{atan2}(p_y, p_x)$ w radianach (w przedziale $[-\pi, \pi]$).

---

## 2. Biblioteki C++ – Pakiet analizy danych CERN **ROOT 6**

Pakiet **ROOT 6** został zastosowany we wszystkich trzech modułach C++ (`generate_events.cc`, `analyze_events.cc` oraz `draw_plots.C`) do zapisu drzew danych, tworzenia histogramów oraz generowania wykresów.

### `"TFile.h"` – obsługa plików binarnych `.root`
- **`TFile::Open(const char* name, Option_t* option)`** – statyczna metoda otwierająca plik ROOT w zadanym trybie (`"RECREATE"` – utworzenie nowego pliku lub nadpisanie istniejącego; `"READ"` – otwarcie pliku w trybie tylko do odczytu).
- **`file->IsZombie()`** – zwraca `true`, jeśli otwarcie pliku zakończyło się niepowodzeniem (plik uszkodzony lub brak dostępu).
- **`file->Get(const char* namecycle)`** – pobiera obiekt (np. drzewo `TTree` lub histogram `TH1D`) zapisany wewnątrz pliku `.root` na podstawie jego nazwy.
- **`file->cd()`** – ustawia dany plik jako bieżący katalog roboczy w pamięci środowiska ROOT, do którego zapisywane są obiekty.
- **`file->Write()`** – zapisuje wszystkie utworzone w bieżącym kontekście obiekty (np. drzewo `TTree`) na dysk.
- **`file->Close()`** – zamyka plik `.root` i zwalnia powiązane bufory wejścia/wyjścia.

### `"TTree.h"` – drzewa danych kolumnowych (zapis zdarzenie po zdarzeniu)
- **`new TTree(const char* name, const char* title)`** – konstruktor tworzący nowe drzewo danych (w projekcie drzewo o nazwie `"Events"`).
- **`tree->Branch(const char* name, void* address)`** – tworzy nową gałąź (kolumnę) w drzewie `TTree` i wiąże ją ze wskaźnikiem na wektor C++ (`std::vector<...>`), do którego wpisywane są właściwości cząstek w danym zdarzeniu.
- **`tree->Fill()`** – zatwierdza bieżące wartości zmiennych i wektorów powiązanych z gałęziami jako nowy wiersz (nowe zdarzenie) w drzewie.
- **`tree->SetBranchAddress(const char* bname, void* add)`** – podczas odczytu pliku `.root` wiąże gałąź drzewa z adresem wskaźnika w programie analizującym.
- **`tree->GetEntries()`** – zwraca całkowitą liczbę zapisanych zdarzeń (wierszy) w drzewie (typu `Long64_t`).
- **`tree->GetEntry(Long64_t entry)`** – wczytuje z dysku dane z pojedynczego zdarzenia o indeksie `entry` do powiązanych wektorów w pamięci operacyjnej.

### `"TH1D.h"` – jednowymiarowe histogramy zmiennoprzecinkowe (podwójnej precyzji)
- **`new TH1D(const char* name, const char* title, Int_t nbinsx, Double_t xlow, Double_t xup)`** – tworzy jednowymiarowy histogram typu `double`. Parametr `title` przyjmuje format `"Tytuł główny;Podpis osi X;Podpis osi Y"`.
- **`h->Sumw2()`** – aktywuje przechowywanie sumy kwadratów wag w każdym binie, co zapewnia poprawne wyznaczanie niepewności statystycznych ($\sqrt{N}$).
- **`h->Fill(Double_t x)`** – zwiększa zawartość binu odpowiadającego wartości `x` o $1$.
- **`h->Write()`** – zapisuje pojedynczy histogram do aktualnie otwartego pliku `TFile`.
- **`h->Clone(const char* newname)`** – tworzy głęboką kopię histogramu pod nową nazwą (funkcja wykorzystywana przy rysowaniu wykresów zbiorczych).
- **`h->GetMaximum()`** – zwraca wartość najwyższego binu w histogramie (służy do automatycznego dopasowania skali osi Y).
- **`h->SetMinimum(Double_t min)` / `h->SetMaximum(Double_t max)`** – ustala dolny i górny zakres osi pionowej (Y) na wykresie.
- **`h->SetLineColor(Color_t color)` / `h->SetLineWidth(Width_t width)` / `h->SetLineStyle(Style_t style)`** – metody formatujące wygląd linii histogramu (kolor np. `kBlack`, `kRed+1`, `kBlue+1`, grubość linii w pikselach, styl linii ciągłej lub przerywanej).
- **`h->SetTitle(const char* title)`** – ustawia tytuł główny wykresu.
- **`h->GetXaxis()` / `h->GetYaxis()`** – zwracają wskaźnik na obiekt osi (`TAxis`), na którym wywoływane są metody:
  - **`SetTitle(const char*)`** – podpis osi (np. `"p_{T} [GeV]"`, `"#eta"`, `"#phi [rad]"`),
  - **`SetTitleSize(Float_t)`** – rozmiar czcionki podpisu osi,
  - **`SetTitleOffset(Float_t)`** – odstęp podpisu od osi.
- **`h->Draw(Option_t* option)`** – rysuje histogram na aktywnym płótnie (`"HIST"` – obrys schodkowy bez znaczników błędów; `"HIST SAME"` – nałożenie kolejnego histogramu na istniejący układ współrzędnych).

### `"TCanvas.h"`, `"TLegend.h"`, `"TStyle.h"`, `"TSystem.h"`, `"TMath.h"` – wizualizacja i narzędzia środowiska ROOT
- **`new TCanvas(const char* name, const char* title, Int_t ww, Int_t wh)`** – tworzy okno graficzne (płótno) o zadanej szerokości `ww` i wysokości `wh` w pikselach.
  - **`c->SetLeftMargin(...)` / `SetRightMargin(...)` / `SetBottomMargin(...)`** – ustawia marginesy wokół układu współrzędnych.
  - **`c->SetGrid()`** – włącza siatkę pomocniczą na wykresie.
  - **`c->SetLogy()`** – przełącza oś Y w skalę logarytmiczną (stosowane dla rozkładów krotności $N$ oraz pędu poprzecznego $p_T$, obejmujących wiele rzędów wielkości).
  - **`c->SaveAs(const char* filename)`** – eksportuje zawartość canvasu do pliku graficznego na podstawie rozszerzenia (`.png` lub `.pdf`).
- **`new TLegend(Double_t x1, Double_t y1, Double_t x2, Double_t y2)`** – tworzy legendę w znormalizowanych współrzędnych padu ($[0, 1]$).
  - **`leg->SetBorderSize(1)` / `SetFillColor(0)` / `SetTextSize(...)`** – konfiguruje obramowanie, białe tło i rozmiar tekstu legendy.
  - **`leg->SetHeader(const char* header, Option_t* option)`** – ustawia wyśrodkowany nagłówek legendy.
  - **`leg->AddEntry(const TObject* obj, const char* label, Option_t* option)`** – dodaje wpis w legendzie powiązany ze stylem linii (`"l"`) danego histogramu.
  - **`leg->Draw()`** – rysuje legendę na aktywnym canvasie.
- **`gStyle`** (globalny wskaźnik klasy `TStyle`):
  - **`gStyle->SetOptStat(Int_t mode)`** – steruje wyświetlaniem ramki statystyk (`1110` – wyświetla liczbę zliczeń, średnią i odchylenie standardowe; `0` – ukrywa ramkę na wykresach porównawczych).
  - **`gStyle->SetStatX(...)` / `SetStatY(...)` / `SetStatW(...)` / `SetStatH(...)`** – precyzyjnie określają położenie (prawy górny róg w znormalizowanych współrzędnych NDC) oraz szerokość i wysokość ramki statystyk, zapobiegając jej nakładaniu się na legendę wykresu.
  - **`gStyle->SetPadTickX(1)` / `SetPadTickY(1)`** – włącza znaczniki podziałki na górnej i prawej krawędzi wykresu.
  - **`gStyle->SetTitleFontSize(...)`** – ustawia rozmiar czcionki tytułów głównych.
- **`gSystem->mkdir(const char* name, Bool_t recursive)`** (z `"TSystem.h"`) – tworzy katalog wyjściowy (np. `plots/`) w sposób niezależny od systemu operacyjnego (`recursive = kTRUE` odpowiada poleceniu `mkdir -p`).
- **`TMath::Pi()`** (z `"TMath.h"`) – zwraca stałą matematyczną $\pi$ z podwójną precyzją.

---

## 3. Biblioteka standardowa C++17 (STL)

- **`<iostream>`**:
  - `std::cout`, `std::cerr`, `std::endl` – strumienie wyjścia standardowego oraz wyjścia błędów.
- **`<vector>`**:
  - `std::vector<T>` – dynamiczna tablica przechowująca właściwości cząstek w pojedynczym zdarzeniu (`pdgId`, `isCharged`, `pt`, `eta`, `phi`) oraz wskaźniki na rysowane histogramy.
  - Metody: `clear()` (opróżnienie wektora przed kolejnym zdarzeniem), `push_back(val)` (dodanie elementu na koniec wektora), `size()` (zwrócenie liczby elementów w wektorze).
- **`<string>`**:
  - `std::string` – obsługa łańcuchów znaków (ścieżki do plików, nazwy i tytuły histogramów).
  - `std::stoi(const std::string&)` – konwersja argumentu linii poleceń (`argv[1]`) z postaci tekstowej na liczbę całkowitą `int` (liczba zdarzeń).
  - `c_str()` – konwersja obiektu `std::string` na wskaźnik `const char*` wymagany przez interfejsy biblioteki ROOT.
- **`<cmath>`**:
  - `std::abs(double)` – wyznaczenie wartości bezwzględnej kąta $\phi$, odwzorowujące przedział $[-\pi, \pi]$ na $[0, \pi]$.

---

## 4. Biblioteki języka Python 3 (`build_presentation.py`)

W skrypcie `build_presentation.py` zastosowano biblioteki języka Python do automatycznego złożenia wyeksportowanych wykresów `.png` w wielostronicową prezentację `prezentacja.pdf`.

- **`os`, `sys` oraz `subprocess`** (biblioteka standardowa języka Python):
  - `os.path.exists(path)`, `os.path.isdir(path)` – weryfikacja istnienia pliku obrazu lub katalogu na dysku przed próbą odczytu.
  - `os.listdir(path)`, `os.path.splitext(filename)` – listowanie zawartości katalogu z wykresami oraz rozdzielanie nazwy pliku i jego rozszerzenia.
  - `os.path.join(a, b)`, `os.path.abspath(path)` – konstruowanie ścieżek do plików w sposób niezależny od systemu operacyjnego.
  - `subprocess.run(...)` – uruchamianie procesu pomocniczego (interfejsu `Windows.Data.Pdf` w PowerShell lub `pdftoppm` w systemie Linux) w celu automatycznej konwersji wykresów z formatu `.pdf` do `.png`.
  - `sys.argv`, `sys.platform` – odczyt argumentów linii poleceń oraz identyfikacja systemu operacyjnego.
- **`matplotlib.pyplot` (`plt`)**:
  - `plt.figure(figsize=(16, 9), facecolor="white")` – utworzenie nowego slajdu o proporcjach panoramicznych 16:9.
  - `fig.add_axes([left, bottom, width, height])` – umieszczenie panelu rysowania w określonym obszarze slajdu (pasek nagłówka, stopka oraz siatka $2 \times 2$ wykresów).
  - `ax.text(...)` – nanoszenie sformatowanego tekstu na slajd (tytuły, opis metodologii, wnioski fizyczne).
  - `ax.imshow(img)` – wyświetlenie wczytanego obrazu PNG wewnątrz osi.
  - `ax.set_xticks([])`, `ax.set_yticks([])`, `ax.axis("off")` – ukrycie osi i podziałek pomocniczych na slajdach prezentacji.
  - `plt.close(fig)` – zamknięcie obiektu figury po zapisaniu slajdu i zwolnienie pamięci operacyjnej.
- **`matplotlib.backends.backend_pdf.PdfPages`**:
  - `PdfPages(out_pdf)` – menedżer kontekstu obsługujący zapis wielostronicowego dokumentu PDF.
  - `pdf.savefig(fig)` – dopisanie bieżącej figury `fig` jako kolejnej strony (slajdu) w pliku PDF.
- **`PIL.Image` oraz `PIL.ImageChops` (biblioteka Pillow)**:
  - `Image.open(img_path)` – odczyt pliku graficznego `.png` i przekazanie go do funkcji `ax.imshow(...)`.
  - `Image.new(...)`, `ImageChops.difference(im1, im2)`, `getbbox()`, `crop(...)`, `save(...)` – wyznaczanie obwiedni obszaru zadrukowanego oraz automatyczne przycinanie nadmiarowych białych marginesów wokół wykresu.
