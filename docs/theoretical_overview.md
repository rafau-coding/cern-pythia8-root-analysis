# Wprowadzenie teoretyczne i przewodnik po zmiennych (`theoretical_overview.md`)

Niniejszy dokument wyjaśnia w przystępny sposób podstawy fizyczne realizowanego zadania, przebieg symulowanych zjawisk, strukturę danych generowanych przez program **Pythia 8** oraz interpretację fizyczną każdej analizowanej zmiennej i wykresu.

---

## 1. Cel i istota zadania (obraz ogólny)

W Wielkim Zderzaczu Hadronów (**LHC** w ośrodku CERN pod Genewą) dwie wiązki **protonów ($p$)** poruszają się w przeciwnych kierunkach wewnątrz rury próżniowej z prędkością bliską prędkości światła i ulegają zderzeniom w punktach detekcji.

W ramach zadania przeprowadzana jest **symulacja komputerowa (Monte Carlo)** odpowiadająca warunkom panującym w akceleratorze LHC (podczas okresu zbierania danych *Run 3*):
1. **Generator Pythia 8** pełni rolę „wirtualnego akceleratora”: symuluje $100\,000$ zderzeń dwóch protonów przy energii $\sqrt{s} = 13.6\text{ TeV}$ i wyznacza listę wyprodukowanych cząstek wraz z ich pędami oraz kierunkami lotu.
2. **Program w C++ / ROOT** realizuje etap analizy fizycznej: wczytuje listę cząstek wyprodukowanych w każdym zderzeniu, klasyfikuje je według gatunków (piony, kaony, protony) i agreguje ich właściwości w postaci **histogramów** (rozkładów statystycznych).
3. **Makro rysujące ROOT** przekształca zgromadzone histogramy w gotowe wykresy naukowe.

---

## 2. Podstawowe pojęcia fizyczne ze specyfikacji zadania

### Znaczenie zapisu `$pp \text{ @ } \sqrt{s} = 13.6\text{ TeV}$`
- **$pp$**: zderzenie **proton–proton** (w konfiguracji generatora Pythia 8 definiowane są dwie wiązki protonowe: `Beams:idA = 2212` oraz `Beams:idB = 2212`, gdzie `2212` stanowi identyfikator PDG protonu).
- **$\sqrt{s}$ (`Beams:eCM`)**: całkowita energia zderzenia w układzie środka masy (*Center-of-Mass Energy*). Każdy z dwóch zderzających się protonów posiada energię $6.8\text{ TeV}$ ($6800\text{ GeV}$), co daje łączną energię zderzenia:
  $$\sqrt{s} = 6.8\text{ TeV} + 6.8\text{ TeV} = 13.6\text{ TeV} = 13\,600\text{ GeV}$$
- **$\text{GeV}$ (gigaelektronowolt)**: podstawowa jednostka energii, pędu oraz masy w fizyce wysokich energii. Masa spoczynkowa pojedynczego protonu wynosi około $0.938\text{ GeV}$. Energia $13\,600\text{ GeV}$ przewyższa zatem masę spoczynkową zderzających się protonów ponad $14\,000$ razy. Zgodnie z relacją równoważności masy i energii $E = mc^2$, energia kinetyczna zderzenia ulega konwersji w dziesiątki lub setki nowych cząstek.

### Znaczenie trybu `Minimum Bias (SoftQCD)`
Zdecydowana większość zderzeń protonów w akceleratorze LHC nie polega na rzadkich, centralnych zderzeniach pojedynczych kwarków o ogromnym przekazie pędu, lecz obejmuje tzw. **oddziaływania miękkie** (*Soft Quantum Chromodynamics* – `SoftQCD`), zachodzące przy relatywnie niewielkich przekazach pędu.
- Określenie **Minimum Bias** („minimalne obciążenie selekcją”) wywodzi się z techniki eksperymentalnej: oznacza rejestrację **wszystkich typowych zderzeń nieelastycznych**, bez narzucania restrykcyjnych progów wyzwalania (triggerów) wybierających wyłącznie rzadkie procesy twarde. Pozwala to na zbadanie reprezentatywnego obrazu typowego zderzenia proton–proton.

