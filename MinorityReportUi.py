#!/usr/bin/python3
from gi.repository import Gtk, GdkPixbuf
import cv2
import numpy
from src.PostitExtract import PostitExtract as PostitExtractor

print(cv2.__version__)

class MyWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Hello World")
    
    self.set_default_size(600, 600)

    ### Layout Objects

    # Main Grid element
    mainvbox = Gtk.VBox(False, 0)
    self.add(mainvbox)

    ### Components

    # Main Menu
    self.menuBar = Gtk.MenuBar()
    mainvbox.pack_start(self.menuBar, False, False, 2)

    # Menu Bar Items
    self.fileMenuItem = Gtk.MenuItem("File")
    self.editMenuItem = Gtk.MenuItem("Edit")
    self.helpMenuItem = Gtk.MenuItem("Help")
    self.menuBar.append(self.fileMenuItem)
    self.menuBar.append(self.editMenuItem)
    self.menuBar.append(self.helpMenuItem)

    # File Menu Container
    self.fileMenu = Gtk.Menu()
    self.fileMenuItem.set_submenu(self.fileMenu)

    self.fileMenuImportButton = Gtk.MenuItem("Import")
    self.fileMenuExportButton = Gtk.MenuItem("Export")
    self.fileMenuQuitButton = Gtk.MenuItem("Quit")

    self.fileMenuImportButton.connect("activate", self.onFileMenuImportClick)

    self.fileMenu.append(self.fileMenuImportButton)
    self.fileMenu.append(self.fileMenuExportButton)
    self.fileMenu.append(self.fileMenuQuitButton)

    # Image Container
    imageDividerHBox = Gtk.HBox(True, 0)
    mainvbox.pack_end(imageDividerHBox, True, True, 2)

    # Settings Container
    settingsHBox = Gtk.HBox(True, 5)
    mainvbox.pack_end(settingsHBox, False, False, 2)
    settingsVBoxLeft = Gtk.VBox(False, 5)
    settingsVBoxMiddle = Gtk.VBox(False, 5)
    settingsVBoxRight = Gtk.VBox(False, 5)
    settingsHBox.pack_start(settingsVBoxLeft, True, True, 2)
    settingsHBox.pack_start(settingsVBoxMiddle, True, True, 2)
    settingsHBox.pack_start(settingsVBoxRight, True, True, 2)

    # Saturation Slider and Label
    self.saturationSlider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(value=50, lower=0, upper=100, step_incr=1, page_incr=10, page_size=0))
    saturationSliderLabel = Gtk.Label("Saturation")
    self.saturationSlider.set_draw_value(False)
    settingsVBoxLeft.pack_end(self.saturationSlider, False, False, 2)
    settingsVBoxLeft.pack_end(saturationSliderLabel, False, False, 2)

    # Contrast Slider and Label
    self.contrastSlider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(value=50, lower=0, upper=100, step_incr=1, page_incr=10, page_size=0))
    contrastSliderLabel = Gtk.Label("Contrast")
    self.contrastSlider.set_draw_value(False)
    settingsVBoxLeft.pack_end(self.contrastSlider, False, False, 2)
    settingsVBoxLeft.pack_end(contrastSliderLabel, False, False, 2)

    # Scale Image
    self.scaleInputImage = Gtk.SpinButton(adjustment=Gtk.Adjustment(value=0.5, lower=0.0, upper=1.0, step_incr=0.05, page_incr=0.1, page_size=0), climb_rate=0, digits=2)
    scaleInputImageLabel = Gtk.Label("Scale Factor")
    settingsVBoxLeft.pack_end(self.scaleInputImage, False, False, 2)
    settingsVBoxLeft.pack_end(scaleInputImageLabel, False, False, 2)

    # Output Image
    self.outputImageWidget = Gtk.Image()
    imageDividerHBox.pack_start(self.outputImageWidget, False, False, 2)

    # Input Image
    self.inputImageWidget = Gtk.Image()
    imageDividerHBox.pack_start(self.inputImageWidget, False, False, 2)

    self.inputImageBuf = None

    ### Event Bindings

    self.saturationSlider.connect("value-changed", self.adjustInputImage)
    self.contrastSlider.connect("value-changed", self.adjustInputImage)

  def onFileMenuImportClick(self, menuItem):
    importDialog = Gtk.FileChooserDialog(title="Open Input Image",
      parent=self,
      action=Gtk.FileChooserAction.OPEN,
      buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

    imageFilter = Gtk.FileFilter()
    imageFilter.set_name("Image Files (JPEG, PNG)")
    imageFilter.add_mime_type("image/png")
    imageFilter.add_mime_type("image/jpeg")
    imageFilter.add_mime_type("image/pjpeg")
    importDialog.add_filter(imageFilter)

    allFilter = Gtk.FileFilter()
    allFilter.set_name("All Files")
    allFilter.add_mime_type("*")
    importDialog.add_filter(allFilter)

    response = importDialog.run()

    if response == Gtk.ResponseType.OK:
      self.inputImageFileName = importDialog.get_filename()

      print("Input Image " + self.inputImageFileName)


      # By Default this will conver the image to RGB (removing alpha channels)
      # FU Opencv! OpenCV returns images in BGR Format , we need to convert them to RGB for gtk
      #
      # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_image_display/py_image_display.html
      #
      self.inputImage = cv2.imread(self.inputImageFileName)

      self.postitExtractor = PostitExtractor(self.inputImage)

      self.adjustInputImage(None)

    importDialog.destroy()

  def adjustInputImage(self, widget):

    if self.postitExtractor is None:
      return

    print("Adjust Image ")

    saturation = int(self.saturationSlider.get_value())
    contrast = int(self.contrastSlider.get_value())

    # TODO: Saturation and contrast

    postits = self.postitExtractor.extractPostits()

    print(len(postits))

    print(postits)

    for postit in postits:
      cv2.imshow("foo" + str(postit), postit["image"])

def equalizeColour(inputColour):
    # BRG to YCrCb
    YCrCb = cv2.cvtColor(inputColour, cv2.COLOR_BGR2YCrCb)
    [YChannel, CrChannel, CbChannel] = cv2.split(YCrCb)
    # Equalize luminance channel
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(20,20))
    YChannel = clahe.apply(YChannel)
    YChannel = cv2.equalizeHist(YChannel)
    # Convert back to BRG
    YCrCb = cv2.merge([YChannel, CrChannel, CbChannel])
    output = cv2.cvtColor(YCrCb, cv2.COLOR_YCrCb2BGR)
    return output

