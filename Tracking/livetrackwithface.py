import cv2
import os
from video import Video

			# # Always between 0 and 1
			# self.velocityWeight = variableList[0]
			# self.scoreWeight = variableList[1]
			# self.minRemovalScore = variableList[2]
			# # Maybe larger than one
			# self.radiusSize = variableList[3]
			# # Probably always larger than one
			# self.timeOut = variableList[4]
			# self.frameGap = variableList[5]
			# self.cleanThresh = variableList[6]
			# self.usingTime = variableList[7]

def goGetEm():
	# vid = Video("facepic3.jpg")
	# isVid = False
	#vid = Video("Slightmovement.MP4", [0,1,0.1,0.1,1000,0])
	vid = Video(0, [0,1,1,0.5,1000,0, 20, False])
	isVid = True
	# vid.readFrame()
	if isVid==True:
		while (True):
			vid.readFrame()
			vid.findFaces()
			vid.display()
			vid.clean()
			# exit on escape key
			key = cv2.waitKey(20)
			if key == 27:
				break
		vid.endWindow()
	else:
		vid.readFrame()
		vid.findFaces()
		vid.display()
		while (True):
			key = cv2.waitKey(20)
			if key == 27:
				break



goGetEm()