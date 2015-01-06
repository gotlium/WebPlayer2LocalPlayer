#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urlparse
import signal
import sys
import os
import re

from PyQt5 import QtCore, QtWebKitWidgets, QtWidgets, QtNetwork
from PyQt5.QtWebKit import QWebSettings

APP_NAME = "WebPlayer2LocalPlayer"
VIDEO_EXT = ["mp4", "flv"]
FORBIDDEN_EXT = ["gif"]
FORBIDDEN_REGEXP = ["rdr.php.*", ".*edgecastcdn.*"]
FORBIDDEN_URL = "http://localhost/forbidden/"
OPEN_CMD = "open -a VLC '%s'"


class QNetworkAccessManager(QtNetwork.QNetworkAccessManager):
    def __init__(self, *args, **kwargs):
        super(QNetworkAccessManager, self).__init__(*args, **kwargs)
        self.request = None

    def createRequest(self, operation, request, *args, **kwargs):
        self.processRequest(operation=operation, request=request)
        reply = QtNetwork.QNetworkAccessManager.createRequest(
            self, operation, request, *args, **kwargs)
        reply.error.connect(self.catchError)
        return reply

    def processRequest(self, operation, request):
        if operation == self.GetOperation:
            self.request = request

            sys.stderr.write("%s\n" % self.getUrl())

            for regexp in FORBIDDEN_REGEXP:
                if re.match(regexp, self.getUrl()):
                    self.interruptRequest()

            if self.getExt() in FORBIDDEN_EXT:
                self.interruptRequest()

            if self.getExt() in VIDEO_EXT:
                self.openPlayer(self.getUrl())
                self.interruptRequest()

    def getExt(self):
        result = urlparse.urlparse(self.getUrl())
        return result.path.split(".")[-1]

    def getUrl(self):
        return self.request.url().toString()

    def interruptRequest(self):
        self.request.setUrl(QtCore.QUrl(FORBIDDEN_URL))

    @staticmethod
    def openPlayer(url):
        print("Url for open: %s" % url)
        os.system(OPEN_CMD % url)

    @staticmethod
    def catchError(eid):
        # print('Error %d:' % eid)
        pass


class MainWindow(QtWebKitWidgets.QWebView):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(APP_NAME)
        self.setPage(QtWebKitWidgets.QWebPage())
        self.showWebView(self.getUrl())
        self.showMaximized()

    def showWebView(self, url):
        self.page().setNetworkAccessManager(QNetworkAccessManager())
        self.load(QtCore.QUrl(url))

    @staticmethod
    def getUrl():
        if len(sys.argv) != 2:
            print("Enter url as secondary argument")
            sys.exit(-1)
        return sys.argv[1]

    @staticmethod
    def setSettings():
        settings = QWebSettings.globalSettings()
        settings.setAttribute(QWebSettings.AutoLoadImages, True)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebSettings.PluginsEnabled, True)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setApplicationName(APP_NAME)

    main = MainWindow()
    main.setSettings()
    main.show()

    if signal.signal(signal.SIGINT, signal.SIG_DFL):
        sys.exit(app.exec_())
    app.exec_()
