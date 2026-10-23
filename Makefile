PYTHON = python3
MAIN = pac-man

.PHONY: install run debug clean lint lint-strict

install:
	uv sync

run:
	uv run python -m $(MAIN) config.json

debug:
	$(PYTHON) -m pdb $(MAIN)

clean:
	rm -rf .venv __pycache__ .mypy_cache src/__pycache__

lint:
	uv run flake8 src
	uv run mypy src
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
