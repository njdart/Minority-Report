class Postit:
    """Individual Postit"""
    def __init__(self, newid, postitdata, physical):
        self.ID = newid
        self.location = [postitdata["position"][0], postitdata["position"][1]]
        self.size = [postitdata["position"][2], postitdata["position"][3]]
        self.image = postitdata["image"]
        self.colour = postitdata["colour"]
        self.keypoints = postitdata["keypoints"]
        self.descriptors = postitdata["descriptors"]
        self.physical = physical
        self.Text = ""

    def update(self, postitdata):
        self.location = [postitdata["position"][0], postitdata["position"][1]]
        self.size = [postitdata["position"][2], postitdata["position"][3]]
        self.image = postitdata["image"]
        self.colour = postitdata["colour"]
        self.keypoints = postitdata["keypoints"]
        self.descriptors = postitdata["descriptors"]

    def getID(self):
        return self.ID

    def setState(self,newstate):
        self.physical = newstate


if __name__ == "__main__":
    pass
