SHELL := /bin/bash

### DOCKER ENVIRONMENTAL VARS #################################################
export DOCKER_BUILDKIT:=1
export COMPOSE_DOCKER_CLI_BUILD:=1
export COMPOSE_OPTS:=--env .env.ecr
export AWS_DEV_PROFILE=genepi-dev
export AWS_PROD_PROFILE=genepi-prod
export BACKEND_APP_ROOT=/usr/src/app

### DATABASE VARIABLES #################################################
LOCAL_DB_NAME = aspen_db
# This has to be "postgres" to ease moving snapshots from RDS.
LOCAL_DB_ADMIN_USERNAME = postgres
LOCAL_DB_ADMIN_PASSWORD = password_postgres
LOCAL_DB_RW_USERNAME = user_rw
LOCAL_DB_RW_PASSWORD = password_rw
LOCAL_DB_RO_USERNAME = user_ro
LOCAL_DB_RO_PASSWORD = password_ro


### HELPFUL #################################################
help: ## display help for this makefile
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help

.PHONY: rm-pycache
rm-pycache: ## remove all __pycache__ files (run if encountering issues with pycharm debugger (containers exiting prematurely))
	find . -name '__pycache__' | xargs rm -rf

### Connecting to remote dbs #########################################
remote-pgconsole: # Get a psql console on a remote db (from OSX only!)
	export ENV=$${ENV:=rdev}; \
	export AWS_PROFILE=$(shell [ $(ENV) = prod ] && echo $(AWS_PROD_PROFILE) || echo $(AWS_DEV_PROFILE)); \
	export config=$$(aws secretsmanager get-secret-value --secret-id $${ENV}/aspen-config | jq -r .SecretString ); \
	export DB_URI=$$(jq -r '"postgresql://\(.DB.admin_username):\(.DB.admin_password)@127.0.0.1:5556/$(DB)"' <<< $$config); \
	echo Connecting to $$(jq -r .DB.address <<< $$config)/$(DB) via $$(jq -r .bastion_host <<< $$config); \
	ssh -f -o ExitOnForwardFailure=yes -L 5556:$$(jq -r .DB.address <<< $$config):5432 $$(jq -r .bastion_host <<< $$config) sleep 10; \
	psql $${DB_URI}

remote-dbconsole: .env.ecr # Get a python console on a remote db (from OSX only!)
	export ENV=$${ENV:=rdev}; \
	export AWS_PROFILE=$(shell [ $(ENV) = prod ] && echo $(AWS_PROD_PROFILE) || echo $(AWS_DEV_PROFILE)); \
	export config=$$(aws secretsmanager get-secret-value --secret-id $${ENV}/aspen-config | jq -r .SecretString ); \
	export OSX_IP=$$(ipconfig getifaddr en0 || ipconfig getifaddr en1); \
	export DB_URI=$$(jq -r '"postgresql://\(.DB.admin_username):\(.DB.admin_password)@'$${OSX_IP}':5555/$(DB)"' <<< $$config); \
	echo Connecting to $$(jq -r .DB.address <<< $$config)/$(DB) via $$(jq -r .bastion_host <<< $$config); \
	ssh -f -o ExitOnForwardFailure=yes -L $${OSX_IP}:5555:$$(jq -r .DB.address <<< $$config):5432 $$(jq -r .bastion_host <<< $$config) sleep 20; \
	docker-compose $(COMPOSE_OPTS) run -e DB_URI backend sh -c 'pip install . && aspen-cli db --remote interact --connect'

### DOCKER LOCAL DEV #########################################
oauth/pkcs12/certificate.pfx:
	# All calls to the openssl cli happen in the oidc-server-mock container.
	@echo "Generating certificates for local dev"
	docker run -v $(PWD)/oauth/pkcs12:/tmp/certs --workdir /tmp/certs --rm=true --entrypoint bash soluto/oidc-server-mock:0.3.0 ./generate_cert.sh
	@if [ "$$(uname -s)" == "Darwin" ]; then \
		echo "Installing generated certs into the local keychain requires sudo access:"; \
		sudo security add-trusted-cert -d -p ssl -k /Library/Keychains/System.keychain oauth/pkcs12/server.crt; \
	fi
	# Linux assumes Ubuntu
	if [ "$$(uname -s)" == "Linux" ]; then \
		sudo cp oauth/pkcs12/server.crt /usr/local/share/ca-certificates/; \
		sudo update-ca-certificates; \
	fi
	docker run -v $(PWD)/oauth/pkcs12:/tmp/certs --workdir /tmp/certs --rm=true --entrypoint bash soluto/oidc-server-mock:0.3.0 ./generate_pfx.sh
	# On Linux, the pkcs12 directory gets written to with root permission. Force ownership to our user.
	sudo chown -R $$(id -u):$$(id -g) $(PWD)/oauth/pkcs12

