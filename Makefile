################################################################
# Cobbler: Makefile for building Ansible roles
# https://github.com/cliffano/cobbler
################################################################

# Cobbler's version number
COBBLER_VERSION = 2.1.0

$(info ################################################################)
$(info Building Ansible role using Cobbler...)

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

deps-extra-apt:
	apt-get update
	apt-get install -y python3-venv

lint:
	$(call python_venv,ansible-lint -v .)
	$(call python_venv,yamllint .)

test:
	$(call python_venv,molecule test)

test-examples:
	mkdir -p stage/test-examples/
	cd examples && \
	for f in *.sh; do \
	  bash -x "$$f"; \
	done

# Update Makefile to the latest version tag
update-to-latest: TARGET_COBBLER_VERSION = $(shell curl -s https://api.github.com/repos/cliffano/cobbler/tags | jq -r '.[0].name')
update-to-latest: update-to-version

# Update Makefile to the main branch
update-to-main:
	curl https://raw.githubusercontent.com/cliffano/cobbler/main/src/Makefile-cobbler -o Makefile

# Update Makefile to the version defined in TARGET_COBBLER_VERSION parameter
update-to-version:
	curl https://raw.githubusercontent.com/cliffano/cobbler/$(TARGET_COBBLER_VERSION)/src/Makefile-cobbler -o Makefile

# Update dotfiles using the generator-ansible
update-dotfiles: GENERATOR_COMPONENT = $(shell yq .generator.component cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_PROJECT_ID = $(shell yq .generator.inputs.project_id cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_PROJECT_NAME = $(shell yq .generator.inputs.project_name cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_PROJECT_DESC = $(shell yq .generator.inputs.project_desc cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_AUTHOR_NAME = $(shell yq .generator.inputs.author_name cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_AUTHOR_EMAIL = $(shell yq .generator.inputs.author_email cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_GITHUB_ID = $(shell yq .generator.inputs.github_id cobbler.yml)
update-dotfiles: GENERATOR_INPUTS_GITHUB_REPO = $(shell yq .generator.inputs.github_repo cobbler.yml)
update-dotfiles: stage
	cd stage/ && \
	  rm -rf generator-ansible/ && \
	  git clone https://github.com/cliffano/generator-ansible && \
	  cd generator-ansible && \
	  make deps && \
	  node_modules/.bin/plop $(GENERATOR_COMPONENT) -- \
	    --project_id "$(GENERATOR_INPUTS_PROJECT_ID)" \
		--project_name "$(GENERATOR_INPUTS_PROJECT_NAME)" \
		--project_desc "$(GENERATOR_INPUTS_PROJECT_DESC)" \
		--author_name "$(GENERATOR_INPUTS_AUTHOR_NAME)" \
		--author_email "$(GENERATOR_INPUTS_AUTHOR_EMAIL)" \
		--github_id "$(GENERATOR_INPUTS_GITHUB_ID)" \
		--github_repo "$(GENERATOR_INPUTS_GITHUB_REPO)"
	cd stage/generator-ansible/stage/$(GENERATOR_COMPONENT) && \
	  cp -R .github/* ../../../../.github/ && \
	  cp .ansible-lint ../../../../.ansible-lint && \
	  cp .gitignore ../../../../.gitignore && \
		cp .yamllint ../../../../.yamllint && \
	  cp .rtk.json ../../../../.rtk.json

.PHONY: ci all stage clean rmdeps deps deps-upgrade deps-extra-apt lint test test-examples update-to-latest update-to-main update-to-version update-dotfiles