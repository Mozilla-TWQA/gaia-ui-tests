# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette.by import By
from gaiatest import GaiaTestCase

MANIFEST = 'http://mozqa.com/data/webapps/mozqa.com/manifest.webapp'
APP_NAME = 'Mozilla QA WebRT Tester'
TITLE = 'Index of /data'


class TestLaunchApp(GaiaTestCase):
    _installed_app_locator = (By.CSS_SELECTOR, 'li.icon[aria-label="%s"]' % APP_NAME)

    # locator for li.icon, because click on label doesn't work.
    _visible_icon_locator = (By.CSS_SELECTOR, 'div.page[style*="transform: translateX(0px);"] li.icon[aria-label="%s"]' % APP_NAME)
    _app_locator = (By.CSS_SELECTOR, 'iframe[src="http://mozqa.com/data"]')
    _header_locator = (By.CSS_SELECTOR, 'h1')

    def setUp(self):
        GaiaTestCase.setUp(self)

        while self._homescreen_has_more_pages():
            self._go_to_next_page()
            if self.is_element_present(*self._visible_icon_locator):
                break
        self.marionette.find_element(*self._visible_icon_locator).tap()

    def _go_to_next_page(self):
        self.marionette.execute_script('window.wrappedJSObject.GridManager.goToNextPage()')
        self.wait_for_condition(lambda m: m.find_element('tag name', 'body')
            .get_attribute('data-transitioning') != 'true')

    def _homescreen_has_more_pages(self):
        # the naming of this could be more concise when it's in an app object!
        return self.marionette.execute_script("""
            var pageHelper = window.wrappedJSObject.GridManager.pageHelper;
            return pageHelper.getCurrentPageNumber() < (pageHelper.getTotalPagesNumber() - 1);""")

    def tearDown(self):
        GaiaTestCase.tearDown(self)
