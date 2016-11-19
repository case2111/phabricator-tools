token = $(PHAB_TOKEN)
slug =
host = $(PHAB_HOST)
bin = build
name = $(shell echo ${slug} | sed "s/\//-/g")
markdown = $(bin)/$(name).md

define build-out =
pandoc $(markdown) \
--output $(bin)/$(name).$1 \
--smart \
-V geometry:margin=0.7in
endef

$(shell mkdir -p $(bin))

all: clean md pdf

md:
ifeq ($(strip $(host)),)
		echo "host is empty"
		exit -1
endif
ifeq ($(strip $(slug)),)
		echo "slug is empty"
		exit -1
endif
ifeq ($(strip $(token)),)
		echo "token is empty"
		exit -1
endif
	python getmd.py --host "$(host)" --token "$(token)" --slug "$(slug)" --output "$(markdown)"

pdf:
	$(call build-out,pdf)

doc:
	$(call build-out,doc)

clean:
	rm -f $(bin)/*