def segmentation(inputColour):
    # BGR to Gray
    inputGray = cv2.cvtColor(inputColour, cv2.COLOR_BGR2GRAY)
    [B, G, R] = cv2.split(inputColour)
    # Adaptative gaussian thresholding
    threshB = cv2.adaptiveThreshold(B, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0)
    threshG = cv2.adaptiveThreshold(G, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0)
    threshR = cv2.adaptiveThreshold(R, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 0)
    # Remove noise
    kernel = numpy.ones((3,3),numpy.uint8)
    threshB = cv2.morphologyEx(src=threshB, op=cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    threshG = cv2.morphologyEx(src=threshG, op=cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    threshR = cv2.morphologyEx(src=threshR, op=cv2.MORPH_OPEN, kernel=kernel, iterations=1)
    kernel = numpy.ones((5,5),numpy.uint8)
    threshB = cv2.morphologyEx(src=threshB, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=2)
    threshG = cv2.morphologyEx(src=threshG, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=2)
    threshR = cv2.morphologyEx(src=threshR, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=2)
    # cv2.imshow("Debug1", threshB)
    # cv2.imshow("Debug0", threshG)
    # cv2.imshow("Debug2", threshR)
    sure_bg = thresholdTotal = cv2.bitwise_or(cv2.bitwise_or(threshB, threshG),threshR)
    # cv2.imshow("Debug3", thresholdTotal)
    # Find foreground mask
    dist_transform = cv2.distanceTransform(src=thresholdTotal, distanceType=cv2.DIST_L2, maskSize=3)
    ret, sure_fg = cv2.threshold(dist_transform,0.2*dist_transform.max(),255,0)
    # Clean the mask
    kernel = numpy.ones((9,9),numpy.uint8)
    sure_fg = cv2.morphologyEx(src=sure_fg, op=cv2.MORPH_OPEN, kernel=kernel, iterations=2)
    # cv2.imshow("Debug4", dist_transform)
    # cv2.imshow("Debug5", sure_fg)
    
    # Finding unknown region
    sure_fg = numpy.uint8(sure_fg)
    unknown = cv2.subtract(sure_bg,sure_fg)

    # Markers labeling
    ret, markers = cv2.connectedComponents(sure_fg)
    # Add one to all labels so that sure background is not 0, but 1
    markers = markers+1
    # Now, mark the region of unknown with zero
    markers[unknown==255] = 0

    markers = cv2.watershed(inputColour,markers)
    inputColour[markers == -1] = [255,0,0]
    # cv2.imshow("Debug6", inputColour)

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()