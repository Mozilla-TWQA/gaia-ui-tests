# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from marionette.by import By
from gaiatest.apps.base import Base


class Homescreen(Base):

    name = 'Homescreen'

    _homescreen_iframe_locator = (By.CSS_SELECTOR, 'div.homescreen iframe')
    _homescreen_icon_locator = (By.CSS_SELECTOR, 'li.icon[aria-label="%s"]')
    _search_bar_icon_locator = (By.ID, 'evme-activation-icon')

    def launch(self):
        self.marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('home'));")

    def switch_to_homescreen_frame(self):
        self.marionette.switch_to_frame()
        hs_frame = self.marionette.find_element(*self._homescreen_iframe_locator)
        self.marionette.switch_to_frame(hs_frame)

    def tap_search_bar(self):
        search_bar = self.marionette.find_element(*self._search_bar_icon_locator)
        search_bar.tap()
        from gaiatest.apps.homescreen.regions.search_panel import SearchPanel
        return SearchPanel(self.marionette)

    def launch_app(self, app_name):
        self.marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('home'));")
        launched = False
        while self.homescreen_has_more_pages:
            if self.is_element_displayed(self._homescreen_icon_locator[0], self._homescreen_icon_locator[1] % app_name):
                self.marionette.find_element(self._homescreen_icon_locator[0], self._homescreen_icon_locator[1] % app_name).tap()
                launched = True
                break
            self.go_to_next_page()
        while self.homescreen_has_previous_pages and not launched:
            if self.is_element_displayed(self._homescreen_icon_locator[0], self._homescreen_icon_locator[1] % app_name):
                self.marionette.find_element(self._homescreen_icon_locator[0], self._homescreen_icon_locator[1] % app_name).tap()
                break
            self.go_to_previous_page()

    def go_to_next_page(self):
        self.marionette.execute_script('window.wrappedJSObject.GridManager.goToNextPage()')

    def go_to_previous_page(self):
        self.marionette.execute_script('window.wrappedJSObject.GridManager.goToPreviousPage()')

    @property
    def homescreen_has_more_pages(self):
        # the naming of this could be more concise when it's in an app object!
        return self.marionette.execute_script("""
        var pageHelper = window.wrappedJSObject.GridManager.pageHelper;
        return pageHelper.getCurrentPageNumber() < (pageHelper.getTotalPagesNumber() - 1);""")

    @property
    def homescreen_has_previous_pages(self):
        # the naming of this could be more concise when it's in an app object!
        return self.marionette.execute_script("""
        var pageHelper = window.wrappedJSObject.GridManager.pageHelper;
        return pageHelper.getCurrentPageNumber() != 0;""")
