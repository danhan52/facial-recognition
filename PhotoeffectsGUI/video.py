import math
import datetime as dt
import cv2
import os
import csv
from face import Face
from sortings import *
# from colorImport import *

class Video:
    def __init__(self, vidSource, variableList=[], showWindow=True):
        self.vidcap = cv2.VideoCapture(vidSource)
        self.vidcap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 600);
        self.vidcap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 380);
        self.cascade = cv2.CascadeClassifier("face_cascade2.xml")
        self.visibleFaceList = []       # contains all Face objects within the frame
        self.notVisibleFaceList = []
        self.inactiveFaceList = []
        self.totalFaceCount = 0         # number of total faces seen so far
        self.faceIDCount = 0
        self.frameCount = 0             # counter to determine when to detect
        self.frameImage = None          # this is whatever kind of image returned by openCV
        self.previousFrame = None
        self.showWindow = showWindow

        if self.showWindow:
            cv2.namedWindow("show")
        #####TWEAKABLE VARIABLES#####
        if variableList == []:
            # Always between 0 and 1
            self.minRemovalScore = 0.25
            # Probably always larger than one
            self.timeOut = 15
            self.cleanThresh = 5
            self.binNum = 100
            self.weights = (1,1,1)
            self.writing = False
            self.deviation = (200.0, 0.34, 0.25)
            self.framesback = 2
        # add a catch statement for if variable list isn't of length 6
        else:
            # Always between 0 and 1
            self.minRemovalScore = variableList[0]
            # Probably always larger than one
            self.timeOut = variableList[1]
            self.cleanThresh = variableList[2]
            self.binNum = variableList[3]
            self.weights = (variableList[4][0], variableList[4][1], variableList[4][2])
            self.writing = variableList[5]
            self.deviation = (variableList[6][0], variableList[6][1], variableList[6][2])
            self.framesback = variableList[7]
        if self.writing:
            self.openCSVWrite("variables.csv")

    """ Getters """
    def getFaces(self):
        allFaceList = self.visibleFaceList + self.notVisibleFaceList
        i = 0
        while i < len(allFaceList):
            if len(allFaceList[i].getPrevPositions()) < self.cleanThresh:
                allFaceList.pop(i)
            # only increment when face isn't popped
            else:
                i += 1
        return allFaceList

    def getCurrentFrame(self):
        return self.frameImage

    """ Main interface for running everything else"""
    def findFaces(self):
        """detects all faces with the frame then analyzes the frame to determine
        which face belongs to which face object"""
        if self.frameCount%2 == 0:
            rects = self.detectAll()
            if len(rects)==0:
                rects = []
            else:
                rects[:, 2:] += rects[:, :2]
            self.analyzeFrame(rects)
            self.clean()
        self.frameCount+=1
        #self.setAllColorProfiles()

    """ The logic for finding the faces"""
    def analyzeFrame(self, rects):
        if (len(self.visibleFaceList)<1 and len(self.notVisibleFaceList)<1):
            for i in range(len(rects)):
                self.addNewFace(rects[i])
        else:
            self.pruneFaceList()
            scoreList = self.listHelper(rects)
            # remove all scores that aren't high enough
            count = 0
            while(count < len(scoreList)):
                if scoreList[count][0] < self.minRemovalScore:
                    scoreList.pop(count)
                else:
                    count += 1
            mergeSortScore(scoreList)
            # tools for remembering
            usedRects = []
            usedVisibleFaces = []
            usedNotVisibleFaces = []
            # set positions for optimum rects and faces (visible and not)
            for i in range(len(scoreList)):
                ur = scoreList[i][3] not in usedRects
                if scoreList[i][1]==0:
                    uvf = scoreList[i][2] not in usedVisibleFaces
                    if (ur and uvf):
                        faceInd = scoreList[i][2]
                        rectInd = scoreList[i][3]
                        self.visibleFaceList[faceInd].setPosition(rects[rectInd])
                        usedRects.append(rectInd)
                        usedVisibleFaces.append(faceInd)
                else:
                    unvf = scoreList[i][2] not in usedNotVisibleFaces
                    if (ur and unvf):
                        faceInd = scoreList[i][2]
                        rectInd = scoreList[i][3]
                        self.notVisibleFaceList[faceInd].setPosition(rects[rectInd])
                        usedRects.append(rectInd)
                        usedNotVisibleFaces.append(faceInd)

            # all unmatched visible faces should be moved to notVisibleFaceList
            count = 0
            while count < len(self.visibleFaceList):
                if (count not in usedVisibleFaces):
