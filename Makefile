CONTAINER_NAME := acv-sfdc-ci
VERSION := $(shell git fetch --tags && git describe --tags)

.PHONY: clean
clean:
	find . -type f -name '.DS_Store' -delete -o -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete

.PHONY: deps
deps:
	pipenv install
	pipenv install --dev

build: clean
	git submodule update --init --recursive
	@docker build \
		--build-arg NEXUS_USER=${NEXUS_USER} \
		--build-arg NEXUS_PASSWORD=${NEXUS_PASSWORD} \
		--build-arg VERSION=${VERSION} \
		--tag $(CONTAINER_NAME):$(VERSION) .

.PHONY: deploy
deploy: build
	docker run \
	    -e APP_MODE=deploy \
        -e NEXUS_USER=${NEXUS_USER} \
        -e NEXUS_PASSWORD=${NEXUS_PASSWORD} \
		-v /var/run/docker.sock:/var/run/docker.sock \
		$(CONTAINER_NAME):$(VERSION)

.PHONY: stop-ci
stop-ci:
	docker ps -a -q --filter ancestor=$(CONTAINER_NAME):$(VERSION) | xargs docker rm -f
	docker ps -a -q --filter ancestor=mysql:5.7git s | xargs docker rm -f
