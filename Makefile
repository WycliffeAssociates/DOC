.PHONY: checkvenv
checkvenv:
# raises error if environment is not active
ifeq ("$(VIRTUAL_ENV)","")
	@echo "Venv is not activated!"
	@echo "Activate venv first."
	@echo
	exit 1
endif

.PHONY: pipupgrade
pipupgrade: checkvenv
	pip install --upgrade pip

.PHONY: pyupgrade
pyupgrade: checkvenv pipupgrade
# checks if pip-tools is installed
ifeq ("$(wildcard .venv/bin/pip-compile)","")
	@echo "Installing Pip-tools..."
	@pip install --no-cache-dir pip-tools
endif

ifeq ("$(wildcard .venv/bin/pip-sync)","")
	@echo "Installing Pip-tools..."
	@pip install --no-cache-dir pip-tools
endif

.PHONY: build
build: checkvenv local-install-deps-prod
	export IMAGE_TAG=local && \
	docker build -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend


.PHONY: build-no-pip-update
build-no-pip-update: checkvenv
	export IMAGE_TAG=local && \
	docker build -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend

.PHONY: build-no-cache
build-no-cache: checkvenv local-install-deps-prod
	export IMAGE_TAG=local && \
	docker build --no-cache -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build --no-cache -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend

.PHONY: up
up: checkvenv
	export IMAGE_TAG=local && \
	BACKEND_API_URL=http://localhost:5005 docker-compose up

.PHONY: up-as-daemon
up-as-daemon: checkvenv
	export IMAGE_TAG=local && \
	BACKEND_API_URL=http://localhost:5005 docker-compose up -d


# This is the entryoint for a non-technical user who just
# wants to type one command and have it work.
.PHONY: build-and-run
build-and-run: build up


.PHONY: down
down:
	docker-compose down --remove-orphans

.PHONY: stop-and-remove
stop-and-remove:
	docker ps -q | xargs docker stop
	docker ps -a -q -f status=exited | xargs docker rm


.PHONY: test
test: up-as-daemon
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e


.PHONY: clean-local-docker-output-dir
clean-local-docker-output-dir:
	find docker_document_output/ -type f -name "*.pdf" -exec rm -- {} +
	find docker_document_output/ -type f -name "*.epub" -exec rm -- {} +
	find docker_document_output/ -type f -name "*.docx" -exec rm -- {} +

.PHONY: unit-tests
unit-tests: up-as-daemon
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api -n auto /tests/unit

.PHONY: e2e-tests
e2e-tests: up-as-daemon clean-local-docker-output-dir
	# NOTE parallel pytests via pytest_xdist fail for e2e tests in Docker but
	# work for unit tests in Docker and work everywhere outside of
	# Docker. So we utilize them everywhere we can pending a fix.
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api -n auto /tests/e2e
	# BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e

.PHONY: smoke-test-with-translation-words
smoke-test-with-translation-words: up-as-daemon clean-local-docker-output-dir
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_hr

.PHONY: smoke-test-with-translation-words2
smoke-test-with-translation-words2: up-as-daemon clean-local-docker-output-dir
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order_2c_sl_hr

.PHONY: smoke-test-with-translation-words3
smoke-test-with-translation-words3: up-as-daemon clean-local-docker-output-dir
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e -k test_stream_pdf

.PHONY: mypy
mypy: checkvenv
	mypy --strict --install-types --non-interactive backend/document/**/*.py
	mypy --strict --install-types --non-interactive tests/**/*.py

.PHONY: mypyc
mypyc:
	mypyc --strict --install-types --non-interactive backend/document/domain/{assembly_strategies,document_generator,resource_lookup,parsing}.py

.PHONY: clean-mypyc-artifacts
clean-mypyc-artifacts:
	find . -type f -name "*.so" -exec rm -- {} +
	find . -type f -name "*.c" -exec rm -- {} +

# https://radon.readthedocs.io/en/latest/commandline.html
.PHONY: radon-cyclomatic-complexity
radon-cyclomatic-complexity: checkvenv
	radon cc backend/document/**/*.py

