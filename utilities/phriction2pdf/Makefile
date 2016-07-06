token = $(PHAB_API_TOKEN)
slug =
host = 
bin = build
name = $(shell echo ${slug} | sed "s/\//-/g")
raw = $(bin)/$(name).json
markdown = $(bin)/$(name).md

define build-out =
pandoc $(markdown) \
--output $(bin)/$(name).$1 \
--smart \
-V geometry:margin=0.7in
endef

$(shell mkdir -p $(bin))

all: clean download md pdf

download:
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
	curl -s $(host)/api/phriction.info \
		    -d api.token=$(token) \
			    -d slug='$(slug)' > $(raw)

md:
	python wiki.py --input $(raw) --output $(markdown)

pdf:
	$(call build-out,pdf)

doc:
	$(call build-out,doc)

clean:
	rm -f $(bin)/*
