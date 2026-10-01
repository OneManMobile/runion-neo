# Runion Neo — build, proof and test
PY = .venv/bin/python

help:
	@echo "make build   glyphs.txt -> UFO -> fonts/ttf + fonts/webfonts + playground data"
	@echo "make proof   contact sheet and documentation images"
	@echo "make test    fontbakery, Google Fonts profile"
	@echo "make serve   open the playground on http://localhost:8417"

venv:
	python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

build:
	$(PY) sources/build.py

proof: build
	$(PY) sources/sheet.py
	$(PY) sources/proof.py

test: build
	fontbakery check-googlefonts fonts/ttf/*.ttf -l WARN --succinct --ghmarkdown out/fontbakery.md

serve:
	python3 -m http.server 8417 --bind 127.0.0.1

.PHONY: help venv build proof test serve
