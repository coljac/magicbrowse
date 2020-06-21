# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'zoomdialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ZoomDialog(object):
    def setupUi(self, ZoomDialog):
        ZoomDialog.setObjectName("ZoomDialog")
        ZoomDialog.resize(366, 502)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ZoomDialog.sizePolicy().hasHeightForWidth())
        ZoomDialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(ZoomDialog)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.zoomimg = QtWidgets.QLabel(ZoomDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.zoomimg.sizePolicy().hasHeightForWidth())
        self.zoomimg.setSizePolicy(sizePolicy)
        self.zoomimg.setObjectName("zoomimg")
        self.gridLayout.addWidget(self.zoomimg, 0, 0, 1, 1)

        self.retranslateUi(ZoomDialog)
        QtCore.QMetaObject.connectSlotsByName(ZoomDialog)

    def retranslateUi(self, ZoomDialog):
        _translate = QtCore.QCoreApplication.translate
        ZoomDialog.setWindowTitle(_translate("ZoomDialog", "Card zoom"))
        self.zoomimg.setText(_translate("ZoomDialog", "new layout"))

