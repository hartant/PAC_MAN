

UV := $(shell command -v uv 2>/dev/null || echo "python3 -m uv")

install:
	@command -v uv >/dev/null 2>&1 || python3 -m pip install --user uv
	$(UV) sync

run:
	$(UV) run python pac-man.py config.json

debug:
	$(UV) run python -m pdb pac-man.py config.json

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist

lint:
	$(UV) run flake8 . --exclude .venv,venv,build,dist
	$(UV) run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs --exclude '(build|dist|venv|\.venv)/'

.PHONY: install run debug clean lint
