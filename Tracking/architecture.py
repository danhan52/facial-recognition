import math
import datetime as dt
import cv2
import os

class Face:
	def __init__(self, useFeatures=False):
		# MAYBE BOUNDING BOX?
		self.position = []		# where the face is in the frame
		self.prevPositions = []		# all previous positions
		self.velocity = (0,0,0)		# vector describing x change, y change, and time change
		self.orientation = 0		# the tilt of the head (degrees)
		self.timeSinceDetection = 0	# frames since last detection
		self.obscured = False		# whether the head was detected in the last detection
		self.colorAvg = 0			# average pixel intensity of facial region
		self.usingFeatures = useFeatures
		
		# list of mini-images that are attached to the face
		# (each entry contains info about what the image is, where it is, size, etc.)
		self.attachedObjects = []  
		# list of features/locations
		self.features = [] 

	
	def getPosition(self):
		return self.position

	def setPosition(self, rects):
		"""takes list of tuples pos and sets that as position
		and updates prevPositions. Also sets velocity"""
		if (rects==[]):
			self.obscured = True
		else:
			self.prevPositions.append(self.position)
			self.position = [(rects[0],rects[1]),(rects[2],rects[3]),dt.datetime.now()]
			self.timeSinceDetection = 0

	def getSize(self):
		"""using position, return size of face"""
		if (self.position==[]):
			return 0
		return abs((self.position[1][0]-self.position[0][0])*(self.position[1][1]-self.position[0][1]))

	def incrementTimeSinceDetection(self):
		self.timeSinceDetection+=1

	def getTimeSinceDetection(self):
		return self.timeSinceDetection

	def isObscured(self):
		return self.obscured

	def setObscured(self, truthVal):
		self.obscured = truthVal

	def setColorAvg(self, avgVal):
		"""method to calculate the average intensity value of the face"""
		pass

	def getColorAvg(self):
		return self.colorAvg

	def estimateNextPosition(self, time):
		"""Use velocity and most recent position
		to calculate a new slightly modified position. Meant for when
		we are estimating where the face is"""
		self.prevPositions.append(self.position)
		self.position[0]
		pass

	def calculateVelocity(self):
		"""Use last detected position and most recent detected position
		to estimate how fast the face is moving"""
		if len(self.prevPositions) < 2:
			self.velocity = 0
		else:
			time = self.position[2] - self.prevPositions[len(self.prevPositions)-1][2]
			xdist = self.position[0][0] - self.prevPositions[len(self.prevPositions)-1][0][0]
			ydist = self.position[0][1] - self.prevPositions[len(self.prevPositions)-1][0][1]
			#self.velocity = math.pow(math.pow(1.0*xdist,2) + math.pow(1.0*ydist,2),0.5) / (1.0*time.total_seconds())
			self.velocity = (xdist,ydist,time.total_seconds())

	def getVelocity(self):
		return self.velocity

	def update(self, pos):
		"""calls most of the above methods to give a complete and new
		representation of the face based on information passed in from the Video

		Also updates features if those are being used"""
		pass

	def findFeatures(self):
		"""find the facial features using a detection algorithm that
		is limited to the facial area"""
		pass

	def likelihoodOfBeingHere(self, location, time):
		"""checks what the chance of the face being at this location is"""
		pass

