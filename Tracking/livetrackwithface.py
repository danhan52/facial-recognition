import cv2
import os
from architecture import Face 

def goGetEm():
	fc = Face()
	vidcap = cv2.VideoCapture(0)
	success, img = vidcap.read()
	fps = vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
	cv2.namedWindow("show")
	cascade = cv2.CascadeClassifier("face_cascade2.xml")		#used for detection
	while (True):
		#detect
		rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
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
			cv2.rectangle(img, pos[0], pos[1], (127, 255, 0), 2)
		cv2.imshow("show", img)
		success, img = vidcap.read()				#read next frame
		key = cv2.waitKey(20)
		if key == 27:
			break
	vidcap.release()
	cv2.destroyWindow("show")


goGetEm()