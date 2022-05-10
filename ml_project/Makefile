.PHONY: clean make_dataset build_features lint\
 requirements download_raw_dataset test train_model all

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROFILE = default
PROJECT_NAME = ml_project
PYTHON_INTERPRETER = python
CONFIG = configs/train_config.yaml

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install Python Dependencies
requirements: test_environment
	$(PYTHON_INTERPRETER) -m pip install -U pip setuptools wheel
	$(PYTHON_INTERPRETER) -m pip install -r requirements.txt

## Download raw data with Kaggle API
download_raw_dataset:
	kaggle datasets download -d cherngs/heart-disease-cleveland-uci -p ./data/raw
	unzip ./data/raw/heart-disease-cleveland-uci -d ./data/raw/
	rm ./data/raw/heart-disease-cleveland-uci.zip

## Make train valid and test datasets from raw dataset
make_dataset:
	$(PYTHON_INTERPRETER) src/data/make_dataset.py $(CONFIG)

## Build features
build_features:
	$(PYTHON_INTERPRETER) src/features/build_features.py $(CONFIG)

## train model
train_model:
	$(PYTHON_INTERPRETER) src/models/train_model.py $(CONFIG)

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Lint using flake8
lint:
	flake8 src

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# DAG                                                                           #
#################################################################################

## download_raw_dataset -> make_dataset -> build_features
all: requirements download_raw_dataset make_dataset build_features train_model
train: make_dataset build_features train_model


#################################################################################
# HELP                                                                          #
#################################################################################

.DEFAULT_GOAL := help

.PHONY: help

help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
