# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import base64
import json
import os
import sys
import time
import traceback

from marionette import MarionetteTestCase
from marionette import Marionette
from marionette.by import By
from marionette.errors import NoSuchElementException
from marionette.errors import ElementNotVisibleException
from marionette.errors import TimeoutException
from marionette.errors import StaleElementException
from marionette.errors import InvalidResponseException
import mozdevice


class LockScreen(object):

    def __init__(self, marionette):
        self.marionette = marionette

    @property
    def is_locked(self):
        self.marionette.switch_to_frame()
        return self.marionette.execute_script('window.wrappedJSObject.LockScreen.locked')

    def unlock(self):
        #TODO: need to make this UI interaction to pass the steps
        self.marionette.switch_to_frame()
        result = self.marionette.execute_async_script('GaiaLockScreen.unlock()')
        assert result, 'Unable to unlock screen'


class GaiaApp(object):

    def __init__(self, origin=None, name=None, frame=None, src=None):
        self.frame = frame
        self.frame_id = frame
        self.src = src
        self.name = name
        self.origin = origin

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class GaiaApps(object):

    def __init__(self, marionette):
        self.marionette = marionette

    def switch_to_frame(self, app_frame, url=None, timeout=30):
        self.marionette.switch_to_frame(app_frame)
        start = time.time()
        if not url:
            def check(now):
                return "about:blank" not in now
        else:
            def check(now):
                return url in now
        while (time.time() - start < timeout):
            if check(self.marionette.get_url()):
                return
            time.sleep(2)
        raise TimeoutException('Could not switch to app frame %s in time' % app_frame)


class GaiaDevice(object):

    def __init__(self, marionette, testvars=None):
        self.marionette = marionette
        self.testvars = testvars or {}

    @property
    def manager(self):
        if hasattr(self, '_manager') and self._manager:
            return self._manager

        if not self.is_android_build:
            raise Exception('Device manager is only available for devices.')

        dm_type = os.environ.get('DM_TRANS', 'adb')
        if dm_type == 'adb':
            self._manager = mozdevice.DeviceManagerADB()
        elif dm_type == 'sut':
            host = os.environ.get('TEST_DEVICE')
            if not host:
                raise Exception('Must specify host with SUT!')
            self._manager = mozdevice.DeviceManagerSUT(host=host)
        else:
            raise Exception('Unknown device manager type: %s' % dm_type)
        return self._manager

    @property
    def is_android_build(self):
        if self.testvars.get('is_android_build') is None:
            self.testvars['is_android_build'] = 'Android' in self.marionette.session_capabilities['platform']
        return self.testvars['is_android_build']

    @property
    def is_online(self):
        # Returns true if the device has a network connection established (cell data, wifi, etc)
        return self.marionette.execute_script('return window.navigator.onLine;')

    @property
    def has_mobile_connection(self):
        return self.marionette.execute_script('return window.navigator.mozMobileConnection !== undefined')

    @property
    def has_wifi(self):
        if not hasattr(self, '_has_wifi'):
            self._has_wifi = self.marionette.execute_script('return window.navigator.mozWifiManager !== undefined')
        return self._has_wifi

    def push_file(self, source, count=1, destination='', progress=None):
        if not destination.count('.') > 0:
            destination = '/'.join([destination, source.rpartition(os.path.sep)[-1]])
        self.manager.mkDirs(destination)
        self.manager.pushFile(source, destination)

        if count > 1:
            for i in range(1, count + 1):
                remote_copy = '_%s.'.join(iter(destination.split('.'))) % i
                self.manager._checkCmd(['shell', 'dd', 'if=%s' % destination, 'of=%s' % remote_copy])
                if progress:
                    progress.update(i)

            self.manager.removeFile(destination)

