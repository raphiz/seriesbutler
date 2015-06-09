.PHONY: default
default: buildimage dev

.PHONY: buildimage
buildimage:
	docker build -t raphiz/pyseries ./

within_docker = docker run --rm -it --name pyseries -u user -v $(shell pwd):/src/ -e "GIT_AUTHOR_NAME=$(shell git config user.name)" -e "GIT_COMMITTER_NAME=$(shell git config user.name)" -e "EMAIL=$(shell git config user.email)" raphiz/pyseries

.PHONY: release
release:
	@echo "Is everything commited? Are you ready to release? Press any key to continue - abort with Ctrl+C"
	@read x
	$(within_docker) bumpversion release
	$(within_docker) python setup.py sdist bdist_wheel
	$(within_docker) bumpversion --no-tag patch
	@echo Don't forget to push the tags!


.PHONY: dev
dev:
	$(within_docker) bash

integration:
	docker run --rm -it -v $(shell pwd):/src/:ro -w /src python:3.4 bash
