import math
import datetime as dt
import cv2
import os
from face import Face

class Video:
	def __init__(self, vidSource, variableList=[], showWindow=True):
		self.vidcap = cv2.VideoCapture(vidSource)
		self.cascade = cv2.CascadeClassifier("face_cascade2.xml")
		self.visibleFaceList = []		# contains all Face objects within the frame
		self.notVisibleFaceList = []
		self.inactiveFaceList = []
		self.totalFaceCount = 0		    # number of total faces seen so far
		self.frameCount = 0			    # counter to determine when to detect
		self.cleanThresh = 0
		# PERHAPS SUBCLASS?
		self.frameImage = None          # this is whatever kind of image returned by openCV
		self.showWindow = showWindow

		if self.showWindow:
			cv2.namedWindow("show")
		#####TWEAKABLE VARIABLES#####
		if variableList == []:
			# Always between 0 and 1
			self.velocityWeight = 0
			self.scoreWeight = 1
			self.minRemovalScore = 0.1
			# Maybe larger than one
			self.radiusSize = 0.5
			# Probably always larger than one
			self.timeOut = 15
			self.frameGap = 0
			self.cleanThresh = 5
			self.usingTime = True
		# add a catch statement for if variable list isn't of length 6
		else:
			# Always between 0 and 1
			self.velocityWeight = variableList[0]
			self.scoreWeight = variableList[1]
			self.minRemovalScore = variableList[2]
			# Maybe larger than one
			self.radiusSize = variableList[3]
			# Probably always larger than one
			self.timeOut = variableList[4]
			self.frameGap = variableList[5]
			self.cleanThresh = variableList[6]
			self.usingTime = variableList[7]


	def getFaces(self):
		return self.visibleFaceList

	def getCurrentFrame(self):
		return self.frameImage

	def pruneFaceList(self):
		i = 0
		while i < len(self.notVisibleFaceList):
			pos = self.notVisibleFaceList[i].getPosition()
			timeSinceDetection = dt.datetime.now()-pos[2]
			if timeSinceDetection.total_seconds() > self.timeOut:
				print timeSinceDetection.total_seconds()
				print self.notVisibleFaceList[i].id
				self.inactiveFaceList.append(self.notVisibleFaceList.pop(i))
			i += 1

	def addNewFace(self, location):
		fc = Face()
		fc.id = self.totalFaceCount
		self.totalFaceCount += 1
		fc.setPosition(location)
		self.visibleFaceList.append(fc)

	def listHelper(self, rects):
		tupList = []
		for i in range(len(rects)):
			for j in range(len(self.visibleFaceList)):
				newPle = (self.scoreForBeingHere(self.visibleFaceList[j],rects[i]), 0, j, i)
				tupList.append(newPle)
			for j in range(len(self.notVisibleFaceList)):
				newPle = (self.scoreForBeingHere(self.notVisibleFaceList[j],rects[i]), 1, j, i)
				tupList.append(newPle)
		return tupList


	def analyzeFrame(self, rects):
		if (len(self.visibleFaceList)<1):
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
			self.mergeSort(scoreList)
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
					self.notVisibleFaceList.append(face)
				else:
					count += 1
			# all matched not visible faces should be moved to visibleFaceList
			notVisLen = len(self.notVisibleFaceList)
			for i in reversed(range(notVisLen)):
				if (i in usedNotVisibleFaces):
					face = self.notVisibleFaceList.pop(i)
					self.visibleFaceList.append(face)
			# create new faces for all unmatched rects
			for i in range(len(rects)):
				if (i not in usedRects):
					self.addNewFace(rects[i])


	def mergeSort(self, alist):
		if len(alist)>1:
			mid = len(alist)//2
			lefthalf = alist[:mid]
			righthalf = alist[mid:]

			self.mergeSort(lefthalf)
			self.mergeSort(righthalf)

			i=0
			j=0
			k=0
			while i<len(lefthalf) and j<len(righthalf):
				if lefthalf[i][0]<righthalf[j][0]:
					alist[k]=lefthalf[i]
					i=i+1
				else:
					alist[k]=righthalf[j]
					j=j+1
				k=k+1

			while i<len(lefthalf):
				alist[k]=lefthalf[i]
				i=i+1
				k=k+1

			while j<len(righthalf):
				alist[k]=righthalf[j]
				j=j+1
				k=k+1

		
	def makeAssignments(self, assignmentList, rects, indices, visibleFaces):
		counter = 0
		for i in range(len(assignmentList)):
			if rects != []:
				if assignmentList[i] != -1:
					if i < visibleFaces:
						self.visibleFaceList[i].setPosition(rects[assignmentList[i]])
					else:
						self.visibleFaceList[counter+visibleFaces].setPosition(rects[assignmentList[indices[counter]]])
						counter += 1


	def scoreForBeingHere(self, face1, rect):
		"""compares face and rect to sees what the chances are that they are the same
		returns float between 0 and 1"""
		time = dt.datetime.now()
		recentPosition = face1.getPosition()
		if not (recentPosition==[]):
			deltaTime = (time - recentPosition[2]).total_seconds()
			velocity = face1.getVelocity()
			area = math.pow(face1.getArea(),0.5)
			if self.usingTime:
				radius = deltaTime*area*self.radiusSize
			else:
				radius = area*self.radiusSize
			middleOfRect = ((rect[2]+rect[0])/2,(rect[3]+rect[1])/2)
			middleOfFace = ((recentPosition[1][0]+recentPosition[0][0])/2,(recentPosition[1][1]+recentPosition[0][1])/2)
			if velocity != 0:
				middleOfFace = (middleOfFace[0] + velocity[0]/velocity[2]*deltaTime*self.velocityWeight, middleOfFace[1] + velocity[1]/velocity[2]*deltaTime*self.velocityWeight)
			diffMiddles = math.pow(math.pow(middleOfFace[0]-middleOfRect[0], 2) + math.pow(middleOfFace[1]-middleOfRect[1], 2), 0.5)
			
			# asymptote equation such that after the difference in middles is more than 1 radius away,
			# prob will be down to 0.25 but after that it slowly goes to 0 never quite reaching it
			x = math.pow(diffMiddles/radius,3)
			# decays with increase in time
			if self.usingTime:
				score = self.scoreWeight/(deltaTime*(3*x+1))
			else:
				score = self.scoreWeight/((3*x+1))
			return score
		else:
			return 0


	def findFaces(self):
		"""detects all faces with the frame then analyzes the frame to determine
		which face belongs to which face object"""
		rects = self.detectAll()
		if len(rects)==0:
			rects = []
		else:
			rects[:, 2:] += rects[:, :2]
		self.analyzeFrame(rects)


	def detectAll(self):
		"""Run face detection algorithm on the whole picture and make adjustments 
		to the faces based on where the are and where they should be"""
		rects = self.cascade.detectMultiScale(self.frameImage, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
		return rects


	def display(self):
		""" Displays current frame with rectangles and boxes"""
		for i in range(len(self.visibleFaceList)):
			self.showRectangle(self.visibleFaceList[i].getPosition(),self.visibleFaceList[i].id)
		cv2.imshow("show", self.frameImage)


	def clean(self):
		i = 0
		while i < len(self.notVisibleFaceList):
			if len(self.notVisibleFaceList[i].prevPositions) < self.cleanThresh:
				self.notVisibleFaceList.pop(i)
				self.totalFaceCount -= 1
			i += 1


	def readFrame(self):
		"""read frame from openCV info"""
		success, self.frameImage = self.vidcap.read()
		return success, self.frameImage


	def showRectangle(self, pos, IDnum):
		cv2.rectangle(self.frameImage, pos[0], pos[1], (255,0,0), 2)
		cv2.putText(self.frameImage, str(IDnum), pos[0], cv2.FONT_HERSHEY_SIMPLEX, 2, [0,255,0], 3)
		

	def endWindow(self):
		"""stops using webcam (or whatever source is) and removes display window"""
		self.vidcap.release()
		cv2.destroyWindow("show")