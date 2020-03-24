from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import urllib
import pafy
import humanize

from PyQt5.uic import loadUiType


ui, _ = loadUiType('main.ui')


class MainApp(QMainWindow, ui):
    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.initUi()
        self.handle_buttons()

    def initUi(self):
        # contain all ui changes in loading
        pass

    ############################## FILE DOWNLOAD ################################

    def handle_buttons(self):
        # handles all buttons in the app
        self.pBtnFileDownload.clicked.connect(self.handle_file_download)
        self.pBtnVideoDownload.clicked.connect(self.handle_single_video_download)
        self.pBtnFileSaveLocation.clicked.connect(self.handle_file_save_location_selection)
        self.pBtnVideoData.clicked.connect(self.get_video_data)
        self.pBtnVideoSaveLocation.clicked.connect(self.handle_video_save_location_selection)

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
                self.pBtnVideoDownload.setEnabled(False)
                urllib.request.urlretrieve(download_url, save_location, self.handle_file_progress)
            except Exception:
                QMessageBox.warning(self, 'Download Error', "Can't download the file from the given URL")
                self.pBtnVideoDownload.setEnabled(True)
                return

            QMessageBox.information(self, 'Download Completed', 'The download completed successfully')
            self.lEdtFileDownloadLink.setText('')
            self.lEdtFileDownloadLocation.setText('')
            self.pBarFileDownload.setValue(0)
            self.pBtnVideoDownload.setEnabled(True)

    ############################################# YOUTUBE SINGLE VIDEO DOWNLOAD #################################

    def get_video_data(self):
        video_url = self.lEdtVideoUrl.text()
        if not video_url:
            QMessageBox.warning(self, 'Data Error', "Provide a valid video URL")
        else:
            video = pafy.new(video_url)
            video_streams = video.streams
            for stream in video_streams:
                size = humanize.naturalsize(stream.get_filesize())
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
            self.pBtnVideoDownload.setEnabled(False)
            video = pafy.new(video_url)
            video_streams = video.streams
            video_quality = self.cBoxVideoQuality.currentIndex()
            # download = video_streams[video_quality].download(
            #     filepath=save_location, callback=self.handle_single_video_progress)

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


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
