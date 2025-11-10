SHELL := /bin/bash

.PHONY: setup start test-unit test-subagent docker-up docker-down

setup:
	./setup.sh

start:
	@echo "Start services with: make docker-up && make start-subagent" 

docker-up:
	docker-compose up -d
	echo "Docker services started"

docker-down:
	docker-compose down

test-unit:
	python -m pytest -q

start-subagent:
	# Run the Claude subagent locally
	python -m claude_subagent.app

test-subagent:
	python -c 'import requests, sys; print("Call subagent at http://localhost:5000/scan")'
	echo "Use curl or httpie to POST JSON {\"text\": \"...\" } to http://localhost:5000/scan"
