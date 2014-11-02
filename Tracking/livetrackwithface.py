import cv2
import os
from architecture import Face
from architecture import Video

def goGetEm():
	vid = Video(0)
	vid.readFrame()
	while (True):
		#detect
		rects = vid.detectAll()
		if len(rects)==0:
			# fc.setPosition()
			# fc.incrementTimeSinceDetection()
			rects = []
		else:
			rects[:, 2:] += rects[:, :2]
		#make box image
		vid.analyzeFrame(rects)
		# for rect in rects:
		# 	fc.setPosition(rect)
		# 	pos = fc.getPosition()
		# 	fc.calculateVelocity()
		# 	vid.showRectangle(pos)
		vid.display()
		vid.readFrame()				#read next frame
		key = cv2.waitKey(20)
		if key == 27:
			break
	vid.endWindow()


goGetEm()