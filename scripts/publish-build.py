#!/usr/bin/env python3
"""Inject the API key into prototype/bo.html for the private artifact build.

Reads the key from prototype/key.local (gitignored). Run --restore afterwards
to put the placeholder back before committing.
"""
import pathlib, sys

root = pathlib.Path(__file__).resolve().parent.parent
src = root / "prototype" / "bo.html"
keyfile = root / "prototype" / "key.local"
PLACEHOLDER = "__BO_API_KEY__"

text = src.read_text()
if "--restore" in sys.argv:
    import re
    text = re.sub(r'var BAKED_KEY = "[^"]*";',
                  'var BAKED_KEY = "%s";' % PLACEHOLDER, text)
    src.write_text(text)
    print("restored placeholder")
else:
    if not keyfile.exists():
        sys.exit("prototype/key.local not found")
    key = keyfile.read_text().strip()
    if PLACEHOLDER not in text:
        sys.exit("placeholder already replaced - run --restore first")
    src.write_text(text.replace(PLACEHOLDER, key))
    print("injected key (%d chars)" % len(key))
