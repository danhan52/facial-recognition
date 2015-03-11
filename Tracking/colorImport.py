from PIL import Image
import math

def setProfile(image, coordinate, bins):
    #sets the color profile of a face found in a frame

    #change to y-x instead of x-y coordinates
    coordinates = [[0,0],[0,0]]
    coordinates[0][0] = coordinate[0][1]
    coordinates[0][1] = coordinate[0][0]
    coordinates[1][0] = coordinate[1][1]
    coordinates[1][1] = coordinate[1][0]
    imageHeight = len(image)
    imageWidth = len(image[0])

    #histograms representing how many pixels we see that have certain redness and greenness values, and whether those pixels are in the face region or outside of it.
    skinHistR = []
    skinHistG = []
    notSkinHistR = []
    notSkinHistG = []
    for i in range(bins): #append 1's to avoid future divide by zero problems
            skinHistR.append(1)
            skinHistG.append(1)
            notSkinHistR.append(1)
            notSkinHistG.append(1)

    #go through pixels in the image, calculate their redness and greenness, and update the histograms accordingly
    for x in range(0, imageHeight, 5): #for performance, look at every 25th pixel since we are using a high-resolution camera.
            for y in range(0, imageWidth, 5):
                intensity = float(image[x][y][0] + image[x][y][1] + image[x][y][2] + 1)
                #redness defined as r-intensity/total-intensity
                R = image[x][y][0] / intensity
                G = image[x][y][1] / intensity
                #check if pixel is inside the face region
                if(x < coordinates[0][0] or y < coordinates[0][1] or x > coordinates[1][0] or y > coordinates[1][1]):
                    #pixels are rarely more than 70% red or green, so the last bin contains all redness values above .7
                    if(R > .7):
                        notSkinHistR[bins - 1] += 1
                    else:
                        notSkinHistR[int(R / (.7 / (bins - 1)))] += 1
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

    #combine histograms using Bayesian analysis to find probability that a pixel of a certain red/greenness is part of the face
    pRed = []
    pGreen = []
    for bin in range(len(skinHistR)):
        pRed.append(float(skinHistR[bin]) / (notSkinHistR[bin] + skinHistR[bin]))
        pGreen.append(float(skinHistG[bin]) / (notSkinHistG[bin] + skinHistG[bin]))
    #return these histograms as the color profile
    return [pRed, pGreen]


def colorScore(image2, coordinates, profile):
    #takes a location of a face in a frame and a color profile from a previous frame and produces a score.
    #meant for use in score function.

	#put {R,G} tuples in 2D-array
	pRed = profile[0]
	pGreen = profile[1]
	pixelData2 = []
    #find red/greenness values of face pixels and store in an array
	for i in range(coordinates[0][0], coordinates[1][0] + 1):
		row = []
		for j in range(coordinates[0][1], coordinates[1][1] + 1):
			intensity = float(image2[i][j][0] + image2[i][j][1] + image2[i][j][2])
			row.append((image2[i][j][0] / intensity, image2[i][j][1] / intensity))
		pixelData2.append(row)

	score = float(0)
    #for each pixel in the face region, use the profile to find the likelihood that it belongs to the previously detected face
	for i in range(len(pixelData2)):
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
            #multiply the red and green probabilities to find an overall probability
			score += x * y
    #normalize score by the number of pixels in the face
	score /= len(pixelData2)*len(pixelData2[0])

	return score

def getPixelP(profile, pixel, bins):
    #given a pixel in a frame, find the probability it belonged to a face in a previous frame

    #find redness/greenness values
	intensity = pixel[0] + pixel[1] + pixel[2] + 1
	r = float(pixel[0]) / intensity
	g = float(pixel[1]) / intensity
	x = 0.0
	y = 0.0
	pRed = profile[0]
	pGreen = profile[1]
    #find probability associated with red/grenness value
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
    #multiply red and green probabilities to find overall probability
	return x * y
