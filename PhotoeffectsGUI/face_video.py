#!/usr/bin/python

#Katja and Charlotte

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os
# Change for particular machine
sys.path.append("/Users/Katja/COMPS/facial-recognition/Tracking")
#sys.path.append("/Accounts/collierk/COMPS/facial-recognition/Tracking")
#import architecture
#from architecture import *
from video import Video
import cv2, cv
import time
from random import *
import subprocess
#from PIL import Image
import numpy
from time import gmtime, strftime


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
        #print self.name, "was clicked!"
        self.window.add_option_clicked(self.name)
   
   
class DrawOptions(QWidget):
    '''Currently creates empty grid. Will include buttons with icons for drawing on image.'''
    def __init__(self):
        QWidget.__init__(self)

        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        self.setMinimumSize(200, 100)

    def paintEvent (self, eventQPaintEvent):
        '''Creates a 4x2 grid that someday will be buttons. Called automatically.'''
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
        for img in os.listdir("icons"):
            if img[0:2] != "._":
                imgPath = os.path.join("icons", img)
                button = PictureButton(imgPath,self.window)
                grid.addWidget(button, count/4, count % 4)
                button.clicked.connect(button.click)
                count+=1
                #print img
        #print count

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
    def __init__(self):
        QWidget.__init__(self)
        self.faces = []
        self.face_pics = []
        self.face_ids = []
        self.old_face_ids = []
        self.checkboxes = []
        self.grid = QGridLayout()
        self.old_face_pics = []
        self.old_checks = []
        
        
    def setFaces(self, face_pics, faces):
        self.faces = faces
        self.face_pics = face_pics
        
#        self.face_ids_new = [f.getID() for f in self.faces if not f.obscured]
#        print "old vs. new face_IDS:", self.face_ids_new
        self.face_ids = [f.getID() for f in self.faces]
        #print "old vs. new face_IDS:", self.old_face_ids, self.face_ids
        #print "checked boxes:", [c.isChecked() for c in self.checkboxes]
        if set(self.old_face_ids) != set(self.face_ids):
            self.draw()
#        self.draw()
#        if set(self.old_face_ids) != set(self.face_ids_new):
#            self.draw()


    def draw(self):
        '''Note: don't call this except in initialization.'''
        print "in draw"
        count = 0
        
        # This is bad. Don't uncomment.
#        for pic in self.old_face_pics:
#            self.grid.removeWidget(pic)
#        for check in self.old_checks:
#            self.grid.removeWidget(check)
    
        self.deleteAll()

        self.old_face_pics = []
        self.old_checks = []
        for img in self.face_pics:
            pixmap = QPixmap(img)
            piclabel = QLabel()
            piclabel.setPixmap(pixmap)
            piclabel.setScaledContents(True)
            width = pixmap.size().width()
            height = pixmap.size().height()
            relationship = float(width)/height
            piclabel.setMaximumSize(relationship*60, 60)
            piclabel.setMinimumSize(relationship*60, 60)
            self.grid.addWidget(piclabel, 2 + 2*(count/3),count % 3)
            checkbox = QCheckBox()
            self.checkboxes.append(checkbox)
            self.grid.addWidget(checkbox, 3 + 2*(count/3), count % 3, Qt.AlignHCenter)
            count+=1
            print "?:", count, 3 + 2*(count/3), count % 3
            self.old_face_pics.append(piclabel)
            self.old_checks.append(checkbox)
            
        while count % 3 != 0:
            self.grid.addWidget(QLabel(), 2 + 2*(count/3),count % 3)
            self.grid.addWidget(QLabel(), 3 + 2*(count/3),count % 3)
            count+=1
            
        self.old_face_ids = [f.getID() for f in self.faces]
        #print self.old_face_IDs
        #self.old_face_ids = [f.getID() for f in self.faces if not f.obscured]
        self.setLayout(self.grid)
    
    def deleteAll(self):
        self.checkboxes = []
        for i in range(self.grid.count()):
            child = self.grid.takeAt(i)
            #print i
            if child:
                x = child.widget()
                x.setParent(None)
                del x
        
    def getCheckedFaces(self):
        '''Returns the face ids of the faces that have been selected
        (checked) in FaceOptions.'''
        #return [self.rects[i] for i in range(len(self.rects)) if self.checkboxes[i].isChecked()]
        
        return [self.faces[i] for i in range(len(self.faces)) if self.checkboxes[i].isChecked()]
            

            
