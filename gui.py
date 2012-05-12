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
    self.builder.add_from_file("gui3.glade")

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
    self.treeview.set_model(gtk.ListStore(str, str, str, str))
    
    self.treeview.get_model().append(("","","", "「メニュー->ファイル->開く」からmotファイルを選択してください"))

    self.sim = SimpleH8simulator()
    self.disAssembly = None
    self.running = False
    
    self.window.show()
    
  def initView(self) :
    listiter = self.treeview.get_model().get_iter_first()
    while listiter :
      self.treeview.get_model().remove(listiter)
      listiter = self.treeview.get_model().get_iter_first()
    for k in sorted(self.disAssembly.keys()) :
      self.treeview.get_model().append(("",("%6X"%k) ,self.disAssembly[k], ""))
      
  def drawView(self) :
    listiter = self.treeview.get_model().get_iter_first()
    while listiter :
      if int(self.treeview.get_model().get_value(listiter, 1), 16) == self.sim.getProgramCounter() :
        self.treeview.get_model().set_value(listiter, 0, 'ER7=')
      else :
        self.treeview.get_model().set_value(listiter, 0, '')
      listiter = self.treeview.get_model().iter_next(listiter)
    
  def runStep(self) :
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
    print self.running
    if self.running :
      gobject.timeout_add(100, self.runStep)
    
  def sim_step(self, widget) :
    self.sim.runStep()
    self.drawView()
    
  def sim_reset(self, widget) :
    self.sim.reset()
    self.drawView()
    
  def main(self) :
    gtk.main()
    
  def exit(self, windows, event) :
    sys.exit(0)

if __name__ == "__main__" :
  app = H8SimGUI()
  app.main()

