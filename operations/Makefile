define say
    $(info [Operations] $1)
endef
define die
    $(error [Operations] $1)
endef

$(call say,---------> Begin some debug outputs)

#	Main dirs
OPERATIONS_DIR := $(realpath .)
SERVICES_DIR := $(OPERATIONS_DIR)/../services
LOG_DIR := $(OPERATIONS_DIR)/../log
$(call say,Operations dir: $(OPERATIONS_DIR))
$(call say,Microservices dir: $(SERVICES_DIR))


#	Caddy
CADDY_PORT := 2015
CADDY_PROCESS_COUNT := 1


#	Services
SERVICE_POSTING_APPNAME := posting_app
SERVICE_POSTING_CONFIG := posting.cfg
SERVICE_POSTING_PORT := $(CADDY_PORT)
SERVICE_POSTING_DEV_PORT := 8000
SERVICE_POSTING_PROCESS_COUNT = 3
#
SERVICE_VOTING_APPNAME := voting_app
SERVICE_VOTING_CONFIG := voting.cfg
SERVICE_VOTING_PORT := $(CADDY_PORT)
SERVICE_VOTING_DEV_PORT := 8001
SERVICE_VOTING_PROCESS_COUNT = 3
#
SERVICE_BFF_APPNAME := bff_app
SERVICE_BFF_CONFIG := bff.cfg
SERVICE_BFF_PORT := $(CADDY_PORT)
SERVICE_BFF_DEV_PORT := 8002
SERVICE_BFF_PROCESS_COUNT = 3


#	Database
DB_DIR=$(OPERATIONS_DIR)/../database
$(call say,Database dir: $(DB_DIR))
SERVICE_DATABASE_FILE_NAME=project2.db
SERVICE_DATABASE_FILE_PATH=$(DB_DIR)/$(SERVICE_DATABASE_FILE_NAME)
$(call say,Database path: $(SERVICE_DATABASE_FILE_PATH))
#
INIT_DATABASE_SCRIPT_PATH=$(OPERATIONS_DIR)/init_database.py
POPULATE_DATABASE_SCRIPT_PATH=$(OPERATIONS_DIR)/populate_database.py
TEST_POSTING_SCRIPT_PATH=$(OPERATIONS_DIR)/test_posting.py
TEST_VOTING_SCRIPT_PATH=$(OPERATIONS_DIR)/test_voting.py



$(call say,---------> End some debug outputs)


#
default:	menu
.PHONY:	default


#	Execute recipies in order, in one shell
.ONESHELL:


#
menu:
	@echo
	@echo "***************************"
	@echo "***** OPERATIONS MENU *****"
	@echo
	@echo "> Initialization Stuff"
	@echo
	@echo "make reset                 ==> Reset microservices database (directly to file; No need for API)"
	@echo
	@echo "> Development Stuff"
	@echo
	@echo "make start-posting-dev     ==> Start the posting microservice in a mode suitable for local debug development (Port $(SERVICE_POSTING_PORT))"
	@echo "make start-voting-dev      ==> Start the voting microservice in a mode suitable for local debug development (Port $(SERVICE_VOTING_PORT))"
	@echo "make start-bff-dev         ==> Start the bff service in a mode suitable for local debug development (Port $(SERVICE_BFF_PORT))"
	@echo
	@echo "make populate-dev          ==> Call 'make populate' below, but with DEV ports"
	@echo
	@echo "make test-posting-dev      ==> Call 'make test-posting' below, but with DEV ports"
	@echo "make test-voting-dev       ==> Call 'make test-voting' below, but with DEV ports"
	@echo
	@echo "> Production Stuff"
	@echo
	@echo "make foreman               ==> Start multiple production instances of all services using foreman, with load balancer on port $(CADDY_PORT)"
	@echo
	@echo "> Test Stuff (Production Server Should Already Be Running)"
	@echo
	@echo "make populate              ==> Populate microservices with data (production server should be started already)"
	@echo "make test-posting          ==> Run tests against the posting microservice (should already be populated)"
	@echo "make test-voting           ==> Run tests against the voting microservice (should already be populated)"
	@echo