class ControlBox(QWidget):
    '''Panel that contains all buttons/widgets except for main image and screenshot button.'''
    def __init__(self,window):
        QWidget.__init__(self)
        self.faces = []
        self.rects = []
        self.window = window
        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Expanding))
        self.setMinimumSize(400, 600)
        self.grid = QGridLayout()
        self.faceChecks = FaceOptions()
        self.draw()
    
    def setFaces(self,face_pics, faces):
        self.face_pics = face_pics
        self.faces = faces
        
        # Redraws image
        self.grid.removeWidget(self.faceChecks)
        self.faceChecks.setFaces(self.face_pics, self.faces)
        self.grid.addWidget(self.faceChecks, 2, 0)

    def draw(self):
        ppbutton = QPushButton("Play/Pause")
        ppbutton.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        ppbutton.setMinimumSize(200, 50)
        self.grid.addWidget(ppbutton, 0, 0)
        
        label = QLabel("Add effects to selected face(s)")
        self.grid.addWidget(label,1,0,Qt.AlignHCenter)
        
        addOptions = AddOptions(self.window)
        self.grid.addWidget(addOptions, 3, 0)
        
        num_button = QPushButton()
        num_button.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Fixed))
        num_button.setMinimumSize(100, 100)
        num_button.setIcon(QIcon("numbers.jpg"))
        num_button.setIconSize(QSize(100, 75))
        num_button.clicked.connect(self.window.toggle_nums)
        self.grid.addWidget(num_button,4,0)
        
#        label = QLabel("Draw")
#        self.grid.addWidget(label,4,0,Qt.AlignHCenter)
        
