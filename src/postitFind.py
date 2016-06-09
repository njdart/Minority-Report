import cv2
import numpy as np

DEBUG_PLOT = True
# Params
# => Initial scale down factor
SCALE_DOWN_FACTOR = 0.75
# => Gaussian blur kernel size
GBLUR_KERNEL_SIZE = 7
# => Bilateral filter params
BILATERAL_PIX_NEIGHBORHOOD = 50
BILATERAL_SIGMA_COLOR = 150
BILATERAL_SIGMA_SPACE = 150

def equalizeColour(inputColour):
    # BRG to YCrCb
    YCrCb = cv2.cvtColor(inputColour, cv2.COLOR_BGR2YCrCb)
    [YChannel, CrChannel, CbChannel] = cv2.split(YCrCb)
    # Equalize luminance channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(20,20))
    YChannel = clahe.apply(YChannel)
    #YChannel = cv2.equalizeHist(YChannel)
    # Convert back to BRG
    YCrCb = cv2.merge([YChannel, CrChannel, CbChannel])
    output = cv2.cvtColor(YCrCb, cv2.COLOR_YCrCb2BGR)
    return output

def segmentation(inputColour):
    # BGR to Gray
    inputGray = cv2.cvtColor(inputColour, cv2.COLOR_BGR2GRAY)
    [B, G, R] = cv2.split(inputColour)
    # Adaptative gaussian thresholding
    threshB = cv2.adaptiveThreshold(B, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0)
    threshG = cv2.adaptiveThreshold(G, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0)
    threshR = cv2.adaptiveThreshold(R, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0)
    # Remove noise
    kernel = np.ones((3,3),np.uint8)
    threshB = cv2.morphologyEx(src=threshB, op=cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    threshG = cv2.morphologyEx(src=threshG, op=cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    threshR = cv2.morphologyEx(src=threshR, op=cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    kernel = np.ones((5,5),np.uint8)
    threshB = cv2.morphologyEx(src=threshB, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=2)
    threshG = cv2.morphologyEx(src=threshG, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=2)
    threshR = cv2.morphologyEx(src=threshR, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=2)
    #cv2.imshow("Debug1", threshB)
    #cv2.imshow("Debug0", threshG)
    #cv2.imshow("Debug2", threshR)
    sure_bg = thresholdTotal = cv2.bitwise_or(cv2.bitwise_or(threshB, threshG),threshR)
    #cv2.imshow("Debug3", thresholdTotal)
    # Find foreground mask
    dist_transform = cv2.distanceTransform(src=thresholdTotal, distanceType=cv2.DIST_L2, maskSize=3)
    ret, sure_fg = cv2.threshold(dist_transform,0.2*dist_transform.max(),255,0)
    # Clean the mask
    kernel = np.ones((9,9),np.uint8)
    sure_fg = cv2.morphologyEx(src=sure_fg, op=cv2.MORPH_OPEN, kernel=kernel, iterations=2)
    #cv2.imshow("Debug4", dist_transform)
    #cv2.imshow("Debug5", sure_fg)

    # Finding unknown region
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    # Markers labeling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    markers = cv2.watershed(inputColour,markers)
    inputColour[markers == -1] = [255,0,0]
    #cv2.imshow("Debug6", inputColour)


if __name__ == "__main__":
    # Load input image
    inputBigColour =  cv2.imread("whiteboard-stickyNote.jpg")
    # Scale down
    inputResizedColour = cv2.resize(inputBigColour, dsize=(0,0), fx=SCALE_DOWN_FACTOR, fy=SCALE_DOWN_FACTOR, interpolation=cv2.INTER_AREA)

    # Gaussian Blur (to remove text in the post-its)
    #blurredColour = cv2.GaussianBlur(inputResizedColour, ksize=(GBLUR_KERNEL_SIZE,GBLUR_KERNEL_SIZE), sigmaX=0)
    # Bilateral filtering
    blurredColour = cv2.bilateralFilter(inputResizedColour, d=BILATERAL_PIX_NEIGHBORHOOD, sigmaColor=BILATERAL_SIGMA_COLOR, sigmaSpace=BILATERAL_SIGMA_SPACE)

    v = np.median(inputResizedColour)
    sigma=0.33
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(inputResizedColour, lower, upper)
    # Histogram equalizationinputResizedColour
    #blurredColourEqual = equalizeColour(blurredColour)

    segmentation(blurredColour)

    # DEBUG PLOT
    if DEBUG_PLOT:
        #cv2.imshow("OriginalInput", inputBigColour)
        #cv2.imshow("ResizedInput", inputResizedColour)
        #cv2.imshow("Blurred", blurredColour)
        cv2.imshow("CannyFiltered",edged)

    cv2.waitKey(0)



