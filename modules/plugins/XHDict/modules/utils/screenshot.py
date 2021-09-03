import base64
from playwright.sync_api import sync_playwright


def getScreenshot(url: str, path: str):
    with sync_playwright() as p:
        bowser_type = p.chromium
        bowser = bowser_type.launch()
        page = bowser.new_page()
        page.goto(url, wait_until='load', timeout=10000)
        page.set_viewport_size({'width': 1600, 'height': 2000})
        card = page.query_selector(".shiyi_content")
        assert card is not None
        card.screenshot(path=path)
        bowser.close()
