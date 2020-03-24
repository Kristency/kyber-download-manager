from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import urllib

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
        self.pBtnFileDownload.clicked.connect(self.handle_download)
        self.pBtnFileSaveLocation.clicked.connect(self.handle_save_location_selection)

    def handle_file_progess(self, blocknum, blocksize, totalsize):
        # calculate the progress
        read_data = blocknum*blocksize
        if totalsize > 0:
            download_percentage = read_data*100/totalsize
            self.pBarFileDownload.setValue(download_percentage)

    def handle_save_location_selection(self):
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
                urllib.request.urlretrieve(download_url, save_location, self.handle_progess)
            except Exception:
                QMessageBox.warning(self, 'Download Error', "Can't download the file from the given URL")
                return

            QMessageBox.information(self, 'Download Completed', 'The download completed successfully')
            self.lEdtFileDownloadLink.setText('')
            self.lEdtFileDownloadLocation.setText('')
            self.pBarFileDownload.setValue(0)

    ############################################# YOUTUBE SINGLE VIDEO DOWNLOAD #################################


def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