.env.ecr:
	export AWS_ACCOUNT_ID=$$(aws sts get-caller-identity --profile $(AWS_DEV_PROFILE) | jq -r .Account); \
	if [ -n "$${AWS_ACCOUNT_ID}" ]; then \
		echo DOCKER_REPO=$${AWS_ACCOUNT_ID}.dkr.ecr.us-west-2.amazonaws.com/ > .env.ecr; \
	else \
		false; \
	fi

.PHONY: local-ecr-login
local-ecr-login:
	if PROFILE=$$(aws configure list-profiles | grep $(AWS_DEV_PROFILE)); then \
		aws ecr get-login-password --region us-west-2 --profile $(AWS_DEV_PROFILE) | docker login --username AWS --password-stdin $$(aws sts get-caller-identity --profile $(AWS_DEV_PROFILE) | jq -r .Account).dkr.ecr.us-west-2.amazonaws.com; \
	fi

.PHONY: init-empty-db
init-empty-db:
	docker-compose stop database
	docker-compose rm database
	docker-compose $(COMPOSE_OPTS) -f docker-compose.yml -f docker-compose-emptydb.yml up -d
	sleep 10 # hack, let postgres start up cleanly.
	-docker-compose exec -T database psql "postgresql://$(LOCAL_DB_ADMIN_USERNAME):$(LOCAL_DB_ADMIN_PASSWORD)@localhost:5432/$(LOCAL_DB_NAME)" -c "ALTER USER $(LOCAL_DB_ADMIN_USERNAME) WITH PASSWORD '$(LOCAL_DB_ADMIN_PASSWORD)';"
	-docker-compose exec -T database psql "postgresql://$(LOCAL_DB_ADMIN_USERNAME):$(LOCAL_DB_ADMIN_PASSWORD)@localhost:5432/$(LOCAL_DB_NAME)" -c "CREATE USER $(LOCAL_DB_RW_USERNAME) WITH PASSWORD '$(LOCAL_DB_RW_PASSWORD)';"
	-docker-compose exec -T database psql "postgresql://$(LOCAL_DB_ADMIN_USERNAME):$(LOCAL_DB_ADMIN_PASSWORD)@localhost:5432/$(LOCAL_DB_NAME)" -c "CREATE USER $(LOCAL_DB_RO_USERNAME) WITH PASSWORD '$(LOCAL_DB_RO_PASSWORD)';"
	-docker-compose exec -T database psql "postgresql://$(LOCAL_DB_ADMIN_USERNAME):$(LOCAL_DB_ADMIN_PASSWORD)@localhost:5432/$(LOCAL_DB_NAME)" -c "GRANT ALL PRIVILEGES ON DATABASE $(LOCAL_DB_NAME) TO $(LOCAL_DB_RW_USERNAME);"
	docker-compose exec -T utility aspen-cli db --docker create
	docker-compose exec -T utility alembic stamp head


.PHONY: local-init
local-init: oauth/pkcs12/certificate.pfx .env.ecr local-ecr-login ## Launch a new local dev env and populate it with test data.
	docker-compose $(COMPOSE_OPTS) up -d
	@docker-compose exec -T database psql "postgresql://$(LOCAL_DB_ADMIN_USERNAME):$(LOCAL_DB_ADMIN_PASSWORD)@localhost:5432/$(LOCAL_DB_NAME)" -c "alter user $(LOCAL_DB_ADMIN_USERNAME) with password '$(LOCAL_DB_ADMIN_PASSWORD)';"
	docker-compose exec -T utility pip3 install awscli
	docker-compose exec -T utility $(BACKEND_APP_ROOT)/scripts/setup_dev_data.sh
	docker-compose exec -T utility alembic upgrade head
	docker-compose exec -T utility python scripts/setup_localdata.py
	docker-compose exec -T utility pip install .

.PHONY: backend-debugger
backend-debugger: ## Attach to the backend service (useful for pdb)
	docker attach $$(docker-compose ps | grep backend | cut -d ' ' -f 1 | head -n 1)

.PHONY: local-status
local-status: ## Show the status of the containers in the dev environment.
	docker ps -a | grep --color=no -e 'CONTAINER\|aspen'

.PHONY: local-rebuild
local-rebuild: .env.ecr local-ecr-login ## Rebuild local dev without re-importing data
	docker-compose $(COMPOSE_OPTS) build frontend backend utility
	docker-compose $(COMPOSE_OPTS) up -d

.PHONY: local-rebuild-workflows
local-rebuild-workflows: .env.ecr local-ecr-login ## Rebuild batch containers
	docker-compose $(COMPOSE_OPTS) build gisaid pangolin nextstrain
	docker-compose $(COMPOSE_OPTS) up -d

