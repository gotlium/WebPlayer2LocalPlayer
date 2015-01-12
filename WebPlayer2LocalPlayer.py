#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'gotlium'
__version__ = '1.0'

import signal
import sys
import os
import re

from PyQt5 import QtCore, QtGui, QtWebKitWidgets, QtWidgets, QtNetwork
from PyQt5.QtWebKit import QWebSettings

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

APP_NAME = "WebPlayer2LocalPlayer"
VIDEO_EXT = ["mp4", "flv"]
FORBIDDEN_EXT = ["gif"]
FORBIDDEN_REGEXP = ["rdr.php.*", ".*edgecastcdn.*"]
FORBIDDEN_URL = "http://localhost/forbidden/"
OPEN_CMD = "open -a VLC '%s'"
DOWNLOAD_CMD = "open -a 'Folx 3' '%s'"


class QNetworkCookieJar(QtNetwork.QNetworkCookieJar):
    def __init__(self, parent=None):
        super(QNetworkCookieJar, self).__init__(parent)
        self.cookie_path = os.path.expanduser("~/.wp2lp.cookie")

    def saveCookies(self):
        all_cookies = QtNetwork.QNetworkCookieJar.allCookies(self)

        cookie_dir = os.path.dirname(self.cookie_path)
        if not os.path.exists(cookie_dir):
            os.makedirs(cookie_dir)

        with open(self.cookie_path, 'w') as f:
            lines = ''
            for cookie in all_cookies:
                lines += '%s\r\n' % cookie.toRawForm()
            f.writelines(lines)

    def restoreCookies(self):
        if os.path.exists(self.cookie_path):
            with open(self.cookie_path, 'r') as f:
                lines = ''
                for line in f:
                    lines += line
                all_cookies = QtNetwork.QNetworkCookie.parseCookies(lines)
                QtNetwork.QNetworkCookieJar.setAllCookies(self, all_cookies)


class UrlDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(UrlDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('Enter URL')
        self.setFixedSize(200, 100)

        self.url = QtWidgets.QLineEdit()
        self.url.setText('http://')
        self.url.setFocus()

        self.button = QtWidgets.QPushButton("Open url")
        self.button.clicked.connect(self.openUrl)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.url)
        layout.addWidget(self.button)

        self.setLayout(layout)
    
    def openUrl(self):
        self.close()
    
    def getUrl(self):
        return self.url.text().strip()


class ActionDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        self._url = kwargs.pop('url')
        super(ActionDialog, self).__init__(*args, **kwargs)

        self.setWindowTitle('Action')
        self.setFixedSize(200, 130)

        self.url = QtWidgets.QLineEdit()
        self.url.setText(self._url)

        self.download = QtWidgets.QPushButton("Download")
        self.download.clicked.connect(self.downloadFile)

        self.open = QtWidgets.QPushButton("Open")
        self.open.clicked.connect(self.openFile)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.url)
        layout.addWidget(self.open)
        layout.addWidget(self.download)

        self.setLayout(layout)

    def doAction(self, cmd):
        os.system(cmd)
        self.close()
        sys.exit(0)

    def openFile(self):
        self.doAction(OPEN_CMD % self._url)

    def downloadFile(self):
        self.doAction(DOWNLOAD_CMD % self._url)


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
        result = urlparse(self.getUrl())
        return result.path.split(".")[-1]

    def getUrl(self):
        return self.request.url().toString()

    def interruptRequest(self):
        self.request.setUrl(QtCore.QUrl(FORBIDDEN_URL))

    @staticmethod
    def openPlayer(url):
        print("Url: %s" % url)
        dialog = ActionDialog(url=url)
        dialog.exec_()

    @staticmethod
    def catchError(eid):
        sys.stderr.write("Error %d\n" % eid)


class MainWindow(QtWebKitWidgets.QWebView):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(APP_NAME)
        self.setPage(QtWebKitWidgets.QWebPage())

        self.cookie_jar = QNetworkCookieJar()
        self.cookie_jar.restoreCookies()

        self.showWebView(self.getUrl())
        self.showMaximized()

    def showWebView(self, url):
        self.page().setNetworkAccessManager(QNetworkAccessManager())
        self.page().networkAccessManager().setCookieJar(self.cookie_jar)
        self.load(QtCore.QUrl(url))

    @staticmethod
    def getUrl():
        if len(sys.argv) != 2:
            dialog = UrlDialog()
            dialog.exec_()
            if dialog.getUrl() == 'http://':
                sys.exit(0)
            return dialog.getUrl()
        return sys.argv[1]

    @staticmethod
    def setSettings():
        settings = QWebSettings.globalSettings()
        settings.setAttribute(QWebSettings.AutoLoadImages, True)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebSettings.PluginsEnabled, True)
        settings.setAttribute(QWebSettings.JavascriptCanOpenWindows, True)

    def closeEvent(self, event):
        self.cookie_jar.saveCookies()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setApplicationName(APP_NAME)
    app.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)
    app.setWindowIcon(QtGui.QIcon('images/app_icon.png'))

    main = MainWindow()
    main.setSettings()
    main.show()

    if signal.signal(signal.SIGINT, signal.SIG_DFL):
        sys.exit(app.exec_())
    app.exec_()
