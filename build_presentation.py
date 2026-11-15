import os
import sys
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PIL import Image, ImageChops


def trim_whitespace(png_path, pad=20):
    if not os.path.exists(png_path) or os.path.getsize(png_path) == 0:
        return

    with Image.open(png_path) as img:
        rgb = img.convert("RGB")
        bg = Image.new("RGB", rgb.size, (255, 255, 255))
        diff = ImageChops.difference(rgb, bg)
        bbox = diff.getbbox()
        if not bbox:
            return

        left = max(0, bbox[0] - pad)
        top = max(0, bbox[1] - pad)
        right = min(rgb.width, bbox[2] + pad)
        bottom = min(rgb.height, bbox[3] + pad)

        if left > 0 or top > 0 or right < rgb.width or bottom < rgb.height:
            cropped = rgb.crop((left, top, right, bottom))
        else:
            return

    cropped.save(png_path, "PNG")


def ensure_png_from_pdf(plots_dir):
    if not os.path.isdir(plots_dir):
        return

    pdf_files = [
        f for f in os.listdir(plots_dir)
        if f.lower().endswith(".pdf")
    ]
    missing_pairs = []
    all_png_paths = []

    for pdf_name in pdf_files:
        base_name = os.path.splitext(pdf_name)[0]
        pdf_path = os.path.abspath(os.path.join(plots_dir, pdf_name))
        png_path = os.path.abspath(os.path.join(plots_dir, base_name + ".png"))
        all_png_paths.append(png_path)

        if (
            not os.path.exists(png_path)
            or os.path.getsize(png_path) == 0
            or (os.path.getmtime(pdf_path) - os.path.getmtime(png_path)) > 5.0
        ):
            missing_pairs.append((pdf_path, png_path))

    if missing_pairs:
        converted = False
        try:
            import fitz
            for pdf_path, png_path in missing_pairs:
                doc = fitz.open(pdf_path)
                page = doc.load_page(0)
                pix = page.get_pixmap(dpi=200)
                pix.save(png_path)
                doc.close()
            converted = True
        except ImportError:
            pass

        if not converted:
            if sys.platform.startswith("win"):
                ps_script = (
                    "Add-Type -AssemblyName System.Runtime.WindowsRuntime; "
                    "$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() | "
                    "Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and "
                    "$_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]; "
                    "$asTaskAction = ([System.WindowsRuntimeSystemExtensions].GetMethods() | "
                    "Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and "
                    "$_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]; "
                    "Function Await($WinRtTask, $ResultType) { "
                    "$asTask = $asTaskGeneric.MakeGenericMethod($ResultType); "
                    "$netTask = $asTask.Invoke($null, @($WinRtTask)); "
                    "$netTask.Wait(-1) | Out-Null; "
                    "$netTask.Result }; "
                    "[Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime] | Out-Null; "
                    "[Windows.Data.Pdf.PdfPageRenderOptions, Windows.Data.Pdf, ContentType = WindowsRuntime] | Out-Null; "
                    "$files = Get-ChildItem -LiteralPath $env:PLOTS_DIR -Filter *.pdf; "
                    "foreach ($f in $files) { "
                    "$pngPath = [System.IO.Path]::ChangeExtension($f.FullName, '.png'); "
                    "$needConv = (-not (Test-Path -LiteralPath $pngPath)) -or "
                    "((Get-Item -LiteralPath $pngPath).Length -eq 0) -or "
                    "($f.LastWriteTimeUtc -ge (Get-Item -LiteralPath $pngPath).LastWriteTimeUtc); "
                    "if ($needConv) { "
                    "$inFs = [System.IO.File]::OpenRead($f.FullName); "
                    "$inRas = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($inFs); "
                    "$pdf = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromStreamAsync($inRas)) ([Windows.Data.Pdf.PdfDocument]); "
                    "$page = $pdf.GetPage(0); "
                    "$outFs = [System.IO.File]::Create($pngPath); "
                    "$outRas = [System.IO.WindowsRuntimeStreamExtensions]::AsRandomAccessStream($outFs); "
                    "$opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions; "
                    "$opts.DestinationWidth = [uint32]($page.Size.Width * 2.5); "
                    "$opts.DestinationHeight = [uint32]($page.Size.Height * 2.5); "
                    "$netAction = $asTaskAction.Invoke($null, @($page.RenderToStreamAsync($outRas, $opts))); "
                    "$netAction.Wait(-1) | Out-Null; "
                    "$outRas.Dispose(); $outFs.Dispose(); $page.Dispose(); $inRas.Dispose(); $inFs.Dispose() "
                    "} }"
                )
                env = os.environ.copy()
                env["PLOTS_DIR"] = os.path.abspath(plots_dir)
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    env=env,
                    check=False
                )
            else:
                for pdf_path, png_path in missing_pairs:
                    prefix = os.path.splitext(png_path)[0]
                    subprocess.run(
                        ["pdftoppm", "-png", "-cropbox", "-r", "200", "-singlefile", pdf_path, prefix],
                        check=False
                    )

    for png_path in all_png_paths:
        trim_whitespace(png_path, pad=20)


