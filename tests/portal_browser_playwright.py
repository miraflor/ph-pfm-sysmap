"""Optional real-Chromium smoke check (not required by the standard-library build).

Run from the repository root after building:
  python tests/portal_browser_playwright.py

Requires Playwright's Python package and an installed Chromium binary, or run
`python -m playwright install chromium` for its managed browser. No network is used by the site.
"""
from __future__ import annotations

from pathlib import Path
import shutil
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('Playwright unavailable: install playwright, then install its Chromium browser.', file=sys.stderr)
        return 2
    # Serve docs/ over local HTTP. file:// origins can prohibit iframe access, and
    # some managed Chromium configurations block file URLs altogether.
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(DOCS)))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f'http://127.0.0.1:{server.server_port}/index.html'
    failures = []
    try:
        return run_browser(sync_playwright, url, failures)
    finally:
        server.shutdown()
        server.server_close()


def run_browser(sync_playwright, url, failures):
    with sync_playwright() as p:
        executable = (shutil.which('chromium') or shutil.which('chromium-browser') or
                      shutil.which('google-chrome'))
        browser = p.chromium.launch(headless=True, executable_path=executable, args=['--no-sandbox'])
        try:
            for width, height in ((1400, 900), (390, 844)):
                page = browser.new_page(viewport={'width': width, 'height': height})
                page.on('pageerror', lambda error: failures.append(str(error)))
                page.goto(url)
                for theme in ('light', 'dark'):
                    root_theme = page.evaluate('document.documentElement.dataset.theme || "light"')
                    if root_theme != theme:
                        page.locator('#theme').click()
                    for view in ('overview', 'processes', 'models', 'records', 'evidence', 'methods'):
                        page.locator(f'.nav button[data-view="{view}"]').click()
                        page.wait_for_function('(v) => location.hash.includes("view=" + v)', arg=view)
                        overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth + 2')
                        if overflow:
                            failures.append(f'{width}px {theme} {view}: horizontal page overflow')
                    # Check the concrete record view, deep link and source back-references.
                    page.goto(url + '#view=records&id=R-NCA')
                    page.get_by_text('Petri-net places and modelled holders').wait_for()
                    page.goto(url + '#view=evidence&id=source:GK')
                    page.get_by_text('Cited by').wait_for()
                page.close()
            # The old hash routes are still supported.
            page = browser.new_page()
            page.goto(url + '#nets')
            page.wait_for_url('**/visualizer.html#nets')
            page.close()
        finally:
            browser.close()
    if failures:
        for e in failures:
            print('FAIL:', e, file=sys.stderr)
        return 1
    print('PASS: real Chromium desktop and mobile, themes, navigation, records, evidence and legacy redirect')
    return 0


if __name__ == '__main__':
    sys.exit(main())
