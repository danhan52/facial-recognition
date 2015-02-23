import numpy as np
import cv2
from detection import *
from PIL import Image


glasses = Image.open('groucho_glasses.png', 'r')
face_cascade = cv2.CascadeClassifier("face_cascade2.xml")

def detect_img(img):
    rects = face_cascade.detectMultiScale(img, 1.3, 5, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img
    
    
def draw_things_2(rects, face_pic):
	for (x1, y1, x2, y2) in rects:
		rescaled_glasses = glasses.resize((x2 - x1, int((y2 - y1)*.75)))
		face_pic.paste(rescaled_glasses, (x1, y1+int((y2 - y1)*.1)), rescaled_glasses)
	return face_pic
    

def capture_video():
	cap = cv2.VideoCapture(0)

	while(True):
		# Capture frame-by-frame
		ret, frame = cap.read()

		# Our operations on the frame come here
		#gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = frame
		frameImage = cv2.flip(gray,1)
		
		rects, img = detect_img(frameImage)
		#box(rects, img)
		#gray = list(.getdata())
		frameImage = np.asarray(draw_things_2(rects, Image.fromarray(frameImage)))
		#print gray

		# Display the resulting frame
		cv2.imshow('frame',frameImage)
		
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# When everything done, release the capture
	cap.release()
	cv2.destroyAllWindows()
	
if __name__ == "__main__":
	capture_video()