VENV_DIR = .ve
VENV_RUN = . $(VENV_DIR)/bin/activate


install:
	./bin/install.sh

tests:
	($(VENV_RUN); ./bin/unit-test.sh $(filter-out $@,$(MAKECMDGOALS)))

format:
	($(VENV_RUN); autopep8 -r observe/ --in-place)
	($(VENV_RUN); autopep8 -r test/ --in-place)
	($(VENV_RUN); isort observe/)
	($(VENV_RUN); isort test/)

lint:
	($(VENV_RUN); ./bin/lint.sh)
