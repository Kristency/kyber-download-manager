from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import urllib
import pafy
import os

from main import Ui_MainWindow


class MainApp(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.initUi()
        self.handle_buttons()
        self.suffixes = {
            "decimal": ("kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"),
            "binary": ("KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"),
            "gnu": "KMGTPEZY",
        }

    def initUi(self):
        # contain all ui changes in the initial loading
        self.tabWidgetMain.tabBar().setVisible(False)
        with open('themes/current_theme.txt', 'r') as f:
            current_theme = f.read()
            if current_theme != 'default':
                with open(f'themes/{current_theme}', 'r') as stylesheet:
                    style = stylesheet.read()
                    self.setStyleSheet(style)

    # humanize module code because it was not working after making exe with cx_freeze
    # was giving module not found error.

    """Bits & Bytes related humanization."""

    def naturalsize(self, value, binary=False, gnu=False, format="%.1f"):
        """Format a number of bytes like a human readable filesize (eg. 10 kB).
        By default, decimal suffixes (kB, MB) are used.
        Non-gnu modes are compatible with jinja2's ``filesizeformat`` filter.
        Args:
            value (int, float, string): Integer to convert.
            binary (Boolean): If `True`, uses binary suffixes (KiB, MiB) with base 2**10
            instead of 10**3.
            gnu (Boolean): If `True`, the binary argument is ignored and GNU-style
            (`ls -sh` style) prefixes are used (K, M) with the 2**10 definition.
            format (str): Custom formatter.
        """
        if gnu:
            suffix = self.suffixes["gnu"]
        elif binary:
            suffix = self.suffixes["binary"]
        else:
            suffix = self.suffixes["decimal"]

        base = 1024 if (gnu or binary) else 1000
        bytes = float(value)
        abs_bytes = abs(bytes)

        if abs_bytes == 1 and not gnu:
            return "%d Byte" % bytes
        elif abs_bytes < base and not gnu:
            return "%d Bytes" % bytes
        elif abs_bytes < base and gnu:
            return "%dB" % bytes

        for i, s in enumerate(suffix):
            unit = base ** (i + 2)
            if abs_bytes < unit and not gnu:
                return (format + " %s") % ((base * bytes / unit), s)
            elif abs_bytes < unit and gnu:
                return (format + "%s") % ((base * bytes / unit), s)
        if gnu:
            return (format + "%s") % ((base * bytes / unit), s)
        return (format + " %s") % ((base * bytes / unit), s)

    ############################## FILE DOWNLOAD ################################

    def handle_buttons(self):
        # handles all buttons in the app
        self.pBtnFileDownload.clicked.connect(self.handle_file_download)
        self.pBtnVideoDownload.clicked.connect(self.handle_single_video_download)
        self.pBtnPlaylistDownload.clicked.connect(self.handle_playlist_download)
        self.pBtnFileSaveLocation.clicked.connect(self.handle_file_save_location_selection)
        self.pBtnVideoData.clicked.connect(self.get_video_data)
        self.pBtnVideoSaveLocation.clicked.connect(self.handle_video_save_location_selection)
        self.pBtnPlaylistSaveLocation.clicked.connect(self.handle_playlist_save_location_selection)

        self.pBtnHomeTab.clicked.connect(self.open_home)
        self.pBtnFileDownloadTab.clicked.connect(self.open_file_download)
        self.pBtnVideoDownloadTab.clicked.connect(self.open_video_download)
        self.pBtnSettingsTab.clicked.connect(self.open_settings)

        self.pBtnDefaultTheme.clicked.connect(self.apply_default_theme)
        self.pBtnQDarkTheme.clicked.connect(self.apply_qdark_theme)
        self.pBtnQDarkGrayTheme.clicked.connect(self.apply_qdarkgray_theme)
        self.pBtnDarkBlueTheme.clicked.connect(self.apply_darkblue_theme)

    def handle_file_progress(self, blocknum, blocksize, totalsize):
        # calculate the progress
        read_data = blocknum*blocksize
        if totalsize > 0:
            download_percentage = read_data*100/totalsize
            self.pBarFileDownload.setValue(download_percentage)
            QApplication.processEvents()

    def handle_file_save_location_selection(self):
        # enable browsing to our os to pick save location
        save_location = QFileDialog.getSaveFileName(self, caption='Save as', directory='.', filter='All Files(*.*)')

        path, file_type = save_location
        self.lEdtFileDownloadLocation.setText(path)

    def handle_file_download(self):
        # downloading any file
        download_url = self.lEdtFileDownloadLink.text()
        save_location = self.lEdtFileDownloadLocation.text()

        if not download_url or not save_location:
            QMessageBox.warning(self, 'Data Error', "Provide a valid URL or save location")
        else:
            try:
                self.pBtnFileDownload.setEnabled(False)
                urllib.request.urlretrieve(download_url, save_location, self.handle_file_progress)
            except Exception:
                QMessageBox.warning(self, 'Download Error', "Can't download the file from the given URL")
                self.pBtnFileDownload.setEnabled(True)
                return

            QMessageBox.information(self, 'Download Completed', 'The download completed successfully')
            self.lEdtFileDownloadLink.setText('')
            self.lEdtFileDownloadLocation.setText('')
            self.pBarFileDownload.setValue(0)
            self.pBtnFileDownload.setEnabled(True)

    ############################################# YOUTUBE SINGLE VIDEO DOWNLOAD #################################

    def get_video_data(self):
        video_url = self.lEdtVideoUrl.text()
        if not video_url:
            QMessageBox.warning(self, 'Data Error', "Provide a valid video URL")
        else:
            video = pafy.new(video_url)
            video_streams = video.streams
            self.cBoxVideoQuality.clear()
            for stream in video_streams:
                size = self.naturalsize(stream.get_filesize())
                data = f'{stream.extension}  {stream.quality}  {size}'
                self.cBoxVideoQuality.addItem(data)

    def handle_video_save_location_selection(self):
        save_location = QFileDialog.getSaveFileName(
            self, caption='Save as', directory='.', filter='MP4 Video File (VLC) (*.mp4);;All Files (*.*)')

        path, file_type = save_location
        self.lEdtVideoDownloadLocation.setText(path)

    def handle_single_video_download(self):
        video_url = self.lEdtVideoUrl.text()
        save_location = self.lEdtVideoDownloadLocation.text()

        if not video_url or not save_location:
            QMessageBox.warning(self, 'Data Error', "Provide a valid video URL or save location")
        elif not self.cBoxVideoQuality.currentText():
            QMessageBox.warning(self, 'Data Error', "Please choose a video quality")
        else:
            try:
                self.pBtnVideoDownload.setEnabled(False)
                video = pafy.new(video_url)
                video_streams = video.streams
                video_quality = self.cBoxVideoQuality.currentIndex()
                download = video_streams[video_quality].download(
                    filepath=save_location, callback=self.handle_single_video_progress)
            except Exception:
                QMessageBox.warning(self, 'Download Error', "Can't download the video from the given URL")
                self.pBtnVideoDownload.setEnabled(True)
                return

            QMessageBox.information(self, 'Download Completed', 'The download completed successfully')
            self.lEdtVideoUrl.setText('')
            self.lEdtVideoDownloadLocation.setText('')
            self.cBoxVideoQuality.clear()
            self.pBarVideoDownload.setValue(0)
            self.pBtnVideoDownload.setEnabled(True)

    def handle_single_video_progress(self, total, received, ratio, rate, time):
        read_data = received
        if total > 0:
            download_percentage = read_data*100/total
            self.pBarVideoDownload.setValue(download_percentage)
            QApplication.processEvents()

    ############################################# YOUTUBE PLAYLIST DOWNLOAD ##################################

    def handle_playlist_download(self):
        playlist_url = self.lEdtPlaylistUrl.text()
        save_location = self.lEdtPlaylistDownloadLocation.text()

        if not playlist_url or not save_location:
            QMessageBox.warning(self, 'Data Error', "Provide a valid playlist URL or save location")
        else:
            try:
                self.pBtnPlaylistDownload.setEnabled(False)
                playlist = pafy.get_playlist(playlist_url)
                playlist_videos = playlist['items']
                quality = self.cBoxPlaylistVideoQuality.currentIndex()

                total_video_count = len(playlist_videos)
                current_video_number = 1
                self.lblCurrentVideoNumber.setText(str(current_video_number))
                self.lblTotalVideoCount.setText(str(total_video_count))

                os.chdir(save_location)
                if os.path.exists(playlist['title']):
                    os.chdir(playlist['title'])
                else:
                    os.mkdir(playlist['title'])
                    os.chdir(playlist['title'])

                    for video in playlist_videos:
                        current_video = video['pafy']
                        current_video_streams = current_video.streams
                        download = current_video_streams[quality].download(callback=self.handle_playlist_progress)
                        current_video_number += 1
                        self.lblCurrentVideoNumber.setText(str(current_video_number))
            except Exception:
                QMessageBox.warning(self, 'Download Error', "Can't download the playlist from the given URL")
                self.pBtnPlaylistDownload.setEnabled(True)
                return

            QMessageBox.information(self, 'Download Completed', 'The download completed successfully')
            self.lEdtPlaylistUrl.setText('')
            self.lEdtPlaylistDownloadLocation.setText('')
            self.pBarPlaylistDownload.setValue(0)
            self.pBtnPlaylistDownload.setEnabled(True)

    def handle_playlist_progress(self, total, received, ratio, rate, time):
        read_data = received
        if total > 0:
            download_percentage = read_data*100/total
            self.pBarPlaylistDownload.setValue(download_percentage)
            QApplication.processEvents()

    def handle_playlist_save_location_selection(self):
        playlist_save_location = QFileDialog.getExistingDirectory(self, 'Select Download Directory')

        self.lEdtPlaylistDownloadLocation.setText(playlist_save_location)

    ############################################# UI CHANGE METHODS ###########################################

    def open_home(self):
        self.tabWidgetMain.setCurrentIndex(0)

    def open_file_download(self):
        self.tabWidgetMain.setCurrentIndex(1)

    def open_video_download(self):
        self.tabWidgetMain.setCurrentIndex(2)

    def open_settings(self):
        self.tabWidgetMain.setCurrentIndex(3)

    ############################################# APP THEME METHODS ###########################################

    def apply_default_theme(self):
        self.setStyleSheet('')
        with open('themes/current_theme.txt', 'w') as f:
            f.write('default')

    def apply_qdark_theme(self):
        self.setStyleSheet('')
        with open('themes/qdark.qss', 'r') as stylesheet:
            style = stylesheet.read()
            self.setStyleSheet(style)

        with open('themes/current_theme.txt', 'w') as f:
            f.write('qdark.qss')

    def apply_qdarkgray_theme(self):
        self.setStyleSheet('')
        with open('themes/qdarkgray.qss', 'r') as stylesheet:
            style = stylesheet.read()
            self.setStyleSheet(style)

        with open('themes/current_theme.txt', 'w') as f:
            f.write('qdarkgray.qss')

    def apply_darkblue_theme(self):
        self.setStyleSheet('')
        with open('themes/darkblue.qss', 'r') as stylesheet:
            style = stylesheet.read()
            self.setStyleSheet(style)

        with open('themes/current_theme.txt', 'w') as f:
            f.write('darkblue.qss')


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  # to disable maximize button
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
