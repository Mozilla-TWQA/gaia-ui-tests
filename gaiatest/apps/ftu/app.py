# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

from marionette.by import By

from gaiatest.apps.base import Base
from gaiatest.apps.base import PageRegion

class Ftu(Base):

    _activation_section_locator = (By.ID, 'activation')
    _main_title_locator = (By.ID, 'main_title')

    _next_button_locator = (By.ID, 'forward')

    # Step Languages section
    _section_languages_locator = (By.ID, 'languages')
    _listed_languages_locator = (By.CSS_SELECTOR, "#languages ul li input[name='language.current']")

    # Step Cell data section
    _section_cell_data_locator = (By.ID, 'data_3g')
    _enable_data_checkbox_locator = (By.CSS_SELECTOR, '#data_3g .pack-end')

    # Step Wifi
    _section_wifi_locator = (By.ID, 'wifi')
    _found_wifi_networks_locator = (By.CSS_SELECTOR, 'ul#networks-list li')
    _network_state_locator = (By.XPATH, 'p[2]')
    _password_input_locator = (By.ID, 'wifi_password')
    _join_network_locator = (By.ID, 'wifi-join-button')

    # Step Date & Time
    _section_date_time_locator = (By.ID, 'date_and_time')
    _timezone_continent_locator = (By.CSS_SELECTOR, '#time-form li:nth-child(1) > .change.icon.icon-dialog')
    _timezone_city_locator = (By.CSS_SELECTOR, '#time-form li:nth-child(2) > .change.icon.icon-dialog')
    _time_zone_title_locator = (By.ID, 'time-zone-title')

    # Step Geolocation
    _section_geolocation_locator = (By.ID, 'geolocation')

    # Section Import contacts
    _section_import_contacts_locator = (By.ID, 'import_contacts')
    _import_from_sim_locator = (By.ID, 'sim-import-button')
    _sim_import_feedback_locator = (By.CSS_SELECTOR, '.ftu p')

    # Section About Your rights
    _section_ayr_locator = (By.ID, 'about-your-rights')

    # Section Welcome Browser
    _section_welcome_browser_locator = (By.ID, 'welcome_browser')
    _enable_statistic_checkbox_locator = (By.ID, 'form_share_statistics')

    # Section Privacy Choices
    _section_browser_privacy_locator = (By.ID, 'browser_privacy')
    _email_field_locator = (By.CSS_SELECTOR, 'input[type="email"]')

    # Section Finish
    _section_finish_locator = (By.ID, 'finish-screen')
    _skip_tour_button_locator = (By.ID, 'skip-tutorial-button')
    _take_tour_button_locator = (By.ID, 'lets-go-button')

    # Section Tutorial Finish
    _section_tutorial_finish_locator = (By.ID, 'tutorialFinish')
    _lets_go_button_locator = (By.ID, 'tutorialFinished')

    # Pattern for import sim contacts message
    _pattern_contacts = re.compile("^No contacts detected on SIM to import$|^Imported one contact$|^Imported [0-9]+ contacts$")
    _pattern_contacts_0 = re.compile("^No contacts detected on SIM to import$")
    _pattern_contacts_1 = re.compile("^Imported one contact$")
    _pattern_contacts_N = re.compile("^Imported ([0-9]+) contacts$")

    ftu_frame = ('css selector', 'iframe[src*="ftu"][src*="/index.html"]')

    def create_language_locator(self, language):
        return (By.CSS_SELECTOR, "#languages ul li input[name='language.current'][value='%s'] ~ p" % language)

    def skip_tour(self):
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.marionette.find_element(*self.ftu_frame))

        self.wait_for_element_displayed(*self._section_languages_locator)

        listed_languages = self.marionette.find_elements(*self._listed_languages_locator)

        # select en-US due to the condition of this test is only for en-US
        language_item = self.marionette.find_element(*self.create_language_locator("en-US"))
        language_item.tap()

        # Tap next
        self.wait_for_element_displayed(*self._next_button_locator)
        self.marionette.find_element(*self._next_button_locator).tap()
        self.wait_for_element_displayed(*self._section_cell_data_locator)

        # Tap enable data
        self.marionette.find_element(*self._enable_data_checkbox_locator).tap()
        self.marionette.find_element(*self._next_button_locator).tap()

        # Go pass wifi section
        self.wait_for_element_displayed(*self._section_wifi_locator)
        self.wait_for_condition(lambda m: len(m.find_elements(*self._found_wifi_networks_locator)) > 0,
                                message="No networks listed on screen")
        self.marionette.find_element(*self._next_button_locator).tap()

        self.wait_for_element_displayed(*self._section_date_time_locator)
        continent_select = self.marionette.find_element(*self._timezone_continent_locator)
        continent_select.tap()
        self._select("Asia")

        self.wait_for_element_displayed(*self._section_date_time_locator)

        city_select = self.marionette.find_element(*self._timezone_city_locator)
        city_select.tap()
        self._select("Taipei")

        self.wait_for_element_displayed(*self._section_date_time_locator)
        self.marionette.find_element(*self._next_button_locator).tap()

        # Verify Geolocation section appears
        self.wait_for_element_displayed(*self._section_geolocation_locator)
        self.marionette.find_element(*self._next_button_locator).tap()

        # Verify contacts importing section appears
        self.wait_for_element_displayed(*self._section_import_contacts_locator)
        self.marionette.find_element(*self._next_button_locator).tap()

        # Verify welcome browser section appears
        self.wait_for_element_displayed(*self._section_welcome_browser_locator)
        self.marionette.find_element(*self._next_button_locator).tap()

        # Verify browser privacy section appears
        self.wait_for_element_displayed(*self._section_browser_privacy_locator)
        self.marionette.find_element(*self._email_field_locator).send_keys("testuser@mozilla.com")
        self.marionette.find_element(*self._next_button_locator).tap()

        # Skip the ftu
        self.wait_for_element_displayed(*self._section_finish_locator)
        self.marionette.find_element(*self._skip_tour_button_locator).tap()

        # Switch back to top level now that FTU app is gone
        self.marionette.switch_to_frame()

    def _select(self, match_string):
        # Cheeky Select wrapper until Marionette has its own
        # Due to the way B2G wraps the app's select box we match on text

        # Have to go back to top level to get the B2G select box wrapper
        self.marionette.switch_to_frame()

        options = self.marionette.find_elements(By.CSS_SELECTOR, '#value-selector-container li')
        close_button = self.marionette.find_element(By.CSS_SELECTOR, 'button.value-option-confirm')

        # Loop options until we find the match
        for li in options:
            if li.text == match_string:
                li.tap()
                break

        close_button.tap()

        # Now back to app
        self.marionette.switch_to_frame(self.marionette.find_element(*self.ftu_frame))
