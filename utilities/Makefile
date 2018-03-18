SRC=src/
MOD=$(shell find modules/ -name "*.d" | grep "src")
APPS=$(shell ls $(SRC) | cut -d "." -f 1)
OUTPUT=bin
FLAGS := -inline -release -O -boundscheck=off

.PHONY: all

all: build

deps:
	git submodule update --init

build: clean $(APPS)

$(APPS):
	dmd $(FLAGS) $(SRC)$@.d $(MOD) -of$(OUTPUT)/phabricator-utils-$@

clean:
	mkdir -p $(OUTPUT)
	rm -f $(OUTPUT)/*
