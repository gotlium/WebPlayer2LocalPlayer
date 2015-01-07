from setuptools import setup
from glob import glob

from WebPlayer2LocalPlayer import __version__

APP = ['WebPlayer2LocalPlayer.py']
DATA_FILES = [
    ('images', glob('images/*.png')),
]

OPTIONS = {
    'argv_emulation': True,
    'includes': [
        'sip',
        'PyQt5', 'PyQt5.QtGui', 'PyQt5.QtPrintSupport',
        'PyQt5.QtCore', 'PyQt5.QtWebKitWidgets',
        'PyQt5.QtWidgets', 'PyQt5.QtNetwork', 'PyQt5.QtWebKit',
    ],
    'semi_standalone': 'False',
    'compressed': True,
    "optimize": 2,
    "iconfile": 'images/app_icon.icns',
    "qt_plugins": ["imageformats", "platforms"],
    "plist": dict(
        LSMinimumSystemVersion='10.8.0',
        LSEnvironment=dict(
            PATH='./../Resources:/usr/local/bin:/usr/bin:/bin'
        )
    )
}

setup(
    name="WP2LP",
    version=__version__,
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
