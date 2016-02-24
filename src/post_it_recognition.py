# Author : Torin Cooper-Bennun (tcb)

import cv2
import numpy as np
import matplotlib.pyplot as plt

# create display window
window = "Post-It Recognition"
cv2.namedWindow(window)

# highlight lines
img = cv2.imread('IR-images/amp10gamma1.PNG', 0)
#img = cv2.imread('postits1.jpg',0)
img_filtered = cv2.GaussianBlur(img, (0, 0), 1.5)
img_filtered = cv2.Canny(img_filtered, 0, 30)

# work in progress: determine contours
contours, hierarchy = cv2.findContours(img_filtered, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
img_contours = np.zeros_like(img)
cv2.drawContours(img_contours, contours, -1, 255)

# show images
cv2.imshow(window, img_filtered)
cv2.waitKey(-1)
cv2.imshow(window, img_contours)
cv2.waitKey(-1)

# write images to disk
cv2.imwrite('img_filtered.jpg', img_filtered)
cv2.imwrite('img_contours.jpg', img_contours)