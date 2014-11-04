import cv2
import os
from architecture import Video

def goGetEm():
	vid = Video(0)
	# vid.readFrame()
	while (True):
		vid.readFrame()
		vid.findFaces()
		vid.display()
		# exit on escape key
		key = cv2.waitKey(20)
		if key == 27:
			break
	vid.endWindow()


goGetEm()