class Video:
	def __init__(self, vidSource, frameGap=0):
		self.vidcap = cv2.VideoCapture(vidSource)
		self.cascade = cv2.CascadeClassifier("face_cascade2.xml")
		self.visibleFaceList = []		# contains all Face objects within the frame
		self.notVisibleFaceList = []
		self.totalFaceCount = 0		    # number of total faces seen so far
		self.frameGap = frameGap		# number of frames skipped before detection algorithm is run again
		self.frameCount = 0			    # counter to determine when to detect
		# PERHAPS SUBCLASS?
		self.frameImage = None          # this is whatever kind of image returned by openCV
		# SOME SORT OF VIDEO OBJECT
		cv2.namedWindow("show")
		self.colors = [(255,0,0), (0,255,0), (0,0,255)]


	def analyzeFrame(self,rects):
		if len(rects)>len(self.visibleFaceList):
			megaList = []
			for i in range(len(self.visibleFaceList)):
				tempList = []
				for j in range(len(rects)):
					tempList.append(self.likelihoodOfBeingHere(self.visibleFaceList[i],rects[j]))
				# if there are issues, it's with copying
				megaList.append(list(tempList))

			assignmentList = []
			while len(assignmentList) < len(self.visibleFaceList):
				highestVal = 0
				highestIndex = ()
				for i in range(len(megaList)):
					for j in range(len(megaList[i])):
						if j not in assignmentList:
							if megaList[i][j] >= highestVal:
								highestVal = megaList[i][j]
								highestIndex = (i, j)
				assignmentList.append(j)
			self.makeAssignments(assignmentList, rects)

			for i in range(len(rects)):
				if i not in assignmentList:
					fc = Face()
					fc.setPosition(rects[i])
					self.visibleFaceList.append(fc)


		elif len(rects)==len(self.visibleFaceList):
			megaList = []
			for i in range(len(self.visibleFaceList)):
				tempList = []
				for j in range(len(rects)):
					tempList.append(self.likelihoodOfBeingHere(self.visibleFaceList[i],rects[j]))
				# if there are issues, it's with copying
				megaList.append(list(tempList))

			assignmentList = []
			while len(assignmentList) < len(rects):
				highestVal = 0
				highestIndex = ()
				for i in range(len(megaList)):
					for j in range(len(megaList[i])):
						if j not in assignmentList:
							if megaList[i][j] >= highestVal:
								highestVal = megaList[i][j]
								highestIndex = (i, j)
				assignmentList.append(j)
			self.makeAssignments(assignmentList, rects)

		else:		# more rects than faces
			pass

	def makeAssignments(self, assignmentList, rects):
		for i in range(len(self.visibleFaceList)):
			self.visibleFaceList[i].setPosition(rects[assignmentList[i]])


	def addNewFace(self, fc):
		"""analyzes movement of a new face to preserve effeciency"""
		self.visibleFaceList.append(fc)

	def likelihoodOfBeingHere(self, face1, rect):
		"""compares to faces and sees what the chances are that these faces are the same"""
		"""returns flot between 0 and 1"""
		# expanding circle
		time = dt.datetime.now()
		recentPosition = face1.getPosition()
		if not (recentPosition==[]):
			deltaTime = (time - recentPosition[2]).total_seconds()
			# eventually depend on size of face, for now straight up linear
			size = math.pow(face1.getSize(),0.5)
			radius = deltaTime*size
			middleOfRect = ((rect[2]+rect[0])/2,(rect[3]+rect[1])/2)
			middleOfFace = ((recentPosition[1][0]+recentPosition[0][0])/2,(recentPosition[1][1]+recentPosition[0][1])/2)
			diffMiddles = math.pow(math.pow(middleOfFace[0]-middleOfRect[0], 2) + math.pow(middleOfFace[1]-middleOfRect[1], 2), 0.5)
			prob = 1-(diffMiddles/radius)
			if prob > 0:
				return prob
			else:
				return 0
		else:
			return 0

	def readFrame(self):
		"""read frame from openCV info"""
		success, self.frameImage = self.vidcap.read()
		return success, self.frameImage

	def detectAll(self):
		"""Run face detection algorithm on the whole picture and make adjustments 
		to the faces based on where the are and where they should be

		Should be run once every frameGap frames"""
		rects = self.cascade.detectMultiScale(self.frameImage, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
		return rects

	def estimateAll(self):
		"""Step forward one frame, update all (visible?) faces based on estimation 
		from velocities; don't run face detection algorithm
		
		Should be run every frame except where detectAll() is run."""
		pass
		# for face in self.visibleFaceList[]:
		# 	face.estimateNextPosition()


	def step(self):
		"""Calls either detectAll() or estimateAll() to update position of faces
		based on frameCount and frameGap

		Also increments frameCount"""
		pass

	def display(self):
		""" Displays current frame, as well as objects associated with faces"""
		print len(self.visibleFaceList)
		for i in range(len(self.visibleFaceList)):
			self.showRectangle(self.visibleFaceList[i].getPosition(),self.colors[i])
			cv2.imshow("show", self.frameImage)

	def showRectangle(self, pos, color):
		cv2.rectangle(self.frameImage, pos[0], pos[1], color, 2)
		
	def endWindow(self):
		self.vidcap.release()
		cv2.destroyWindow("show")