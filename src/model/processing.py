import cv2


def grayscale_smooth(np_image):
    """
    Convert an image to black+white and apply a bilarteral smooth filter
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_img = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    norm_img = clahe.apply(gray_img)
    smooth_img = cv2.bilateralFilter(norm_img, 3, 75, 75)
    return smooth_img
