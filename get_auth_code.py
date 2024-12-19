#!/usr/bin/python3

# please install dependencies with
# ```
# pip install pytest-playwright
# playwright install
# ```
# copy auth.ini.template to auth.ini
# and set your username and password for PSA there

import re
import sys
from playwright.sync_api import Playwright, sync_playwright, expect
from urllib.parse import urlparse, parse_qs, unquote
import configparser

redirect_url=input("Please copy and paste the redirect URL: ")

parsed_url = urlparse(redirect_url)

if parsed_url.netloc != "idpcvs.peugeot.com":
    print("Decoded URL does not match idpcvs.peugeot.com")
    sys.exit(1)

auth = configparser.ConfigParser()
auth.read('auth.ini')
username=auth['psa']['username']
password=auth['psa']['password']

def handle_request(request):
    url = request.url
    if url.startswith("mymap://oauth2redirect/"):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        code = query_params.get("code", [None])[0]
        print("Authorization code captured:", code)
        # capture and use the code to continue to OTP

def run(playwright: Playwright, redirect_url, username, password) -> None:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    page.on("request", handle_request)

    page.goto(redirect_url)
    page.get_by_placeholder("E-mail *").fill(username)
    page.get_by_placeholder("Mot de passe *").fill(password)
    page.get_by_role("button", name="Envoyer").click()
    page.get_by_role("button", name="OK").click()

    # Wait until the redirect is expected to occur
    page.wait_for_timeout(10000)

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright, redirect_url, username, password)