---

## 3. Struktura danych generowanych przez pakiet Pythia 8

Wywołanie metody `pythia.next()` powoduje wygenerowanie jednego zderzenia (jednego **zdarzenia**, ang. *event*). Wynik zapisywany jest w strukturze `pythia.event`, stanowiącej **kompletną listę (historię genealogiczną) wszystkich cząstek** biorących udział w zderzeniu – od nadlatujących wiązek aż po stabilne produkty końcowe.

### Cząstki pośrednie a cząstki stanu końcowego (`isFinal()`)
Ewolucja pojedynczego zderzenia w generatorze Pythia 8 obejmuje cztery główne etapy:
1. **Wiązki początkowe**: dwa nadlatujące protony.
2. **Rozpraszanie partonowe (kwarki i gluony)**: oddziaływanie elementarnych składników protonów (partonów) oraz emisja promieniowania gluonowego.
3. **Hadronizacja i rezonanse (cząstki pośrednie)**: wiązanie kwarków i gluonów w bezbarwne hadrony; na tym etapie powstają liczne cząstki niestabilne (np. mezony $\rho$, $\omega$, bariony $\Delta$, neutralne piony $\pi^0$), które ulegają natychmiastowemu rozpadowi (w czasie rzędu $10^{-23} - 10^{-16}\text{ s}$) na lżejsze cząstki.
4. **Cząstki stanu końcowego (*final state particles*)**: cząstki stabilne lub długożyjące, które nie ulegają dalszym rozpadom w obrębie punktu zderzenia i docierają bezpośrednio do warstw detektora.

> **Znaczenie flagi `p.isFinal()`:**
> Pominięcie warunku filtrującego `if (!p.isFinal()) continue;` prowadziłoby do wielokrotnego zliczania tej samej materii – raz jako niestabilnej cząstki macierzystej (pośredniej) i ponownie jako cząstek potomnych powstałych z jej rozpadu. Rzeczywisty detektor rejestruje wyłącznie cząstki docierające do jego objętości czynnej, co odpowiada cząstkom posiadającym status `isFinal() == true`.

### Struktura danych w pliku `events.root` (`TTree "Events"`)
Program `generate_events` wybiera z kontenera `pythia.event` wyłącznie cząstki w stanie końcowym i zapisuje je do drzewa `TTree` w pliku `events.root`.
- **Każdy wiersz drzewa `Events` reprezentuje jedno kompletne zderzenie ($1\text{ z }100\,000$)**.
- Ze względu na zmienną liczbę cząstek produkowanych w poszczególnych zderzeniach, każda kolumna (gałąź `Branch`) w danym wierszu jest **wektorem (`std::vector`)** o długości równej liczbie cząstek końcowych w tym zdarzeniu:
  - `pdgId[i]` – kod identyfikacyjny PDG $i$-tej cząstki,
  - `isCharged[i]` – informacja o ładunku elektrycznym $i$-tej cząstki (`1` – cząstka naładowana, `0` – cząstka obojętna),
  - `pt[i]` – pęd poprzeczny $i$-tej cząstki,
  - `eta[i]` – pseudopospieszność (*pseudorapidity*) $i$-tej cząstki,
  - `phi[i]` – kąt azymutalny $i$-tej cząstki.

---

## 4. Charakterystyka badanych cząstek i kody PDG

Zgodnie ze standardem **PDG** (*Particle Data Group*) każdemu typowi cząstki przypisany jest unikalny identyfikator liczbowy. Liczba dodatnia oznacza cząstkę, natomiast liczba przeciwna (ujemna) oznacza odpowiadającą jej **antycząstkę** (posiadającą identyczną masę spoczynkową, lecz przeciwny ładunek elektryczny i liczby kwantowe).

