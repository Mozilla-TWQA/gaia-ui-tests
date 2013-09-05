# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.fmradio.app import FmRadio


class TestFMRadioTurnOnOff(GaiaTestCase):

    def setUp(self):
        GaiaTestCase.setUp(self, "FM Radio")

    def test_turn_radio_on_off(self):
        """ Turn off and then Turn on the radio

        https://moztrap.mozilla.org/manage/case/1930/
        https://moztrap.mozilla.org/manage/case/1931/

        """
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.marionette.find_element('css selector', 'iframe[src*="fm"][src*="/index.html"]'))
        self.fm_radio = FmRadio(self.marionette)

        self.wait_for_condition(lambda m: self.is_fm_radio_enabled)

        # check the headphone is plugged-in or not
        self.assertTrue(self.is_antenna_available, 'Antenna (headphones) not plugged in')

        # wait for the radio start-up
        self.wait_for_condition(lambda m: self.is_fm_radio_enabled)

        # turn the radio off
        self.fm_radio.tap_power_button()

        # check the radio is off
        self.fm_radio.wait_for_radio_off()

        self.assertFalse(self.is_fm_radio_enabled)

        # turn the radio on
        self.fm_radio.tap_power_button()
        self.wait_for_condition(lambda m: self.is_fm_radio_enabled)

        # check the radio is on
        self.assertTrue(self.fm_radio.is_power_button_on)
        self.assertTrue(self.is_fm_radio_enabled)

    @property
    def is_antenna_available(self):
        return self.marionette.execute_script('return window.navigator.mozFMRadio.antennaAvailable')

    @property
    def is_fm_radio_enabled(self):
        return self.marionette.execute_script('return window.navigator.mozFMRadio.enabled')

    def tearDown(self):
        GaiaTestCase.tearDown(self)
