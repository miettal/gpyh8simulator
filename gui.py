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
    self.window.connect("delete-event", self.exit);

    self.treeview.modify_font(pango.FontDescription('Courier'))
    self.treeview.append_column(gtk.TreeViewColumn('', gtk.CellRendererText(), text=0))
    self.treeview.append_column(gtk.TreeViewColumn('メモリ番地', gtk.CellRendererText(), text=1))
    self.treeview.append_column(gtk.TreeViewColumn('アセンブリ', gtk.CellRendererText(), text=2))
    self.treeview.append_column(gtk.TreeViewColumn('備考', gtk.CellRendererText(), text=3))
    col = gtk.TreeViewColumn('id', gtk.CellRendererText(), text=4)
    col.set_visible(False)
    self.treeview.append_column(col)
    col = gtk.TreeViewColumn('id2', gtk.CellRendererText(), text=4)
    col.set_visible(False)
    self.treeview.append_column(col)
    self.treeview.set_model(gtk.TreeStore(str, str, str, str, int, str))
    
    self.treeview.get_model().append(None, ("","","", "「メニュー->ファイル->開く」からmotファイルを選択してください", 0, ''))

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
      parent = self.treeview.get_model().append(None, ("",("%08X"%k) ,self.disAssembly[k], "", k, 'MEM'))
      for x in range(8) :
        self.treeview.get_model().append(parent, ("", "" , "", "ER%d:00000000"%x, x, 'ER%d'%x))
      self.treeview.get_model().append(parent, ("", "" , "", "PC :00000000", 0, 'PC'))
      parent2 = self.treeview.get_model().append(parent, ("", "" , "", "CCR:00000000", 0, 'CCR'))
      self.treeview.get_model().append(parent2, ("", "" , "", "I :False", 0, 'I'))
      self.treeview.get_model().append(parent2, ("", "" , "", "UI:False", 0, 'UI'))
      self.treeview.get_model().append(parent2, ("", "" , "", "H :False", 0, 'H'))
      self.treeview.get_model().append(parent2, ("", "" , "", "U :False", 0, 'U'))
      self.treeview.get_model().append(parent2, ("", "" , "", "N :False", 0, 'N'))
      self.treeview.get_model().append(parent2, ("", "" , "", "Z :False", 0, 'Z'))
      self.treeview.get_model().append(parent2, ("", "" , "", "V :False", 0, 'V'))
      self.treeview.get_model().append(parent2, ("", "" , "", "C :False", 0, 'C'))
      self.treeview.get_model().append(parent, ("", "" , "", "STACK", 0, 'STACK'))
      
  def drawView(self) :
    i = self.treeview.get_model().iter_children(None)
    while i :
      if self.treeview.get_model().get_value(i, 4) == self.pc :
        self.treeview.get_model().set_value(i, 0, 'PC=')
        
        j = self.treeview.get_model().iter_children(i)
        while j :
          for x in range(8) :
            if self.treeview.get_model().get_value(j, 5) == "ER%d"%x :
              r = self.sim.get32bitRegistor(x)
              self.treeview.get_model().set_value(j, 3, "ER%d:%08X" % (x, r))
              self.treeview.get_model().set_value(j, 4, x)
            
          if self.treeview.get_model().get_value(j, 5) == "PC" :
            pc = self.sim.getProgramCounter()
            self.treeview.get_model().set_value(j, 3, "PC :%08X"%pc)
            self.treeview.get_model().set_value(j, 4, pc)
          
          if self.treeview.get_model().get_value(j, 5) == "CCR" :
            ccr = self.sim.getConditionCode()
            self.treeview.get_model().set_value(j, 3, "CCR:%08X"%ccr)
            self.treeview.get_model().set_value(j, 4, ccr)
            k = self.treeview.get_model().iter_children(j)
            while k :
              if self.treeview.get_model().get_value(k, 5)[:1] == "I" :
                self.treeview.get_model().set_value(k, 3, "I :"+str(self.sim.conditionCodeI))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeI))
              elif self.treeview.get_model().get_value(k, 5)[:2] == "UI" :
                self.treeview.get_model().set_value(k, 3, "UI:"+str(self.sim.conditionCodeUI))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeUI))
              elif self.treeview.get_model().get_value(k, 5)[:1] == "H" :
                self.treeview.get_model().set_value(k, 3, "H :"+str(self.sim.conditionCodeH))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeH))
              elif self.treeview.get_model().get_value(k, 5)[:1] == "U" :
                self.treeview.get_model().set_value(k, 3, "U :"+str(self.sim.conditionCodeU))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeU))
              elif self.treeview.get_model().get_value(k, 5)[:1] == "N" :
                self.treeview.get_model().set_value(k, 3, "N :"+str(self.sim.conditionCodeN))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeN))
              elif self.treeview.get_model().get_value(k, 5)[:1] == "Z" :
                self.treeview.get_model().set_value(k, 3, "Z :"+str(self.sim.conditionCodeZ))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeZ))
              elif self.treeview.get_model().get_value(k, 5)[:1] == "V" :
                self.treeview.get_model().set_value(k, 3, "V :"+str(self.sim.conditionCodeV))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeV))
              elif self.treeview.get_model().get_value(k, 5)[:1] == "C" :
                self.treeview.get_model().set_value(k, 3, "C :"+str(self.sim.conditionCodeC))
                self.treeview.get_model().set_value(k, 4, int(self.sim.conditionCodeC))
              k = self.treeview.get_model().iter_next(k)
              
          if self.treeview.get_model().get_value(j, 5) == "STACK" :
            k = self.treeview.get_model().iter_children(j)
            while k :
              self.treeview.get_model().remove(k)
              k = self.treeview.get_model().iter_children(j)
            address = self.sim.get32bitRegistor(7)
            while address < 0x600000 :
              self.treeview.get_model().append(j, ("", "%08X"%address , "", "%02X"%self.sim.get8bitMemory(address) , 0, ''))
              address += 1
            
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

  def main(self) :
    gtk.main()
    
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
      gobject.timeout_add(0, self.runStep)
    
  def sim_step(self, widget) :
    self.runStep()
    
  def sim_reset(self, widget) :
    self.sim.reset()
    
  def exit(self, windows, event) :
    gtk.main_quit()

if __name__ == "__main__" :
  app = H8SimGUI()
  app.main()

