import os
import sys
import json
from cards import *
from config import save_config
from mainwin import *
from zoomdialog import *
import random
import os
# import PIL
# from PIL import Image
from PyQt5.QtGui import QIcon, QPixmap, QPainter
# from PyQt5.QtCore import
from PIL.ImageQt import ImageQt
# from PyQt5.QtCore import Qt
from PyQt5.QtCore import *
# from QtWidgets import QDialog
import glob
import time

# TODO: Allow resizing
# TODO: 2 card sizes
# TODO: Show latest card (need to order the sets)
# TODO: Sort by color, cmc by default
# TODO: Click to flip image
# TODO: Esc to quit
# TODO: Different layouts
# TODO: custom sorting
# TODO: Docs
# TODO: Only do the search if it's been X ms since typing
# TODO: Null pixmap
# TODO: Show number of cards and pages
# TODO: Package
# TODO: Bootstrap
# X TODO: Update card display in thread - abort with keystroke
# X TODO: Most recent card art
# X hacky TODO: Turn on/off the zoom window
# X first version TODO: save queries
# X TODO: Paging
# X TODO: cache next page pixmaps

NUM_LABELS = 15
DEFAULT_IMG_WIDTH = 220 #252
PADDING = 1
KEY_DELAY = .05

class UpdateThread(QThread):
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self, app):
        QThread.__init__(self)
        self.app = app

    def run(self):
        time.sleep(KEY_DELAY)
        QMetaObject.invokeMethod(self.app, "search_and_update")

    # def finished(self):
    #     print("Thread", self, " finished")

    # def stop(self):
    #     self.threadactive = False
    #     self.wait()

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
        # self.setMaximumWidth(self.height()*.717)

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


class MtgBrowse(QtWidgets.QMainWindow, Ui_MtgBrowse):

    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__(parent)
        self.update_threads = {}
        self.setupUi(self)
        self.main_window = self
        self.cards = Cards()
        self.current_cards = self.cards.search_on("s:grn")
        self.page = 1
        self.image_cache = {}
        self.update_card_view()
        self.zoom_window = None
        self.save_mode = False
        self.last_keystroke = time.time()
        self.setupMTG()

    def check_buttons(self):
        self.prevPage.setEnabled(self.page > 1)
        N = len(self.current_cards)
        self.nextPage.setEnabled(N > (self.page * NUM_LABELS))


    def text_changed(self, text):
        try:
            self.last_keystroke = time.time()
            thread = UpdateThread(self)
            self.update_threads[thread] = thread
            thread.start()
            # self.update_card_view()
            # self.search_and_update()
        except Exception as e:
            pass


    def update_status_bar(self):
        self.statusBarLabel.setText("%d cards in search, page (%d/%d)" % (len(self.current_cards), self.page,
                                                                       1 + len(self.current_cards)//15))

    def next(self):
        self.page += 1
        self.update_card_view()

    def prev(self):
        self.page = max(self.page - 1, 1)
        self.update_card_view()

    def paintCardImages(self, event, page=None, paint=True):
        qp = QPainter()
        qp.begin(self.mainWidget)
        if page is None:
            page = self.page
        for i in range(NUM_LABELS):
            # pixmap = QPixmap(None)
            idx = (page - 1)*NUM_LABELS + i
            xi = i%5
            yi = i//5
            if idx >= len(self.current_cards):
                continue
            row = self.current_cards.iloc[idx]
            id = row.name
            image = config.get("images_dir") + "large/" + id + ".jpg"
            if not os.path.exists(image):
                try:
                    id = eval(row['card_faces'])[0]['id']
                    image = config.get("images_dir") + "large/" + id + ".jpg"
                except Exception as e:
                    # print(e)
                    pass

            if image is not None and os.path.exists(image):
                pixmap = self.image_cache.get(image, None)
                if pixmap is None:
                    pixmap = QPixmap(image)
                    try:
                        pixmap = pixmap.scaledToWidth(DEFAULT_IMG_WIDTH, mode=Qt.SmoothTransformation)
                        self.image_cache[image] = pixmap
                    except:
                        pass
                if paint:
                    x = xi * (DEFAULT_IMG_WIDTH + PADDING)
                    y = yi * (pixmap.height() + PADDING)
                    qp.drawPixmap(x, y, pixmap)
            else:
                pass
                # self.cards.fetch_images(self.current_cards.iloc[idx:idx+1])
                # print(image, row['name'], os.path.exists(image))

            i += 1
        qp.end()
        self.check_buttons()
        if not paint:
            self.paintCardImages(event, page=page+1, paint=False)


    def closeEvent(self, event):
        save_config()
        pass

    def setupMTG(self):
        self.lineEdit.textChanged.connect(self.text_changed)
        self.nextPage.pressed.connect(self.next)
        self.prevPage.pressed.connect(self.prev)
        self.zoomToggleButton.pressed.connect(self.toggle_zoom)
        self.loadButton_1.pressed.connect(lambda: self.load_preset(1))
        self.loadButton_2.pressed.connect(lambda: self.load_preset(2))
        self.loadButton_3.pressed.connect(lambda: self.load_preset(3))
        self.saveButton.pressed.connect(self.save_button)
        self.mainWidget.paintEvent = self.paintCardImages
        self.mainWidget.setMouseTracking(True)
        # self.label_listeners()
        self.widget_listeners()
        for i in range(1, 4):
            try:
                saved = config.get('preset_' + str(i))
                button = self.main_window.findChild(QtWidgets.QPushButton, "loadButton_" + str(i))
                button.setText(saved[0:10])
            except Exception as e:
                pass

        # self.toggle_zoom()
        # Setup key listener

    def save_button(self):
        self.save_mode = True


    def load_preset(self, number):
        if self.save_mode:
            search_text = self.lineEdit.text()
            config['preset_' + str(number)] = search_text
            self.save_mode = False
        else:
            try:
                saved_search = config['preset_' + str(number)]
                self.lineEdit.setText(saved_search)
            except:
                pass


    def toggle_zoom(self):
        if self.zoom_window is None:
            self.zoom_window = ZoomDialog(self)
        else:
            self.zoom_window.close()
            self.zoom_window = None

    def widget_listeners(self):
       self.mainWidget.installEventFilter(self)

    def eventFilter(self, object, event):
        if self.zoom_window is None:
            return False

        if object == self.mainWidget and type(event) == QtGui.QMouseEvent:
            x, y = event.x(), event.y()
            xi = x//(DEFAULT_IMG_WIDTH + PADDING)
            yi = y//(DEFAULT_IMG_WIDTH*1.389 + PADDING)
            index = int(yi*5 + xi)
            if index >= len(self.current_cards):
                return False
            try:
                card = self.current_cards.iloc[(self.page - 1) * NUM_LABELS + index]
                id = card.name
                self.zoom_window.set_image(config.get("images_dir") + "large/" + id + ".jpg")
                self.zoom_window.setWindowTitle(card['name'])
            except Exception as e:
                pass

        return False

    @pyqtSlot()
    def search_and_update(self): # , thread_caller=None):
        now = time.time()
        if now - self.last_keystroke < KEY_DELAY:
            return
        try:
            self.current_cards = self.cards.search_on(self.lineEdit.text())
            self.page = 1
            self.update_card_view()
            self.update_threads.clear()
        except:
            pass # Invalid search

    def update_card_view(self):
        try:
            self.mainWidget.repaint()
            self.update_status_bar()
        except:
            pass


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mtgapp = MtgBrowse()#MainWindow)
    mtgapp.show()
    sys.exit(app.exec_())