def add_header(fig, title, subtitle=""):
    ax_hdr = fig.add_axes([0.0, 0.88, 1.0, 0.12])
    ax_hdr.set_facecolor("#0033A0")
    ax_hdr.set_xticks([])
    ax_hdr.set_yticks([])
    for spine in ax_hdr.spines.values():
        spine.set_visible(False)

    ax_hdr.text(
        0.04, 0.58, title,
        color="white", fontsize=20, fontweight="bold", va="center", ha="left"
    )
    if subtitle:
        ax_hdr.text(
            0.04, 0.22, subtitle,
            color="#D0E0FF", fontsize=12, va="center", ha="left"
        )


def add_footer(fig, page_num, total_pages):
    ax_ftr = fig.add_axes([0.0, 0.0, 1.0, 0.04])
    ax_ftr.set_facecolor("#F4F6FA")
    ax_ftr.set_xticks([])
    ax_ftr.set_yticks([])
    for spine in ax_ftr.spines.values():
        spine.set_visible(False)

    ax_ftr.text(
        0.04, 0.5,
        "Symulacja i analiza rozkładów cząstek dla pp @ √s = 13.6 TeV (Pythia 8 + ROOT 6)",
        color="#444444", fontsize=10, va="center", ha="left"
    )
    ax_ftr.text(
        0.96, 0.5,
        f"Slajd {page_num} / {total_pages}",
        color="#444444", fontsize=10, fontweight="bold", va="center", ha="right"
    )


def draw_image_on_axes(ax, img_path, title=""):
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor("#CCCCCC")
        spine.set_linewidth(0.8)

    if os.path.exists(img_path):
        img = Image.open(img_path)
        ax.imshow(img)
        if title:
            ax.set_title(title, fontsize=11, fontweight="bold", pad=6, color="#1A1A1A")
    else:
        ax.text(
            0.5, 0.5, f"Brak pliku:\n{img_path}",
            ha="center", va="center", fontsize=11, color="red"
        )