| Oznaczenie w kodzie | Symbol fizyczny | Kod PDG | Charakterystyka fizyczna |
| :--- | :---: | :---: | :--- |
| **`ch` / `all`** | $h^\pm, e^\pm, \mu^\pm$ | dowolny z $Q \neq 0$ | **Wszystkie cząstki naładowane**: w detektorach śladowych umieszczonych w polu magnetycznym tory lotu wyznaczane są wyłącznie dla cząstek obdarzonych niezerowym ładunkiem elektrycznym. |
| **`pip`** | $\pi^+$ | `+211` | **Pion dodatni** (zbudowany z kwarku górnego i antykwarku dolnego: $u\bar{d}$). Piony są **najlżejszymi mezonami** (masa ok. $0.140\text{ GeV}$), wskutek czego stanowią dominującą frakcję (ok. 70–80%) wszystkich cząstek naładowanych produkowanych w zderzeniach $pp$. |
| **`pim`** | $\pi^-$ | `-211` | **Pion ujemny** ($\bar{u}d$) – antycząstka pionu dodatniego, produkowana w niemal identycznej liczbie co $\pi^+$. |
| **`Kp`** | $K^+$ | `+321` | **Kaon dodatni** ($u\bar{s}$). Zawiera cięższy **kwark dziwny ($s$)** i posiada masę ok. $0.494\text{ GeV}$ (ok. $3.5$-krotnie większą od masy pionu). Ze względu na wyższy próg energetyczny produkcji kwarków dziwnych, krotność kaonów jest wyraźnie niższa niż pionów. |
| **`Km`** | $K^-$ | `-321` | **Kaon ujemny** ($\bar{u}s$) – antycząstka kaonu dodatniego. |
| **`p`** | $p$ | `+2212` | **Proton** ($uud$, masa ok. $0.938\text{ GeV}$). Najlżejszy barion (układ trójkwarkowy). W stanie końcowym występują zarówno protony wyprodukowane w obszarze centralnym, jak i protony pochodzące z fragmentacji zderzających się wiązek. |
| **`pbar`** | $\bar{p}$ | `-2212` | **Antyproton** ($\bar{u}\bar{u}\bar{d}$) – antycząstka protonu, powstająca w procesach kreacji par barion–antybarion. |

---

## 5. Interpretacja zmiennych kinematycznych i histogramów

W fizyce akceleratorowej stosowany jest kartezjańsko-cylindryczny układ współrzędnych związany z geometrią detektora:
- **Oś $Z$** pokrywa się z osią wiązki (kierunkiem ruchu protonów przed zderzeniem).
- **Płaszczyzna $XY$** (płaszczyzna poprzeczna) jest prostopadła do osi wiązki.

W projekcie wyznaczane są **cztery rozkłady jednowymiarowe**:

---

### 5.1. Krotność cząstek na zdarzenie – `N` (histogramy `hN_*`)
- **Definicja:**
  Liczba cząstek danej kategorii wyprodukowanych w **pojedynczym zderzeniu**. Przykładowo, jeśli w danym zdarzeniu zarejestrowano $45$ cząstek naładowanych, w tym $18$ pionów $\pi^+$, histogram `hN_ch` jest inkrementowany w binie odpowiadającym wartości $N = 45$, natomiast histogram `hN_pip` – w binie $N = 18$.
- **Sposób wypełniania:**
  Histogram `hN_*` wypełniany jest **jednokrotnie na każde zdarzenie** (całkowita liczba zliczeń *Entries* w histogramie `hN_*` wynosi dokładnie $100\,000$). Pozostałe histogramy (`hPt`, `hEta`, `hPhi`) wypełniane są **dla każdej pojedynczej cząstki**.
- **Kształt rozkładu:**
  Rozkład krotności w zdarzeniach *Minimum Bias* charakteryzuje się maksimum dla niskich krotności (odpowiadających zderzeniom peryferyjnym) oraz długim, asymetrycznym ogonem sięgającym wysokich wartości $N$, będącym efektem wielokrotnych oddziaływań partonowych (*Multiparton Interactions – MPI*).

---

### 5.2. Pęd poprzeczny – `pT` (histogramy `hPt_*`, oś `p_{T} [GeV]`)
- **Definicja:**
  Składowa wektora pędu cząstki rzutowana na płaszczyznę $XY$ **prostopadłą do osi wiązki ($Z$)**:
  $$p_T = \sqrt{p_x^2 + p_y^2}$$
