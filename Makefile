PYTHON  = python3
PIP     = $(PYTHON) -m pip

MAZE_WHL = $(wildcard mazegenerator-*.whl)

install:
	$(PIP) install pygame flake8 mypy pytest pyinstaller
	$(PIP) install --force-reinstall $(MAZE_WHL)

run:
	$(PYTHON) pac-man.py config.json

debug:
	$(PYTHON) -m pdb pac-man.py config.json

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist

lint:
	flake8 . --exclude .venv,venv,build,dist
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs --exclude '(build|dist|venv|\.venv)/'

.PHONY: install run debug clean lint