#!/usr/bin/python

#Katja and Charlotte

# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import os

from video import Video
import cv2, cv
import time
from random import *
import subprocess

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
        for img in os.listdir("icons"):
            if img[0:2] != "._":
                imgPath = os.path.join("icons", img)
                button = PictureButton(imgPath,self.window)
                grid.addWidget(button, count/4, count % 4)
                button.clicked.connect(button.click)
                count+=1

        self.setLayout(grid)

    def paintEvent (self, eventQPaintEvent):
        '''Creates a 4x2 grid that surrounds buttons. Called automatically.'''
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
        self.count = 0
           
    def setFaces(self, face_pics, faces):
        '''Called each frame. Keeps track of current faces, redraws every 50 frames or whenever
        number of faces changes.'''
        self.faces = faces
        self.face_pics = face_pics
        self.count += 1
        self.face_ids = [f.getID() for f in self.faces]
        if set(self.old_face_ids) != set(self.face_ids) or (self.count%50 == 0):
            # Deletes old faces/checkboxes
            self.deleteAll()
            self.draw()

    def draw(self):
        '''Draws the small faces and checkboxes.'''
               
        count = 0
        self.old_face_pics = []
        self.old_checks = []
        
        # For each found face, add a face/checkbox pair
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
            self.old_face_pics.append(piclabel)
            self.old_checks.append(checkbox)
            
        # Add empty faces to fill up space   
        while count % 3 != 0:
            piclabel = QLabel()
            piclabel.setMaximumSize(relationship*60, 60)
            piclabel.setMinimumSize(relationship*60, 60)
            self.grid.addWidget(piclabel, 2 + 2*(count/3),count % 3)
            self.grid.addWidget(QLabel(), 3 + 2*(count/3),count % 3)
            count+=1
            
        self.old_face_ids = [f.getID() for f in self.faces]
        self.setLayout(self.grid)
    
    def deleteAll(self):
        '''Deletes old faces and checkboxes (has some issues)'''
        self.checkboxes = []
        q = self.grid.count()

        for i in range(q):
            child = self.grid.takeAt(0)
            if child:
                x = child.widget()
                x.setParent(None)
                x.deleteLater()
                del x

                
        
    def getCheckedFaces(self):
        '''Returns the face ids of the faces that have been selected
        (checked) in FaceOptions.'''
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
                QSizePolicy.Fixed))
        self.setMinimumSize(400, 600)
        self.setMaximumSize(400, 600)
        self.grid = QGridLayout()
        self.faceChecks = FaceOptions()
        self.draw()
    
    def setFaces(self,face_pics, faces):
        '''Called every frame; refreshes faces'''
        self.face_pics = face_pics
        self.faces = faces
        
        # Redraws image
        self.grid.removeWidget(self.faceChecks)
        self.faceChecks.setFaces(self.face_pics, self.faces)
        self.grid.addWidget(self.faceChecks, 2, 0)

    def draw(self):
        '''Creates the right control panel'''
        
        font = QFont("ArialMT",25)
        label = QLabel("Add effects to selected face(s)")
        label.setFont(font)
        self.grid.addWidget(label,1,0,Qt.AlignHCenter)
        
        addOptions = AddOptions(self.window)
        self.grid.addWidget(addOptions, 3, 0)
        
        # Button that controls whether boxes are drawn around faces
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
        self.all_faces = []

        
        self.setSizePolicy (
            QSizePolicy (
                QSizePolicy.Expanding,
                QSizePolicy.Expanding))
        
    def set_image(self, img, faces, face_pics):
        '''Called every frame. Draws main image + effects.'''
        self.pixmap = img
        self.face_pics = face_pics
        self.all_faces = faces
        self.draw_objects(faces)
        
        
    def draw(self):
        '''Called once, sets up picture area and screenshot button.'''
        self.piclabel.setPixmap(self.pixmap)
        self.piclabel.setScaledContents(True)
        width = self.pixmap.size().width()
        height = self.pixmap.size().height()
        relationship = float(width)/height
        self.piclabel.setMinimumSize(relationship*500, 500)
        self.grid.addWidget(self.piclabel,0,0,1,3)
        
        button = QPushButton("Screenshot")
        button.clicked.connect(self.take_screenshot)
        self.grid.addWidget(button,1,1)
        self.setLayout(self.grid)
        
    def take_screenshot(self):
        '''Makes screenshot buttom functional. Takes screenshot of entire screen.'''
        time_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        name = "Screenshots/screenshot-" + time_str + ".jpg"
        #call(["screencapture", '-l$(osascript', '-e', '"tell', 'app', '"Python"', 'to', 'id', 'of', 'window', '1")', "test.png"])
        #subprocess.check_call('screencapture -l$(osascript -e \'tell app "Python" to id of window 1\') test.png')
        subprocess.call(["screencapture", name])
        
    def draw_objects(self,faces):
        '''Redraws main image to include clicked item/effect for given faces.'''
        base = self.pixmap
        result = QPixmap(base.width(), base.height())
        result.fill(Qt.black)
        painter = QPainter(result)
        painter.drawPixmap(0, 0, base)
        
        # Draws icon on each face given.
        for face in faces:
            if not face.isObscured():
                tuples = face.getPosition()
                rect = [tuples[0][0], tuples[0][1], tuples[1][0], tuples[1][1]]
                for icon_name, id_to_swap in face.attachedObjects:
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
                    elif icon_name == "panda.png":
                        overlay_copy = overlay_copy.scaledToWidth(width * 1.4)
                        amount_to_go_down = -.2*height
                        painter.drawPixmap(rect[0] - width/6.0, rect[1] + amount_to_go_down, overlay_copy)
                    elif icon_name == "blurry.jpg":
                        face_image = base.copy(rect[0], rect[1], width, height).toImage()
                        blurred_image = face_image.copy()
                        blur_amount = width/8
                        # Keeps a specific color to set many pixels to
                        current_color = QColor.fromRgb(blurred_image.pixel(blur_amount/2, blur_amount/2))
                        # Loops over each pixel in range of face, set to current color, change every 1/8 of image
                        for y in range(blur_amount, face_image.height() - blur_amount):
                            for x in range(blur_amount, face_image.width() - blur_amount):
                                if (x + blur_amount/2) % blur_amount == 0 or (y + blur_amount/2) % blur_amount == 0:
                                    current_color = QColor.fromRgb(blurred_image.pixel(x, y))
                                else: 
                                    blurred_image.setPixel(x, y, qRgb(current_color.red(), current_color.green(), current_color.blue()))
                        blurred_pixmap = QPixmap.fromImage(blurred_image)
                        amount_to_go_down = 0  
                        painter.drawPixmap(rect[0], rect[1]+amount_to_go_down, blurred_pixmap)
                    elif icon_name == "trashcan.png":
                        for face in faces:
                            face.attachedObjects = []       
                    elif icon_name == "faceswap.png": 
                        # As long as there are at least two faces in the frame
                        if len(self.all_faces) >= 2:
                            # If face id to swap with is already set to a face currently/recently in the image, keep it
                            face_to_swap = [f for f in self.all_faces if f.id == id_to_swap]
                            # If there was no face that matched the desired swapping id 
                            # (either it left the frame, or id == -1, aka it had not been chosen yet)
                            # then pick a new face
                            while not face_to_swap:
                                index_to_swap = randint(0, len(self.face_pics) - 1)
                                # Don't swap with yourself
                                while index_to_swap == self.all_faces.index(face):
                                    index_to_swap = randint(0, len(self.face_pics) - 1)
                                face.removeAttachedObject(("faceswap.png", id_to_swap))
                                id_to_swap = self.all_faces[index_to_swap].id
                                face.addAttachedObject(("faceswap.png", id_to_swap))
                                face_to_swap = [f for f in self.all_faces if f.id == id_to_swap]
                            # Finds the actual face image to swap, given the ID
                            pic = self.face_pics[self.all_faces.index(face_to_swap[0])]
                            overlay_copy = QPixmap(pic)
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
        self.setWindowTitle("Live Video Tracking with Effects!")
        self.draw()
        self.connect(self, Qt.SIGNAL('triggered()'), self.closeEvent)
        
      
    def closeEvent(self, e):
        '''If top red x clicked, end program.'''
        sys.exit()
             

    def draw(self):
        '''Draws main GUI, then loops on frames'''
        grid = QGridLayout()
        
        self.leftbox = ImageBox()
        grid.addWidget(self.leftbox,0,0)

        self.rightbox = ControlBox(self)
        grid.addWidget(self.rightbox, 0, 1)
        
        variables = (0.25, 10, 5, 100, (0.5,0,0.5), False, (200.0,0.34,0.25), 2)
        #create Video object
        vid = Video(0,variables)
        
        while(True):
            
            # Read every frame and extract images
            vid.readFrame()
            frame_as_string_before = vid.getCurrentFrame().tostring()
            vid.findFaces()
            self.face_list = vid.getFaces()
            
            # If we've clicked the num button, draw rectangles around each face
            if self.draw_nums:
                for i in range(len(self.face_list)):
                    # Uncomment if we don't want to use predicted position
