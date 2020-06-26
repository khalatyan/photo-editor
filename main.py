from PyQt5 import QtWidgets
from mainWindow import Ui_MainWindow  # импорт нашего сгенерированного файла
import sys
import random

from PIL import Image, ImageDraw, ImageQt #Подключим необходимые библиотеки.
from PIL.ImageQt import ImageQt
from PIL import Image
from PIL import ImageTk
import cv2

import pyqtgraph as pg

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *

from logging.config import fileConfig
import logging
logger = logging.getLogger()




class mywindow(QtWidgets.QMainWindow):
    resized = QtCore.pyqtSignal()
    def __init__(self, parent = None):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.img_path = None

        self._img_original = None
        self._img_preview = None

        self.ALL = [0 for i in range(256)]
        self.RED = [0 for i in range(256)]
        self.GREEN = [0 for i in range(256)]
        self.BLUE = [0 for i in range(256)]


        self.ui.editorWidget.setVisible(False)
        self.reset_sliders()
        self.resized.connect(self.someFunction)
        self.ui.reset_btn.setEnabled(False)
        self.ui.saveBtn.setEnabled(False)
        self.ui.uploadBtn.clicked.connect(self.upload_img)
        self.ui.reset_btn.clicked.connect(self.reset)
        self.ui.saveBtn.clicked.connect(self.save_img)
        self.ui.brightness_sld.valueChanged.connect(self.Change)
        self.ui.contrast_sld.valueChanged.connect(self.Change)
        self.ui.red_sld.valueChanged.connect(self.Change)
        self.ui.green_sld.valueChanged.connect(self.Change)
        self.ui.blue_sld.valueChanged.connect(self.Change)

    def resizeEvent(self, event):
        self.resized.emit()
        return super(mywindow, self).resizeEvent(event)

    def someFunction(self):
        if (self._img_preview):
            pix  = QPixmap.fromImage(self._img_preview)
            my_pix = pix.copy()
            ratio = my_pix.width()/my_pix.height()
            if (ratio <= 1):
                height = self.ui.imgLabel.height()
                width = height / ratio
            else:
                width = self.ui.imgLabel.width()
                height = width / ratio
            my_pix = my_pix.scaled(width, height, Qt.KeepAspectRatio)
            self.ui.imgLabel.setPixmap(my_pix)

    def save_img(self):
        logger.debug("open save dialog")
        new_img_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Images (*.png *.xpm *.jpg)")

        if new_img_path:
            logger.debug(f"save output image to {new_img_path}")

            img  = QPixmap.fromImage(self._img_preview)
            width = int(self.ui.width_edit.text())
            height = int(self.ui.height_edit.text())

            my_pix = img.scaled(width, height, Qt.KeepAspectRatio)

            my_pix.save(new_img_path, "PNG")

        

    def reset(self):
        self.reset_sliders()
        if self._img_original is not None:
            self.ui.width_edit.setText(str(self._img_original.width()))
            self.ui.height_edit.setText(str(self._img_original.height()))


    def reset_sliders(self):
        self.ui.contrast_sld.setValue(0)
        self.ui.brightness_sld.setValue(0)
        self.ui.blue_sld.setValue(0)
        self.ui.red_sld.setValue(0)
        self.ui.green_sld.setValue(0)

    def upload_img (self):
        logger.debug("upload")
        #Загружаем изображение
        self.img_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "/Users", "Image Files (*.png *.jpg *.bmp)")

        if self.img_path:
            self.reset()
            self.ui.editorWidget.setVisible(True)

            self.ui.reset_btn.setEnabled(True)
            self.ui.saveBtn.setEnabled(True)


            #Храним изображение
            pix = QPixmap(self.img_path).toImage()
            self._img_original = pix
            self._img_preview = pix

            self.ui.width_edit.setText(str(self._img_original.width()))
            self.ui.height_edit.setText(str(self._img_original.height()))

            #Рисуем гистограмму
            self.drawGist()

            #####################pix.save("somefile.png", "PNG")
            ###################pix.setPixel(0,0,qRgb(0,0,0))

            #####print(pix.width())
            my_pix = pix.copy()
            print(my_pix.width(), my_pix.height())
            ratio = my_pix.width()/my_pix.height()
            if (ratio <= 1):
                height = self.ui.imgLabel.height()
                width = height / ratio
            else:
                width = self.ui.imgLabel.width()
                height = width / ratio
            my_pix  = QPixmap.fromImage(my_pix)
            my_pix = my_pix.scaled(width, height, Qt.KeepAspectRatio)

            self.ui.imgLabel.setPixmap(my_pix)
            #self.ui.imgLabel.setScaledContents(True)



    #Функция для рисования гистограмм
    def drawGist(self):
        self.ui.red_gist.clear()
        self.ui.all_gist.clear()
        self.ui.blue_gist.clear()
        self.ui.green_gist.clear()
        self.ALL = [0 for i in range(256)]
        self.RED = [0 for i in range(256)]
        self.GREEN = [0 for i in range(256)]
        self.BLUE = [0 for i in range(256)]

        (width, height) = (self._img_preview.width(), self._img_preview.height())
        rgb_img = self._img_preview

        for i in range(width):
            for j in range(height):
                cc = QColor(rgb_img.pixel(i,j))
                R, G, B = (cc.red(), cc.green(), cc.blue())
                A = int(0.3 * R + 0.59 * G + 0.11 * B)
                self.GREEN[G] += 1
                self.BLUE[B] += 1
                self.RED[R] += 1
                self.ALL[A] += 1

        #Строим гистограмму
        self.ui.green_gist.plot(self.GREEN, pen=(0,255,0))
        self.ui.red_gist.plot(self.RED, pen=(255,0,0))
        self.ui.blue_gist.plot(self.BLUE, pen=(0,0,255))
        self.ui.all_gist.plot(self.ALL, brush=(50,50,200,100))


    def get_edit_image(self):
        self._img_preview = self._img_original.copy()

        if (self.ui.brightness_sld.value() != 0):
            self.changeBrightness(self.ui.brightness_sld.value())
        if (self.ui.contrast_sld.value() != 0):
            self.changeContrast(self.ui.contrast_sld.value())
        if (self.ui.red_sld.value() != 0):
            self.changeRGB(self.ui.red_sld.value(),0)
        if (self.ui.green_sld.value() != 0):
            self.changeRGB(self.ui.green_sld.value(),1)
        if (self.ui.blue_sld.value() != 0):
            self.changeRGB(self.ui.blue_sld.value(),2)

        pix  = QPixmap.fromImage(self._img_preview)

        self.drawGist()
        my_pix = pix.copy()
        print(my_pix.width(), my_pix.height())
        ratio = my_pix.width()/my_pix.height()
        if (ratio <= 1):
            height = self.ui.imgLabel.height()
            width = height / ratio
        else:
            width = self.ui.imgLabel.width()
            height = width / ratio
        #my_pix  = QPixmap.fromImage(my_pix)
        my_pix = my_pix.scaled(width, height, Qt.KeepAspectRatio)

        self.ui.imgLabel.setPixmap(my_pix)





    def changeBrightness(self, value):
        (width, height) = (self._img_preview.width(), self._img_preview.height())
        N  = value
        for i in range(width):
                for j in range(height):
                    cc = QColor(self._img_preview.pixel(i,j))
                    R, G, B = (self.getbyte(cc.red() + (N * 128)/100), self.getbyte(cc.green() + (N * 128)/100 ), self.getbyte(cc.blue() + (N * 128)/100))
                    self._img_preview.setPixel(i,j, qRgb(R,G,B))
                    #pix[i,j] = (self.getbyte(pix[i,j][0] + value), self.getbyte(pix[i,j][1] + value), self.getbyte(pix[i,j][2] + value))


    def changeContrast(self, value):
        (width, height) = (self._img_preview.width(), self._img_preview.height())
        N  = value
        for i in range(width):
                for j in range(height):
                    cc = QColor(self._img_preview.pixel(i,j))
                    if (N > 0):
                        R, G, B = (self.getbyte((cc.red() * (100 - N) - 128 * N)/(100)),
                        self.getbyte((cc.green() * (100 - N) - 128 * N)/(100)),
                        self.getbyte((cc.blue() * (100 - N) - 128 * N)/(100)))
                    else:
                        R, G, B = (self.getbyte((cc.red() * 100 - 128 * N)/(100 - N)),
                        self.getbyte((cc.green() * 100 - 128 * N)/(100 - N)),
                        self.getbyte((cc.blue() * 100 - 128 * N)/(100 - N)))
                    self._img_preview.setPixel(i,j, qRgb(R,G,B))
                    #pix[i,j] = (self.getbyte(pix[i,j][0] + value), self.getbyte(pix[i,j][1] + value), self.getbyte(pix[i,j][2] + value))

    def changeRGB(self, value, imt):
        (width, height) = (self._img_preview.width(), self._img_preview.height())
        N  = value
        for i in range(width):
                for j in range(height):
                    cc = QColor(self._img_preview.pixel(i,j))
                    if (imt == 0):
                        R, G, B = (self.getbyte((cc.red() + (N * 128)/100)), cc.green(), cc.blue())
                    elif (imt == 1):
                        R, G, B = (cc.red(), self.getbyte((cc.green() + (N * 128)/100)), cc.blue())
                    else:
                        R, G, B = (cc.red(), cc.green(), self.getbyte((cc.blue() + (N * 128)/100)))
                    self._img_preview.setPixel(i,j, qRgb(R,G,B))
                    #pix[i,j] = (self.getbyte(pix[i,j][0] + value), self.getbyte(pix[i,j][1] + value), self.getbyte(pix[i,j][2] + value))


    def Change(self, value):
        self.get_edit_image()


    def getbyte(self, i):
        if (i > 255):
            return 255
        if (i < 0):
            return 0
        return int(i)




class ResizeDialog(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.btn = QPushButton('Dialog', self)
        self.btn.move(20, 20)
        self.btn.clicked.connect(self.showDialog)

        self.le = QLineEdit(self)
        self.le.move(65, 22)

        self.le = QLineEdit(self)
        self.le.move(65, 22)

        self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Input dialog')
        self.show()


    def showDialog(self):

        text, ok = QInputDialog.getText(self, 'Input Dialog',
            'Enter your name:')

        if ok:
            self.le.setText(str(text))








import pyqtgraph.examples
#pyqtgraph.examples.run()

app = QtWidgets.QApplication([])
application = mywindow()
application.show()

sys.exit(app.exec())
