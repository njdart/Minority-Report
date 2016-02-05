# Author : Torin Cooper-Bennun (tcb)

import cv2
import numpy as np

# highlight lines
img = cv2.imread('postits1.jpg',0)
img_filtered = cv2.GaussianBlur(img, (0, 0), 1.5)
img_filtered = cv2.Canny(img_filtered, 0, 30)

# work in progress: determine contours
contours, hierarchy = cv2.findContours(img_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
img_contours = np.zeros_like(img)
cv2.drawContours(img_contours, contours, -1, 0xff0000)

# write to disk
cv2.imwrite('img_filtered.jpg', img_filtered)
cv2.imwrite('img_contours.jpg', img_contours)