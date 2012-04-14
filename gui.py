# -*- coding:utf-8 -*-
import sys
import gtk
import pprint
import pango
import time
sys.path.append("python-h8simulator")
from simpleh8simulator import *

class GtkGladeSample:
  
  def __init__(self):
    self.builder = gtk.Builder()
    self.builder.add_from_file("gui.glade")
    
    self.window = self.builder.get_object("window1")
    self.window.connect("delete-event", self.exit)

    self.filechooserdialog = self.builder.get_object("filechooserdialog1")
    self.filechooserdialog_open = self.builder.get_object("button7")
    self.filechooserdialog_open = self.builder.get_object("button7")
    self.menu_open = self.builder.get_object("imagemenuitem2")
    self.menu_exit = self.builder.get_object("imagemenuitem5")
    self.dis_assembly = self.builder.get_object("textview1")
    self.run_button = self.builder.get_object("button1")
    self.step_button = self.builder.get_object("button2")
    self.reset_button = self.builder.get_object("button3")

    self.filechooserdialog_open.connect("clicked", self.hideFileChooserDialog)
    self.filechooserdialog.connect("file-activated", self.hideFileChooserDialog)
    self.menu_open.connect("button-release-event", self.showFileChooserDialog)
    self.menu_exit.connect("button-release-event", self.exit)
    self.run_button.connect("clicked", self.run_event)
    self.step_button.connect("clicked", self.step_event)
    self.reset_button.connect("clicked", self.reset_event)

    self.sim = SimpleH8simulator()
    self.disAssembly = None

    self.window.show()

  def showFileChooserDialog(self, widget, event) :
    self.filechooserdialog.show()

  def hideFileChooserDialog(self, widget) :
    self.sim.loadSFormatFromFile(self.filechooserdialog.get_file().get_path())
    self.disAssembly = self.sim.getDisAssembly()
    self.sim.loadEntryAddressToProgramCounter()
    self.filechooserdialog.hide()
    self.drawSourceWindow()

  def exit(self, windows, event) :
    sys.exit(0)

  def run_event(self, widget) :
    while True :
      self.sim.runStep()
      self.drawSourceWindow()
      time.sleep(1)
    
  def step_event(self, widget) :
    self.sim.runStep()
    self.drawSourceWindow()
    print "run "+("%8x" % self.sim.getProgramCounter())
    
  def reset_event(self, widget) :
    self.sim.loadEntryAddressToProgramCounter()
    print ("%8x" % self.sim.getProgramCounter())
    self.drawSourceWindow()
    print ("%8x" % self.sim.entryAddress)+" -> programcounter"

  def main(self):
    gtk.main()

  def drawSourceWindow(self) :
    text = ''
    i = 0
    for k in sorted(self.disAssembly.keys()) :
      if k == self.sim.getProgramCounter() :
        text += "->"
      else :
        text += "  "
      text += self.disAssembly[k]+"\n"
    tb = gtk.TextBuffer()
    tb.set_text(text)
    self.dis_assembly.modify_font(pango.FontDescription('Courier'))
    self.dis_assembly.modify_base(gtk.STATE_NORMAL, gtk.gdk.color_parse('black'))
    self.dis_assembly.modify_text(gtk.STATE_NORMAL, gtk.gdk.color_parse('white'))
    self.dis_assembly.set_buffer(tb)
    self.dis_assembly.show()

if __name__ == "__main__":
  app = GtkGladeSample()
  app.main()
