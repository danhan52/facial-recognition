import cv2
import os
from newVid import Video

	# # Always between 0 and 1
	# self.minRemovalScore = variableList[0]
	# # Probably always larger than one
	# self.timeOut = variableList[1]
	# self.cleanThresh = variableList[2]
	# self.binNum = variableList[3]
	# self.weights = (variableList[4], variableList[5], variableList[6])

def goGetEm():
	minRemovalScore = 0.0001
	timeOut = 10
	cleanThresh = 5
	binNumber = 100
	distanceWeight = 1
	timeWeight = 1
	sizeWeight = 1
	weights = (distanceWeight, timeWeight, sizeWeight)
	writingToFiles = True
	variables = [minRemovalScore, timeOut, cleanThresh, binNumber, weights, writingToFiles]
	# vid = Video("test/Crossing_front.MP4", variables)
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
		key = cv2.waitKey(20)
		if key == 27:
			break
	vid.endWindow()


goGetEm()