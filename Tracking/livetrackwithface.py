import cv2
import os
from video import Video

	# # Always between 0 and 1
	# self.minRemovalScore = variableList[0]
	# # Probably always larger than one
	# self.timeOut = variableList[1]
	# self.cleanThresh = variableList[2]
	# self.binNum = variableList[3]
	# self.weights = (variableList[4], variableList[5], variableList[6])
	#self.framesback = variableList[7]

def goGetEm():
	minRemovalScore = 0.0001
	timeOut = 10
	cleanThresh = 5
	binNumber = 100
	distanceWeight = 0.5
	sizeWeight = 0.0
	timeWeight = 0.5
	weights = (distanceWeight, timeWeight, sizeWeight)
	writingToFiles = True
	distDev = 200
	timeDev = 0.34
	sizeDev = 0.25
	devs = (distDev, timeDev, sizeDev)
	framesback = 2
	variables = [minRemovalScore, timeOut, cleanThresh, binNumber, weights, writingToFiles, devs, framesback]
	vid = Video(0, variables)
	# vidFile = "outvid.avi"
	# csvFile = "variable.csv"
	# if writingToFiles:
	# 	vid.openVidWrite(vidFile)
	# 	vid.openCSVWrite(csvFile)
	while (True):
		vid.readFrame()
		vid.findFaces()
		vid.display()
		# vid.writeToVideo()
		# exit on escape key
		key = cv2.waitKey(1)
		if key == 27:
			break
	vid.endWindow()


goGetEm()