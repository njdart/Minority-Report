import numpy as np
import cv2
import math



def getImage():
    image = 'test2.jpg'
    image = cv2.imread(image)
    return image


def findChessboardCorners(image, pattern_size):
    ret, corners = cv2.findChessboardCorners(image, pattern_size, None)
    return corners


def calibDist(pattern_size, image):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= 6

    imgpoints = [] # 2d points in image plane.
    objpoints = [] # 3d point in real world space

    #open image, turn to grey
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    #find checkerboard
    corners = findChessboardCorners(gray, pattern_size)

    #will fail if there is no board found
    objpoints.append(pattern_points)

    cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
    imgpoints.append(corners.reshape(-1,2))

    #calibration
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

    h,  w = image.shape[:2]

    undistorted = cv2.undistort(image, mtx, dist)

    corners = findChessboardCorners(undistorted, pattern_size)

    cv2.imwrite('undis.jpg',undistorted)

    corners = findChessboardCorners(undistorted, pattern_size)

    return mtx, dist, corners, (h, w)


def getHypot(i):
    return math.hypot(i[0],i[1])


def cropSquare(corners, image, imgsize):

    a = (corners[0][0][0],corners[0][0][1])
    b = (corners[pattern_size[0]-1][0][0],corners[pattern_size[0]-1][0][1])
    c = (corners[pattern_size[0]*pattern_size[1]-1][0][0],corners[pattern_size[0]*pattern_size[1]-1][0][1])
    d = (corners[-pattern_size[0]][0][0],corners[-pattern_size[0]][0][1])

    cornerpoints = [a,b,c,d]
    origin = []

    origin = sorted(cornerpoints, key=getHypot ,reverse=False)


    origin = np.float32(origin)
    destinaiton = np.float32([[0,0],[0,imgsize[0]],[imgsize[1],0],[imgsize[1],imgsize[0]]])

    print origin
    print destinaiton

    M = cv2.getPerspectiveTransform(origin, destinaiton)
    dst = cv2.warpPerspective(image, M, tuple(reversed(imgsize)))

    return dst
    #returns cropped and squared off image


def undistortImage(mtx, dist, img, corners, imgsize):
    unfishified = cv2.undistort(img, mtx, dist)
    final = cropSquare(corners, unfishified, imgsize)
    cv2.imwrite('final.jpg',final)
    return final


if __name__ == "__main__":


    pattern_size = (4,8)#(9,6)

    img = getImage()

    mtx, dist, corners, imgsize = calibDist(pattern_size, img)


    #todo: store mtx, dist, corners, imgsize


    final = undistortImage(mtx, dist, img, corners, imgsize)