.PHONY: radon-raw-stats
radon-raw-stats: checkvenv
	radon raw backend/document/**/*.py

.PHONY: radon-maintainability-index
radon-maintainability-index: checkvenv
	radon mi backend/document/**/*.py

.PHONY: radon-halstead-complexity
radon-halstead-complexity: checkvenv
	radon hal backend/document/**/*.py

.PHONY: vulture-dead-code
vulture-dead-code: checkvenv
	vulture backend/document/ --min-confidence 100
	vulture tests/ --min-confidence 100

.PHONY: generate-class-diagrams
generate-class-diagrams:
	pyreverse backend/document
	dot -Tpng classes.dot -o docs/classes.png

.PHONY: all
all: down build up test

.PHONY: all-plus-linting
all-plus-linting: mypy down build up test

# Run a local Uvicorn server outside Docker
.PHONY: local-server
local-server: checkvenv
	BACKEND_API_URL="http://localhost:5005" IN_CONTAINER=false uvicorn document.entrypoints.app:app --reload --host "0.0.0.0" --port "5005" --app-dir "./backend/"

# Run a local Gunicorn server outside Docker
.PHONY: local-gunicorn-server
local-gunicorn-server: checkvenv
	exec gunicorn --name DOC --worker-class uvicorn.workers.UvicornWorker --conf ./backend/gunicorn.conf.py --pythonpath ./backend  document.entrypoints.app:app

.PHONY: local-update-deps-base
local-update-deps-base: pyupgrade
	pip-compile ./backend/requirements.in
	# pip-compile --upgrade ./backend/requirements.in

.PHONY: local-update-deps-prod
local-update-deps-prod: local-update-deps-base
	pip-compile ./backend/requirements-prod.in
	# pip-compile --upgrade ./backend/requirements-prod.in

.PHONY: local-update-deps-dev
local-update-deps-dev: local-update-deps-base
	pip-compile ./backend/requirements-dev.in
	# pip-compile --upgrade ./backend/requirements-dev.in

.PHONY: local-install-deps-base
local-install-deps-base: local-update-deps-base
	pip install --no-cache-dir -r ./backend/requirements.txt

.PHONY: local-install-deps-dev
local-install-deps-dev: local-update-deps-dev local-install-deps-base
	pip install --no-cache-dir -r ./backend/requirements-dev.txt

.PHONY: local-install-deps-prod
local-install-deps-prod: local-update-deps-prod local-install-deps-base
	pip install --no-cache-dir -r ./backend/requirements-prod.txt

.PHONY: local-prepare-for-tests
local-prepare-for-tests: mypy local-clean-working-output-dir

.PHONY: local-prepare-for-tests-without-cleaning
local-prepare-for-tests-without-cleaning: mypy

.PHONY: local-clean-working-output-dir
local-clean-working-output-dir:
	find working/output/ -type f -name "*.html" -exec rm -- {} +
	find working/output/ -type f -name "*.pdf" -exec rm -- {} +

.PHONY: local-unit-tests
local-unit-tests:  local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest -n auto tests/unit/ -vv

.PHONY: local-e2e-tests
local-e2e-tests:  local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest -n auto tests/e2e/ -vv

.PHONY: local-repeat-randomized-tests
local-repeat-randomized-tests: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest -n auto --count 10 tests/e2e/ -k test_api_randomized_combinatoric.py

.PHONY: local-smoke-test-with-translation-words
local-smoke-test-with-translation-words: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_sr

.PHONY: local-smoke-test-with-translation-words2
local-smoke-test-with-translation-words2: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order_2c_sl_hr_c

.PHONY: local-smoke-test-with-translation-words3
local-smoke-test-with-translation-words3: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_book_language_order_2c_sl_hr

.PHONY: local-smoke-test-with-translation-words4
local-smoke-test-with-translation-words4: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_jon_en_tn_wa_jon_en_tq_wa_jon_en_tw_wa_jon_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order_2c_sl_hr_test


