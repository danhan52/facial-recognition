from PIL import Image
import math

#uses a/(a+b) for the probability

image = Image.open("jessica.jpg")
image = image.convert('RGB')
image2 = Image.open("jessica.jpg")
image2 = image2.convert('RGB')
bins = 122

image.getpixel((1,1))
print image.size
imageHeight = image.size[1]
imageWidth = image.size[0]
nSkin = None
nTotal = imageHeight * imageWidth

faceTopLeft = (292,384) #150,30 #192,365
faceBottomRight = (72,200) #190,100 #416,600

#mean/mediam filter?
#put {R,G} tuples in 2D-array
pixelData = []
for i in range(imageWidth):
	row = []
	for j in range(imageHeight):
		#adjust intensity r = R/(R+G+B)
		intensity = float(image.getpixel((i,j))[0] + image.getpixel((i,j))[1] + image.getpixel((i,j))[2])
		row.append((image.getpixel((i,j))[0] / intensity, image.getpixel((i,j))[1] / intensity))
		#FOR LATER, GROUP ANYTHING ABOVE .7
	pixelData.append(row)

#put {R,G} tuples in 2D-array
pixelData2 = []
for i in range(imageWidth):
	row = []
	for j in range(imageHeight):
		#adjust intensity r = R/(R+G+B)
		intensity = float(image2.getpixel((i,j))[0] + image2.getpixel((i,j))[1] + image2.getpixel((i,j))[2])
		row.append((image2.getpixel((i,j))[0] / intensity, image2.getpixel((i,j))[1] / intensity))
	pixelData2.append(row)


#are there enough pixels for it to be 2D array?  increase bin size as result?
skinHistR = []
skinHistG = []
notSkinHistR = []
notSkinHistG = []
for i in range(bins): #append 1's to avoid future divide by zero problems
	skinHistR.append(1)
	skinHistG.append(1)
	notSkinHistR.append(1)
	notSkinHistG.append(1)

#smooth histogram?
nSkin = 0
for x in range(imageWidth):
	for y in range(imageHeight):
		#assuming better accuracy by assuming face is a diamond.  checking if pixel is outside of the face
		if(y + x * imageHeight / imageWidth <= imageHeight / 2 or y - x * imageHeight / imageWidth >= imageHeight / 2 or y + x * imageHeight / imageWidth >= 1.5 * imageHeight or y - x * imageHeight / imageWidth <= -0.5 * imageHeight):
			if(pixelData[x][y][0] > .7):
				notSkinHistR[bins - 1] += 1
			else:
				notSkinHistR[int((pixelData[x][y][0]) / (.7 / (bins - 1)))] += 1
			if(pixelData[x][y][1] > .7):
				notSkinHistG[bins - 1] += 1
			else:
				notSkinHistG[int((pixelData[x][y][1]) / (.7 / (bins - 1)))] += 1
		else:
			if(pixelData[x][y][0] > .7):
				skinHistR[bins - 1] += 1
			else:
				skinHistR[int((pixelData[x][y][0]) / (.7 / (bins - 1)))] += 1
			if(pixelData[x][y][1] > .7):
				skinHistG[bins - 1] += 1
			else:
				skinHistG[int((pixelData[x][y][1]) / (.7 / (bins - 1)))] += 1
			nSkin += 1

pRed = [] #method 1 for calculating probability
pGreen = []
pRed2 = [] #method 2 for calculating probability
pGreen2 = []
for bin in range(len(skinHistR)):								#risk of dividing by 0 in this block
	pRed.append(float(skinHistR[bin]) / (notSkinHistR[bin] + skinHistR[bin]))
	pGreen.append(float(skinHistG[bin]) / (notSkinHistG[bin] + skinHistG[bin]))
	#pRed2.append(math.exp(skinHistR[bin]) / nSkin * nTotal / (notSkinHistR[bin]))
	#pGreen2.append(math.exp(skinHistG[bin]) / nSkin * nTotal / (notSkinHistG[bin]))
print pRed
densityImg = Image.new( 'RGB', (imageWidth, imageHeight), "black") # create a new black image
densityPixels = densityImg.load() # create the pixel map
score = float(0)
for i in range(densityImg.size[0]):    # for every pixel:
    for j in range(densityImg.size[1]):
		if(pixelData2[i][j][0] > .7 and pixelData2[i][j][1] > .7):
			x = pRed[bins - 1]
			y = pGreen[bins - 1]
		elif(pixelData2[i][j][0] > .7):
			x = pRed[bins - 1]
			y = pGreen[int(pixelData2[i][j][1] / (.7 / (bins - 1)))]
		elif(pixelData[i][j][1] > .7):
			x = pRed[int(pixelData2[i][j][0] / (.7 / (bins - 1)))]
			y = pGreen[bins - 1]
		else:
			x = pRed[int(pixelData2[i][j][0] / (.7 / (bins - 1)))]
			y = pGreen[int(pixelData2[i][j][1] / (.7 / (bins - 1)))]
		densityPixels[i,j] = (int(x * 150), int(y * 150), 0)
		score += x * y * 10
		'''if(pixelData2[i][j][0] > .7 and pixelData2[i][j][1] > .7):
			densityPixels[i,j] = (int(pRed[bins - 1] * 40), 0, 0)
		elif(pixelData2[i][j][0] > .7):
			densityPixels[i,j] = (int(pRed[bins - 1] * 40), 0, 0)
		elif(pixelData[i][j][1] > .7):
			densityPixels[i,j] = (int(pRed[int(pixelData2[i][j][0] / (.7 / (bins - 1)))] * 40), 0, 0)
		else:
			densityPixels[i,j] = (int(pRed[int(pixelData2[i][j][0] / (.7 / (bins - 1)))] * 40), 0, 0)'''
		'''if(pixelData2[i][j][0] > .7 and pixelData2[i][j][1] > .7):
			densityPixels[i,j] = (int(pRed[bins - 1] * pGreen[bins - 1] * 40), 0, 0)
		elif(pixelData2[i][j][0] > .7):
			densityPixels[i,j] = (int(pRed[bins - 1] * pGreen[int(pixelData2[i][j][1] / (.7 / (bins - 1)))] * 40), 0, 0)
		elif(pixelData[i][j][1] > .7):
			densityPixels[i,j] = (int(pRed[int(pixelData2[i][j][0] / (.7 / (bins - 1)))] * pGreen[bins - 1] * 40), 0, 0)
		else:
			densityPixels[i,j] = (int(pRed[int(pixelData2[i][j][0] / (.7 / (bins - 1)))] * pGreen[int(pixelData2[i][j][1] / (.7 / (bins - 1)))] * 40), 0, 0)'''	
score /= imageHeight*imageWidth
densityImg.show()
 	
#AT THIS POINT, CAN PLOT FOR PROOF OF CONCEPT

#create new grayscale image.  make pixel proportional to pRed * pGreen from pixelData2.  display.
#someUnscaledValue = pRed[pixelData2[x][y][0] // binSize] * pGreen[pixelData2[x][y][0] // binSize]


#optimization algorithm for new face.  go back to using square for this part maybe.

#for all possible squares, which gives the highest combined average probability and size.  experiment - should they be maximized when multiplied?
#what ratio/exponents/weights should size and probability have? how will we factor in previous size and position?  will it on average
#shrink or grow over time?  put in a scale factor to account for this?
#scale midpoint probability by gaussian with stdev related to velocity