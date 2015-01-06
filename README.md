WebPlayer2LocalPlayer
=====================

Simple launcher for view video from browser on VLC player.

Example
-------
```
python WebPlayer2LocalPlayer.py http://example.com 2> /dev/null
```

Open page with player, and click to play on video player. When VLC will be opened, close python browser.

For what & why?
Chrome uses a lot of memory and CPU, while VLC used 13-15% of CPU. Chrome uses at least 40-50% and 2-3 GB of memory.
Overall, the program helps to save battery and do not heats the computer.
Perhaps it makes sense to download video, but then in the future there will be problems with the SSD.

Installation
------------
```
brew install qt5 pyqt5 || sudo apt-get install pyqt5-dev-tools
git clone --depth 1 https://github.com/gotlium/WebPlayer2LocalPlayer.git
cd WebPlayer2LocalPlayer
python WebPlayer2LocalPlayer.py http://example.com 2> /dev/null
```
