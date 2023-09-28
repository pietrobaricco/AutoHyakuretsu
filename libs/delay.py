from PyQt5 import QtTest


class NonBlockingDelay():
    @staticmethod
    def wait(delay):
        QtTest.QTest.qWait(delay)
