import math
import datetime as dt
import cv2
import os

class Face:
	def __init__(self, weights=(1,1,1), useFeatures=False):
		self.position = []		# where the face is in the frame
		self.prevPositions = []		# all previous positions and times that they were seen
		self.velocity = ()		# vector describing x change, y change, and time change
		self.orientation = 0		# the tilt of the head (degrees)
		self.obscured = False		# whether the head was detected in the last detection
		self.usingFeatures = useFeatures
		self.id = 0
		self.colorProfile = []
		self.dWeight = weights[0]
		self.tWeight = weights[1]
		self.wWeight = weights[2]
		
		#Kalman filters for top left and bottom right
		self.rightKalman = cv2.cv.CreateKalman(4, 2, 0)
		self.leftKalman = cv2.cv.CreateKalman(4, 2, 0) 
		# list of mini-images that are attached to the face
		# (each entry contains info about what the image is, where it is, area, etc.)
		self.attachedObjects = []  
		# list of features/locations
		self.features = [] 

	def setColorProfile(self, colorProfile):
		self.colorProfile = colorProfile

	def getColorProfile(self):
		return self.colorProfile

	def getPosition(self):
		return self.position

	def getPrevPositions(self):
		return self.prevPositions

	def setPosition(self, rects):
		"""takes list of tuples pos and sets that as position
		and updates prevPositions. Also sets velocity"""
		if (rects==[]):
			self.obscured = True
		else:
			self.prevPositions.append(self.position)
			self.position = [(rects[0],rects[1]),(rects[2],rects[3]),dt.datetime.now()]
			self.timeSinceDetection = 0

	def getID(self):
		return self.id

	def setID(self, newID):
		self.id = newID

	def getWidth(self):
		"""using position, return width of face"""
		if (self.position==[]):
			return 0
		return abs(self.position[1][0]-self.position[0][0])

	def getAge(self):
		age = (dt.datetime.now()-timeself.prevPositions[0][2]).total_seconds()
		return age
		
	def isObscured(self):
		return self.obscured

	def setObscured(self, truthVal):
		self.obscured = truthVal

	def estimateNextPosition(self, time):
		"""Use velocity and most recent position
		to calculate a new slightly modified position. Meant for when
		we are estimating where the face is"""
		deltaTime = (time - self.position[2]).total_seconds()
		self.getVelocity()
		middleOfFace = ((self.position[1][0]+self.position[0][0])/2,(self.position[1][1]+self.position[0][1])/2)
		if self.velocity != 0:
			dx = self.velocity[0]/self.velocity[2]*deltaTime
			dy = self.velocity[1]/self.velocity[2]*deltaTime
			middleOfFace = (middleOfFace[0] + dx, middleOfFace[1] + dy)	
		return middleOfFace

	def getVelocity(self):
		"""Use last detected position and most recent detected position
		to estimate how fast the face is moving"""
		if len(self.prevPositions) < 2:
			self.velocity = 0
		else:
			time = self.position[2] - self.prevPositions[len(self.prevPositions)-1][2]
			xdist = self.position[0][0] - self.prevPositions[len(self.prevPositions)-1][0][0]
			ydist = self.position[0][1] - self.prevPositions[len(self.prevPositions)-1][0][1]
			self.velocity = (xdist,ydist,time.total_seconds())
		return self.velocity
			#speed = math.pow(math.pow(1.0*xdist,2) + math.pow(1.0*ydist,2),0.5) / (1.0*time.total_seconds())

	def getTopLeftVelocity(self):
		"""Use last detected position and most recent detected position
		to estimate how fast the face is moving"""
		if len(self.prevPositions) < 2:
			self.velocity = (0,0,0)
		else:
			time = self.position[2] - self.prevPositions[len(self.prevPositions)-1][2]
			xdist = self.position[0][0] - self.prevPositions[len(self.prevPositions)-1][0][0]
			ydist = self.position[0][1] - self.prevPositions[len(self.prevPositions)-1][0][1]
			self.velocity = (xdist,ydist,time.total_seconds())
		return self.velocity

	def getBotRightVelocity(self):
		"""Use last detected position and most recent detected position
		to estimate how fast the face is moving"""
		if len(self.prevPositions) < 2:
			self.velocity = (0,0,0)
		else:
			time = self.position[2] - self.prevPositions[len(self.prevPositions)-1][2]
			xdist = self.position[1][0] - self.prevPositions[len(self.prevPositions)-1][1][0]
			ydist = self.position[1][1] - self.prevPositions[len(self.prevPositions)-1][1][1]
			self.velocity = (xdist,ydist,time.total_seconds())
		return self.velocity

	def update(self, pos):
		"""Calls most of the above methods to give a complete and new
		representation of the face based on information passed in from the Video

		Also updates features if those are being used"""
		pass

	def findFeatures(self):
		"""Find the facial features using a detection algorithm that
		is limited to the facial area"""
		pass

	def addAttachedObject(self, attachedObject):
		"""Adds an object or photo effect (silly hat, blur, ...) to the face."""
		self.attachedObjects.append(attachedObject)

	def removeAttachedObject(self, attachedObject):
		"""Removes an object/effect from the face."""
		self.attachedObjects.remove(attachedObject)

	def getAttachedObjects(self):
		"""Returns a list of objects and/or effects that are associated with this face."""
		return self.attachedObjects