#!/usr/bin/env python3
"""Wrap prototype/bo.html (artifact-format: no <html>/<head>) into a
standalone, installable page at the repo root for GitHub Pages."""
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
body = (root / "prototype" / "bo.html").read_text()

# the artifact head-tags live at the top of bo.html; lift them into a real <head>
head_tags = []
for pat in (r'<title>.*?</title>', r'<link [^>]*>'):
    for m in re.findall(pat, body, re.S):
        head_tags.append(m)
        body = body.replace(m, "", 1)
body = body.lstrip("\n")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<meta name="description" content="Feel prototype for a toddler play companion.">
<meta name="theme-color" content="#16181D">
<meta name="color-scheme" content="dark">
<!-- launches fullscreen with no URL bar once added to the home screen -->
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Bo">
<link rel="apple-touch-icon" href="icons/bo-180.png">
<link rel="icon" type="image/png" sizes="512x512" href="icons/bo-512.png">
<link rel="manifest" href="manifest.webmanifest">
%s
<style>
  html { background: #16181D; color-scheme: dark; }
  body { margin: 0; font: 14px system-ui, sans-serif; }
  img { max-width: 100%%; }
  [hidden] { display: none !important; }
  /* keep content clear of the notch and home indicator */
  #start { padding-top: max(28px, env(safe-area-inset-top)) !important;
           padding-bottom: max(28px, env(safe-area-inset-bottom)) !important; }
  #panel { padding-top: max(24px, env(safe-area-inset-top)) !important;
           padding-bottom: max(24px, env(safe-area-inset-bottom)) !important; }
</style>
</head>
<body>
""" % "\n".join(head_tags)

(root / "index.html").write_text(HEAD + body + "\n</body>\n</html>\n")
print("wrote index.html (%d bytes)" % (root / "index.html").stat().st_size)
