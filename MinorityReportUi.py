#!/usr/bin/python3
from gi.repository import Gtk, GdkPixbuf
import cv2
import numpy

class MyWindow(Gtk.Window):

  def __init__(self):
    Gtk.Window.__init__(self, title="Hello World")
    
    # self.set_default_size(600, 600)
    # self.set_geometry_hints(min_width=600, min_height=600, max_width=1920, max_height=1080)

    ### Layout Objects

    # Main Grid element
    vbox = Gtk.VBox(False, 0)
    self.add(vbox)

    grid = Gtk.Grid()
    # grid.set_row_spacing(5)
    # Homogeneous sets all rows/columns to have the same height/width
    grid.set_column_spacing(5)
    grid.set_column_homogeneous(True)
    vbox.pack_end(grid, True, True, 2)

    ### Components

    # Main Menu
    self.menuBar = Gtk.MenuBar()
    vbox.pack_start(self.menuBar, False, False, 2)

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

    # Saturation Slider and Label
    self.saturationSlider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(50, 0, 100, 1, 10, 0))
    saturationSliderLabel = Gtk.Label("Saturation")
    grid.attach(saturationSliderLabel, left=0, top=0, width=1, height=1)
    grid.attach(self.saturationSlider, left=0, top=1, width=2, height=1)

    # Contrast Slider and Label
    self.contrastSlider = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Gtk.Adjustment(50, 0, 100, 1, 10, 0))
    contrastSliderLabel = Gtk.Label("Contrast")
    grid.attach(contrastSliderLabel, left=0, top=2, width=1, height=1)
    grid.attach(self.contrastSlider, left=0, top=3, width=2, height=1)

    # Input Image
    self.inputImageWidget = Gtk.Image()
    grid.attach(self.inputImageWidget, left=0, top=5, width=1, height=2)
    # self.inputImageWidget.set_from_file("/tmp/in.png")

    # Output Image
    self.outputImageWidget = Gtk.Image()
    grid.attach(self.outputImageWidget, left=1, top=7, width=1, height=1)
    # self.outputImageWidget.set_from_file("/tmp/out.jpg")

    self.inputImageBuf = None
    ### Event Bindings
    self.connect('check-resize', lambda w: adjustInputImage(None, self.inputImageBuf, self.inputImageWidget))


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

    importDialog.destroy()


    # By Default this will conver the image to RGB (removing alpha channels)
    # FU Opencv! OpenCV returns images in BGR Format , we need to convert them to RGB for gtk
    #
    # http://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_image_display/py_image_display.html
    #
    im = cv2.imread(self.inputImageFileName)
    
    b,g,r = cv2.split(im)                           # FFFFUUUUU!
    self.inputImage = cv2.merge([r,g,b]) 

    height, width, channels = self.inputImage.shape

    self.inputImageBuf = GdkPixbuf.Pixbuf.new_from_data(self.inputImage.tobytes(),
      GdkPixbuf.Colorspace.RGB,
      False,
      8, # HACK, cant find out how to get this from the image
      width,
      height,
      width * channels)

    adjustInputImage(None, self.inputImageBuf, self.inputImageWidget)

def adjustInputImage(widget, pixbuf, imageWidget):
  
  if pixbuf is not None:
    print("adjustInputImage")
    bounds = imageWidget.get_allocation()

    imageWidget.set_from_pixbuf(pixbuf.scale_simple(bounds.width, bounds.height, GdkPixbuf.InterpType.BILINEAR))

win = MyWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()