# -*- coding:utf-8 -*-
import sys
import gtk
import gobject
import pango

sys.path.append("python-h8simulator")
from simpleh8simulator import *


class H8SimGUI :
  def __init__(self) :
    self.builder = gtk.Builder()
    self.builder.add_from_file("gui.glade")

    self.window = self.builder.get_object("window1")
    self.filechooserdialog = self.builder.get_object("filechooserdialog1")
    self.treeview = self.builder.get_object("treeview1")
    
    self.menu_open_item = self.builder.get_object("imagemenuitem2")
    self.menu_exit_item = self.builder.get_object("imagemenuitem5")
    
    self.dis_assembly = self.builder.get_object("textview1")
    self.run_button = self.builder.get_object("button1")
    self.step_button = self.builder.get_object("button2")
    self.reset_button = self.builder.get_object("button3")
    
    self.fdialog_ok_button = self.builder.get_object("button4")
    self.fdialog_cancel_button = self.builder.get_object("button5")
    
    self.fdialog_ok_button.connect("clicked", self.hideFileChooserDialog)
    self.menu_open_item.connect("button-release-event", self.showFileChooserDialog)
    self.menu_exit_item.connect("button-release-event", self.exit)
    self.run_button.connect("clicked", self.sim_run)
    self.step_button.connect("clicked", self.sim_step)
    self.reset_button.connect("clicked", self.sim_reset)

    self.treeview.modify_font(pango.FontDescription('Courier'))
    self.treeview.append_column(gtk.TreeViewColumn('', gtk.CellRendererText(), text=0))
    self.treeview.append_column(gtk.TreeViewColumn('メモリ番地', gtk.CellRendererText(), text=1))
    self.treeview.append_column(gtk.TreeViewColumn('アセンブリ', gtk.CellRendererText(), text=2))
    self.treeview.append_column(gtk.TreeViewColumn('備考', gtk.CellRendererText(), text=3))
    self.treeview.set_model(gtk.TreeStore(str, str, str, str))
    
    self.treeview.get_model().append(None, ("","","", "「メニュー->ファイル->開く」からmotファイルを選択してください"))

    self.sim = SimpleH8simulator()
    self.pc = 0
    self.disAssembly = None
    self.running = False
    
    self.window.show()
    
  def initView(self) :
    i = self.treeview.get_model().iter_children(None)
    while i :
      self.treeview.get_model().remove(i)
      i = self.treeview.get_model().iter_children(None)
    for k in sorted(self.disAssembly.keys()) :
      parent = self.treeview.get_model().append(None, ("",("%6X"%k) ,self.disAssembly[k], ""))
      for x in range(8) :
        self.treeview.get_model().append(parent, ("", "" , "", "ER%d=000000"%x))
      
  def drawView(self) :
    i = self.treeview.get_model().iter_children(None)
    while i :
      if int(self.treeview.get_model().get_value(i, 1), 16) == self.pc :
        self.treeview.get_model().set_value(i, 0, 'PC=')
        for x in range(8) :
          r = self.sim.get32bitRegistor(x)
          j = self.treeview.get_model().iter_children(i)
          while j :
            if self.treeview.get_model().get_value(j, 3)[:3] == ("ER%d"%x) :
              self.treeview.get_model().set_value(j, 3, "ER%d=%06X" % (x, r))
            j = self.treeview.get_model().iter_next(j)
      else :
        self.treeview.get_model().set_value(i, 0, '')
      i = self.treeview.get_model().iter_next(i)
    
  def runStep(self) :
    self.pc = self.sim.getProgramCounter()
    self.sim.runStep()
    self.drawView()
    if self.running :
      gobject.timeout_add(100, self.runStep)

  def showFileChooserDialog(self, widget, event) :
    self.filechooserdialog.show()

  def hideFileChooserDialog(self, widget) :
    self.sim.load(self.filechooserdialog.get_file().get_path())
    self.disAssembly = self.sim.getDisAssembly()
    self.sim.reset()
    self.initView()
    self.filechooserdialog.hide()
  
  def sim_run(self, widget) :
    self.running = not self.running
    if self.running :
      gobject.timeout_add(100, self.runStep)
    
  def sim_step(self, widget) :
    self.runStep()
    
  def sim_reset(self, widget) :
    self.sim.reset()
    
  def main(self) :
    gtk.main()
    
  def exit(self, windows, event) :
    sys.exit(0)

if __name__ == "__main__" :
  app = H8SimGUI()
  app.main()

