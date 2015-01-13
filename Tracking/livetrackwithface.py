import cv2
import os
from video import Video

def goGetEm():
	# vid = Video("facepic3.jpg")
	# isVid = False
	vid = Video(0)
	isVid = True
	# vid.readFrame()
	if isVid==True:
		while (True):
			vid.readFrame()
			vid.findFaces()
			vid.display()
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