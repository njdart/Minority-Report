import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MinorityReportGtkHandler:
    def application_quit(self, *args):
        Gtk.main_quit(*args)

    def load_file(self, *args):
        print("'load file' clicked")

    def save_file(self, *args):
        print("'save file' clicked")

def start_gui():
    """
    Blocking function that starts the GUI. Will only return when Gtk.main_quit
    is called (i.e. when the top-level window is destroyed).
    """
    builder = Gtk.Builder()
    builder.add_from_file("AppDesign.glade")
    builder.connect_signals(MinorityReportGtkHandler())
    
    window = builder.get_object("window1")
    window.show_all()

    Gtk.main()
