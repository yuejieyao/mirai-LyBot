from playwright.sync_api import sync_playwright

path_to_extension = "modules/resource/chrome_extension"
user_data_dir = "modules/resource/chrome_user_data"


def getScreenshot(url: str, path: str):
    with sync_playwright() as p:
        bowser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=True,
            args=[
                f"--disable-extensions-except={path_to_extension}",
                f"--load-extension={path_to_extension}",
            ],
        )
        page = bowser.new_page()
        page.goto(url, wait_until='load', timeout=10000)
        page.set_viewport_size({'width': 1600, 'height': 2000})
        card = page.query_selector(".shiyi_content")
        assert card is not None
        card.screenshot(path=path)