def build_presentation(plots_dir="plots", out_pdf="prezentacja.pdf"):
    ensure_png_from_pdf(plots_dir)
    total_pages = 11

    with PdfPages(out_pdf) as pdf:
        fig = plt.figure(figsize=(16, 9), facecolor="white")
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_facecolor("#002266")
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.text(
            0.5, 0.64,
            "Symulacja i analiza rozkładów cząstek\ndla zderzeń pp @ √s = 13.6 TeV",
            color="white", fontsize=32, fontweight="bold", ha="center", va="center"
        )
        ax.text(
            0.5, 0.45,
            "Generator Pythia 8 (Minimum Bias / SoftQCD) + Analiza w C++17 / ROOT 6",
            color="#A8C8FF", fontsize=18, ha="center", va="center"
        )
        ax.text(
            0.5, 0.28,
            "Rozkłady krotności (N), pędu poprzecznego (pT), pseudorapidity (η) oraz kąta azymutalnego (φ)\n"
            "dla wszystkich cząstek naładowanych, pionów (π⁺, π⁻), kaonów (K⁺, K⁻) i protonów (p, p̄)",
            color="#E0ECFF", fontsize=13, ha="center", va="center"
        )
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(16, 9), facecolor="white")
        add_header(fig, "1. Metodologia i parametry symulacji", "Konfiguracja generatora Pythia 8 oraz programu analizującego C++/ROOT")
        add_footer(fig, 2, total_pages)

        ax = fig.add_axes([0.06, 0.08, 0.88, 0.76])
        ax.axis("off")

        methodology_text = (
            "• Generator zdarzeń (Pythia 8, generate_events.cc):\n"
            "   – Wiązki: zderzenia proton–proton (Beams:idA = 2212, Beams:idB = 2212)\n"
            "     przy energii w układzie środka masy √s = 13.6 TeV (Beams:eCM = 13600 GeV)\n"
            "   – Procesy fizyczne: Minimum Bias (SoftQCD:all = on), liczba wygenerowanych zdarzeń: N_events = 100 000\n"
            "   – Selekcja stanu końcowego: zapisywane są wyłącznie cząstki spełniające warunek p.isFinal() == true\n\n"
            "• Program analizujący (C++17 / ROOT 6, analyze_events.cc -> analysis.root):\n"
            "   – Badane kategorie cząstek:\n"
            "       * Wszystkie cząstki naładowane (All charged: ładunek ≠ 0 oraz status final)\n"
            "       * Piony: π⁺ (PDG = +211) oraz π⁻ (PDG = −211)\n"
            "       * Kaony: K⁺ (PDG = +321) oraz K⁻ (PDG = −321)\n"
            "       * Protony i antyprotony: p (PDG = +2212) oraz p̄ (PDG = −2212)\n\n"
            "• Zakresy i binowanie histogramów (TH1D):\n"
            "   – Krotność cząstek na zdarzenie (N): zakres 0 – 400 (400 binów)\n"
            "   – Pęd poprzeczny (pT): zakres 0 – 10 GeV (100 binów)\n"
            "   – Pseudorapidity (η): zakres −5 do 5 (100 binów)\n"
            "   – Kąt azymutalny (φ): zakres 0 – π rad (64 biny)"
        )
        ax.text(0.0, 0.95, methodology_text, fontsize=14, va="top", ha="left", linespacing=1.55, color="#1A1A1A")
        pdf.savefig(fig)
        plt.close(fig)

        fig = plt.figure(figsize=(16, 9), facecolor="white")
        add_header(fig, "2. Porównanie zbiorcze rozkładów (wszystkie kategorie)", "Zestawienie N, pT, η oraz φ na wspólnych układach współrzędnych")
        add_footer(fig, 3, total_pages)

        summary_files = [
            ("summary_hN.png", "Krotność cząstek N"),
            ("summary_hPt.png", "Pęd poprzeczny pT [GeV]"),
            ("summary_hEta.png", "Pseudorapidity η"),
            ("summary_hPhi.png", "Kąt azymutalny φ [rad]"),
        ]
        positions_2x2 = [
            [0.05, 0.47, 0.43, 0.38],
            [0.52, 0.47, 0.43, 0.38],
            [0.05, 0.06, 0.43, 0.38],
            [0.52, 0.06, 0.43, 0.38],
        ]
        for (fname, title), pos in zip(summary_files, positions_2x2):
            ax = fig.add_axes(pos)
            draw_image_on_axes(ax, os.path.join(plots_dir, fname), title)

        pdf.savefig(fig)
        plt.close(fig)

        species_slides = [
            ("ch",   "Wszystkie cząstki naładowane (All charged)", "Łączna liczba zliczeń: 7 219 842 (średnia krotność Mean N = 71.89)"),
            ("pip",  "Piony dodatnie (π⁺, PDG = +211)",            "Liczba zliczeń: 2 989 654 (średnia krotność Mean N = 29.90, Mean pT = 0.48 GeV)"),
            ("pim",  "Piony ujemne (π⁻, PDG = −211)",              "Liczba zliczeń: 2 938 243 (średnia krotność Mean N = 29.38, Mean pT = 0.48 GeV)"),
            ("Kp",   "Kaony dodatnie (K⁺, PDG = +321)",            "Liczba zliczeń: 330 755 (średnia krotność Mean N = 3.31, Mean pT = 0.68 GeV)"),
            ("Km",   "Kaony ujemne (K⁻, PDG = −321)",              "Liczba zliczeń: 321 998 (średnia krotność Mean N = 3.22, Mean pT = 0.67 GeV)"),
            ("p",    "Protony (p, PDG = +2212)",                   "Liczba zliczeń: 342 684 (średnia krotność Mean N = 3.43, Mean pT = 0.62 GeV)"),
            ("pbar", "Antyprotony (p̄, PDG = −2212)",               "Liczba zliczeń: 202 834 (średnia krotność Mean N = 2.03, Mean pT = 0.77 GeV)"),
        ]

        for idx, (suffix, sp_title, sp_sub) in enumerate(species_slides, start=4):
            fig = plt.figure(figsize=(16, 9), facecolor="white")
            add_header(fig, f"{idx - 1}. Rozkłady indywidualne: {sp_title}", sp_sub)
            add_footer(fig, idx, total_pages)

            indiv_files = [
                (f"hN_{suffix}.png",   f"Krotność N ({suffix})"),
                (f"hPt_{suffix}.png",  f"Pęd poprzeczny pT ({suffix})"),
                (f"hEta_{suffix}.png", f"Pseudorapidity η ({suffix})"),
                (f"hPhi_{suffix}.png", f"Kąt azymutalny φ ({suffix})"),
            ]
            for (fname, title), pos in zip(indiv_files, positions_2x2):
                ax = fig.add_axes(pos)
                draw_image_on_axes(ax, os.path.join(plots_dir, fname), title)

            pdf.savefig(fig)
            plt.close(fig)

        fig = plt.figure(figsize=(16, 9), facecolor="white")
        add_header(fig, "10. Podsumowanie i wnioski z analizy danych", "Zestawienie statystyk i obserwacji na podstawie uzyskanych rozkładów")
        add_footer(fig, 11, total_pages)

        ax = fig.add_axes([0.06, 0.08, 0.88, 0.76])
        ax.axis("off")

        conclusions_text = (
            "1. Liczebność grup i krotność cząstek na zdarzenie (N):\n"
            "   • W 100 000 przeanalizowanych zdarzeń zarejestrowano łącznie 7 219 842 cząstki naładowane\n"
            "     (średnio Mean = 71.89 cząstki na zdarzenie przy odchyleniu standardowym Std Dev = 76.20).\n"
            "   • Zdecydowaną większość (ponad 82% wszystkich cząstek naładowanych) stanowią piony: π⁺ (2 989 654 zliczeń,\n"
            "     Mean N = 29.90) oraz π⁻ (2 938 243 zliczeń, Mean N = 29.38). Kaony stanowią ok. 9% próbki (K⁺: 330 755, K⁻: 321 998).\n"
            "   • Największą różnicę liczebności między cząstką a antycząstką widać dla protonów (342 684, Mean N = 3.43)\n"
            "     względem antyprotonów (202 834, Mean N = 2.03). Wszystkie rozkłady N są silnie prawostronnie skośne.\n\n"
            "2. Rozkład pędu poprzecznego (pT):\n"
            "   • Rozkłady pT opadają wykładniczo wraz ze wzrostem wartości na osi X – przeważająca większość zliczeń\n"
            "     koncentruje się w przedziale 0 – 2 GeV.\n"
            "   • Piony charakteryzują się najniższym średnim pędem poprzecznym (Mean ≈ 0.48 GeV, Std Dev ≈ 0.45 GeV),\n"
            "     natomiast wyższe średnie wartości osiągają kaony (Mean ≈ 0.67–0.68 GeV) oraz protony i antyprotony (Mean = 0.62 GeV i 0.77 GeV).\n\n"
            "3. Rozkłady geometryczne – pseudorapidity (η) oraz kąt azymutalny (φ):\n"
            "   • Rozkłady η dla każdej kategorii są symetryczne względem zera (średnia we wszystkich grupach wynosi Mean ≈ 0,\n"
            "     a odchylenie standardowe Std Dev zawiera się w przedziale 2.79 – 2.97), z dwoma symetrycznymi maksimami wokół |η| ≈ 2.\n"
            "   • Rozkłady kąta φ w przedziale [0, π] są idealnie równomierne (płaskie): dla każdej kategorii średnia wynosi\n"
            "     dokładnie Mean = 1.57 rad (π/2), a odchylenie standardowe Std Dev ≈ 0.907 rad."
        )
        ax.text(0.0, 0.95, conclusions_text, fontsize=13.5, va="top", ha="left", linespacing=1.48, color="#1A1A1A")
        pdf.savefig(fig)
        plt.close(fig)

    print(f"Pomyslnie wygenerowano prezentacje PDF: {out_pdf}")


if __name__ == "__main__":
    plots_directory = sys.argv[1] if len(sys.argv) > 1 else "plots"
    output_pdf = sys.argv[2] if len(sys.argv) > 2 else "prezentacja.pdf"
    build_presentation(plots_directory, output_pdf)
