"""Playwright as an LLM tool"""

import atexit
import yaml

import llm
from playwright.sync_api import sync_playwright
from pydantic import HttpUrl


playwright = sync_playwright().start()
atexit.register(playwright.stop)


class Browser(llm.Toolbox):
    def __init__(self, browser: str = "firefox"):
        self._browser_name = browser
        self._page = None
        self._context = None
        self._browser = None


    def _get_page(self):
        if self._page is None:
            if self._context is None:
                if self._browser is None:
                    self._browser = getattr(playwright, self._browser_name).launch(headless=True)
                self._context = self._browser.new_context()
            self._page = self._context.new_page()
        return self._page


    def _screenshot(self, full_page: bool = True):
        image = self._get_page().screenshot(type="jpeg", full_page=full_page)
        return llm.Attachment(content=image, type="image/jpeg")


    def goto(self, url: HttpUrl):
        response = self._get_page().goto(url)
        return llm.ToolOutput(output=repr(response), attachments=[self._screenshot()])


    def screenshot(self, full_page: bool = True):
        return llm.ToolOutput(attachments=[self._screenshot(full_page)])


    def aria_snapshot(self, selector: str = "HTML"):
        """The accessibility tree of the current page."""

        snapshot = self._get_page().locator(selector).aria_snapshot(ref=True)
        return yaml.safe_load(snapshot)


@llm.hookimpl
def register_tools(register):
    register(Browser)
