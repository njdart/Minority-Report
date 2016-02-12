"""
This should be interpreted using Python 2.7, with OpenCV 2.4.
"""

import cv2
import matplotlib.pyplot as plt
import numpy as np

MAX_IMG_WIDTH = 1360
MAX_IMG_HEIGHT = 768

def resize_and_show(img, scale = 0.0):
    img_resize = np.copy(img)
    if scale != 0.0:
        scale_factor = scale
    else:
        scale_factor = min(float(MAX_IMG_WIDTH) / img_resize.shape[0], float(MAX_IMG_HEIGHT) / img_resize.shape[1])
    img_resize = cv2.resize(img_resize, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    cv2.imshow("an image", img_resize)
    cv2.waitKey(-1)

def binary_threshold(img):
    gaussian_ksize = (11, 11)
    gaussian_sigmax = 0

    img_blur = cv2.GaussianBlur(img, gaussian_ksize, gaussian_sigmax)
    resize_and_show(img_blur)

    img_blur = cv2.cvtColor(img_blur, cv2.COLOR_BGR2GRAY)
    img_blur = np.array(img_blur, np.uint8)
    resize_and_show(img_blur)

    val_threshold, img_threshold = cv2.threshold(img_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resize_and_show(img_threshold)

    return img_threshold

def get_distinct_boxes(img):
    img_binary = binary_threshold(img)

    contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_KCOS)
    img_contours = np.zeros_like(img_binary)
    cv2.drawContours(img_contours, contours, -1, 255)
    resize_and_show(img_contours)

    total = 0
    for i in range(len(contours)):
        if cv2.contourArea(contours[i]) > 1000:
            total += 1
            img_contour = np.zeros_like(img_contours)
            cv2.drawContours(img_contour, contours, i, 255)
            resize_and_show(img_contour, 0.3 )
    print total

    markers = img_contours
    markers = np.int32(markers)

    cv2.watershed(img, markers)
    # resize_and_show(markers)

    img[markers == -1] = [255, 0, 0]
    resize_and_show(img)
    cv2.imwrite("imgoutlel.jpg", img)

    # contours, hierarchy = cv2.findContours(img_canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
    # print len(contours)
    # print hierarchy
    # cv2.waitKey(1)
    # idx = 0
    # while hierarchy[0][idx][0] >= 0:
    #     contour_img = np.zeros_like(img_binary)
    #     idx = hierarchy[0][idx][0]
    #     cv2.drawContours(contour_img, contours, idx, 255)
    #     plt.imshow(contour_img, "gray")
    #     plt.show()

"""
Temporary: Testing algorithms
"""
if __name__ == "__main__":
    #img = cv2.imread("../kinect-imgs/colour/KinectScreenshot-Color-10-50-36.png", 0)
    img = cv2.imread("../camera-imgs/postits1.jpg")
    get_distinct_boxes(img)