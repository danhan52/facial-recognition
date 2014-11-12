#!/usr/bin/python

#Katja and Charlotte

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os
sys.path.append("/Users/Katja/COMPS/facial-recognition/Tracking")
sys.path.append("/Accounts/collierk/COMPS/facial-recognition/Tracking")
import architecture
from architecture import *
import cv2
from PIL import Image


class PictureButton(QPushButton):
    def __init__(self, filename, window):
        QPushButton.__init__(self)
        self.window = window
        self.name = filename.split("/")[-1]
        #self.name = self.name.split(".")[0]
        self.setIcon(QIcon(filename))
        self.setFlat(1)
        self.setIconSize(QSize(50, 50))

    def click(self):
        print self.name, "was clicked!"
        self.window.add_option_clicked(self.name)


class ImageBox(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.pixmap = QPixmap("screenshot.jpg")
        
        self.piclabel = QLabel()
        self.grid = QGridLayout()
        self.draw()
        

    def draw(self):
        self.piclabel.setPixmap(self.pixmap)

        self.piclabel.setScaledContents(True)
        width = self.pixmap.size().width()
        height = self.pixmap.size().height()
        relationship = float(width)/height
        self.piclabel.setMaximumSize(relationship*500, 500)
        self.piclabel.setMinimumSize(relationship*500, 500)
        self.grid.addWidget(self.piclabel,0,0,1,3)

        button = QPushButton("Screenshot")
        self.grid.addWidget(button,1,1)

        self.setLayout(self.grid)
        
    def draw_object(self,rects,icon_name):
        base = self.pixmap
        overlay = QPixmap(os.path.join("icons", icon_name))
        result = QPixmap(base.width(), base.height())
        result.fill(Qt.black)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, base)
        
        for rect in rects:
            overlay_copy = overlay.copy()
            width = rect[2]-rect[0]
            height = rect[3]-rect[1]
            if icon_name == "yellow-sunglasses.png":
                overlay_copy = overlay_copy.scaledToWidth(width)
                amount_to_go_down = height/4.5
                painter.drawPixmap(rect[0], rect[1] + amount_to_go_down, overlay_copy)
            elif icon_name == "mustache.png":
                overlay_copy = overlay_copy.scaledToWidth(width/2.0)
                amount_to_go_down = 3.0*height/5.0
                painter.drawPixmap(rect[0]+width/4.0, rect[1] + amount_to_go_down, overlay_copy)
            elif icon_name == "purplehat.png":
                overlay_copy = overlay_copy.scaledToWidth(width*2)
                amount_to_go_down = -3.0*height/5.0
                painter.drawPixmap(rect[0]-width/2.25, rect[1] + amount_to_go_down, overlay_copy)
            elif icon_name == "groucho_glasses.png":
                overlay_copy = overlay_copy.scaledToWidth(width)
                amount_to_go_down = 0
                painter.drawPixmap(rect[0], rect[1] + amount_to_go_down, overlay_copy)
            elif icon_name == "blurry.jpg":
                overlay_copy = overlay_copy.scaledToWidth(width*1.5)
                amount_to_go_down = -height/3.0
                painter.drawPixmap(rect[0]-width/4.0, rect[1] + amount_to_go_down, overlay_copy)
            else:
                print "Not implemeneted yet"
        
        
        
        
        self.pixmap = result
        self.grid.removeWidget(self.piclabel)
        self.draw()
        painter.end()
        
    

class TopSection(QWidget):
    def __init__(self, faces, rects, window):
        QWidget.__init__(self)
        self.window = window
        self.faces = faces
        self.rects = rects
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

        label = QLabel("Add effects to selected face(s)")
        grid.addWidget(label,1,0,Qt.AlignHCenter)

        self.faceChecks = FaceOptions(self.faces, self.rects)
        grid.addWidget(self.faceChecks, 2, 0)

        addOptions = AddOptions(self.window)
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
    def __init__(self, faces, rects):
        QWidget.__init__(self)
        self.faces = faces
        self.rects = rects
        self.checkboxes = []
        self.draw()
        

    def draw(self):
       # self.checkboxes = []
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
        
    def getCheckedFaces(self):
        return [self.rects[i] for i in range(len(self.rects)) if self.checkboxes[i].isChecked()]
            

class AddOptions(QWidget):
    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.setSizePolicy (QSizePolicy (QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.setMinimumSize(200, 100)

        self.draw()



    def draw(self):
        grid = QGridLayout()

        count = 0
        for img in os.listdir("icons"):
            imgPath = os.path.join("icons", img)
            button = PictureButton(imgPath,self.window)
            grid.addWidget(button, count/4, count % 4)
            button.clicked.connect(button.click)
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
    def __init__(self, faces, rects,window):
        QWidget.__init__(self)
        self.faces = faces
        self.rects = rects
        self.window = window
        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Expanding))
        self.setMinimumSize(350, 600)

        self.draw()

    def draw(self):

        grid = QGridLayout()

        self.top_box = TopSection(self.faces, self.rects, self.window)
        grid.addWidget(self.top_box,0,0)

        self.bottom_box = BottomSection()
        grid.addWidget(self.bottom_box, 1, 0)

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

        self.leftbox = ImageBox()
        grid.addWidget(self.leftbox,0,0)


        self.rightbox = ControlBox(faces,rects,self)
        grid.addWidget(self.rightbox, 0, 1)


        self.setLayout(grid)
        self.show()

    def add_option_clicked(self, button_name):
        checked_boxes = self.rightbox.top_box.faceChecks.getCheckedFaces()
        print checked_boxes
        print button_name
        self.leftbox.draw_object(checked_boxes,button_name)
        
        # need to know which boxes are checked in FaceOptions
        # apply new add_option to all checked faces (which are rects in imageBox)

def detect(path):
    img = cv2.imread(path)
    face_cascade = cv2.CascadeClassifier("/Accounts/collierk/Downloads/haarcascade_frontalface_alt.xml")
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
        copy = qimg.copy(listrect[0],listrect[1],listrect[2]-listrect[0],listrect[3]-listrect[1])
        faces.append(copy)
    return faces, rects

def main():
    app = QApplication(sys.argv)
    face_window = GuiWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()