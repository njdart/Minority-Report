import cv2
import numpy as np

class Postit:
    """Individual Postit"""
    def __init__(self,id,x,y,width,height,colour,physical,last_canvas_ID):
        self.ID = id
        self.location = [x,y]
        self.size = [width,height]
        self.colour = colour
        self.physical = physical
        self.last_canvas_ID = last_canvas_ID

    def update(self, postitdata,new_canvas_ID ,state):
        self.location = [postitdata["position"][0], postitdata["position"][1]]
        self.size = [postitdata["position"][2], postitdata["position"][3]]
        self.image = postitdata["image"]
        self.colour = postitdata["colour"]
        self.last_canvas_ID = new_canvas_ID
        self.physical = state

    def getID(self):
        return self.ID

    def setState(self,newstate):
        self.physical = newstate

    def getDescriptors(self,canvasImage):
        sift  = cv2.xfeatures2d.SIFT_create()
        postit = self.getImage(canvasImage)
        gray = cv2.cvtColor(postit, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = sift.detectAndCompute(gray,None)
        return descriptors

    def getImage(self,canvasImage):
        postit = canvasImage[self.location[1]:(self.location[1]+self.size[1]), self.location[0]:(self.location[0]+self.size[0])]
        return postit

if __name__ == "__main__":
    pass