.PHONY: local-sync
local-sync: local-rebuild local-init ## Re-sync the local-environment state after modifying library deps or docker configs

.PHONY: local-start
local-start: .env.ecr ## Start a local dev environment that's been stopped.
	docker-compose $(COMPOSE_OPTS) up -d

.PHONY: local-stop
local-stop: ## Stop the local dev environment.
	docker-compose stop

.PHONY: local-clean
local-clean: ## Remove everything related to the local dev environment (including db data!)
	-if [ -f ./oauth/pkcs12/server.crt ] ; then \
		if [ "$$(uname -s)" == "Linux" ]; then \
			echo "Removing this certificate from /usr/local/share requires sudo access"; \
		sudo cp oauth/pkcs12/server.crt /usr/local/share/ca-certificates/; \
		sudo update-ca-certificates; \
		fi; \
		if [ "$$(uname -s)" == "Darwin" ]; then \
			export CERT=$$(docker run -v $(PWD)/oauth/pkcs12:/tmp/certs --workdir /tmp/certs --rm=true --entrypoint "" soluto/oidc-server-mock:0.3.0 bash -c "openssl x509 -in server.crt -outform DER | sha1sum | cut -d ' ' -f 1"); \
			echo ""; \
			echo "Removing this certificate requires sudo access"; \
			sudo security delete-certificate -Z $${CERT} /Library/Keychains/System.keychain; \
		fi; \
	fi;
	-rm -rf ./oauth/pkcs12/server*
	-rm -rf ./oauth/pkcs12/certificate*
	docker-compose rm -sf
	-docker volume rm aspen_database
	-docker volume rm aspen_localstack

.PHONY: local-logs
local-logs: ## Tail the logs of the dev env containers. ex: make local-logs CONTAINER=backend
	docker-compose logs -f $(CONTAINER)

.PHONY: local-shell
local-shell: ## Open a command shell in one of the dev containers. ex: make local-shell CONTAINER=frontend
	docker-compose exec $(CONTAINER) bash

.PHONY: local-pgconsole
local-pgconsole: ## Connect to the local postgres database.
	docker-compose exec database psql "postgresql://$(LOCAL_DB_ADMIN_USERNAME):$(LOCAL_DB_ADMIN_PASSWORD)@localhost:5432/$(LOCAL_DB_NAME)"

.PHONY: local-dbconsole
local-dbconsole: ## Connect to the local postgres database.
	docker-compose exec utility aspen-cli db --docker interact

.PHONY: local-dbconsole-profile
local-dbconsole-profile: ## Connect to the local postgres database and profile queries.
	docker-compose exec utility aspen-cli db --docker interact --profile

.PHONY: local-update-deps
local-update-deps: ## Update requirements.txt to reflect pipenv file changes.
	docker-compose exec utility pipenv --python 3.9
	docker-compose exec utility pipenv update
	docker-compose exec utility bash -c "pipenv lock -r >| requirements.txt"


### ACCESSING CONTAINER MAKE COMMANDS ###################################################
utility-%: ## Run make commands in the utility container (src/backend/Makefile)
	docker-compose exec utility make $(subst utility-,,$@) MESSAGE="$(MESSAGE)"

backend-%: .env.ecr ## Run make commands in the backend container (src/backend/Makefile)
	docker-compose $(COMPOSE_OPTS) run --no-deps --rm backend make $(subst backend-,,$@)

frontend-%: .env.ecr ## Run make commands in the backend container (src/frontend/Makefile)
	docker-compose $(COMPOSE_OPTS) run -e CI=true --no-deps --rm frontend make $(subst frontend-,,$@)

### DOCKER FOR WORKFLOWS ###################################################

build-docker: export ASPEN_DOCKER_IMAGE_VERSION=$(shell date +%Y%m%d_%H%M)
build-docker:
	docker pull nextstrain/base
	docker build --no-cache -t cziaspen/batch:latest --build-arg ASPEN_DOCKER_IMAGE_VERSION=$${ASPEN_DOCKER_IMAGE_VERSION} docker/aspen-batch
	docker tag cziaspen/batch:latest cziaspen/batch:$${ASPEN_DOCKER_IMAGE_VERSION}
	@echo "Please push the tags cziaspen/batch:latest and cziaspen/batch:$${ASPEN_DOCKER_IMAGE_VERSION} when done, i.e.,"
	@echo "  docker push cziaspen/batch:latest"
	@echo "  docker push cziaspen/batch:$${ASPEN_DOCKER_IMAGE_VERSION}"
	@echo ""
	@echo "If you wish to clean up some of your old aspen docker images, run:"
	@echo "  docker image rm \$\$$(docker image ls -q cziaspen/batch -f 'before=cziaspen/batch:latest')"


### TERRAFORM ###################################################
include terraform.mk
