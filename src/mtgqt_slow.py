import os
import sys
import json
from cards import *
from mainwin import *
from zoomdialog import *
import random
import os
# import PIL
# from PIL import Image
from PyQt5.QtGui import QIcon, QPixmap
# from PyQt5.QtCore import
from PIL.ImageQt import ImageQt
# from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
# from QtWidgets import QDialog
import glob
import time

# TODO: Allow resize
# TODO: cache next page pixmaps
# TODO: 2 card sizes
# TODO: Paging
# TODO: Esc to quit
# TODO: Turn on/off the zoom window
# TODO: save queries
# TODO: Different layouts
# Todo: Update card display in thread - abort with keystroke
# TODO: sorting
# TODO: Docs
# TODO: Null pixmap
# TODO: Package
# TODO: Bootstrap

NUM_LABELS = 15
DEFAULT_IMG_WIDTH = 252

class UpdateThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, app):
        QThread.__init__(self)
        self.app = app

    def run(self):
        self.app._update_card_view()

    def finished(self):
        self.app.update_thread = None

    def stop(self):
        self.threadactive = False
        self.wait()

class ZoomDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent)
        self.setModal(0)
               # dialog = QtWidgets.QDialog()
        self.ui = Ui_ZoomDialog()
        self.ui.setupUi(self)
        # dialog.exec_()
        self.setWindowTitle("Card zoom")
        self.ui.zoomimg.resizeEvent = self.onResize
        self.image = None
        self.set_image(None) # config['images_dir'] + "/large/" + "f6d3c086-9ce4-41c3-8402-2818f1b27192.jpg")
        self.show()

    def onResize(self,  event):
        self.set_image(self.image)
        self.setMaximumWidth(self.height()*.717)

    def set_image(self, image):
        label = self.ui.zoomimg
        pixmap = QPixmap(None)
        if image is not None:
            try:
                pixmap = QPixmap(image)
                pixmap = pixmap.scaledToWidth(label.width(), mode=Qt.SmoothTransformation)
                self.image = image
            except:
                pass
        label.setPixmap(pixmap)

    def exit(self):
        pass

class MtgBrowse(QtWidgets.QMainWindow, Ui_MtgBrowse):

    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.update_thread = None
        self.setupUi(self)
        self.main_window = self
        self.cards = Cards()
        self.current_cards = self.cards.do_search("s:grn")
        self.page = 1
        self.image_cache = {}
        self.update_card_view()
        self.zoom_window = None
        self.setupMTG()

    def check_buttons(self):
        self.prevPage.setEnabled(self.page > 1)
        N = len(self.current_cards)
        self.nextPage.setEnabled(N > (self.page * NUM_LABELS))


    def text_changed(self, text):
        try:
            self.current_cards = self.cards.search_on(text)
            self.page = 1
        except Exception as e:
            pass

        self.update_card_view()

    def next(self):
        self.page += 1
        self.update_card_view()

    def prev(self):
        self.page = max(self.page - 1, 1)
        self.update_card_view()


    def setupMTG(self):
        self.lineEdit.textChanged.connect(self.text_changed)
        self.nextPage.pressed.connect(self.next)
        self.prevPage.pressed.connect(self.prev)
        self.label_listeners()
        self.show_zoom()
        # Setup key listener

    def show_zoom(self):
        self.zoom_window = ZoomDialog(self)

    def label_listeners(self):
       for i in range(1, NUM_LABELS+1):
           label = self.main_window.findChild(QtWidgets.QLabel, "imglabel_" + str(i))
           if label is not None:
               label.installEventFilter(self)
           i += 1

    def eventFilter(self, object, event):
        if self.zoom_window is None:
            return False

        if type(object) == QtWidgets.QLabel:
            name = object.objectName()
            index = int(name.split("_")[-1]) -1
            if index >= len(self.current_cards):
                return False
            try:
                card = self.current_cards.iloc[(self.page - 1) * NUM_LABELS + index]
                id = card.name
                self.zoom_window.set_image(config.get("images_dir") + "large/" + id + ".jpg")
            except:
                pass

        return False

    def update_card_view(self):
        if self.update_thread is not None:
            self.update_thread.stop()
        self.update_thread = UpdateThread(self)
        # Connect the signal from the thread to the finished method
        self.update_thread.signal.connect(self.update_thread.finished)
        self.update_thread.start()

    def _update_card_view(self):
        page = self.page
        for i in range(NUM_LABELS):
            idx = (page - 1)*NUM_LABELS + i
            try:
                row = self.current_cards.iloc[idx]
                id = row.name
                # print(row['name'])
                self.set_image("imglabel_" + str(i+1),
                           config.get("images_dir") + "large/" + id + ".jpg")
            except Exception as e:
                self.set_image("imglabel_" + str(i+1), None)
            i += 1

        page += 1
        # Put next page in cache
        for i in range(NUM_LABELS):
            idx = (page - 1)*NUM_LABELS + i
            if idx > len(self.current_cards) + 1:
                break
            try:
                row = self.current_cards.iloc[idx]
                id = row.name
                self.set_image(None, config.get("images_dir") + "large/" + id + ".jpg")
            except Exception as e:
                pass
            i += 1

    def set_image(self, label, image):
        if label is not None:
            label = self.main_window.findChild(QtWidgets.QLabel, label)
        # if label is None:
        #     return
        pixmap = QPixmap(None)
        if image is not None and os.path.exists(image):
            # im = Image.open(image)
            # im = im.resize((168, 234), resample=PIL.Image.LANCZOS)
            # qim = ImageQt(im)
            # pixmap = QtGui.QPixmap.fromImage(qim)
            pixmap = self.image_cache.get(image, None)
            if pixmap is None:
                pixmap = QPixmap(image)
                print(image)
                try:
                    pixmap = pixmap.scaledToWidth(DEFAULT_IMG_WIDTH, mode=Qt.SmoothTransformation)
                    self.image_cache[image] = pixmap
                except:
                    pass
            else:
                pass
                # print("Cache hit")
        if label is not None:
            label.setPixmap(pixmap)
        self.check_buttons()


    # def set_card_list(self, cards):
    #     self.card_list = cards

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    # MainWindow = QtWidgets.QMainWindow()
    mtgapp = MtgBrowse()#MainWindow)
    # MainWindow.show()
    mtgapp.show()
    # print(MainWindow.findChild(QtWidgets.QLabel, "imglabel_1"))
    sys.exit(app.exec_())