.PHONY: local-smoke-test-with-translation-words5
local-smoke-test-with-translation-words5: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_kbt_reg_2co_ajg_x_adjtalagbe_reg_2co_pmm_reg_mrk_language_book_order_2c_sl_hr_c

.PHONY: local-smoke-test-with-translation-words6
local-smoke-test-with-translation-words6: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_hr_c

.PHONY: local-smoke-test-with-translation-words7
local-smoke-test-with-translation-words7: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_layout_for_print

.PHONY: local-smoke-test-with-translation-words8
local-smoke-test-with-translation-words8: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_layout_not_for_print

.PHONY: local-smoke-test-with-translation-words9
local-smoke-test-with-translation-words9: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_random_non_english_fixtures

.PHONY: local-smoke-test-with-translation-words10
local-smoke-test-with-translation-words10: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_send_email_with_ar_nav_jud_pdf

.PHONY: local-smoke-test-with-translation-words11
local-smoke-test-with-translation-words11: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_stream_ar_nav_jud_pdf

.PHONY: local-smoke-test-with-translation-words12
local-smoke-test-with-translation-words12: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr

.PHONY: local-smoke-test-with-translation-words13
local-smoke-test-with-translation-words13: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_c

.PHONY: local-smoke-test-with-translation-words14
local-smoke-test-with-translation-words14: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_sw_ulb_col_sw_tn_col_sw_tq_col_sw_tw_col_sw_ulb_tit_sw_tn_tit_sw_tq_tit_sw_tw_tit_language_book_order_2c_sl_hr

.PHONY: local-smoke-test-with-translation-words15
local-smoke-test-with-translation-words15: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_api_randomized_combinatoric

.PHONY: local-smoke-test-with-translation-words16
local-smoke-test-with-translation-words16: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_en_bc_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_layout_for_print

.PHONY: local-smoke-test-with-translation-words17
local-smoke-test-with-translation-words17: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_en_bc_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_layout_not_for_print

.PHONY: local-smoke-test-with-translation-words18
local-smoke-test-with-translation-words18: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_document_requests

.PHONY: local-smoke-test-with-translation-words19
local-smoke-test-with-translation-words19: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_all_document_requests

.PHONY: local-smoke-test-with-translation-words20
local-smoke-test-with-translation-words20: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order_2c_sl_sr

.PHONY: local-smoke-test-with-translation-words21
local-smoke-test-with-translation-words21: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_hr_docx

.PHONY: local-smoke-test-with-translation-words22
local-smoke-test-with-translation-words22: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_epub

.PHONY: local-smoke-test-with-translation-words23
local-smoke-test-with-translation-words23: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_sr


.PHONY: local-smoke-test-with-translation-words24
local-smoke-test-with-translation-words24: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_tw_wa_col_en_bc_wa_col_book_language_order

.PHONY: local-smoke-test-with-translation-words25
local-smoke-test-with-translation-words25: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_pt_br_ulb_tn_en_ulb_wa_tn_wa_luk_language_book_order_2c_sl_hr

.PHONY: local-smoke-test-with-translation-words26
local-smoke-test-with-translation-words26: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_long_document_request_key

.PHONY: local-smoke-test-with-translation-words27
local-smoke-test-with-translation-words27: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_es_419_ulb_col_es_419_ulb_eph_es_419_tn_col_es_419_tq_col_es_419_tw_col_es_419_tw_eph_book_language_order


.PHONY: local-smoke-test-with-translation-words28
local-smoke-test-with-translation-words28: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_kbt_reg_2co_fr_ulb_2co_sl_sr

.PHONY: local-smoke-test-with-translation-words29
local-smoke-test-with-translation-words29: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_mat_language_book_order_1c


# This is one to run after running local-e2e-tests or any tests which
# has yielded HTML and PDFs that need to be checked for linking
# correctness.
.PHONY: local-check-anchor-links
local-check-anchor-links: checkvenv
	IN_CONTAINER=false python tests/e2e/test_anchor_linking.py
