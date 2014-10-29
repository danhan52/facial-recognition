import math
import datetime as dt
import cv2
import os

class Face:
	def __init__(self, useFeatures=False):
		# MAYBE BOUNDING BOX?
		self.position = [(),(), dt.datetime.now()]		# where the face is in the frame
		self.prevPositions = []		# all previous positions
		self.velocity = (0,0)		# vector describing x change, y change in pixels per frame
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

	def setPosition(self, x1, y1, x2, y2):
		"""takes list of tuples pos and sets that as position
		and updates prevPositions. Also sets velocity"""
		if (x1==None):
			self.obscured = True
		else:
			self.prevPositions.append(self.position)
			self.position = [(x1,y1),(x2,y2),dt.datetime.now()]
			self.timeSinceDetection = 0

	def getSize(self):
		"""using position, return size of face"""
		if (self.position==[(),()]):
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

	def estimateNextPosition(selfself):
		"""Use velocity and most recent position
		to calculate a new slightly modified position. Meant for when
		we are estimating where the face is"""
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
			self.velocity = math.pow(math.pow(1.0*xdist,2) + math.pow(1.0*ydist,2),0.5) / (1.0*time.total_seconds())

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


	def addNewFace(self):
		"""analyzes movement of a new face to preserve effeciency"""
		pass

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


	def step(self):
		"""Calls either detectAll() or estimateAll() to update position of faces
		based on frameCount and frameGap

		Also increments frameCount"""
		pass

	def display(self):
		""" Displays current frame, as well as objects associated with faces"""
		cv2.imshow("show", self.frameImage)

	def showRectangle(self, pos):
		cv2.rectangle(self.frameImage, pos[0], pos[1], (127, 255, 0), 2)
		
	def endWindow(self):
		self.vidcap.release()
		cv2.destroyWindow("show")