- **Znaczenie fizyczne:**
  Przed zderzeniem protony wiązki poruszają się wyłącznie wzdłuż osi $Z$, w związku z czym ich początkowy pęd poprzeczny wynosi zero ($p_T = 0$). Niezerowy pęd poprzeczny cząstek stanu końcowego jest bezpośrednim rezultatem przekazu pędu w procesie rozpraszania partonowego.
- **Kształt rozkładu:**
  Widmo $p_T$ osiąga maksimum w obszarze niskich pędów ($p_T < 1\text{ GeV}$), a następnie zanika o kilka rzędów wielkości wraz ze wzrostem $p_T$. Z tego względu rozkłady $p_T$ prezentowane są w skali logarytmicznej na osi pionowej.

---

### 5.3. Pseudopospieszność (*pseudorapidity*) – `η` (histogramy `hEta_*`, oś `\eta`)
- **Definicja:**
  Zmienna bezwymiarowa będąca logarytmiczną miarą **kąta polarnego $\theta$** (kąta pomiędzy wektorem pędu cząstki a osią wiązki $Z$):
  $$\eta = -\ln\left(\tan\frac{\theta}{2}\right)$$
- **Interpretacja geometryczna:**
  - **$\eta = 0$** odpowiada kątowi $\theta = 90^\circ$ – cząstka porusza się **prostopadle** do osi wiązki.
  - **$\eta \approx \pm 2$** – cząstka porusza się pod niewielkim kątem względem rury akceleratora (odpowiednio w kierunku dodatnim lub ujemnym osi $Z$).
  - **$\eta \to \pm\infty$** ($\theta \to 0^\circ$ lub $180^\circ$) – cząstka porusza się niemal równolegle do osi wiązki.
- **Uzasadnienie stosowania zmiennej $\eta$:**
  Dla cząstek o energiach znacznie przewyższających ich masę spoczynkową ($E \gg m$) pseudopospieszność $\eta$ stanowi dobre przybliżenie pospieszności (*rapidity* $y$), w funkcji której gęstość produkowanych cząstek $dN/d\eta$ jest w przybliżeniu niezmiennicza względem pchnięć Lorentza wzdłuż osi $Z$.
- **Cechy charakterystyczne rozkładu:**
  - Dla pionów i kaonów rozkład $\eta$ tworzy szerokie *plateau* w obszarze centralnym ($|\eta| < 2.5$) z niewielkim lokalnym minimum wokół $\eta = 0$ (wynikającym z jakobianu transformacji pomiędzy zmiennymi $y$ oraz $\eta$).
  - W rozkładzie **protonów (`hEta_p`)**, oprócz składowej centralnej, przy dużych wartościach $|\eta| > 3.5$ widoczne są dwa symetryczne maksima pochodzące od protonów z fragmentacji wiązek oraz procesów dyfrakcyjnych. Zjawisko to nie występuje w rozkładzie antyprotonów (`hEta_pbar`), ponieważ wiązki początkowe składają się wyłącznie z protonów.

---

### 5.4. Kąt azymutalny – `φ` (histogramy `hPhi_*`, oś `\phi [rad]`)
- **Definicja:**
  Kąt w płaszczyźnie poprzecznej $XY$ wyznaczany wokół osi wiązki $Z$, wyrażony w radianach:
  $$\phi = \text{atan2}(p_y, p_x)$$
  W analizie histogramowany jest w przedziale $[0, \pi]\text{ rad}$ z podziałem na $64$ biny.
- **Kształt rozkładu:**
  Rozkład kąta azymutalnego $\phi$ po uśrednieniu po wielu zdarzeniach jest **jednorodny (płaski)**. Wynika to z symetrii osiowej (obrotowej) zderzeń niespolaryzowanych wiązek protonowych wokół osi $Z$ – żaden kierunek azymutalny w płaszczyźnie poprzecznej nie jest uprzywilejowany.
