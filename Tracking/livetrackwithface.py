import cv2
import os
from architecture import Face
from architecture import Video

def goGetEm():
	fc = Face()
	vid = Video(0)
	vid.readFrame()
	while (True):
		#detect
		rects = vid.detectAll()
		if len(rects)==0:
			fc.setPosition(None,1,1,1)
			fc.incrementTimeSinceDetection()
			rects = []
		else:
			rects[:, 2:] += rects[:, :2]
		#make box image
		#print fc.getTimeSinceDetection()
		for x1, y1, x2, y2 in rects:
			fc.setPosition(x1, y1, x2, y2)
			pos = fc.getPosition()
			fc.calculateVelocity()
			print fc.getVelocity()
			# print pos
			vid.showRectangle(pos)
		vid.display()
		vid.readFrame()				#read next frame
		key = cv2.waitKey(20)
		if key == 27:
			break
	vid.endWindow()


goGetEm()