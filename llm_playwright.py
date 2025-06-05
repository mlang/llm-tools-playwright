import llm
from playwright.sync_api import sync_playwright
from pydantic import HttpUrl


playwright = sync_playwright().start()


class Browser(llm.Toolbox):
    _browser = None
    def _get_browser(self):
        if self._browser is None:
            self._browser = getattr(playwright, self._browser_name).launch(headless=True)
        return self._browser

    _context = None
    def _get_context(self):
        if self._context is None:
            self._context = self._get_browser().new_context()
        return self._context

    _page = None
    def _get_page(self):
        if self._page is None:
            self._page = self._get_context().new_page()
        return self._page

    def goto(self, url: HttpUrl, full_page: bool = True):
        page = self._get_page()
        response = page.goto(url)
        image = page.screenshot(type="jpeg", full_page=full_page)
        screenshot = llm.Attachment(content=image, type="image/jpeg")
        return llm.ToolOutput(output=repr(response), attachments=[screenshot])


class Firefox(Browser):
    _browser_name = "firefox"


@llm.hookimpl
def register_tools(register):
    register(Firefox)
