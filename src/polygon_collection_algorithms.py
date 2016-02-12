"""
This should be interpreted using Python 2.7, with OpenCV 2.4.
"""

import cv2
import matplotlib.pyplot as plt

"""
Blurs/smooths with a bilateral filter, grayscales the image, then applies an adaptive threshold to ease structural
analysis of the image.
"""
def bilateral_threshold(img):
    BI_NEIGHBORHOOD = 30
    BI_SIGMACOLOR = 150
    BI_SIGMASPACE = 150

    img_blurred_color = cv2.bilateralFilter(img, d=BI_NEIGHBORHOOD, sigmaColor=BI_SIGMACOLOR, sigmaSpace=BI_SIGMASPACE)
    img_blurred_gray = cv2.cvtColor(img_blurred_color, cv2.COLOR_BGR2GRAY)

    # change this line as the algorithm develops
    img_final = img_blurred_gray

    return img_final

"""
Temporary: Testing algorithms
"""
if __name__ == "__main__":
    img = cv2.imread("../camera-imgs/postits2.jpg", 0)
    img_processed = bilateral_threshold(img)
    plt.imshow(img_processed)
    plt.show()