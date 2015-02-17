from PIL import Image
import math

def setProfile(image, coordinate, bins):
    #change to y-x instead of x-y coordinates
    coordinates = [[0,0],[0,0]]
    coordinates[0][0] = coordinate[0][1]
    coordinates[0][1] = coordinate[0][0]
    coordinates[1][0] = coordinate[1][1]
    coordinates[1][1] = coordinate[1][0]
    imageHeight = len(image)
    imageWidth = len(image[0])

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
    for x in range(0, imageHeight, 5):
            for y in range(0, imageWidth, 5):
                intensity = float(image[x][y][0] + image[x][y][1] + image[x][y][2] + 1)
                R = image[x][y][0] / intensity
                G = image[x][y][1] / intensity
                #check if pixel is with face box
                if(x < coordinates[0][0] or y < coordinates[0][1] or x > coordinates[1][0] or y > coordinates[1][1]):
                    if(R > .7):
                        notSkinHistR[bins - 1] += 1
                    else:
                        notSkinHistR[int(R / (.7 / (bins - 1)))] += 1 #got rid of pixelData, which was R / intensity, for sake of time wasted constructing that array
                    if(G > .7):
                        notSkinHistG[bins - 1] += 1
                    else:
                        notSkinHistG[int(G / (.7 / (bins - 1)))] += 1
                else:
                    if(R > .7):
                        skinHistR[bins - 1] += 1
                    else:
                        skinHistR[int(R / (.7 / (bins - 1)))] += 1
                    if(G > .7):
                        skinHistG[bins - 1] += 1
                    else:
                        skinHistG[int(G / (.7 / (bins - 1)))] += 1
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
			intensity = float(image2[i][j][0] + image2[i][j][1] + image2[i][j][2])
			row.append((image2[i][j][0] / intensity, image2[i][j][1] / intensity))
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
	intensity = pixel[0] + pixel[1] + pixel[2] + 1
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
		y = pGreen[int(g / (.7 / (bins - 1)))]
	elif(g > .7):
		x = pRed[int(r / (.7 / (bins - 1)))]
		y = pGreen[bins - 1]
	else:
		x = pRed[int(r / (.7 / (bins - 1)))]
		y = pGreen[int(g / (.7 / (bins - 1)))]
	return x * y
