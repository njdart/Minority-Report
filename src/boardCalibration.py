import numpy as np
import cv2
import math



def getImage():
    image = 'test3.jpg'
    image = cv2.imread(image)
    return image


def calibrateTilt():
    pass


def untiltImage(lb, lt, rt, rb):
    pass


def calibrateDistortion():
    print 'one'
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    #pattern_size = (7,6) #todo
    pattern_size = (9,6)
    pattern_points = np.zeros((np.prod(pattern_size), 3), np.float32)
    pattern_points[:, :2] = np.indices(pattern_size).T.reshape(-1, 2)
    pattern_points *= 6

    imgpoints = [] # 2d points in image plane.
    objpoints = [] # 3d point in real world space

    #original image
    image = getImage()
    print 'two'
    #open image, turn to grey
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite('grey.jpg', gray)
    #find checkerboard
    ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)
    print 'three'


    #if there is a board found within the image
    if ret == True:
        objpoints.append(pattern_points)

        cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners.reshape(-1,2))
        #draw checkerboard circles to new image
        cv2.drawChessboardCorners(image, pattern_size, corners, ret)
        #new image
        cv2.imwrite('image1.jpg', image)
        print 'four'
        #calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        h,  w = image.shape[:2]
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w, h),1,(w, h))

        return ret, mtx, dist, rvecs, tvecs, newcameramtx, roi, corners, imgpoints, (h, w)

def undistortImage(ret, mtx, dist, rvecs, tvecs, newcameramtx, roi):
    image = getImage()

    dst = cv2.undistort(image, mtx, dist, None, newcameramtx)

    #dst = cv2.undistort(image, mtx, dist)

    cv2.imwrite('image2.jpg', dst)

def getHypot(i):
    print i
    return math.hypot(i[0],i[1])

if __name__ == "__main__":

     #todo
    #pattern_size = (7,6) #todo
    pattern_size = (9,6)
    ret, mtx, dist, rvecs, tvecs, newcameramtx, roi, corners, imgpoints, imgsize = calibrateDistortion()

    #undistortImage(ret, mtx, dist, rvecs, tvecs, newcameramtx, roi)



    img2 = getImage()


    a = (corners[0][0][0],corners[0][0][1])
    b = (corners[pattern_size[0]-1][0][0],corners[pattern_size[0]-1][0][1])
    c = (corners[pattern_size[0]*pattern_size[1]-1][0][0],corners[pattern_size[0]*pattern_size[1]-1][0][1])
    d = (corners[-pattern_size[0]][0][0],corners[-pattern_size[0]][0][1])

    cornerpoints = [a,b,c,d]
    origin = []

    origin = sorted(cornerpoints, key=getHypot,reverse=False)
    print origin

    origin = np.float32(origin)
    destinaiton = np.float32([[0,0],[imgsize[1],0],[0,imgsize[0]],[imgsize[1],imgsize[1]]])

    M = cv2.getPerspectiveTransform(origin, destinaiton)
    dst = cv2.warpPerspective(img2, M, tuple(reversed(imgsize)))
    cv2.imwrite('new2.jpg',dst)

    #cv2.drawMarker(img2, lb,(255,0,125))
    #cv2.drawMarker(img2, lt,(255,0,125))
    #cv2.drawMarker(img2, rt,(255,0,125))
    #cv2.drawMarker(img2, rb,(255,0,125))



    cv2.imwrite('new.jpg',img2)



