token = $(PHAB_API_TOKEN)
host = $(PHAB_HOST)
jenkins =
user =
pass =
room =
timeout = 10
colors = red
ignores = "" 
outputs = artifacts/
results = $(outputs)output

all: install clean run

install:
	pip install python-jenkins

clean:
	rm -f $(results)

run:
	mkdir -p $(outputs)
ifeq ($(strip $(jenkins)),)
		echo "jenkins is empty"
		exit -1
endif
ifeq ($(strip $(token)),)
		echo "token is empty"
		exit -1
endif
ifeq ($(strip $(user)),)
		echo "user is empty"
		exit -1
endif
ifeq ($(strip $(pass)),)
		echo "password is empty"
		exit -1
endif
ifeq ($(strip $(colors)),)
		echo "colors is empty"
		exit -1
endif
ifeq ($(strip $(host)),)
		echo "host is empty"
		exit -1
endif
ifeq ($(strip $(room)),)
		echo "room is empty"
		exit -1
endif
	python jobs_by_color.py --host $(jenkins) --user $(user) --pwd $(pass) --colors $(colors) --ignore $(ignores) > $(results)
	./post.sh "$(host)" "$(token)" "$(results)" "$(room)" "$(timeout)"

