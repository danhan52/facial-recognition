import math
import datetime as dt
import cv2
import os
from face import Face
from sortings import *
# from colorImport import *

class Video:
	def __init__(self, vidSource, variableList=[], showWindow=True):
		self.vidcap = cv2.VideoCapture(vidSource)
		self.cascade = cv2.CascadeClassifier("face_cascade2.xml")
		self.visibleFaceList = []		# contains all Face objects within the frame
		self.notVisibleFaceList = []
		self.inactiveFaceList = []
		self.totalFaceCount = 0		    # number of total faces seen so far
		self.faceIDCount = 0
		self.frameCount = 0			    # counter to determine when to detect
		self.frameImage = None          # this is whatever kind of image returned by openCV
		self.previousFrame = None
		self.showWindow = showWindow

		if self.showWindow:
			cv2.namedWindow("show")
		#####TWEAKABLE VARIABLES#####
		if variableList == []:
			# Always between 0 and 1
			self.minRemovalScore = 0.1
			# Probably always larger than one
			self.timeOut = 15
			self.cleanThresh = 5
			self.binNum = 100
			self.weights = (1,1,1)
		# add a catch statement for if variable list isn't of length 6
		else:
			# Always between 0 and 1
			self.minRemovalScore = variableList[0]
			# Probably always larger than one
			self.timeOut = variableList[1]
			self.cleanThresh = variableList[2]
			self.binNum = variableList[3]
			self.weights = (variableList[4][0], variableList[4][1], variableList[4][2])


	def getFaces(self):
		allFaceList = self.visibleFaceList + self.notVisibleFaceList
		mergeSortFaces(allFaceList)
		return allFaceList

	def getCurrentFrame(self):
		return self.frameImage

	def pruneFaceList(self):
		i = 0
		while i < len(self.notVisibleFaceList):
			pos = self.notVisibleFaceList[i].getPosition()
			timeSinceDetection = dt.datetime.now()-pos[2]
			if timeSinceDetection.total_seconds() > self.timeOut:
				print timeSinceDetection.total_seconds()
				print self.notVisibleFaceList[i].getID()
				self.inactiveFaceList.append(self.notVisibleFaceList.pop(i))
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
				newPle = (self.visibleFaceList[j].scoreForBeingHere(rects[i]), 0, j, i)
				tupList.append(newPle)
			for j in range(len(self.notVisibleFaceList)):
				newPle = (self.notVisibleFaceList[j].scoreForBeingHere(rects[i]), 1, j, i)
				tupList.append(newPle)
		return tupList


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
					face = self.visibleFaceList.pop(count)
					face.setObscured(True)
					self.notVisibleFaceList.append(face)
				else:
					count += 1
			# all matched not visible faces should be moved to visibleFaceList
			notVisLen = len(self.notVisibleFaceList)
			for i in reversed(range(notVisLen)):
				if (i in usedNotVisibleFaces):
					print "Not visible to visible"
					face = self.notVisibleFaceList.pop(i)
					face.setObscured(False)
					self.visibleFaceList.append(face)
			# create new faces for all unmatched rects
			for i in range(len(rects)):
				if (i not in usedRects):
					print "Make new face"
					self.addNewFace(rects[i])


	def findFaces(self):
		"""detects all faces with the frame then analyzes the frame to determine
		which face belongs to which face object"""
		rects = self.detectAll()
		if len(rects)==0:
			rects = []
		else:
			rects[:, 2:] += rects[:, :2]
		self.analyzeFrame(rects)
		self.clean()
		#self.setAllColorProfiles()
    
	def setAllColorProfiles(self):
		for face in self.visibleFaceList:
			prof = setProfile(self.frameImage, face.getPosition(), self.binNum)
			face.setColorProfile(prof)


	def detectAll(self):
		"""Run face detection algorithm on the whole picture and make adjustments 
		to the faces based on where the are and where they should be"""
		rects = self.cascade.detectMultiScale(self.frameImage, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
		return rects


	def display(self):
		""" Displays current frame with rectangles and boxes"""
		allface = self.getFaces()
		for i in range(len(allface)):
			print allface[i].getID(), " ",
		print
		for i in range(len(self.visibleFaceList)):
			self.showRectangle(self.visibleFaceList[i].getPosition(),self.visibleFaceList[i].getID())
		cv2.imshow("show", self.frameImage)


	def clean(self):
		i = 0
		while i < len(self.notVisibleFaceList):
			if len(self.notVisibleFaceList[i].prevPositions) < self.cleanThresh:
				self.notVisibleFaceList.pop(i)
				self.totalFaceCount -= 1
				print "Deleted ghost face"
			i += 1


	def readFrame(self):
		"""read frame from openCV info"""
		self.previousFrame = self.frameImage
		success, self.frameImage = self.vidcap.read()
		return success, self.frameImage


	def showRectangle(self, pos, IDnum):
		cv2.rectangle(self.frameImage, pos[0], pos[1], (255,0,0), 2)
		cv2.putText(self.frameImage, str(IDnum), pos[0], cv2.FONT_HERSHEY_SIMPLEX, 2, [0,255,0], 3)
		

	def endWindow(self):
		"""stops using webcam (or whatever source is) and removes display window"""
		self.vidcap.release()
		cv2.destroyWindow("show")