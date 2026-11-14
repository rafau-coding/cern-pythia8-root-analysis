CXX      = g++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra

ROOT_CFLAGS   := $(shell root-config --cflags)
ROOT_LIBS     := $(shell root-config --libs)
PYTHIA_CFLAGS := $(shell pythia8-config --cflags)
PYTHIA_LIBS   := $(shell pythia8-config --libs)

TARGETS = generate_events analyze_events

all: $(TARGETS)

generate_events: generate_events.cc
	$(CXX) $(CXXFLAGS) $< -o $@ $(PYTHIA_CFLAGS) $(ROOT_CFLAGS) $(PYTHIA_LIBS) $(ROOT_LIBS)

analyze_events: analyze_events.cc
	$(CXX) $(CXXFLAGS) $< -o $@ $(ROOT_CFLAGS) $(ROOT_LIBS)

run: all
	./generate_events 100000 events.root
	./analyze_events events.root analysis.root
	root -b -q 'draw_plots.C("analysis.root", "plots")'

clean:
	rm -f $(TARGETS) events.root
