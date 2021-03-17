VENV_DIR = .ve
VENV_RUN = . $(VENV_DIR)/bin/activate

install:
	./bin/install.sh

tests:
	($(VENV_RUN); ./bin/unit-test.sh $(filter-out $@,$(MAKECMDGOALS)))

format:
	($(VENV_RUN); autopep8 -r atl_observe/ --in-place)
	($(VENV_RUN); autopep8 -r test/ --in-place)
	($(VENV_RUN); isort atl_observe/)
	($(VENV_RUN); isort test/)

lint:
	($(VENV_RUN); ./bin/lint.sh)

compile:
	python -m venv .ve --prompt="(compile)"
	($(VENV_RUN); pip install --upgrade setuptools)
	($(VENV_RUN); pip install --upgrade wheel)
	($(VENV_RUN); pip install --upgrade pip-compile-multi)
	($(VENV_RUN); pip install --upgrade pip-tools)
	# will look for requirements/requirements.in file to compile packages (.txt)
	($(VENV_RUN); pip-compile-multi)
