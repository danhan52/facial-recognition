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
		# for i in range(len(self.notVisibleFaceList)):
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

	def listHelper(self, listChoice, rects):
		megaList = []
		for i in range(len(rects)):
			tempList = []
			for j in range(len(listChoice)):
				tempList.append(self.scoreForBeingHere(listChoice[j],rects[i]))
			# if there are issues, it's with copying
			megaList.append(list(tempList))
		return megaList

	def dualListHelper(self, list1, list2, rects):
		megaList = []
		breakPoint = 0
		for i in range(len(rects)):
			tempList = []
			for j in range(len(list1)):
				tempList.append(self.scoreForBeingHere(list1[j],rects[i]))
				breakPoint = j
			for k in range(len(list2)):
				tempList.append(self.scoreForBeingHere(list2[k],rects[i]))
			# if there are issues, it's with copying
			megaList.append(list(tempList))

		return megaList, breakPoint		

	def analyzeFrame(self, rects):
		self.pruneFaceList()
		#Case 1
		if len(rects)>len(self.visibleFaceList):
			# print "case1"
			if len(self.visibleFaceList)>0:
				megaList, breakPoint = self.dualListHelper(self.visibleFaceList, self.notVisibleFaceList, rects)
				assignmentList = []
				for i in range(len(megaList)):
					highest = 0
					index = 0
					for j in range(len(megaList[i])):
						# ensure that face hasn't been used already
						if megaList[i][j] >= highest and j not in assignmentList:
							index = j
							highest = megaList[i][j]
					if highest > self.minRemovalScore:
						if j > breakPoint:
							face = self.notVisibleFaceList.pop(index-breakPoint-1)
							self.visibleFaceList.append(face)
							index = len(self.visibleFaceList)-1
						assignmentList.append(index)
					else:
						face = Face()
						face.id = self.totalFaceCount
						self.totalFaceCount += 1
						self.visibleFaceList.append(face)
						assignmentList.append(len(self.visibleFaceList)-1)

				self.makeAssignments(assignmentList, rects)
				k = 0
				while k < breakPoint:
					if k not in assignmentList:
						face = self.visibleFaceList.pop(k)
						self.notVisibleFaceList.append(face)
					k+=1

			else:
				for i in range(len(rects)):
					self.addNewFace(rects[i])

		#Case 2
		elif len(rects)==len(self.visibleFaceList):
			# print "case2"
			megaList, breakPoint = self.dualListHelper(self.visibleFaceList, self.notVisibleFaceList, rects)
			assignmentList = []
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					# ensure that face hasn't been used already
					if megaList[i][j] >= highest and j not in assignmentList:
						index = j
						highest = megaList[i][j]
				if highest > self.minRemovalScore:
					if j > breakPoint:
						face = self.notVisibleFaceList.pop(index-breakPoint-1)
						self.visibleFaceList.append(face)
						index = len(self.visibleFaceList)-1
					assignmentList.append(index)
				else:
					face = Face()
					face.id = self.totalFaceCount
					self.totalFaceCount += 1
					self.visibleFaceList.append(face)
					assignmentList.append(len(self.visibleFaceList)-1)

			self.makeAssignments(assignmentList, rects)
			k = 0
			while k < breakPoint:
				if k not in assignmentList:
					face = self.visibleFaceList.pop(k)
					self.notVisibleFaceList.append(face)
				k+=1

		#Case 3 (less rects than faces)
		else:
			# print "case3"
			megaList, breakPoint = self.dualListHelper(self.visibleFaceList, self.notVisibleFaceList, rects)
			assignmentList = []
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					# ensure that face hasn't been used already
					if megaList[i][j] >= highest and j not in assignmentList:
						index = j
						highest = megaList[i][j]
				if highest > self.minRemovalScore:
					if j > breakPoint:
						face = self.notVisibleFaceList.pop(index-breakPoint-1)
						self.visibleFaceList.append(face)
						index = len(self.visibleFaceList)-1
					assignmentList.append(index)
				else:
					face = Face()
					face.id = self.totalFaceCount
					self.totalFaceCount += 1
					self.visibleFaceList.append(face)
					assignmentList.append(len(self.visibleFaceList)-1)

			self.makeAssignments(assignmentList, rects)
			k = 0
			while k < breakPoint:
				if k not in assignmentList:
					face = self.visibleFaceList.pop(k)
					self.notVisibleFaceList.append(face)
				k+=1

			

	def analyzeFrame2(self,rects):
		self.pruneFaceList()
		if len(rects)>len(self.visibleFaceList):
			if len(self.visibleFaceList)>0:
				megaList = self.listHelper(self.visibleFaceList,rects)
				# print megaList
				assignmentList = []
				for i in range(len(megaList)):
					highest = 0
					index = 0
					for j in range(len(megaList[i])):
						# ensure that face hasn't been used already
						if megaList[i][j] >= highest and j not in assignmentList:
							index = j
							highest = megaList[i][j]
					assignmentList.append(index)

				self.makeAssignments(assignmentList, rects)

				notList = self.listHelper(self.notVisibleFaceList,rects)

				if notList != []:
					for i in range(len(rects)):
						index = -1
						highest = 0
						for j in range(len(self.notVisibleFaceList)):
							if j not in assignmentList:
							# print notList
								if notList[i][j] > highest:
									index = j
									highest = notList[j][i]
						if index != -1:
							if notList[index][i] > self.minRemovalScore:
								face = self.notVisibleFaceList.pop(index)
								face.setPosition(rects[i])
								self.visibleFaceList.append(face)
						else:
							fc = Face()
							fc.id = self.totalFaceCount
							# print fc.id
							self.totalFaceCount += 1
							fc.setPosition(rects[i])
							self.visibleFaceList.append(fc)
				else:
					for i in range(len(rects)):
						fc = Face()
						fc.id = self.totalFaceCount
						# print fc.id
						self.totalFaceCount += 1
						fc.setPosition(rects[i])
						self.visibleFaceList.append(fc)
			else:
				for i in range(len(rects)):
					fc = Face()
					fc.id = self.totalFaceCount
					# print fc.id
					self.totalFaceCount += 1
					fc.setPosition(rects[i])
					self.visibleFaceList.append(fc)


		elif len(rects)==len(self.visibleFaceList):
			megaList = self.listHelper(self.visibleFaceList,rects)
			# print megaList
			assignmentList = []
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					if megaList[i][j] >= highest and j not in assignmentList:
						index = j
						highest = megaList[i][j]
				assignmentList.append(index)
			
			self.makeAssignments(assignmentList, rects)

		else:
			# less rects than faces
			megaList = self.listHelper(self.visibleFaceList,rects)
			# print megaList
			assignmentList = []
			probabilityList = []
			for i in range(len(megaList)):
				highest = 0
				index = 0
				for j in range(len(megaList[i])):
					if megaList[i][j] >= highest and j not in assignmentList:
						index = j
						highest = megaList[i][j]
				assignmentList.append(index)
				probabilityList.append(highest)

			if len(probabilityList)!=0:
				lowIndex = probabilityList.index(min(probabilityList))
				self.notVisibleFaceList.append(self.visibleFaceList.pop(lowIndex))
				assignmentList.pop(lowIndex)
				self.makeAssignments(assignmentList, rects)




	def makeAssignments(self, assignmentList, rects):
		# print assignmentList
		# print rects
		# print len(self.visibleFaceList)
		for i in range(len(assignmentList)):
			# if rects != []:
			self.visibleFaceList[assignmentList[i]].setPosition(rects[i])


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


	def readFrame(self):
		"""read frame from openCV info"""
		success, self.frameImage = self.vidcap.read()
		return success, self.frameImage


	def detectAll(self):
		"""Run face detection algorithm on the whole picture and make adjustments 
		to the faces based on where the are and where they should be"""
		rects = self.cascade.detectMultiScale(self.frameImage, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
		return rects


	# # won't really ever use
	# def estimateAll(self):
	# 	"""Step forward one frame, update all (visible?) faces based on estimation 
	# 	from velocities; don't run face detection algorithm
	# 	Should be run every frame except where detectAll() is run."""
	# 	pass
	# 	# for face in self.visibleFaceList[]:
	# 	# 	face.estimateNextPosition()


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
		""" Displays current frame with rectangles and boxes"""
		# print len(self.visibleFaceList)
		print "not visible: "
		for face in self.notVisibleFaceList:
			print face.id
		print "visibel: "
		for i in range(len(self.visibleFaceList)):
			print self.visibleFaceList[i].id
			self.showRectangle(self.visibleFaceList[i].getPosition(),self.visibleFaceList[i].id)
		cv2.imshow("show", self.frameImage)

	def clean(self):
		i = 0
		while i < len(self.notVisibleFaceList):
			if len(self.notVisibleFaceList[i].prevPositions) < self.cleanThresh:
				self.notVisibleFaceList.pop(i)
				self.totalFaceCount -= 1
			i += 1


	def showRectangle(self, pos, IDnum):
		cv2.rectangle(self.frameImage, pos[0], pos[1], (255,0,0), 2)
		cv2.putText(self.frameImage, str(IDnum), pos[0], cv2.FONT_HERSHEY_SIMPLEX, 2, [0,255,0], 3)
		

	def endWindow(self):
		"""stops using webcam (or whatever source is) and removes display window"""
		self.vidcap.release()
		cv2.destroyWindow("show")