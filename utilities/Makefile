SRC    := src/
FILES  := $(shell find src/helpers -type f -name "*.d")
MODDIR := $(shell find modules/ -type d -name "src")
MOD    := $(shell find $(MODDIR) -type f -name "*.d")
APPS   := tasks wiki
OUTPUT := bin
FLAGS  := -inline -release -O -boundscheck=off
DMD    := dmd

all: build

deps:
	git submodule update --init

build: clean $(APPS)

$(APPS):
	$(DMD) $(FLAGS) $(SRC)common.d $(SRC)$@.d $(MOD) $(FILES) -of$(OUTPUT)/phab-utilities-$@

clean:
	mkdir -p $(OUTPUT)
	rm -f $(OUTPUT)/*
