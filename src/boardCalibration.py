import numpy as np
import cv2


if __name__ == "__main__":

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    pattern_size = (7,6)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= 6

    print pattern_points

    imgpoints = [] # 2d points in image plane.
    objpoints = [] # 3d point in real world space

    #original image
    image = 'test3.jpg'

    #open image, turn to grey
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #find checkerboard
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

    #if there is a board found within the image
    if ret == True:
        objpoints.append(pattern_points)

        cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners.reshape(-1,2))
        #draw checkerboard circles to new image
        cv2.drawChessboardCorners(img, pattern_size, corners, ret)
        #new image
        cv2.imwrite('image1.jpg', img)


        #doesnt work...


        #calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)


        #undistortion
        outimg = cv2.imread(image)

        h,  w = img.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w, h),1,(w, h))
        dst = cv2.undistort(outimg, mtx, dist, None, newcameramtx)

        dst = cv2.undistort(outimg, mtx, dist)

        cv2.imwrite('image2.jpg', dst)

        img2 = cv2.imread('image2.jpg')
        print corners
        #print corners[0][0]
        #print corners[41][0]
        print corners[-1][0][0]
        print corners[-1][0][1]
        print imgpoints
        cv2.drawMarker(img2, (corners[0][0][0],corners[0][0][1]),2)
        cv2.drawMarker(img2, (corners[pattern_size[0]-1][0][0],corners[pattern_size[0]-1][0][1]),2)
        cv2.drawMarker(img2, (corners[pattern_size[0]*pattern_size[1]-1][0][0],corners[pattern_size[0]*pattern_size[1]-1][0][1]),1)
        cv2.drawMarker(img2, (corners[-1][0][0],corners[-1][0][1]),1)

        cv2.imwrite('new.jpg',img2)


