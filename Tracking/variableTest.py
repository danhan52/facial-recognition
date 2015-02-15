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
	minRemovalScore = 0.25
	timeOut = 10
	cleanThresh = 5
	binNumber = 100
	distanceWeight = 0.5
	timeWeight = 0.0
	sizeWeight = 0.5
	weights = (distanceWeight, timeWeight, sizeWeight)
	writingToFiles = True
	distDev = 200
	timeDev = 1
	sizeDev = 0.25
	devs = (distDev, timeDev, sizeDev)
	framesback = 5

	# minRemovals = [0.0001, 0.1, 0.25]
	# weightDev = [((0.5,0,0.5),(100,0.34,0.15)),((0.5,0,0.5),(200,0.34,0.25)),((0.45,0.2,0.35),(100,0.34,0.15)),((0.45,0.2,0.35),(200,0.34,0.25))]
	i = 0
	# for minRemovalScore in minRemovals:
	# 	for setting in weightDev:
			# weights = setting[0]
			# devs = setting[1]
	variables = [minRemovalScore, timeOut, cleanThresh, binNumber, weights, writingToFiles, devs, framesback]
	vidFile = "datums/outvideo"+str(i)+".avi"
	vid = Video("Testvideos/Movie1.mov", variables, False)
	vid.openVidWrite(vidFile)
	success = vid.readFrame()
	while (success):
		vid.findFaces()
		vid.writeToVideo()
		success = vid.readFrame()
	vid.endWindow()
			# i += 1

goGetEm()