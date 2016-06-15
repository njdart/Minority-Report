import cv2
import numpy as np
 
c = cv2.VideoCapture(0)
_,f = c.read()
static = f
avg1 = np.float32(f)
avg2 = np.float32(f)
 
while(1):
    _,f = c.read()
    cv2.accumulateWeighted(f,avg1,0.1)
    cv2.accumulateWeighted(f,avg2,0.01)
     
    res1 = cv2.convertScaleAbs(avg1)
    res2 = cv2.convertScaleAbs(avg2)
    res3 = np.subtract(f.astype(np.int16), static.astype(np.int16))
    res3[np.where((res3 < [0, 0, 0]).any(axis=2))] = [0, 0, 0]
    cv2.imshow('img',f)
    cv2.imshow('avg1',res1)
    cv2.imshow('avg2',res2)
    cv2.imshow('resullt',res3.astype(np.uint8))
    k = cv2.waitKey(20)
 
    if k == 27:
        break
 
cv2.destroyAllWindows()
c.release()
