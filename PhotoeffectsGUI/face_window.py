#!/usr/bin/python

#Katja and Charlotte

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os
import cv2
from time import gmtime, strftime
import subprocess


class PictureButton(QPushButton):
    '''QPushButton that contains an icon. Instantiated with a filename that 
    specifies the icon's path.'''
    def __init__(self, filename, window):
        QPushButton.__init__(self)
        self.window = window
        self.name = filename.split("/")[-1]
        self.setIcon(QIcon(filename))
        self.setFlat(1)
        self.setIconSize(QSize(50, 50))

    def click(self):
        '''Called automatically when button is clicked'''
        self.window.add_option_clicked(self.name)
   
   
        

class AddOptions(QWidget):
    '''Contains PictureButtons for each item/effect that can be added to a face.'''
    def __init__(self, window):
        QWidget.__init__(self)
        self.window = window
        self.setSizePolicy (QSizePolicy (QSizePolicy.Expanding, QSizePolicy.Fixed))
        self.setMinimumSize(200, 100)

        self.draw()

    def draw(self):
        '''Displays a PictureButton for each image in the icons directory.'''
        grid = QGridLayout()

        count = 0
        for img in os.listdir("photo_icons"):
            imgPath = os.path.join("photo_icons", img)
            button = PictureButton(imgPath,self.window)
            grid.addWidget(button, count/4, count % 4)
            button.clicked.connect(button.click)
            count+=1

        self.setLayout(grid)

    def paintEvent (self, eventQPaintEvent):
        '''Creates a 4x2 grid that surrounds buttons. Called automatically. Likely will be
        replaced by something cleaner.'''
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


class FaceOptions(QWidget):
    '''Displays all faces detected in the main image, with a checkbox for each face. Keeps track
    of where faces are located and which ones have been checked.'''
    def __init__(self, faces, rects):
        QWidget.__init__(self)
        self.faces = faces
        self.rects = rects
        self.checkboxes = []
        self.draw()
        
    def draw(self):
        '''Note: don't call this except in initialization.'''
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
        '''Returns the coordinates (in the original image) of the faces that have been selected
        (checked) in FaceOptions.'''
        return [self.rects[i] for i in range(len(self.rects)) if self.checkboxes[i].isChecked()]
            


            
class ControlBox(QWidget):
    '''Panel that contains all buttons/widgets except for main image and screenshot button.'''
    def __init__(self, faces, rects,window):
        QWidget.__init__(self)
        self.faces = faces
        self.rects = rects
        self.window = window
        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        self.setMinimumSize(400, 600)
        self.setMaximumSize(400, 700)

        self.draw()

    def draw(self):
        grid = QGridLayout()

        
        font = QFont("ArialMT",25)

        label = QLabel("Add effects to selected face(s)")
        label.setFont(font)
        grid.addWidget(label,1,0,Qt.AlignHCenter)
        
        self.faceChecks = FaceOptions(self.faces, self.rects)
        grid.addWidget(self.faceChecks, 2, 0)
        
        addOptions = AddOptions(self.window)
        grid.addWidget(addOptions, 3, 0)
        
        self.setLayout(grid)

    def paintEvent (self, eventQPaintEvent):
        '''Creates a black rectangle around the entire ControlBox. Called automatically.'''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        winHeight = self.size().height()
        winWidth  = self.size().width()

        painter.setPen(Qt.black)
        painter.drawRect(0, 0, winWidth, winHeight)

        painter.end()
        
     
class ImageBox(QWidget):
    '''Contains and regulates main image/video. Also contains screenshot button.'''
    def __init__(self):
        QWidget.__init__(self)
        self.pixmap = QPixmap("screenshot.jpg")
        self.piclabel = QLabel()
        self.grid = QGridLayout()
        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Expanding))
        self.draw()
        
    def draw(self):
        self.piclabel.setPixmap(self.pixmap)
        self.piclabel.setScaledContents(True)
        width = self.pixmap.size().width()
        height = self.pixmap.size().height()
        relationship = float(width)/height
        self.piclabel.setMinimumSize(relationship*600, 600)
        self.grid.addWidget(self.piclabel,0,0,1,3)
        
        
        button = QPushButton("Screenshot")
        button.clicked.connect(self.take_screenshot)
        self.grid.addWidget(button,1,1)
        self.setLayout(self.grid)
        
    def take_screenshot(self):
        time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        name = "PhotoScreenshots/screenshot-" + time_str + ".jpg"
        #call(["screencapture", '-l$(osascript', '-e', '"tell', 'app', '"Python"', 'to', 'id', 'of', 'window', '1")', "test.png"])
        #subprocess.check_call('screencapture -l$(osascript -e \'tell app "Python" to id of window 1\') test.png')
        subprocess.call(["screencapture", name])
        
    def draw_object(self,rects,icon_name):
        '''Redraws main image to include clicked item/effect for given faces.'''
        base = self.pixmap
        overlay = QPixmap(os.path.join("icons", icon_name))
        result = QPixmap(base.width(), base.height())
        result.fill(Qt.black)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, base)
        
        # Draws icon on each face given.
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
                face_image = base.copy(rect[0], rect[1], width, height).toImage()

                blurred_image = face_image.copy()

                blur_amount = width/8
                current_color = QColor.fromRgb(blurred_image.pixel(blur_amount/2, blur_amount/2))
                for y in range(blur_amount, face_image.height() - blur_amount):
                    for x in range(blur_amount, face_image.width() - blur_amount):
                        if (x+ blur_amount/2)%blur_amount == 0 or (y+ blur_amount/2)%blur_amount == 0:
                            current_color = QColor.fromRgb(blurred_image.pixel(x, y))
                        else: 
                            blurred_image.setPixel(x, y, qRgb(current_color.red(), current_color.green(), current_color.blue()))
                blurred_pixmap = QPixmap.fromImage(blurred_image)
                amount_to_go_down = 0

                painter.drawPixmap(rect[0], rect[1]+amount_to_go_down, blurred_pixmap)
            else:
                print "Not implemeneted yet"
        
        # Redraws image
        self.pixmap = result
        self.grid.removeWidget(self.piclabel)
        self.draw()
        painter.end()


class GuiWindow(QWidget):
    '''Creates a main GUI Window that contains all other objects and handles interactions between them.'''
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
        '''When PictureButton is clicked, tells main image to redraw appropriately.'''
        checked_boxes = self.rightbox.faceChecks.getCheckedFaces()
        self.leftbox.draw_object(checked_boxes,button_name)
        

def detect(path):
    '''Detects areas of given image that contain faces. Will be replaced by something from the architecture.'''
    img = cv2.imread(path)
    face_cascade = cv2.CascadeClassifier("face_cascade2.xml")
    rects = face_cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img

def get_faces(image_path):
    '''Returns images of faces and their locations in the original image. 
    Will be replaced by something from our architecture.'''
    rects, img = detect(image_path)
    faces = []
    for rect in rects:
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