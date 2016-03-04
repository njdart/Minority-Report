import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from time import sleep

def showRGBImage(img):
	mng = plt.get_current_fig_manager()
	mng.window.state('zoomed')
	plt.axis("off")
	plt.imshow(img)
	plt.show()

def showGreyImage(img):
	mng = plt.get_current_fig_manager()
	mng.window.state('zoomed')
	plt.axis("off")
	plt.imshow(img, cmap="Greys_r")
	plt.show()

loaded = cv2.imread("..\kinect-imgs\colour\KinectScreenshot-Color-10-50-36.png")

#colourimg = cv2.blur(loaded,(5,5))

colourimg = loaded

showRGBImage(colourimg)
res1,board = cv2.threshold(colourimg,200,255,cv2.THRESH_TOZERO)

showRGBImage(board)

grayBoard = cv2.cvtColor(board, cv2.COLOR_RGB2GRAY)

#showGreyImage(grayBoard)

res3, contours, hier = cv2.findContours(grayBoard, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#showGreyImage(res3)

# Find the index of the largest contour
areas = [cv2.contourArea(c) for c in contours]
max_index = np.argmax(areas)
cnt=contours[max_index]

x,y,w,h = cv2.boundingRect(cnt)
temp = colourimg
cv2.rectangle(temp,(x,y),(x+w,y+h),(0,255,0),2)

showRGBImage(temp)

loadedCropped = loaded[y:y+h, x:x+w]
#boardCropped = cv2.blur(loadedCropped, (5,5))
boardCropped = loadedCropped
showRGBImage(boardCropped)

res5,postitBoard = cv2.threshold(boardCropped,200,255,cv2.THRESH_TOZERO_INV)

showRGBImage(postitBoard)
greyPostitBoard = cv2.cvtColor(postitBoard, cv2.COLOR_RGB2GRAY)
#showGreyImage(greyPostitBoard)
res7, contours2, hier2 = cv2.findContours(greyPostitBoard, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

showGreyImage(res7)

notes = loadedCropped.copy()
print "number of contours: " + str(len(contours2))
for c in contours2:
	#notes = loadedCropped.copy()
	print "contour: " + str(c)

	#approx = cv2.approxPolyDP(c,0.01*cv2.arcLength(c,True),True)
	#print len(approx)
	#print approx
	#if len(approx) is 4:
	x1,y1,x2,y2 = cv2.boundingRect(c)
	#cv2.rectangle(notes,(x1,y1), (x1+x2,y1+y2), (0,255,0), 2)
	cv2.drawContours(notes, [c], 0, (0,255,0), 3)

showRGBImage(notes)
#cv2.imwrite("output1.png", notes)