import numpy as np
import cv2


criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((6*7,3), np.float32)
objp[:,:2] = np.mgrid[0:7,0:6].T.reshape(-1,2)

imgpoints = [] # 2d points in image plane.
objpoints = [] # 3d point in real world space

#original image
image = 'test1.jpg'

#open image, turn to grey
img = cv2.imread(image)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#find checkerboard
ret, corners = cv2.findChessboardCorners(gray, (8,4), None)

#if there is a board
if ret == True:
    objpoints.append(objp)

    cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
    imgpoints.append(corners)
    #draw checkerboard circles to new image
    cv2.drawChessboardCorners(img, (8,4), corners, ret)
    cv2.imwrite('image1.jpg', img)


    #doesnt work...

    #calibration
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


    #undistortion
    outimg = cv2.imread(img)

    dst = cv2.undistort(outimg, mtx, dist)
    cv2.imwrite('image2.jpg', dst)
