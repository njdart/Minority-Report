import cv2
import numpy


def grayscale_smooth(np_image):
    """
    Convert an image to black+white and apply a bilarteral smooth filter
    """
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray_img = cv2.cvtColor(np_image, cv2.COLOR_RGB2GRAY)
    norm_img = clahe.apply(gray_img)
    smooth_img = cv2.bilateralFilter(norm_img, 3, 75, 75)
    return smooth_img


    # Takes 4 corner points and use them to try and unwarp a rectangular image


def four_point_transform(image, pts):
    """
    transforms an image using four given points to flatten and transform into a rectangle
    Magic taken from http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
    """
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    width_a = numpy.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = numpy.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    height_a = numpy.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = numpy.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = numpy.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    transform_matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, transform_matrix, (max_width, max_height))

    # return the warped image
    return warped


def order_points(pts):
    """
    takes a tuple of four point tuples and order then in the following order;
    [topLeft, topRight, bottomRight, bottomLeft]
    Magic taken from http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
    """
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = numpy.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum

    s = pts.sum(axis=1)
    rect[0] = pts[numpy.argmin(s)]
    rect[2] = pts[numpy.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = numpy.diff(pts, axis=1)
    rect[1] = pts[numpy.argmin(diff)]
    rect[3] = pts[numpy.argmax(diff)]

    # return the ordered coordinates
    return rect


def guess_colour(r, g, b):
    # Use the average RGB values of a postit and then using the difference between them
    # to establish which of the four supported colours it is.
    r = int(r)
    g = int(g)
    b = int(b)

    rg = r - g
    rb = r - b
    gb = g - b

    colour_thresholds = {
        "ORANGE": {
            "min_rg": 20,
            "max_rg": 90,
            "min_rb": 60,
            "max_rb": 160,
            "min_gb": 25,
            "max_gb": 100
        },
        "YELLOW": {
            "min_rg": -30,
            "max_rg": 15,
            "min_rb": 35,
            "max_rb": 140,
            "min_gb": 40,
            "max_gb": 140
        },
        "BLUE": {
            "min_rg": -110,
            "max_rg": -20,
            "min_rb": -140,
            "max_rb": -40,
            "min_gb": -45,
            "max_gb": 0
        },
        "MAGENTA": {
            "min_rg": 40,
            "max_rg": 135,
            "min_rb": 25,
            "max_rb": 100,
            "min_gb": -55,
            "max_gb": -10
        },
    }

    for colour in colour_thresholds:
        if ((rg >= colour_thresholds[colour]["min_rg"]) and
                (rg <= colour_thresholds[colour]["max_rg"]) and
                (rb >= colour_thresholds[colour]["min_rb"]) and
                (rb <= colour_thresholds[colour]["max_rb"]) and
                (gb >= colour_thresholds[colour]["min_gb"]) and
                (gb <= colour_thresholds[colour]["max_gb"])):
            return colour

    return None

def binarize(image, lightest=True):
    # Process converts an image to black and white using clustering to the lightest and darkest areas
    Z = image.reshape((-1,3))
    # convert to np.float32
    Z = numpy.float32(Z)
    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    if lightest:
        K = 3
    else:
        K = 2
    ret,label,center = cv2.kmeans(data=Z,
                                  K=K,
                                  bestLabels=None,
                                  criteria=criteria,
                                  attempts=10,
                                  flags=cv2.KMEANS_RANDOM_CENTERS)
    # Now convert back into uint8, and make original image
    center = numpy.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((image.shape))

    bmin = res2[..., 0].min()
    gmin = res2[..., 1].min()
    rmin = res2[..., 2].min()
    bmax = res2[..., 0].max()
    gmax = res2[..., 1].max()
    rmax = res2[..., 2].max()
    if lightest:
        image[numpy.where((res2 < [bmax, gmax, rmax]).all(axis=2))] = [0, 0, 0]
        image[numpy.where((res2 == [bmax, gmax, rmax ]).all(axis=2))] = [255, 255, 255]
    else:
        image[numpy.where((res2 > [0, 0, 0]).all(axis=2))] = [0, 0, 0]
        image[numpy.where((res2 > [bmin, gmin, rmin]).all(axis=2))] = [255, 255, 255]
    return image


def edge(img):
    kernel = numpy.ones((5, 5), numpy.uint8)
    #img = cv2.medianBlur(img, 9)
    img = cv2.bilateralFilter(img,9,75,75)
    gray_image = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    edged = cv2.Canny(gray_image, 1, 30)

    return edged


def get_area(points):
    #if len(points) == 4:
    #    points = self.order_points(points)
    pointsum = 0
    for index in range(-1, len(points) - 1):
        pointsum = pointsum + (points[index][0] * points[index + 1][1] - points[index][1] * points[index + 1][0])
    area = abs(pointsum / 2)
    return area