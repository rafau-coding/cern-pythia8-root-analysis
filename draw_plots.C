#include "TFile.h"
#include "TH1D.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TStyle.h"
#include "TSystem.h"
#include "TMath.h"

#include <iostream>
#include <vector>
#include <string>

struct SpeciesInfo {
    std::string suffix;
    std::string label;
    int color;
    int lineStyle;
};

struct ObservableInfo {
    std::string prefix;
    std::string title;
    std::string xTitle;
    std::string yTitle;
    bool logY;
};

void draw_plots(const char* inFileName = "analysis.root", const char* outDir = "plots") {
    gStyle->SetOptStat(1110);
    gStyle->SetStatX(0.94);
    gStyle->SetStatY(0.90);
    gStyle->SetStatW(0.20);
    gStyle->SetStatH(0.14);
    gStyle->SetPadTickX(1);
    gStyle->SetPadTickY(1);
    gStyle->SetTitleFontSize(0.045);

    gSystem->mkdir(outDir, kTRUE);

    TFile* file = TFile::Open(inFileName, "READ");
    if (!file || file->IsZombie()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku " << inFileName << std::endl;
        return;
    }

    std::vector<SpeciesInfo> species = {
        {"ch",   "All charged", kBlack,   1},
        {"pip",  "#pi^{+}",     kRed+1,   1},
        {"pim",  "#pi^{-}",     kRed-7,   2},
        {"Kp",   "K^{+}",       kBlue+1,  1},
        {"Km",   "K^{-}",       kBlue-7,  2},
        {"p",    "p",           kGreen+2, 1},
        {"pbar", "#bar{p}",     kGreen-6, 2}
    };

    std::vector<ObservableInfo> observables = {
        {"hN",   "Particle Multiplicity per Event (pp @ #sqrt{s} = 13.6 TeV)", "Multiplicity N", "Events",    true},
        {"hPt",  "Transverse Momentum Distribution (pp @ #sqrt{s} = 13.6 TeV)", "p_{T} [GeV]",   "Particles", true},
        {"hEta", "Pseudorapidity Distribution (pp @ #sqrt{s} = 13.6 TeV)",      "#eta",          "Particles", false},
        {"hPhi", "Azimuthal Angle Distribution (pp @ #sqrt{s} = 13.6 TeV)",     "#phi [rad]",    "Particles", false}
    };

    for (const auto& obs : observables) {
        for (const auto& sp : species) {
            std::string histName = obs.prefix + "_" + sp.suffix;
            TH1D* h = dynamic_cast<TH1D*>(file->Get(histName.c_str()));
            if (!h) {
                std::cerr << "Ostrzezenie: Brak histogramu " << histName << std::endl;
                continue;
            }

            std::string canvName = "c_" + histName;
            TCanvas* c = new TCanvas(canvName.c_str(), canvName.c_str(), 900, 650);
            c->SetLeftMargin(0.13);
            c->SetRightMargin(0.06);
            c->SetBottomMargin(0.12);
            c->SetTopMargin(0.10);
            c->SetGrid();
            if (obs.logY) {
                c->SetLogy();
            }

            h->SetLineColor(sp.color);
            h->SetLineWidth(2);
            h->SetTitle((obs.title + " - " + sp.label).c_str());
            h->GetXaxis()->SetTitle(obs.xTitle.c_str());
            h->GetYaxis()->SetTitle(obs.yTitle.c_str());
            h->GetXaxis()->SetTitleSize(0.045);
            h->GetYaxis()->SetTitleSize(0.045);
            h->GetXaxis()->SetTitleOffset(1.1);
            h->GetYaxis()->SetTitleOffset(1.3);

            if (obs.logY) {
                h->SetMaximum(h->GetMaximum() * 5.0);
            } else {
                h->SetMinimum(0.0);
                h->SetMaximum(h->GetMaximum() * 1.35);
            }

            h->Draw("HIST");

            TLegend* leg = new TLegend(0.55, 0.80, 0.71, 0.88);
            leg->SetBorderSize(1);
            leg->SetFillColor(0);
            leg->SetTextSize(0.035);
            leg->AddEntry(h, sp.label.c_str(), "l");
            leg->Draw();

            std::string outPathBase = std::string(outDir) + "/" + histName;
            c->SaveAs((outPathBase + ".png").c_str());
            c->SaveAs((outPathBase + ".pdf").c_str());

            delete leg;
            delete c;
        }
    }

    gStyle->SetOptStat(0);
    for (const auto& obs : observables) {
        std::string canvName = "c_summary_" + obs.prefix;
        TCanvas* c = new TCanvas(canvName.c_str(), canvName.c_str(), 950, 680);
        c->SetLeftMargin(0.13);
        c->SetRightMargin(0.05);
        c->SetBottomMargin(0.12);
        c->SetTopMargin(0.10);
        c->SetGrid();
        if (obs.logY) {
            c->SetLogy();
        }

        TLegend* leg = new TLegend(0.72, 0.58, 0.93, 0.88);
        leg->SetBorderSize(1);
        leg->SetFillColor(0);
        leg->SetTextSize(0.032);
        leg->SetHeader("Particle species", "C");

        double maxVal = 0.0;
        std::vector<TH1D*> drawnHists;

        for (const auto& sp : species) {
            std::string histName = obs.prefix + "_" + sp.suffix;
            TH1D* hOrig = dynamic_cast<TH1D*>(file->Get(histName.c_str()));
            if (!hOrig) continue;

            TH1D* h = dynamic_cast<TH1D*>(hOrig->Clone((histName + "_clone").c_str()));
            if (h->GetMaximum() > maxVal) maxVal = h->GetMaximum();
            drawnHists.push_back(h);

            h->SetLineColor(sp.color);
            h->SetLineStyle(sp.lineStyle);
            h->SetLineWidth(2);
            h->SetTitle(obs.title.c_str());
            h->GetXaxis()->SetTitle(obs.xTitle.c_str());
            h->GetYaxis()->SetTitle(obs.yTitle.c_str());
            h->GetXaxis()->SetTitleSize(0.045);
            h->GetYaxis()->SetTitleSize(0.045);
            h->GetXaxis()->SetTitleOffset(1.1);
            h->GetYaxis()->SetTitleOffset(1.3);

            leg->AddEntry(h, sp.label.c_str(), "l");
        }

        for (size_t i = 0; i < drawnHists.size(); ++i) {
            if (i == 0) {
                if (obs.logY) {
                    drawnHists[i]->SetMinimum(0.5);
                    drawnHists[i]->SetMaximum(maxVal * 5.0);
                } else {
                    drawnHists[i]->SetMinimum(0.0);
                    drawnHists[i]->SetMaximum(maxVal * 1.35);
                }
                drawnHists[i]->Draw("HIST");
            } else {
                drawnHists[i]->Draw("HIST SAME");
            }
        }

        leg->Draw();

        std::string outPathBase = std::string(outDir) + "/summary_" + obs.prefix;
        c->SaveAs((outPathBase + ".png").c_str());
        c->SaveAs((outPathBase + ".pdf").c_str());

        for (auto* h : drawnHists) delete h;
        delete leg;
        delete c;
    }

    file->Close();
    delete file;
    std::cout << "Wyeksportowano wszystkie wykresy PNG oraz PDF do katalogu: " << outDir << std::endl;
}
