SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
MAKEFLAGS+= --warn-undefined-variables --no-builtin-rules


PREFIX?=~/.local
INSTALL_BIN?=$(PREFIX)/bin/lazytime
PYTHON=python

PATH_SOURCES_PY=src/py
SOURCES_PY:=$(wildcard $(PATH_SOURCES_PY)/*.py $(PATH_SOURCES_PY)/*/*.py $(PATH_SOURCES_PY)/*/*/*.py $(PATH_SOURCES_PY)/*/*/*/*.py)
MODULES_PY:=$(patsubst $(PATH_SOURCES_PY)/%,%,$(patsubst %/__init__.py,%,$(wildcard src/py/*/__init__.py src/py/*/*/__init__.py src/py/*/*/*/__init__.py)))
MAIN_MODULES_PY:=$(patsubst $(PATH_SOURCES_PY)/%,%,$(patsubst %/__init__.py,%,$(wildcard src/py/*/__init__.py)))



.PHONY: install
install:
	@
	echo "--- Installing $(notdir $(INSTALL_BIN)) at $(INSTALL_BIN)"
	ln -sfr bin/lazytime ~/.local/bin/lazytime

.PHONY: uninstall
uninstall:
	@if [ -L $(INSTALL_BIN) ]; then
		unlink $(INSTALL_BIN)
	fi

.PHONY: audit
audit: require-py-bandit
	bandit -r $(PATH_SOURCES_PY)

# NOTE: The compilation seems to create many small modules instead of a big single one
.PHONY: compile
compile:
	# NOTE: Output is going to be like 'extra/__init__.cpython-310-x86_64-linux-gnu.so'
	for module in $(MAIN_MODULES_PY): do
		env -C build MYPYPATH=$(realpath .)/src/py mypyc -p $$module
	done

.PHONY: check
check: lint
	@

.PHONY: lint
lint:
	@flake8 --ignore=E1,E203,E302,E401,E501,E741,F821,W $(SOURCES_PY)

.PHONY: format
format:
	@black $(SOURCES_PY)

.PHONY: format
require-py-%:
	@if [ -z "$$(which '$*' 2> /dev/null)" ]; then $(PYTHON) -mpip install --user --upgrade '$*'; fi

print-%:
	$(info $*=$($*))

.ONESHELL:
# EOF
