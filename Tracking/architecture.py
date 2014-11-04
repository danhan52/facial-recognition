import math
import datetime as dt
import cv2
import os

class Face:
	def __init__(self, useFeatures=False):
		# MAYBE BOUNDING BOX?
		self.position = []		# where the face is in the frame
		self.prevPositions = []		# all previous positions
		self.velocity = ()		# vector describing x change, y change, and time change
		self.orientation = 0		# the tilt of the head (degrees)
		self.timeSinceDetection = 0	# frames since last detection
		self.obscured = False		# whether the head was detected in the last detection
		self.colorAvg = 0			# average pixel intensity of facial region
		self.usingFeatures = useFeatures
		self.id = 0
		
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
			self.velocity = (xdist,ydist,time.total_seconds())
			#self.velocity = math.pow(math.pow(1.0*xdist,2) + math.pow(1.0*ydist,2),0.5) / (1.0*time.total_seconds())
			
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
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					if megaList[i][j] >= highest:
						index = j
						highest = megaList[i][j]
				assignmentList.append(index)

			# while len(assignmentList) < len(self.visibleFaceList):
			# 	highestVal = 0
			# 	highestIndex = ()
			# 	for i in range(len(megaList)):
			# 		for j in range(len(megaList[i])):
			# 			if j not in assignmentList:
			# 				if megaList[i][j] >= highestVal:
			# 					highestVal = megaList[i][j]
			# 					highestIndex = (i, j)
			# 	assignmentList.append(j)
			self.makeAssignments(assignmentList, rects)

			for i in range(len(rects)):
				if i not in assignmentList:
					fc = Face()
					fc.id = self.totalFaceCount
					self.totalFaceCount += 1
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
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					if megaList[i][j] >= highest:
						index = j
						highest = megaList[i][j]
				assignmentList.append(index)
			# print assignmentList

			# assignmentList = [-1]*len(self.visibleFaceList)
			# while (-1 in assignmentList):
			# 	print assignmentList
			# 	highestVal = 0
			# 	highestIndex = -1		# maybe change initial value
			# 	for i in range(len(megaList)):
			# 		if assignmentList[i] == -1:
			# 			for j in range(len(megaList[i])):
			# 				if j not in assignmentList:
			# 					if megaList[i][j] >= highestVal:
			# 						highestVal = megaList[i][j]
			# 						highestIndex = j
			# 	if highestIndex != -1:
			# 		assignmentList[i] = highestIndex
			# 	else:
			# 		print "error"
			# 	highestVal = 0
			# 	highestIndex = -1
			# print assignmentList
			self.makeAssignments(assignmentList, rects)

		else:
			# more rects than faces
			megaList = []
			for i in range(len(self.visibleFaceList)):
				tempList = []
				for j in range(len(rects)):
					tempList.append(self.likelihoodOfBeingHere(self.visibleFaceList[i],rects[j]))
				# if there are issues, it's with copying
				megaList.append(list(tempList))

			assignmentList = []
			probabilityList = []
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					if megaList[i][j] >= highest:
						index = j
						highest = megaList[i][j]
				assignmentList.append(index)
				probabilityList.append(highest)

			lowIndex = probabilityList.index(min(probabilityList))
			self.notVisibleFaceList.append(self.visibleFaceList.pop(lowIndex))
			assignmentList.pop(lowIndex)
			self.makeAssignments(assignmentList, rects)



	def makeAssignments(self, assignmentList, rects):
		print len(self.visibleFaceList)
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
			size = math.pow(face1.getSize(),0.5)
			radius = deltaTime*size
			middleOfRect = ((rect[2]+rect[0])/2,(rect[3]+rect[1])/2)
			middleOfFace = ((recentPosition[1][0]+recentPosition[0][0])/2,(recentPosition[1][1]+recentPosition[0][1])/2)
			diffMiddles = math.pow(math.pow(middleOfFace[0]-middleOfRect[0], 2) + math.pow(middleOfFace[1]-middleOfRect[1], 2), 0.5)
			# asymptote equation such that after the difference in middles is more than 1 radius away,
			# prob will be down to 0.25 but after that it slowly goes to 0 never quite reaching it
			x = math.pow(diffMiddles/radius,2)
			prob = 1/(3*x+1)
			if prob > 0:
				# print "prob = ", prob
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


	def findFaces(self):
		"""detects all faces with the frame then analyzes the frame to determine
		which face belongs to which face object"""
		rects = self.detectAll()
		if len(rects)==0:
			rects = []
		else:
			rects[:, 2:] += rects[:, :2]
		self.analyzeFrame(rects)

	def display(self):
		""" Displays current frame, as well as objects associated with faces"""
		# print len(self.visibleFaceList)
		for i in range(len(self.visibleFaceList)):
			self.showRectangle(self.visibleFaceList[i].getPosition(),self.visibleFaceList[i].id)
			cv2.imshow("show", self.frameImage)

	def showRectangle(self, pos, IDnum):
		cv2.rectangle(self.frameImage, pos[0], pos[1], (255,0,0), 2)
		cv2.putText(self.frameImage, str(IDnum), pos[0], cv2.FONT_HERSHEY_SIMPLEX, 1, [0,0,0])
		
	def endWindow(self):
		"""stops using webcam (or whatever source is) and removes display window"""
		self.vidcap.release()
		cv2.destroyWindow("show")