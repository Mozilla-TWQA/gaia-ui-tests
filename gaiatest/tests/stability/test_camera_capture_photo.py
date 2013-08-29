# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from gaiatest import GaiaTestCase
from gaiatest.apps.camera.app import Camera

class TestCamera(GaiaTestCase):

    def setUp(self):
        GaiaTestCase.setUp(self)

    def test_capture_a_photo(self):
        self.marionette.switch_to_frame()
        self.marionette.switch_to_frame(self.marionette.find_element('css selector', 'iframe[src*="camera"][src*="/index.html"]'))

        self.camera = Camera(self.marionette)
        self.camera.wait_for_camera_ready()
        self.camera.take_photo()

        if not self.camera.is_filmstrip_visible:
            self.camera.tap_to_display_filmstrip()

        image_preview = self.camera.filmstrip_images[0].tap()
        self.assertTrue(image_preview.is_image_preview_visible)
        image_preview.tap_camera()
