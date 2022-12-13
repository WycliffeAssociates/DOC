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
build: checkvenv clean-mypyc-artifacts local-install-deps-prod
	export IMAGE_TAG=local && \
	docker build --progress=plain -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build --progress=plain -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend


.PHONY: build-no-pip-update
build-no-pip-update: checkvenv clean-mypyc-artifacts
	export IMAGE_TAG=local && \
	docker build --progress=plain -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build --progress=plain -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend

.PHONY: build-no-pip-update-run-tests
build-no-pip-update-run-tests: checkvenv clean-mypyc-artifacts
	export IMAGE_TAG=local && \
	docker build --build-arg RUN_TESTS=true --progress=plain -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build --progress=plain -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend

.PHONY: build-no-cache
build-no-cache: checkvenv clean-mypyc-artifacts local-install-deps-prod
	export IMAGE_TAG=local && \
	docker build --progress=plain --no-cache -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build --progress=plain --no-cache -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend

.PHONY: build-no-cache-no-pip-update
build-no-cache-no-pip-update: checkvenv clean-mypyc-artifacts
	export IMAGE_TAG=local && \
	docker build --progress=plain --no-cache -t wycliffeassociates/doc:$${IMAGE_TAG} . && \
	docker build --progress=plain --no-cache -t wycliffeassociates/doc-ui:$${IMAGE_TAG} ./frontend

.PHONY: up
up: checkvenv
	export IMAGE_TAG=local && \
	BACKEND_API_URL=http://localhost:5005 docker-compose up

.PHONY: up-as-daemon
up-as-daemon: checkvenv
	export IMAGE_TAG=local && \
	BACKEND_API_URL=http://localhost:5005 docker-compose up -d


# This is the entrypoint for a non-technical user who just
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

.PHONY: list-pytest-markers
list-pytest-markers:
	pytest --strict-markers

.PHONY: clean-local-docker-output-dir
clean-local-docker-output-dir:
	find docker_document_output/ -type f -name "*.pdf" -exec rm -- {} +
	find docker_document_output/ -type f -name "*.epub" -exec rm -- {} +
	find docker_document_output/ -type f -name "*.docx" -exec rm -- {} +

.PHONY: test
test: up-as-daemon
	BACKEND_API_URL=http://localhost:5005 docker-compose run --rm --no-deps --entrypoint=pytest api -v -m "not randomized" -n auto /app/tests/unit /app/tests/e2e

.PHONY: unit-tests
unit-tests: up-as-daemon
	BACKEND_API_URL=http://localhost:5005 docker-compose run --rm --no-deps --entrypoint=pytest api -v -m "not randomized" -n auto /app/tests/unit

.PHONY: e2e-tests
e2e-tests: up-as-daemon clean-local-docker-output-dir
	BACKEND_API_URL=http://localhost:5005 docker-compose run --rm --no-deps --entrypoint=pytest api -v -m "not randomized" -n auto /app/tests/e2e

.PHONY: frontend-tests
frontend-tests: up-as-daemon
	cd frontend && FRONTEND_API_URL=http://localhost:8001 envsubst < playwright.config.ts | sponge playwright.config.ts
	cd frontend && npx playwright install --with-deps && npx playwright test

.PHONY: smoke-test-with-translation-words
smoke-test-with-translation-words: up-as-daemon clean-local-docker-output-dir
	BACKEND_API_URL="http://localhost:5005" docker-compose run --rm --no-deps --entrypoint=pytest api /app/tests/e2e -k test_stream_pdf

.PHONY: get-usfm-tools-source-locally
get-usfm-tools-source-locally:
	# In Docker we build usfm_tools package into a .so, but outside
	# Docker we need the source to let mypy check it locally, i.e., when
	# checking outside Docker build.
	cd /tmp && \
	git clone -b develop --depth 1 https://github.com/linearcombination/USFM-Tools  && \
	cd ./USFM-Tools && \
	cp -r ./usfm_tools ${VIRTUAL_ENV}/lib/python3.11/site-packages/
.PHONY: test-randomized
test-randomized: up-as-daemon
	BACKEND_API_URL=http://localhost:5005 docker-compose run --rm --no-deps --entrypoint=pytest api -v -m randomized -n auto /app/tests/unit /app/tests/e2e

