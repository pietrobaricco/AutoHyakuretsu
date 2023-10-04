import time

from libs.delay import NonBlockingDelay
from libs.macro import Macro


class vpn(Macro):
    def run(self, screenshot_cv, parameters={}):
        if self.search_and_click("forticlient_connect", screenshot_cv):
            print("VPN died at date " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

        if self.search_and_click("bitvise_login", screenshot_cv):
            print("SSH died died at date " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
