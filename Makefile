# Pac-Man - usage: make <rule>

install:
	pip install pygame flake8 mypy pytest pyinstaller

run:
	python3 pac-man.py config.json

debug:
	python3 -m pdb pac-man.py config.json

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist *.spec

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict --ignore-missing-imports

test:
	python3 -m pytest src/tests

# standalone game for Itch.io: dist/pac-man/ (run the file "pac-man")
package:
	pyinstaller --noconfirm --onedir --name pac-man --exclude-module numpy pac-man.py
	cp config.json README.md dist/pac-man/

.PHONY: install run debug clean lint lint-strict test package
