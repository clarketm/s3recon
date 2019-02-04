SHELL:=$(shell which bash)

.PHONY: list
l h list help:
	@make -pq | awk -F':' '/^[a-zA-Z0-9][^$$#\/\t=]*:([^=]|$$)/ {split($$1,A,/ /);for(i in A)print A[i]}' | sed '/Makefile/d' | sort

.PHONY: create-venv
create-venv:
ifeq (, $(shell which pipenv))
	test -d venv || python -m venv venv
endif

.PHONY: venv
venv: create-venv
ifeq (, $(shell which pipenv))
	@echo $(shell realpath ./venv/bin/activate) | tee >(pbcopy)
else
	@echo $(shell pipenv --venv)/bin/activate | tee >(pbcopy)

endif

.PHONY: format
f format:
	python -m black .

.PHONY: docstring
docstring:
	pyment -w ./s3recon
