#!/usr/bin/python

#Katja and Charlotte

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os


class ImageBox(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

    def draw(self):

        grid2 = QGridLayout()

        pixmap = QPixmap("tree1.jpg")
        piclabel = QLabel()
        piclabel.setPixmap(pixmap)

        piclabel.setScaledContents(True)
        width = pixmap.size().width()
        height = pixmap.size().height()
        relationship = float(width)/height
        piclabel.setMaximumSize(relationship*300, 300)
        piclabel.setMinimumSize(relationship*300, 300)
        grid2.addWidget(piclabel,0,0,1,3)

        button = QPushButton("Screenshot")
        grid2.addWidget(button,1,1)

        self.setLayout(grid2)

class TopSection(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

    def draw(self):
        grid = QGridLayout()
        ppbutton = QPushButton("Play/Pause")
        grid.addWidget(ppbutton, 0, 0)

        ppbutton.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        ppbutton.setMinimumSize(200, 50)

        label = QLabel("Do things to face")
        grid.addWidget(label,1,0,Qt.AlignHCenter)

        faceChecks = FaceOptions()
        grid.addWidget(faceChecks, 2, 0)

        drawOptions = DrawOptions()
        grid.addWidget(drawOptions, 3, 0)

        self.setLayout(grid) 


class BottomSection(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

    def draw(self):
        grid = QGridLayout()

        label = QLabel("Add")
        grid.addWidget(label,0,0,Qt.AlignHCenter)


        drawOptions = DrawOptions()
        grid.addWidget(drawOptions, 1, 0)

        self.setLayout(grid) 




class FaceOptions(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

    def draw(self):
        grid = QGridLayout()

        count = 0
        for img in os.listdir("testpics"):
            imgPath = os.path.join("testpics", img)
            pixmap = QPixmap(imgPath)
            piclabel = QLabel()
            piclabel.setPixmap(pixmap)
            piclabel.setScaledContents(True)
            width = pixmap.size().width()
            height = pixmap.size().height()
            relationship = float(width)/height
            piclabel.setMaximumSize(relationship*60, 60)
            piclabel.setMinimumSize(relationship*60, 60)
            grid.addWidget(piclabel, 2 + 2*(count/3),count % 3)

            checkbox = QCheckBox()
            grid.addWidget(checkbox, 3 + 2*(count/3), count % 3, Qt.AlignHCenter)
            count+=1

        self.setLayout(grid)
            

class DrawOptions(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        self.setMinimumSize(200, 100)

    def draw(self):
        grid = QGridLayout()

        
        self.setLayout(grid)

    def paintEvent (self, eventQPaintEvent):


        myQPainter = QPainter(self)
        myQPainter.setRenderHint(QPainter.Antialiasing)
        winHeight = self.size().height()
        heightStep = winHeight / 2
        winWidth  = self.size().width()
        widthStep = winWidth / 4

        myQPainter.setPen(Qt.black)
        for i in range(8):
            myQPainter.drawLine(QPoint(i * widthStep, 0), QPoint(i * widthStep, winHeight))
            myQPainter.drawLine(QPoint(0,heightStep * i), QPoint(winWidth,heightStep * i))


            


class ControlBox(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Expanding))
        self.setMinimumSize(350, 600)

        self.draw()

    def draw(self):

        grid = QGridLayout()

        top_box = TopSection()
        grid.addWidget(top_box,0,0)

        bottom_box = BottomSection()
        grid.addWidget(bottom_box, 1, 0)

        self.setLayout(grid)

    def paintEvent (self, eventQPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        winHeight = self.size().height()
        winWidth  = self.size().width()

        painter.setPen(Qt.black)
        painter.drawRect(0, 0, winWidth, winHeight)

        painter.end()

    
class GuiWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.make_shit()

    def make_shit(self):
        grid = QGridLayout()

        leftbox = ImageBox()
        grid.addWidget(leftbox,0,0)

        rightbox = ControlBox()
        grid.addWidget(rightbox, 0, 1)


        self.setLayout(grid)
        self.show()



def main():
    app = QApplication(sys.argv)
    face_window = GuiWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()