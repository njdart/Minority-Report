import cv2
from matplotlib import pyplot as plt

class PostitDetector():
    def __init__(self, filename=None):
        if filename is not None:
            self.img = cv2.imread(filename)
        else:
            raise ValueError("No filename provided")

    def show_img(self, image):
        """
        Convenience function
        Will eventually have error checking
        """
        plt.imshow(image)
        plt.show()

    def img_to_binary(self, image):
        """
        Converts an image into a binary image with hopefully
        the post it notes in white and the rest in black
        """
        if image is None:
            raise ValueError("Image was None")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        print("ret was {0}".format(ret))
        return thresh

    def resize_img(self, image, axis=None, res_val=None):
        """
        Resizes an image to fit on the screen by default
        when supplying X or Y, it will resize (keeping aspect ratio)
        to that
        """
        try:
            height, width, channels = image.shape
        except ValueError:
            height, width = image.shape
            channels = 1
        except:
            raise

        if axis is not None and res_val is not None:
            if axis == "X":
                res_factor = float(res_val) / width
            elif axis == "Y":
                res_factor = float(res_val) / height
            else:
                raise ValueError("Incorrect value supplied for axis")
        else:
            res_factor = 1000.0 / width

        return cv2.resize(image, None, fx=res_factor, fy=res_factor, interpolation=cv2.INTER_CUBIC)

    def edge_detect(self, image, lower_thresh=100, upper_thresh=200):
        blur = cv2.blur(image, (3, 3))
        return cv2.Canny(blur, lower_thresh, upper_thresh)

if __name__ == "__main__":
    p = PostitDetector("C:\\src\\Minority-Report\\camera-imgs\\postits1.jpg")
    p.img = p.resize_img(p.img)
    # p.show_img(p.img)
    p.img = p.img_to_binary(p.img)
    #p.show_img(p.img)
    edge = p.edge_detect(p.img)