.PHONY: build-usfm-tools
build-usfm-tools:
	cd /tmp && \
	git clone -b develop --depth 1 https://github.com/linearcombination/USFM-Tools
	cd /tmp/USFM-Tools && python setup.py build install
	cp -r /tmp/USFM-Tools/usfm_tools ~/src/WA/github.com/linearcombination/DOC/.venv/lib/python3.11/site-packages/
	rm -rf /tmp/USFM-Tools

# You may need to run 'make get-usfm-tools-source-locally' first if it
# complains about usfm_tools not being typed.
.PHONY: mypy
mypy: checkvenv
	mypy --strict --install-types --non-interactive backend/document/**/*.py
	mypy --strict --install-types --non-interactive tests/**/*.py

.PHONY: mypyc
mypyc:
	mypyc --strict --install-types --non-interactive backend/document/domain/document_generator.py backend/document/domain/resource_lookup.py backend/document/domain/assembly_strategies.py backend/document/domain/parsing.py backend/document/domain/worker.py backend/document/entrypoints/app.py


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
	BACKEND_API_URL=http://localhost:5005 uvicorn document.entrypoints.app:app --reload --host "0.0.0.0" --port "5005" --app-dir "./backend/"

# Run a local Gunicorn server outside Docker
.PHONY: local-gunicorn-server
local-gunicorn-server: checkvenv
	exec gunicorn --name DOC --worker-class uvicorn.workers.UvicornWorker --conf ./backend/gunicorn.conf.py --pythonpath ./backend  document.entrypoints.app:app

.PHONY: local-update-deps-base
local-update-deps-base: pyupgrade
	pip-compile --resolver=backtracking -v ./backend/requirements.in
	# pip-compile --upgrade ./backend/requirements.in

.PHONY: local-update-deps-prod
local-update-deps-prod: local-update-deps-base
	pip-compile --resolver=backtracking -v ./backend/requirements-prod.in
	# pip-compile --upgrade ./backend/requirements-prod.in

.PHONY: local-update-deps-dev
local-update-deps-dev: local-update-deps-base
	pip-compile --resolver=backtracking -v ./backend/requirements-dev.in
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
	TO_EMAIL="foo@example.com" pytest -n auto tests/unit/ -vv

.PHONY: local-e2e-tests
local-e2e-tests:  local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest -n auto tests/e2e/ -vv

.PHONY: local-repeat-randomized-tests
local-repeat-randomized-tests: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest -n auto --count 10 tests/e2e/ -k test_api_randomized_combinatoric.py

.PHONY: local-smoke-test-with-translation-words
local-smoke-test-with-translation-words: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_sr

.PHONY: local-smoke-test-with-translation-words8
local-smoke-test-with-translation-words8: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_layout_not_for_print

.PHONY: local-smoke-test-with-translation-words9
local-smoke-test-with-translation-words9: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_random_non_english_fixtures

.PHONY: local-smoke-test-with-translation-words10
local-smoke-test-with-translation-words10: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_send_email_with_ar_nav_jud_pdf

.PHONY: local-smoke-test-with-translation-words11
local-smoke-test-with-translation-words11: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_stream_ar_nav_jud_pdf

.PHONY: local-smoke-test-with-translation-words12
local-smoke-test-with-translation-words12: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr

.PHONY: local-smoke-test-with-translation-words13
local-smoke-test-with-translation-words13: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_c

.PHONY: local-smoke-test-with-translation-words20
local-smoke-test-with-translation-words20: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_sw_ulb_col_sw_tn_col_sw_ulb_tit_sw_tn_tit_book_language_order_2c_sl_sr

.PHONY: local-smoke-test-with-translation-words22
local-smoke-test-with-translation-words22: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order_2c_sl_sr_epub

.PHONY: local-smoke-test-with-translation-words23
local-smoke-test-with-translation-words23: local-prepare-for-tests
	TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_fr_f10_col_fr_tn_col_fr_tq_col_fr_tw_col_book_language_order_2c_sl_sr

# This is one to run after running local-e2e-tests or any tests which
# has yielded HTML and PDFs that need to be checked for linking
# correctness.
.PHONY: local-check-anchor-links
local-check-anchor-links: checkvenv
	python tests/e2e/test_anchor_linking.py