#                   print "Visible to not visible"
                    face = self.visibleFaceList.pop(count)
                    face.setObscured(True)
                    self.notVisibleFaceList.append(face)
                else:
                    count += 1
            # all matched not visible faces should be moved to visibleFaceList
            notVisLen = len(self.notVisibleFaceList)
            for i in reversed(range(notVisLen)):
                if (i in usedNotVisibleFaces):
#                   print "Not visible to visible"
                    face = self.notVisibleFaceList.pop(i)
                    face.setObscured(False)
                    self.visibleFaceList.append(face)
            # create new faces for all unmatched rects
            for i in range(len(rects)):
                if (i not in usedRects):
#                   print "Make new face"
                    self.addNewFace(rects[i])
        for face in self.visibleFaceList:
            self.updateKalman(face)
            # face.colorProfile = setProfile(self.frameImage,face.getPosition(),self.binNum)
        for face in self.notVisibleFaceList:
            self.updateKalman(face)


    def scoreForBeingHere(self, face, rect):
        """compares face and rect to sees what the chances are that they are the same
        returns float between 0 and 1"""
        time = dt.datetime.now()
        recentPosition = face.getPosition()
        if not (recentPosition==[]):
            deltaTime = (time - recentPosition[2]).total_seconds()
            if deltaTime > 0.5 and face.predictedPosition != []:
                recentPosition = face.predictedPosition
            face.getVelocity()
            # get time change
            # get size change
            width = face.getWidth()
            rectWidth = abs(rect[0]-rect[2])
            diffWidths = 1.0*abs(width-rectWidth)/width
            # get position change
            middleOfRect = ((rect[2]+rect[0])/2,(rect[3]+rect[1])/2)
            middleOfFace = ((recentPosition[1][0]+recentPosition[0][0])/2,(recentPosition[1][1]+recentPosition[0][1])/2)
            diffMiddles = math.pow(math.pow(middleOfFace[0]-middleOfRect[0], 2) + math.pow(middleOfFace[1]-middleOfRect[1], 2), 0.5)
            
            # asymptote equation such that after the difference in middles is more than 1 radius away,
            # prob will be down to 0.25 but after that it slowly goes to 0 never quite reaching it
            xMid = math.pow(diffMiddles/self.deviation[0],3)
            scoreMid = 1.0/((3*xMid+1))
            xWidth = math.pow(diffWidths/self.deviation[2],3)
            scoreWidth = 1.0/((3*xWidth+1))
            xTime = math.pow(deltaTime/self.deviation[1],3)
            scoreTime = 1.0/((3*xTime+1))
            score = self.weights[0]*scoreMid+self.weights[2]*scoreWidth+self.weights[1]*scoreTime

            # linearScore = self.weights[0]*diffMiddles+self.weights[2]*diffWidths+self.weights[1]*deltaTime
            # score = 1/linearScore
            if self.writing:
                data = [face.getID(),diffMiddles,diffWidths,deltaTime,score]
                self.writeToCSV(data)
            return score
        else:
            return 0

    """Helper functions"""    
    def setAllColorProfiles(self):
        for face in self.visibleFaceList:
            prof = setProfile(self.frameImage, face.getPosition(), self.binNum)
            face.setColorProfile(prof)

    def detectAll(self):
        """Run face detection algorithm on the whole picture and make adjustments 
        to the faces based on where the are and where they should be"""
        rects = self.cascade.detectMultiScale(self.frameImage, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
        return rects

    def pruneFaceList(self):
        i = 0
        while i < len(self.notVisibleFaceList):
            pos = self.notVisibleFaceList[i].getPosition()
            timeSinceDetection = dt.datetime.now()-pos[2]
            if timeSinceDetection.total_seconds() > self.timeOut:
#               print "Removed face FOREVER"
                self.inactiveFaceList.append(self.notVisibleFaceList.pop(i))
            # only increment when face isn't popped
            else:
                i += 1

    def addNewFace(self, location):
        fc = Face(self.weights)
        fc.setID(self.faceIDCount)
        self.totalFaceCount += 1
        self.faceIDCount += 1
        fc.setPosition(location)
        self.visibleFaceList.append(fc)

    def listHelper(self, rects):
        tupList = []
        for i in range(len(rects)):
            for j in range(len(self.visibleFaceList)):
                newPle = (self.scoreForBeingHere(self.visibleFaceList[j], rects[i]), 0, j, i)
                tupList.append(newPle)
            for j in range(len(self.notVisibleFaceList)):
                newPle = (self.scoreForBeingHere(self.notVisibleFaceList[j], rects[i]), 1, j, i)
                tupList.append(newPle)
        return tupList

    def clean(self):
        i = 0
        while i < len(self.notVisibleFaceList):
            if len(self.notVisibleFaceList[i].getPrevPositions()) < self.cleanThresh:
                self.notVisibleFaceList.pop(i)
                self.totalFaceCount -= 1
#               print "Deleted ghost face"
            # only increment when face isn't popped
            else:
                i += 1

    """Opencv interface functions"""
    def readFrame(self):
        """read frame from openCV info"""
        self.previousFrame = self.frameImage
        success, self.frameImage = self.vidcap.read()
        self.frameImage = cv2.flip(self.frameImage,1)
        cv2.resize(self.frameImage,  (600, 380), 0, 0, cv2.INTER_CUBIC);
        return success, self.frameImage

    def display(self):
        """ Displays current frame with rectangles and boxes"""
        allface = self.getFaces()
        for i in range(len(self.visibleFaceList)):
            if len(self.visibleFaceList[i].getPrevPositions()) > self.cleanThresh:
                self.showRectangle(self.visibleFaceList[i].getPosition(),self.visibleFaceList[i].getID())
        cv2.imshow("show", self.frameImage)

    def showRectangle(self, pos, IDnum):
        if not pos==[]:
            cv2.rectangle(self.frameImage, pos[0], pos[1], (255,0,0), 2)
            cv2.putText(self.frameImage, str(IDnum), pos[0], cv2.FONT_HERSHEY_SIMPLEX, 2, [0,255,0], 3)

    def endWindow(self):
        """stops using webcam (or whatever source is) and removes display window"""
        self.vidcap.release()
        cv2.destroyWindow("show")

    """Meant for testing"""
    def openVidWrite(self, filen):
        fourcc = int(cv2.cv.CV_FOURCC('I', 'Y', 'U', 'V'))
        fps = 15        # self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        framew = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        frameh = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))
        self.vidwrite = cv2.VideoWriter()
        self.vidwrite.open(filen,fourcc,fps,(framew,frameh))

    def writeToVideo(self):
        if self.writing:
            for i in range(len(self.visibleFaceList)):
                self.showRectangle(self.visibleFaceList[i].getPosition(),self.visibleFaceList[i].getID())
            self.vidwrite.write(self.frameImage)

    def openCSVWrite(self, filen):
        b = open(filen,'wb')
        self.cwrite = csv.writer(b)
        headings = ["FaceID", "dPostion", "dWidth", "dTime", "score"]
        self.writeToCSV(headings)

    def writeToCSV(self, data):
        self.cwrite.writerow(data)
        
    """Prediction stuff"""
    def updateKalman(self, face1):
        recentPosition = face1.getPosition()
        topLeft = (recentPosition[0])
        # Initialize the kalman filter with the point, transition matrix and velocity equal to 0
        if face1.leftKalman.state_pre[0,0] == 0.0:
            face1.leftKalman.state_pre[0,0]  = topLeft[0]
            face1.leftKalman.state_pre[1,0]  = topLeft[1]
            face1.leftKalman.state_pre[2,0]  = 0
            face1.leftKalman.state_pre[3,0]  = 0

            face1.leftKalman.transition_matrix[0,0] = 1
            face1.leftKalman.transition_matrix[0,2] = 1
            face1.leftKalman.transition_matrix[1,1] = 1
            face1.leftKalman.transition_matrix[1,3] = 1
            face1.leftKalman.transition_matrix[2,2] = 1
            face1.leftKalman.transition_matrix[3,3] = 1

            cv2.cv.SetIdentity(face1.leftKalman.measurement_matrix, cv2.cv.RealScalar(1))
            cv2.cv.SetIdentity(face1.leftKalman.process_noise_cov, cv2.cv.RealScalar(1e-5))## 1e-5
            cv2.cv.SetIdentity(face1.leftKalman.measurement_noise_cov, cv2.cv.RealScalar(1e-1))
            cv2.cv.SetIdentity(face1.leftKalman.error_cov_post, cv2.cv.RealScalar(0.1))

        velocity = face1.getTopLeftVelocity()
        time = dt.datetime.now()
        deltaTime = (time - recentPosition[2]).total_seconds()
        if velocity[2] != 0:
            xvel = velocity[0]/velocity[2]*deltaTime
            yvel = velocity[1]/velocity[2]*deltaTime
        else:
            xvel = 0
            yvel = 0

        # Predict with kalman filter
        time = dt.datetime.now()
        deltaTime = (time - recentPosition[2]).total_seconds()
        kalman_prediction = cv2.cv.KalmanPredict(face1.leftKalman)
        # we average the prediction point with the last "framesback" points
        top_left = [0,0]
        counter = max(len(face1.prevPositions)-1, 0)    
        if not counter < self.framesback and not self.framesback == 0:
            while counter != len(face1.prevPositions)-self.framesback:
                top_left[0] += (face1.prevPositions[counter][0][0])
                top_left[1] += (face1.prevPositions[counter][0][1])
                counter-=1
            top_left[0] += kalman_prediction[0, 0]
            top_left[0] = top_left[0]/self.framesback+1
            top_left[1] += kalman_prediction[1,0]
            top_left[1] = top_left[1]/self.framesback+1
        else:
            top_left = [kalman_prediction[0,0], kalman_prediction[1,0]]

        rightPoints = cv2.cv.CreateMat(2, 1, cv2.cv.CV_32FC1)
        rightPoints[0,0]=topLeft[0]
        rightPoints[1,0]=topLeft[1]

        face1.leftKalman.state_pre[0,0]  = topLeft[0]
        face1.leftKalman.state_pre[1,0]  = topLeft[1]
        face1.leftKalman.state_pre[2,0]  = xvel
        face1.leftKalman.state_pre[3,0]  = yvel

        # Correct the kalman prediction with the actual face point
        estimated = cv2.cv.KalmanCorrect(face1.leftKalman, rightPoints)
        ############################
        # Here we initialize the bottom right point kalman filter in the same manner
        botRight = (recentPosition[1])
        if face1.rightKalman.state_pre[0,0] == 0.0:
            face1.rightKalman.state_pre[0,0]  = botRight[0]
            face1.rightKalman.state_pre[1,0]  = botRight[1]
            face1.rightKalman.state_pre[2,0]  = 0
            face1.rightKalman.state_pre[3,0]  = 0

            face1.rightKalman.transition_matrix[0,0] = 1
            face1.rightKalman.transition_matrix[0,2] = 1
            face1.rightKalman.transition_matrix[1,1] = 1
            face1.rightKalman.transition_matrix[1,3] = 1
            face1.rightKalman.transition_matrix[2,2] = 1
            face1.rightKalman.transition_matrix[3,3] = 1

            cv2.cv.SetIdentity(face1.rightKalman.measurement_matrix, cv2.cv.RealScalar(1))
            cv2.cv.SetIdentity(face1.rightKalman.process_noise_cov, cv2.cv.RealScalar(1e-5))## 1e-5
            cv2.cv.SetIdentity(face1.rightKalman.measurement_noise_cov, cv2.cv.RealScalar(1e-1))
            cv2.cv.SetIdentity(face1.rightKalman.error_cov_post, cv2.cv.RealScalar(0.1))

        velocity = face1.getBotRightVelocity()
        time = dt.datetime.now()
        deltaTime = (time - recentPosition[2]).total_seconds()
        if velocity[2] != 0:
            xvel = velocity[0]/velocity[2]*deltaTime
            yvel = velocity[1]/velocity[2]*deltaTime
        else:
            xvel = 0
            yvel = 0

        kalman_prediction = cv2.cv.KalmanPredict(face1.rightKalman)
        bot_right = [0,0]
        counter = max(len(face1.prevPositions)-1, 0)    
        if not counter < self.framesback and not self.framesback == 0:
            while counter != len(face1.prevPositions)-self.framesback:
                bot_right[0] += (face1.prevPositions[counter][1][0])
                bot_right[1] += (face1.prevPositions[counter][1][1])
                counter-=1
            bot_right[0] += kalman_prediction[0, 0]
            bot_right[0] = bot_right[0]/self.framesback+1
            bot_right[1] += kalman_prediction[1,0]
            bot_right[1] = bot_right[1]/self.framesback+1
        else:
            bot_right = [kalman_prediction[0,0], kalman_prediction[1,0]]

        rightPoints = cv2.cv.CreateMat(2, 1, cv2.cv.CV_32FC1)
        rightPoints[0,0]=botRight[0]
        rightPoints[1,0]=botRight[1]

        face1.rightKalman.state_pre[0,0]  = botRight[0]
        face1.rightKalman.state_pre[1,0]  = botRight[1]
        face1.rightKalman.state_pre[2,0]  = xvel
        face1.rightKalman.state_pre[3,0]  = yvel

        estimated = cv2.cv.KalmanCorrect(face1.rightKalman, rightPoints)
        
        prediction = [(int(top_left[0]),int(top_left[1])), (int(bot_right[0]),int(bot_right[1]))]
        if top_left[0] >= bot_right[0] or top_left[1] >= bot_right[1]:
            face1.predictedPosition = []
        else:
            face1.predictedPosition = prediction