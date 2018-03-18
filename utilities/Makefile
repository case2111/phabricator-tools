SRC=src/
MOD=$(shell find modules/ -name "*.d" | grep "src")
APPS=$(shell ls $(SRC) | cut -d "." -f 1 | grep -v "common")
OUTPUT=bin
FLAGS := -inline -release -O -boundscheck=off

.PHONY: all

all: build

deps:
	git submodule update --init

build: clean $(APPS)

$(APPS):
	dmd $(FLAGS) $(SRC)/common.d $(SRC)$@.d $(MOD) -of$(OUTPUT)/phab-utilities-$@

clean:
	mkdir -p $(OUTPUT)
	rm -f $(OUTPUT)/*