#                    vid.showRectangle(self.face_list[i].getPosition(),self.face_list[i].getID())
                    # If the face is obscured, draw the rectangle around the predicted position
                    if not face.isObscured():
                        vid.showRectangle(self.face_list[i].getPosition(),self.face_list[i].getID())
                    else:
                        vid.showRectangle(self.face_list[i].getPredictedPosition(),self.face_list[i].getID())
     
                
            frame = vid.getCurrentFrame()
            
            rects = []
        
            #Get position of each face
            for face in self.face_list:
                # Position of each face (for use in Control Box) based on last detected position, not predicted
                tuples = face.getPosition()
                rects.append([tuples[0][0], tuples[0][1], tuples[1][0], tuples[1][1]])
                # Uncomment if we want to base it on predicted
#                if not face.isObscured():
#                    tuples = face.getPosition()
#                    rects.append([tuples[0][0], tuples[0][1], tuples[1][0], tuples[1][1]])
#                else:
#                    tuples = face.getPredictedPosition()
#                    if tuples:
#                        rects.append([tuples[0][0], tuples[0][1], tuples[1][0], tuples[1][1]])
               
                
            # Transform cv2 frame (numpy array) into QPixmap via string and QImage
            cv2.cvtColor(frame, cv.CV_BGR2RGB, frame)
            frame_as_string = frame.tostring()
            
            image = QImage(frame_as_string,\
            frame.shape[1],frame.shape[0],QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image) 
            
            # Get images of faces for use in Control Box
            face_pics = get_imgs_from_rects(image, rects)
           
            # DON'T DELETE
            # What does it do
            # WHO KNOWS
            if cv2.waitKey(1) & 0xFF == ord('q'):
                vid.endWindow()
                break
            
            # Update everything with current face info
            self.leftbox.set_image(pixmap, self.face_list, face_pics)
            self.rightbox.setFaces(face_pics, self.face_list)
            
            self.setLayout(grid)
            self.show()

            
    def toggle_nums(self):
        '''When num button clicked, changes if we draw rectangles or not.'''
        self.draw_nums = not self.draw_nums
            
    

    def add_option_clicked(self, button_name):
        '''When PictureButton is clicked, attaches new effect to Face object, tells main image to redraw appropriately.'''
        checked_faces = self.rightbox.faceChecks.getCheckedFaces()

        for face in checked_faces:
            face.addAttachedObject((button_name, -1))
        
        self.leftbox.draw_objects(checked_faces)
        
        

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
        qimg = QImage(image_path)
        copy = qimg.copy(rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1])
        faces.append(copy)
    return faces, rects
    
    
def get_imgs_from_rects(img, rects):
    '''Returns images of faces and their locations in the original image. 
    Will be replaced by something from our architecture.'''
    faces = []
    for rect in rects:
        copy = img.copy(rect[0],rect[1],rect[2]-rect[0],rect[3]-rect[1])
        faces.append(copy)
    return faces
    


def main():
    app = QApplication(sys.argv)
    face_window = GuiWindow()
    print "made it to the end"
    sys.exit()


if __name__ == '__main__':
#    import cProfile
#    cProfile.run('main()')
    main()
