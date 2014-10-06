import cv2
from PIL import Image

def detect(path):
    img = cv2.imread(path)
    face_cascade = cv2.CascadeClassifier("/Users/Katja/Downloads/haarcascade_frontalface_alt.xml")
    rects = face_cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))

    if len(rects) == 0:
        return [], img
    rects[:, 2:] += rects[:, :2]
    return rects, img

def box(rects, img):
    #eye_cascade = cv2.CascadeClassifier("/usr/local/Cellar/opencv/2.4.9/share/OpenCV/haarcascades/haarcascade_eye.xml")
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)
        #roi_color = img[y1:y2, x1:x2]
        #eyes = eye_cascade.detectMultiScale(roi_color, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20,20))
        #for (ex,ey,ew,eh) in eyes:
        #    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(42,150,0),2)
    cv2.imwrite('/Users/Katja/Desktop/detected.jpg', img);
    
def draw_things(rects, img_path):
	face_pic = Image.open(img_path, 'r')
	glasses = Image.open('/Users/Katja/Downloads/groucho_glasses.png', 'r')
	
	for (x1, y1, x2, y2) in rects:
		rescaled_glasses = glasses.resize((x2 - x1, y2 - y1))
		face_pic.paste(rescaled_glasses, (x1, y1), rescaled_glasses)
	face_pic.save('/Users/Katja/Desktop/detected-glasses.png')

    
    
    
if __name__ == "__main__":
	rects, img = detect("/Users/Katja/Downloads/charlotte-katja-4.jpg")
	print "rects:", rects
	#box(rects, img)
	draw_things(rects, '/Users/Katja/Downloads/charlotte-katja-4.jpg')


	#/usr/local/Cellar/opencv/2.4.9/share/OpenCV/haarcascades/