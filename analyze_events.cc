#include <iostream>
#include <vector>
#include <string>
#include <map>

#include "TFile.h"
#include "TTree.h"
#include "TH1D.h"
#include "TMath.h"

struct CategoryHists {
    TH1D* hN = nullptr;
    TH1D* hPt = nullptr;
    TH1D* hEta = nullptr;
    TH1D* hPhi = nullptr;
    int countInEvent = 0;

    void init(const std::string& suffix, const std::string& label) {
        hN = new TH1D(("hN_" + suffix).c_str(),
                      ("Multiplicity (" + label + ");Multiplicity N;Events").c_str(),
                      400, 0.0, 400.0);
        hPt = new TH1D(("hPt_" + suffix).c_str(),
                       ("Transverse Momentum (" + label + ");p_{T} [GeV];Particles").c_str(),
                       100, 0.0, 10.0);
        hEta = new TH1D(("hEta_" + suffix).c_str(),
                        ("Pseudorapidity (" + label + ");#eta;Particles").c_str(),
                        100, -5.0, 5.0);
        hPhi = new TH1D(("hPhi_" + suffix).c_str(),
                        ("Azimuthal Angle (" + label + ");#phi [rad];Particles").c_str(),
                        64, 0.0, TMath::Pi());

        hN->Sumw2();
        hPt->Sumw2();
        hEta->Sumw2();
        hPhi->Sumw2();
    }

    void resetEventCounter() {
        countInEvent = 0;
    }

    void fillParticle(double pt, double eta, double phi) {
        ++countInEvent;
        hPt->Fill(pt);
        hEta->Fill(eta);
        hPhi->Fill(std::abs(phi));
    }

    void fillEventMultiplicity() {
        hN->Fill(countInEvent);
    }

    void write() {
        hN->Write();
        hPt->Write();
        hEta->Write();
        hPhi->Write();
    }
};

int main(int argc, char* argv[]) {
    std::string inFileName = "events.root";
    std::string outFileName = "analysis.root";

    if (argc > 1) {
        inFileName = argv[1];
    }
    if (argc > 2) {
        outFileName = argv[2];
    }

    TFile* inFile = TFile::Open(inFileName.c_str(), "READ");
    if (!inFile || inFile->IsZombie()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku wejsciowego: " << inFileName << std::endl;
        return 1;
    }

    TTree* tree = dynamic_cast<TTree*>(inFile->Get("Events"));
    if (!tree) {
        std::cerr << "Blad: Nie znaleziono drzewa 'Events' w pliku " << inFileName << std::endl;
        inFile->Close();
        return 1;
    }

    std::vector<int>* pdgId = nullptr;
    std::vector<int>* isCharged = nullptr;
    std::vector<double>* pt = nullptr;
    std::vector<double>* eta = nullptr;
    std::vector<double>* phi = nullptr;

    tree->SetBranchAddress("pdgId", &pdgId);
    tree->SetBranchAddress("isCharged", &isCharged);
    tree->SetBranchAddress("pt", &pt);
    tree->SetBranchAddress("eta", &eta);
    tree->SetBranchAddress("phi", &phi);

    TFile* outFile = TFile::Open(outFileName.c_str(), "RECREATE");
    if (!outFile || outFile->IsZombie()) {
        std::cerr << "Blad: Nie mozna utworzyc pliku wyjsciowego: " << outFileName << std::endl;
        inFile->Close();
        return 1;
    }

    CategoryHists cat_ch, cat_all, cat_pip, cat_pim, cat_Kp, cat_Km, cat_p, cat_pbar;

    cat_ch.init("ch", "All charged");
    cat_all.init("all", "All charged");
    cat_pip.init("pip", "#pi^{+}");
    cat_pim.init("pim", "#pi^{-}");
    cat_Kp.init("Kp", "K^{+}");
    cat_Km.init("Km", "K^{-}");
    cat_p.init("p", "p");
    cat_pbar.init("pbar", "#bar{p}");

    Long64_t nEntries = tree->GetEntries();
    std::cout << "Analiza " << nEntries << " zdarzen z pliku " << inFileName << "..." << std::endl;

    for (Long64_t iEntry = 0; iEntry < nEntries; ++iEntry) {
        tree->GetEntry(iEntry);

        cat_ch.resetEventCounter();
        cat_all.resetEventCounter();
        cat_pip.resetEventCounter();
        cat_pim.resetEventCounter();
        cat_Kp.resetEventCounter();
        cat_Km.resetEventCounter();
        cat_p.resetEventCounter();
        cat_pbar.resetEventCounter();

        size_t nParticles = pdgId->size();
        for (size_t i = 0; i < nParticles; ++i) {
            int id = (*pdgId)[i];
            int chg = (*isCharged)[i];
            double p_pt = (*pt)[i];
            double p_eta = (*eta)[i];
            double p_phi = (*phi)[i];

            if (chg != 0) {
                cat_ch.fillParticle(p_pt, p_eta, p_phi);
                cat_all.fillParticle(p_pt, p_eta, p_phi);
            }

            switch (id) {
                case 211:
                    cat_pip.fillParticle(p_pt, p_eta, p_phi);
                    break;
                case -211:
                    cat_pim.fillParticle(p_pt, p_eta, p_phi);
                    break;
                case 321:
                    cat_Kp.fillParticle(p_pt, p_eta, p_phi);
                    break;
                case -321:
                    cat_Km.fillParticle(p_pt, p_eta, p_phi);
                    break;
                case 2212:
                    cat_p.fillParticle(p_pt, p_eta, p_phi);
                    break;
                case -2212:
                    cat_pbar.fillParticle(p_pt, p_eta, p_phi);
                    break;
                default:
                    break;
            }
        }

        cat_ch.fillEventMultiplicity();
        cat_all.fillEventMultiplicity();
        cat_pip.fillEventMultiplicity();
        cat_pim.fillEventMultiplicity();
        cat_Kp.fillEventMultiplicity();
        cat_Km.fillEventMultiplicity();
        cat_p.fillEventMultiplicity();
        cat_pbar.fillEventMultiplicity();
    }

    outFile->cd();
    cat_ch.write();
    cat_all.write();
    cat_pip.write();
    cat_pim.write();
    cat_Kp.write();
    cat_Km.write();
    cat_p.write();
    cat_pbar.write();

    outFile->Close();
    inFile->Close();

    delete outFile;
    delete inFile;

    std::cout << "Zapisano wszystkie histogramy do pliku: " << outFileName << std::endl;
    return 0;
}