#
reset:   reset-say
reset:   reset-database
reset-say:
	$(call say,Resetting microservices data)
.PHONY: reset reset-say


#
reset-database:
	$(call say,Resetting the microservice databases)
	python3 \
		"$(INIT_DATABASE_SCRIPT_PATH)" \
		--db "$(SERVICE_DATABASE_FILE_PATH)" \
		| tee "$(LOG_DIR)/reset.log"
.PHONY: reset-database


populate-dev:	SERVICE_POSTING_PORT := $(SERVICE_POSTING_DEV_PORT)
populate-dev:	SERVICE_VOTING_PORT := $(SERVICE_VOTING_DEV_PORT)
populate-dev:	populate
.PHONY: populate-dev


populate:
	$(call say,Populating the microservice databases)
	python3 \
		"$(POPULATE_DATABASE_SCRIPT_PATH)" \
		--posting-port "$(SERVICE_POSTING_PORT)" \
		--voting-port "$(SERVICE_VOTING_PORT)" \
		| tee "$(LOG_DIR)/populate.log"
.PHONY: populate


#
start-posting-dev: start-posting-dev-say
	cd "$(SERVICES_DIR)" && \
		FLASK_APP=$(SERVICE_POSTING_APPNAME) \
		FLASK_ENV=development \
		APP_CONFIG=$(SERVICE_POSTING_CONFIG) \
		flask run -p $(SERVICE_POSTING_DEV_PORT)
start-posting-dev-say:
	$(call say,Starting posting microservice for local development)
.PHONY: start-posting-dev start-posting-dev-say


#
start-voting-dev: start-voting-dev-say
	cd "$(SERVICES_DIR)" && \
		FLASK_APP=$(SERVICE_VOTING_APPNAME) \
		FLASK_ENV=development \
		APP_CONFIG=$(SERVICE_VOTING_CONFIG) \
		flask run -p $(SERVICE_VOTING_DEV_PORT)
start-voting-dev-say:
	$(call say,Starting voting microservice for local development)
.PHONY: start-voting-dev start-voting-dev-say


#
start-bff-dev: start-bff-dev-say
	cd "$(SERVICES_DIR)" && \
		FLASK_APP=$(SERVICE_BFF_APPNAME) \
		FLASK_ENV=development \
		APP_CONFIG=$(SERVICE_BFF_CONFIG) \
		flask run -p $(SERVICE_BFF_DEV_PORT)
start-bff-dev-say:
	$(call say,Starting BFF microservice for local development)
.PHONY: start-bff-dev start-bff-dev-say


#
foreman:
	cd "$(SERVICES_DIR)" && \
		foreman start \
			--formation caddy=$(CADDY_PROCESS_COUNT),posting=$(SERVICE_POSTING_PROCESS_COUNT),voting=$(SERVICE_VOTING_PROCESS_COUNT),bff=$(SERVICE_BFF_PROCESS_COUNT)
foreman-say:
	$(call say,Starting foreman)
.PHONY: foreman foreman-say


#
test-posting-dev:	SERVICE_POSTING_PORT := $(SERVICE_POSTING_DEV_PORT)
test-posting-dev:	test-posting
.PHONY: test-posting-dev


#
test-posting:
	$(call say,Calling the posting microservice test script)
	python3 \
		"$(TEST_POSTING_SCRIPT_PATH)" \
		--port "$(SERVICE_POSTING_PORT)" \
		| tee "$(LOG_DIR)/test-posting.log"
.PHONY: test-posting


#
test-voting-dev:	SERVICE_VOTING_PORT := $(SERVICE_VOTING_DEV_PORT)
test-voting-dev:	test-voting
.PHONY: test-voting-dev


#
test-voting:
	$(call say,Calling the voting microservice test script)
	python3 \
		"$(TEST_VOTING_SCRIPT_PATH)" \
		--port "$(SERVICE_VOTING_PORT)" \
		| tee "$(LOG_DIR)/test-voting.log"
.PHONY: test-voting





