from contextlib import asynccontextmanager

import pyppeteer

CHROME_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2)"
    + " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
)
DEFAULT_VIEWPORT = {"width": 1280, "height": 800, "isMobile": False}


@asynccontextmanager
async def with_page() -> pyppeteer.page.Page:
    browser = await pyppeteer.launch(headless=True)
    try:
        page = await browser.newPage()
        await page.setUserAgent(CHROME_AGENT)
        await page.setViewport(DEFAULT_VIEWPORT)
        yield page
    finally:
        await browser.close()