#        drawOptions = DrawOptions()
#        self.grid.addWidget(drawOptions, 5, 0)
        
        self.setLayout(self.grid)
        
        
        

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
        self.piclabel = QLabel()
        self.grid = QGridLayout()
        self.pixmap = None
        self.face_pics = []
        #self.draw()
        #self.faces = []
        
    def set_image(self, img, faces, face_pics):
        #self.pixmap = QPixmap(img)
        self.pixmap = img
        self.draw_objects(faces)
        self.face_pics = face_pics
        
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
        button.clicked.connect(self.take_screenshot)
        self.grid.addWidget(button,1,1)
        self.setLayout(self.grid)
        
    def take_screenshot(self):
        time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        name = "Screenshots/screenshot-" + time_str + ".jpg"
        #call(["screencapture", '-l$(osascript', '-e', '"tell', 'app', '"Python"', 'to', 'id', 'of', 'window', '1")', "test.png"])
        #subprocess.check_call('screencapture -l$(osascript -e \'tell app "Python" to id of window 1\') test.png')
        subprocess.call(["screencapture", name])
        
    def draw_objects(self,faces):
        '''Redraws main image to include clicked item/effect for given faces.'''
        base = self.pixmap
        #overlay = QPixmap(os.path.join("icons", icon_name))
        result = QPixmap(base.width(), base.height())
        result.fill(Qt.black)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, base)
        
        # Draws icon on each face given.
        for face in faces:
            if not face.isObscured():
                tuples = face.getPosition()
                rect = [tuples[0][0], tuples[0][1], tuples[1][0], tuples[1][1]]
                for icon_name, icon_id in face.attachedObjects:
                    overlay = QPixmap(os.path.join("icons", icon_name))
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
                        face_image = base.copy(rect[0]+5, rect[1]-10, width-10, height+20).toImage()
                        blurred_image = face_image.copy()
                        b_a = width/12
                        cur = QColor.fromRgb(blurred_image.pixel(b_a/2, b_a/2))
                        for y in range(b_a, face_image.height() - b_a):
                            for x in range(b_a, face_image.width() - b_a):
                                if (x+ b_a/2)%b_a == 0 or (y+ b_a/2)%b_a == 0:
                                    cur = QColor.fromRgb(blurred_image.pixel(x, y))
                                else: 
                                    blurred_image.setPixel(x, y, qRgb(cur.red(), cur.green(), cur.blue()))
                        blurred_pixmap = QPixmap.fromImage(blurred_image)
                        painter.drawPixmap(rect[0], rect[1], blurred_pixmap)
                    elif icon_name == "trashcan.png":
                        for face in faces:
                            face.attachedObjects = []       
                    elif icon_name == "faceswap.png": 
                        index_to_swap = icon_id
                        #if (icon_id < 0) or (icon_id not in [f.getID for f in faces]):
                        if (icon_id < 0):
                            index_to_swap = randint(0, len(self.face_pics) - 1)
                            while index_to_swap == faces.index(face):
                                index_to_swap = randint(0, len(self.face_pics) - 1)
                            face.removeAttachedObject(("faceswap.png", icon_id))
                            face.addAttachedObject(("faceswap.png", index_to_swap))
                        overlay_copy = QPixmap(self.face_pics[index_to_swap])
                        overlay_copy = overlay_copy.scaledToWidth(width)
                        painter.drawPixmap(rect[0], rect[1], overlay_copy)
                        
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
        self.face_list = []
        self.draw_nums = False
        self.draw()
        
        

    def draw(self):
        grid = QGridLayout()
        
        self.leftbox = ImageBox()
        grid.addWidget(self.leftbox,0,0)

        self.rightbox = ControlBox(self)
        grid.addWidget(self.rightbox, 0, 1)
        
        variables = (0.001, 10, 5, 100, (1,1,1), False)
        #vid = Video(0,variables, showWindow=False)
        vid = Video(0,variables)
        
        while(True):
            vid.readFrame()
            #self.rightbox.setFaces(faces2, rects)
            frame_as_string_before = vid.getCurrentFrame().tostring()
            vid.findFaces()
            self.face_list = vid.getFaces()
            
            
            if self.draw_nums:
                for i in range(len(self.face_list)):
                    vid.showRectangle(self.face_list[i].getPosition(),self.face_list[i].getID())
                
                
                
            frame = vid.getCurrentFrame()
            
            rects = []
            #self.face_list = vid.getFaces()
            for face in self.face_list:
                tuples = face.getPosition()
                rects.append([tuples[0][0], tuples[0][1], tuples[1][0], tuples[1][1]])
                #print face.getID()
                

            frame_as_string_in_between = frame.tostring()
            #assert frame_as_string_before == frame_as_string_in_between

            cv2.cvtColor(frame, cv.CV_BGR2RGB, frame)
            frame_as_string = frame.tostring()
            
            image = QImage(frame_as_string,\
            frame.shape[1],frame.shape[0],QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image) 
            
            
            face_pics = get_imgs_from_rects(image, rects)
           
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            self.leftbox.set_image(pixmap, self.face_list, face_pics)
            self.rightbox.setFaces(face_pics, self.face_list)
            
            self.setLayout(grid)
            self.show()
            
    def toggle_nums(self):
        self.draw_nums = not self.draw_nums
            
    

    def add_option_clicked(self, button_name):
        '''When PictureButton is clicked, tells main image to redraw appropriately.'''
        checked_faces = self.rightbox.faceChecks.getCheckedFaces()
        #print "face ids:", checked_faces, " button_name:", button_name
        
        # Make this actually work! Should alter face objects to add the new "thing", then 
        # need to change code in ImageBox or GuiWindow.draw() to draw things on faces
        for face in checked_faces:
            face.addAttachedObject((button_name, -1))
        
        # Old code: drew on image
        self.leftbox.draw_objects(checked_faces)
        
        # 
        

def detect(path):
    '''Detects areas of given image that contain faces. Will be replaced by something from the architecture.'''
    img = cv2.imread(path)
    # Change for particular machine.
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
        #listrect = rect.tolist()
        qimg = QImage(image_path)
        copy = qimg.copy(rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1])
        faces.append(copy)
    return faces, rects
    
    
def get_imgs_from_rects(img, rects):
    '''Returns images of faces and their locations in the original image. 
    Will be replaced by something from our architecture.'''
    #rects, img = detect(image_path)
    faces = []
    for rect in rects:
        #listrect = rect.tolist()
        #qimg = QImage(image_path)
        copy = img.copy(rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1])
        faces.append(copy)
    return faces
    


def main():
    app = QApplication(sys.argv)
    face_window = GuiWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
