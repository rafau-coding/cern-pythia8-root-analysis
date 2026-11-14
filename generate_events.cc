#include <iostream>
#include <vector>
#include <string>

#include "Pythia8/Pythia.h"
#include "TFile.h"
#include "TTree.h"

int main(int argc, char* argv[]) {
    int nEvents = 100000;
    std::string outFileName = "events.root";

    if (argc > 1) {
        nEvents = std::stoi(argv[1]);
    }
    if (argc > 2) {
        outFileName = argv[2];
    }

    Pythia8::Pythia pythia;

    pythia.readString("Beams:idA = 2212");
    pythia.readString("Beams:idB = 2212");
    pythia.readString("Beams:eCM = 13600.");

    pythia.readString("SoftQCD:all = on");

    pythia.readString("Random:setSeed = on");
    pythia.readString("Random:seed = 12345");

    pythia.readString("Next:numberCount = 10000");

    if (!pythia.init()) {
        std::cerr << "Blad: Nie udalo sie zainicjalizowac Pythia 8!" << std::endl;
        return 1;
    }

    TFile* outFile = TFile::Open(outFileName.c_str(), "RECREATE");
    if (!outFile || outFile->IsZombie()) {
        std::cerr << "Blad: Nie mozna otworzyc pliku wyjsciowego: " << outFileName << std::endl;
        return 1;
    }

    TTree* tree = new TTree("Events", "Final state particles from Pythia 8 pp @ 13.6 TeV");

    std::vector<int> pdgId;
    std::vector<int> isCharged;
    std::vector<double> pt;
    std::vector<double> eta;
    std::vector<double> phi;

    tree->Branch("pdgId", &pdgId);
    tree->Branch("isCharged", &isCharged);
    tree->Branch("pt", &pt);
    tree->Branch("eta", &eta);
    tree->Branch("phi", &phi);

    for (int iEvent = 0; iEvent < nEvents; ++iEvent) {
        if (!pythia.next()) continue;

        pdgId.clear();
        isCharged.clear();
        pt.clear();
        eta.clear();
        phi.clear();

        for (int i = 0; i < pythia.event.size(); ++i) {
            const auto& p = pythia.event[i];

            if (!p.isFinal()) continue;

            pdgId.push_back(p.id());
            isCharged.push_back(p.isCharged() ? 1 : 0);
            pt.push_back(p.pT());
            eta.push_back(p.eta());
            phi.push_back(p.phi());
        }

        tree->Fill();
    }

    pythia.stat();

    outFile->Write();
    outFile->Close();
    delete outFile;

    std::cout << "Zakonczono generacje " << nEvents << " zdarzen. Zapisano do: " << outFileName << std::endl;
    return 0;
}
