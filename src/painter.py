#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial

In the example, we draw randomly 1000 red points
on the window.

Author: Jan Bodnar
Website: zetcode.com
Last edited: August 2017
"""

import sys
sys.path.append("/home/coljac/build/coltools")
import coltools as ct
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QIcon, QPixmap
from PyQt5.QtCore import Qt
import sys, random
from config import config

DEFAULT_IMG_WIDTH = 252
DEFAULT_IMG_HEIGHT = int(DEFAULT_IMG_WIDTH*1.3928)

class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.images = ct.find_files(config['images_dir'], "jpg")

    def initUI(self):
        self.setGeometry(100, 100, 1000, 1000)
        self.setWindowTitle('Blit')
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawPoints(qp)
        qp.end()

    def drawPoints(self, qp):
        pad = 1
        qp.setPen(Qt.red)
        size = self.size()
        for i in range(9):
            xi = i%3
            yi = i//3
            x = xi * (DEFAULT_IMG_WIDTH + pad)
            y = yi * (DEFAULT_IMG_HEIGHT + pad)
            pixmap = QPixmap(random.choice(self.images))
            pixmap = pixmap.scaledToWidth(DEFAULT_IMG_WIDTH, mode=Qt.SmoothTransformation)
            qp.drawPixmap(x, y, pixmap)

        # for i in range(1000):
        #     x = random.randint(1, size.width() - 1)
        #     y = random.randint(1, size.height() - 1)
        #     qp.drawPoint(x, y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())