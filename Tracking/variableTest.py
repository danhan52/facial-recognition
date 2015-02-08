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
	distanceWeight = 0.4
	sizeWeight = 0.35
	timeWeight = 0.25
	weights = (distanceWeight, timeWeight, sizeWeight)
	writingToFiles = True
	distDev = 204
	timeDev = 0.34
	sizeDev = 0.28
	devs = (distDev, timeDev, sizeDev)
	variables = [minRemovalScore, timeOut, cleanThresh, binNumber, weights, writingToFiles, devs]
	vidFile = "outvid.avi"
	vid = Video("test/part_o.MP4", variables, False)
	vid.openVidWrite(vidFile)
	success = vid.readFrame()
	while (success):
		vid.findFaces()
		vid.writeToVideo()
		success = vid.readFrame()
	vid.endWindow()

goGetEm()