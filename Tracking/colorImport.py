from PIL import Image
import math

def setProfile(image, coordinates, bins):
	#put {R,G} tuples in 2D-array
	imageWidth = len(image)
	imageHeight = len(image[0])
	pixelData = []
	for i in range(imageWidth, 10):
		row = []
		for j in range(imageHeight, 10):
			#adjust intensity r = R/(R+G+B)
			intensity = float(image[i][j][0] + image.getpixel[i][j][1] + image.getpixel[i][j][2])
			row.append((image.getpixel[i][j][0] / intensity, image.getpixel[i][j][1] / intensity))
			#FOR LATER, GROUP ANYTHING ABOVE .7
		pixelData.append(row)

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

	#nSkin = 0 #nSkin not used right now
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
				#nSkin += 1

	pRed = [] #method 1 for calculating probability
	pGreen = []
	for bin in range(len(skinHistR)):
		pRed.append(float(skinHistR[bin]) / (notSkinHistR[bin] + skinHistR[bin]))
		pGreen.append(float(skinHistG[bin]) / (notSkinHistG[bin] + skinHistG[bin]))
	return [pRed, pGreen]


def colorScore(image2, coordinates, profile):
	#put {R,G} tuples in 2D-array
	pRed = profile[0]
	pGreen = profile[1]
	pixelData2 = []
	for i in range(coordinates[0][0], coordinates[1][0] + 1): #assuming coordinates in certain form
		row = []
		for j in range(coordinates[0][1], coordinates[1][1] + 1):
			#adjust intensity r = R/(R+G+B)
			intensity = float(image2.getpixel[i][j][0] + image2.getpixel[i][j][1] + image2.getpixel[i][j][2])
			row.append((image2.getpixel[i][j][0] / intensity, image2.getpixel[i][j][1] / intensity))
		pixelData2.append(row)

	score = float(0)
	for i in range(len(pixelData2)):    # for every pixel:
	    for j in range(len(pixelData2[0])):
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
			score += x * y
	score /= len(pixelData2)*len(pixelData2[0])

	return score

def getPixelP(profile, pixel, bins):
	intensity = pixel[0] + pixel[1] + pixel[2]
	r = float(pixel[0]) / intensity
	g = float(pixel[1]) / intensity
	x = 0.0
	y = 0.0
	pRed = profile[0]
	pGreen = profile[1]
	if(r > .7 and g > .7):
		x = pRed[bins - 1]
		y = pGreen[bins - 1]
	elif(r > .7):
		x = pRed[bins - 1]
		y = pGreen[g / (.7 / (bins - 1)))]
	elif(g > .7):
		x = pRed[int(r / (.7 / (bins - 1)))]
		y = pGreen[bins - 1]
	else:
		x = pRed[r / (.7 / (bins - 1)))]
		y = pGreen[g / (.7 / (bins - 1)))]
	return x * y