class GaiaTestCase(MarionetteTestCase):
    tests = []

    _script_timeout = 60000
    _search_timeout = 10000

    # deafult timeout in seconds for the wait_for methods
    _default_timeout = 30

    def __init__(self, *args, **kwargs):
        self.restart = kwargs.pop('restart', False)
        MarionetteTestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        MarionetteTestCase.setUp(self)

        self.device = GaiaDevice(self.marionette, self.testvars)

        # the emulator can be really slow!
        self.marionette.set_script_timeout(self._script_timeout)
        self.marionette.set_search_timeout(self._search_timeout)
        self.lockscreen = LockScreen(self.marionette)
        self.apps = GaiaApps(self.marionette)
        from gaiatest.apps.keyboard.app import Keyboard
        self.keyboard = Keyboard(self.marionette)

    def add_to_list(self, test, app):
        self.tests.append([test, app])

    def run_tests(self):
        import pdb; pdb.set_trace()
        for test in self.tests:
            self.setUp()
            from gaiatest.apps.homescreen.app import Homescreen
            self.marionette.switch_to_frame()
            self.marionette.switch_to_frame(self.marionette.find_element('css selector', 'iframe[src*="homescreen"][src*="/index.html"]'))

            self.homescreen = Homescreen(self.marionette)
            self.homescreen.launch()
            self.homescreen.launch_app(test[1])
            test[0]()
            self.testDown()

    def push_resource(self, filename, count=1, destination=''):
        self.device.push_file(self.resource(filename), count, '/'.join(['sdcard', destination]))

    def resource(self, filename):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources', filename))

    def wait_for_element_present(self, by, locator, timeout=_default_timeout):
        timeout = float(timeout) + time.time()

        while time.time() < timeout:
            time.sleep(0.5)
            try:
                return self.marionette.find_element(by, locator)
            except NoSuchElementException:
                pass
        else:
            raise TimeoutException(
                'Element %s not present before timeout' % locator)

    def wait_for_element_not_present(self, by, locator, timeout=_default_timeout):
        timeout = float(timeout) + time.time()

        while time.time() < timeout:
            time.sleep(0.5)
            try:
                self.marionette.find_element(by, locator)
            except NoSuchElementException:
                break
        else:
            raise TimeoutException(
                'Element %s still present after timeout' % locator)

    def wait_for_element_displayed(self, by, locator, timeout=_default_timeout):
        timeout = float(timeout) + time.time()
        e = None
        while time.time() < timeout:
            time.sleep(0.5)
            try:
                if self.marionette.find_element(by, locator).is_displayed():
                    break
            except (NoSuchElementException, StaleElementException) as e:
                pass
        else:
            # This is an effortless way to give extra debugging information
            if isinstance(e, NoSuchElementException):
                raise TimeoutException('Element %s not present before timeout' % locator)
            else:
                raise TimeoutException('Element %s present but not displayed before timeout' % locator)

    def wait_for_element_not_displayed(self, by, locator, timeout=_default_timeout):
        timeout = float(timeout) + time.time()

        while time.time() < timeout:
            time.sleep(0.5)
            try:
                if not self.marionette.find_element(by, locator).is_displayed():
                    break
            except StaleElementException:
                pass
            except NoSuchElementException:
                break
        else:
            raise TimeoutException(
                'Element %s still visible after timeout' % locator)

    def wait_for_condition(self, method, timeout=_default_timeout,
                           message="Condition timed out"):
        """Calls the method provided with the driver as an argument until the \
        return value is not False."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                value = method(self.marionette)
                if value:
                    return value
            except (NoSuchElementException, StaleElementException):
                pass
            time.sleep(0.5)
        else:
            raise TimeoutException(message)

    def is_element_present(self, by, locator):
        try:
            self.marionette.find_element(by, locator)
            return True
        except:
            return False

    def is_element_displayed(self, by, locator):
        try:
            return self.marionette.find_element(by, locator).is_displayed()
        except (NoSuchElementException, ElementNotVisibleException):
            return False

    def tearDown(self):
         # switch to homescreem
        self.run_tests()

        self.marionette.switch_to_frame()
        self.marionette.execute_script("window.wrappedJSObject.dispatchEvent(new Event('home'));")

        # self.lockscreen = None
        # self.apps = None
        # MarionetteTestCase.tearDown(self)
