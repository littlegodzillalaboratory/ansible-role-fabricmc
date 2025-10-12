################################################################
# MDH: Makefile for building Ansible roles
# https://github.com/cliffano/mdh
################################################################

# MDH's version number
MDH_VERSION = 0.10.0

$(info ################################################################)
$(info Building Ansible role using MDH:)

define python_venv
	. .venv/bin/activate && $(1)
endef

################################################################
# Base targets

# CI target to be executed by CI/CD tool
ci: clean deps lint test

# All target is just an alias to ci target
all: clean deps lint test

# Ensure stage directory exists
stage:
	mkdir -p stage

# Remove all temporary (staged, generated, cached) files
clean:
	rm -rf stage/

rmdeps:
	rm -rf .venv/

deps:
	python3 -m venv .venv
	$(call python_venv,python3 -m pip install -r requirements.txt)

deps-upgrade:
	python3 -m venv .venv
	$(call python_venv,python3 -m pip install -r requirements-dev.txt)
	$(call python_venv,pip-compile --upgrade)

lint:
	$(call python_venv,molecule lint)

test:
	$(call python_venv,molecule test)

# Update Makefile to the latest version tag
update-to-latest: TARGET_MDH_VERSION = $(shell curl -s https://api.github.com/repos/cliffano/mdh/tags | jq -r '.[0].name')
update-to-latest: update-to-version

# Update Makefile to the main branch
update-to-main:
	curl https://raw.githubusercontent.com/cliffano/mdh/main/src/Makefile-mdh -o Makefile

# Update Makefile to the version defined in TARGET_MDH_VERSION parameter
update-to-version:
	curl https://raw.githubusercontent.com/cliffano/mdh/$(TARGET_MDH_VERSION)/src/Makefile-mdh -o Makefile

################################################################

.PHONY: ci all clean rmdeps deps deps-upgrade lint test update-to-latest update-to-main update-to-version stage
