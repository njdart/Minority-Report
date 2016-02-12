"""
This should be interpreted using Python 2.7, with OpenCV 2.4.
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np

def binary_threshold(img):
    gaussian_ksize = (11, 11)
    gaussian_sigmax = 0
    img_blur = cv2.GaussianBlur(img, gaussian_ksize, gaussian_sigmax)
    val_threshold, img_threshold = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return img_threshold

def get_distinct_boxes(img):
    img_binary = binary_threshold(img)

    contours, hierarchy = cv2.findContours(img_binary, cv2.)

"""
Temporary: Testing algorithms
"""
if __name__ == "__main__":
    #img = cv2.imread("../kinect-imgs/colour/KinectScreenshot-Color-10-50-36.png", 0)
    img = cv2.imread("../camera-imgs/postits1.jpg", 0)
    img_processed = otsu(img)
    plt.imshow(img_processed, "gray")
    plt.show()