#!/usr/bin/python

#Katja and Charlotte

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os
sys.path.append("/Users/Katja/COMPS/facial-recognition/Tracking")
import architecture
from architecture import *
import cv2
from PIL import Image


class PictureButton(QPushButton):
    def __init__(self, filename):
        QPushButton.__init__(self)
        self.name = filename.split("/")[-1]
        self.name = self.name.split(".")[0]
        self.setIcon(QIcon(filename))
        self.setFlat(1)
        self.setIconSize(QSize(50, 50))

    def something(self):
        print self.name, "was clicked!"
        #self.window.add_option_clicked(self.name)


class ImageBox(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

    def draw(self):

        grid2 = QGridLayout()

        pixmap = QPixmap("screenshot.jpg")
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
    def __init__(self, faces, rects):
        QWidget.__init__(self)
        self.faces = faces
        self.rects = rects
        self.draw()

    def something(self, imgPath):
        pass

    def draw(self):
        grid = QGridLayout()
        ppbutton = QPushButton("Play/Pause")
        grid.addWidget(ppbutton, 0, 0)

        ppbutton.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        ppbutton.setMinimumSize(200, 50)

        label = QLabel("Add effects to selected face(s)")
        grid.addWidget(label,1,0,Qt.AlignHCenter)

        faceChecks = FaceOptions(self.faces,self)
        grid.addWidget(faceChecks, 2, 0)

        addOptions = AddOptions(self)
        grid.addWidget(addOptions, 3, 0)

        self.setLayout(grid) 


class BottomSection(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.draw()

    def draw(self):
        grid = QGridLayout()

        label = QLabel("Draw")
        grid.addWidget(label,0,0,Qt.AlignHCenter)


        drawOptions = DrawOptions()
        grid.addWidget(drawOptions, 1, 0)

        self.setLayout(grid) 




class FaceOptions(QWidget):
    def __init__(self, faces,parent):
        QWidget.__init__(self)
        self.faces = faces
        self.parent = parent
        self.draw()
        self.checkboxes = []

    def draw(self):
        self.checkboxes = []
        grid = QGridLayout()

        count = 0
        for img in self.faces:
            pixmap = QPixmap(img)
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
            self.checkboxes.append(checkbox)
            grid.addWidget(checkbox, 3 + 2*(count/3), count % 3, Qt.AlignHCenter)
            count+=1

        self.setLayout(grid)
            

class AddOptions(QWidget):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.parent = parent
        self.setSizePolicy (QSizePolicy (QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.setMinimumSize(200, 100)

        self.draw()



    def draw(self):
        grid = QGridLayout()

        count = 0
        for img in os.listdir("icons"):
            imgPath = os.path.join("icons", img)
            button = PictureButton(imgPath)
            grid.addWidget(button, count/4, count % 4)
            button.clicked.connect(button.something)
            count+=1

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

        # count = 0
        # for img in os.listdir("icons"):
        #     imgPath = os.path.join("icons", img)
        #     button = PictureButton(imgPath)
        #     grid.addWidget(button, count/4, count % 4)
        #     button.clicked.connect(button.print_words)
        #     count+=1
        
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
    def __init__(self, faces, rects):
        QWidget.__init__(self)
        self.faces = faces
        self.rects = rects
        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Expanding))
        self.setMinimumSize(350, 600)

        self.draw()

    def draw(self):

        grid = QGridLayout()

        top_box = TopSection(self.faces, self.rects)
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
        self.draw()

    def draw(self):
        grid = QGridLayout()

        faces, rects = get_faces("screenshot.jpg")

        leftbox = ImageBox()
        grid.addWidget(leftbox,0,0)


        rightbox = ControlBox(faces,rects)
        grid.addWidget(rightbox, 0, 1)


        self.setLayout(grid)
        self.show()

    def add_option_clicked(self, button_name):
        # need to know which boxes are checked in FaceOptions
        # apply new add_option to all checked faces (which are rects in imageBox)
        pass

def detect(path):
    img = cv2.imread(path)
    face_cascade = cv2.CascadeClassifier("/Users/Katja/Downloads/haarcascade_frontalface_alt.xml")
    rects = face_cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img

def get_faces(image_path):
    rects, img = detect(image_path)
    faces = []
    for rect in rects:
        print rect
        listrect = rect.tolist()
        qimg = QImage(image_path)
        # copy = QImage()
        copy = qimg.copy(listrect[0],listrect[1],listrect[2]-listrect[0],listrect[3]-listrect[1]);
        # face = Face()
        # face.setPosition(rect)
        faces.append(copy)
    return faces, rects

def main():
    app = QApplication(sys.argv)
    face_window = GuiWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()