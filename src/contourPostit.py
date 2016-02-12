import cv2
import numpy as np

DEBUG_PLOT = True
# => Bilateral filter params
BILATERAL_PIX_NEIGHBORHOOD = 1
BILATERAL_SIGMA_COLOR = 1
BILATERAL_SIGMA_SPACE = 1

if __name__ == "__main__":

    image = cv2.imread("whiteboard-postit.jpg")
    ratio = image.shape[0] / 300.0
    orig = image.copy()

    # convert the image to grayscale, blur it, and find edges
    # in the image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, d=BILATERAL_PIX_NEIGHBORHOOD, sigmaColor=BILATERAL_SIGMA_COLOR, sigmaSpace=BILATERAL_SIGMA_SPACE)    #gray = cv2.bilateralFilter(gray, 11, 17, 17)
    v = np.median(image)
    sigma=0.8
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    #edged = cv2.Canny(gray, 30, 200)

    (_,cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:]
    screenCnt = None
    for c in cnts:

        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        box = cv2.boxPoints(cv2.minAreaRect(c))
        box = np.int0(box)

        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        #if cv2.arcLength(c,False) > 300:
        if (cv2.arcLength(c,False) > 300) and (cv2.arcLength(c,False) < 1000)and (cv2.contourArea(box) > 3000) and (cv2.contourArea(box) <20000) :

            cv2.drawContours(image, [box], 0, (0, 255, 0), 3)
            print(cv2.contourArea(box))

        if len(approx) ==4:
            screenCnt = approx



#cv2.drawContours(image, [screenCnt], -1, (0, 255, 0), 3)
screenCnt
# DEBUG PLOT
if DEBUG_PLOT:
    #cv2.imshow("gray",gray)
    cv2.imshow("edged",edged)
    cv2.imshow("CannyFiltered", image)
cv2.waitKey(0)
