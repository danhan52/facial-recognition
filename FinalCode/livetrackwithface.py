import cv2
import os
from video import Video

# file to play around with the variables for tracking. Uses simple output window from opencv

def goGetEm():
	minRemovalScore = 0.25
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
	writeVideo = False
	if writeVideo:
		vidFile = "outvid.avi"
		vid.openVidWrite(vidFile)
	while (True):
		vid.readFrame()
		vid.findFaces()
		vid.display()
		if writeVideo:
			vid.writeToVideo()
		# exit on escape key
		key = cv2.waitKey(1)
		if key == 27:
			break
	vid.endWindow()


goGetEm()