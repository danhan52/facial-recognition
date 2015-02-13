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

def goGetEm():
	minRemovalScore = 0.1
	timeOut = 10
	cleanThresh = 5
	binNumber = 100
	distanceWeight = 0.5
	timeWeight = 0.0
	sizeWeight = 0.5
	weights = (distanceWeight, timeWeight, sizeWeight)
	writingToFiles = True
	distDev = 200
	timeDev = 0.34
	sizeDev = 0.25
	devs = (distDev, timeDev, sizeDev)
	framesback = 5
	variables = [minRemovalScore, timeOut, cleanThresh, binNumber, weights, writingToFiles, devs, framesback]
	vidFile = "outvid.avi"
	vid = Video("Testvideos/Movie1.mov", variables, False)
	vid.openVidWrite(vidFile)
	success = vid.readFrame()
	while (success):
		vid.findFaces()
		vid.writeToVideo()
		success = vid.readFrame()
	vid.endWindow()

goGetEm()