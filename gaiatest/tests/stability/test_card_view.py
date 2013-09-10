# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from random import randrange

class TestCardview(GaiaTestCase):
    app = ['Camera', 'Gallery', 'FM Radio', "Settings", "Marketplace", "Clock", "Calendar", "Usage", "Music", "Video"]
    selection = 0

    def setUp(self):
        self.selection = randrange(0, len(self.app)+1)
        GaiaTestCase.setUp(self, self.app[self.selection])

    def test_cardview(self):
        self.marionette.switch_to_frame()
        self.marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('holdhome'));")

        self.assertEqual(self.app[self.selection], self.marionette.find_elements('css selector', '#cards-view li.card')[0].text)

        card_view_apps = self.marionette.find_elements('css selector', '#cards-view li')
        len_apps = len(card_view_apps)
        
        self.wait_for_element_displayed('css selector', '#cards-view li[data-origin*="%s"] .close-card' % self.app[self.selection].lower())
        self.marionette.find_element('css selector', '#cards-view li[data-origin*="%s"] .close-card' % self.app[self.selection].lower()).tap()
        self.wait_for_element_not_displayed('css selector', '#cards-view li[data-origin*="%s"]' % self.app[self.selection].lower())

        self.marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('home'));")
        self.wait_for_element_not_displayed("id", "cards-view")
        self.marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('holdhome'));")
        self.wait_for_element_displayed("id", "cards-view")

        self.assertEqual(len_apps-1, len(self.marionette.find_elements('css selector', '#cards-view li')))
