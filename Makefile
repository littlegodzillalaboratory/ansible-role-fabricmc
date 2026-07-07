################################################################
# Cobbler: Makefile for building Ansible roles
# https://github.com/cliffano/cobbler
################################################################

# Cobbler's version number
COBBLER_VERSION = 2.3.0

################################################################
# User configuration variables
# https://github.com/cliffano/cobbler#configuration
# These variables should be stored in cobbler.yml config file,
# and they will be parsed using yq https://github.com/mikefarah/yq

# PACKAGE_NAME is the name of the Ansible role
PACKAGE_NAME=$(shell yq .package_name cobbler.yml)

# AUTHOR is the author of the Ansible role
AUTHOR ?= $(shell yq .author cobbler.yml)

define set_generator_vars
$(1): GENERATOR_COMPONENT = $$(shell yq .generator.component cobbler.yml)
$(1): GENERATOR_INPUTS_PROJECT_ID = $$(shell yq .generator.inputs.project_id cobbler.yml)
$(1): GENERATOR_INPUTS_PROJECT_NAME = $$(shell yq .generator.inputs.project_name cobbler.yml)
$(1): GENERATOR_INPUTS_PROJECT_DESC = $$(shell yq .generator.inputs.project_desc cobbler.yml)
$(1): GENERATOR_INPUTS_AUTHOR_NAME = $$(shell yq .generator.inputs.author_name cobbler.yml)
$(1): GENERATOR_INPUTS_AUTHOR_EMAIL = $$(shell yq .generator.inputs.author_email cobbler.yml)
$(1): GENERATOR_INPUTS_GITHUB_ID = $$(shell yq .generator.inputs.github_id cobbler.yml)
$(1): GENERATOR_INPUTS_GITHUB_REPO = $$(shell yq .generator.inputs.github_repo cobbler.yml)
$(1): GENERATOR_INPUTS_GITHUB_TOKEN_PREFIX = $$(shell yq .generator.inputs.github_token_prefix cobbler.yml)
endef

$(info ################################################################)
$(info Building Ansible role using Cobbler...)
$(info - Package name = ${PACKAGE_NAME})
$(info - Author = ${AUTHOR})

define python_venv
	. .venv/bin/activate && $(1)
endef

define run_hook
	@if [ -f Makefile-extras ] && grep -q "^$(1):" Makefile-extras; then \
		$(MAKE) -f Makefile-extras $(1); \
	fi
endef

define deps_extra
	@if command -v apt-get > /dev/null 2>&1; then \
		if [ "$$(id -u)" = "0" ]; then \
			$(MAKE) deps-extra-apt; \
		else \
			sudo $(MAKE) deps-extra-apt; \
		fi; \
	fi
endef

################################################################
# Base targets

# CI target to be executed by CI/CD tool
all: ci
ci: clean lint test

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
	$(call deps_extra)

deps-upgrade:
	python3 -m venv .venv
	$(call python_venv,python3 -m pip install -r requirements-dev.txt)
	$(call python_venv,pip-compile --upgrade)

deps-extra-apt:
	apt-get update
	apt-get install -y python3-venv 
	apt-get install -y markdownlint

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
$(eval $(call set_generator_vars,update-dotfiles))
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
		--github_repo "$(GENERATOR_INPUTS_GITHUB_REPO)" \
		--github_token_prefix "$(GENERATOR_INPUTS_GITHUB_TOKEN_PREFIX)"
	cd stage/generator-ansible/stage/$(GENERATOR_COMPONENT) && \
	  cp -R .github/* ../../../../.github/ && \
	  cp .ansible-lint ../../../../.ansible-lint && \
	  cp .gitignore ../../../../.gitignore && \
	  cp .yamllint ../../../../.yamllint && \
	  cp .rtk.json ../../../../.rtk.json

# Update partial snippets using the generator-ansible
$(eval $(call set_generator_vars,update-partials))
update-partials: stage
	cd stage/ && \
	  rm -rf generator-ansible/ && \
	  git clone https://github.com/cliffano/generator-ansible && \
	  cd generator-ansible && \
	  make deps && \
	  node_modules/.bin/plop $(GENERATOR_COMPONENT)-partials -- \
	    --project_id "$(GENERATOR_INPUTS_PROJECT_ID)" \
		--project_name "$(GENERATOR_INPUTS_PROJECT_NAME)" \
		--project_desc "$(GENERATOR_INPUTS_PROJECT_DESC)" \
		--author_name "$(GENERATOR_INPUTS_AUTHOR_NAME)" \
		--author_email "$(GENERATOR_INPUTS_AUTHOR_EMAIL)" \
		--github_id "$(GENERATOR_INPUTS_GITHUB_ID)" \
		--github_repo "$(GENERATOR_INPUTS_GITHUB_REPO)" \
		--github_token_prefix "$(GENERATOR_INPUTS_GITHUB_TOKEN_PREFIX)"
	for block in AVATAR BADGES BUILD_REPORTS DEVELOPERS_GUIDE; do \
	  partial_file=$$(printf "%s" "$$block" | tr "A-Z" "a-z"); \
	  ex -s \
	    -c "/<!-- BEGIN:$$block -->/+1,/<!-- END:$$block -->/-1d" \
	    -c "/<!-- BEGIN:$$block -->/r stage/generator-ansible/stage/$(GENERATOR_COMPONENT)-partials/$$partial_file.txt" \
	    -c 'wq' \
	    README.md; \
	done

lint:
	mkdir -p docs/lint/
	$(call python_venv,ansible-lint tasks/ &> docs/lint/ansible-lint.txt)
	$(call python_venv,yamllint .)
 
test:
	$(call run_hook,x-pre-test)
	mkdir -p docs/test/
	$(call python_venv,molecule test > docs/test/molecule.txt)

test-examples:
	mkdir -p stage/test-examples/
	cd examples && \
	for f in *.sh; do \
	  bash -x "$$f"; \
	done

.PHONY: $(1) ci all stage clean rmdeps deps deps-upgrade deps-extra-apt lint test test-examples update-to-latest update-to-main update-to-version update-dotfiles update-partials
