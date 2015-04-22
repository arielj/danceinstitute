import gtk
from main_menu import *

class MainWindow(gtk.Window):
  def __init__(self,controller):
    gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
    
    self.controller = controller
    
    self.menu = MainMenu(self)
    self.v_box = gtk.VBox()
    self.add(self.v_box)
    self.v_box.pack_start(self.menu,False)
    
    self.notebook = gtk.Notebook()
    self.notebook.set_tab_pos(gtk.POS_LEFT)
    self.v_box.pack_start(self.notebook,True)

    self.show_all()

  def add_page(self, page):
    label = NotebookTabLabel(page)
    num = self.notebook.append_page(page,label)
    self.notebook.set_current_page(num)
    
    label.close_handler = label.close.connect_object('clicked', self.controller.close_tab, page)
  
  def remove_page(self, page):
    label = self.notebook.get_tab_label(page)
    label.close.disconnect(label.close_handler)
    num = self.notebook.page_num(page)
    self.notebook.remove_page(num)

class NotebookTabLabel(gtk.HBox):
  def __init__(self, page):
    gtk.HBox.__init__(self, False, 0)
    self.close_handler = False
    
    label = gtk.Label(page.get_tab_label())
    self.pack_start(label)

    close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
    image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
        
    self.close = gtk.Button()
    self.close.set_relief(gtk.RELIEF_NONE)
    self.close.set_focus_on_click(False)
    self.close.add(close_image)
    self.pack_start(self.close, False, False)
        
    style = gtk.RcStyle()
    style.xthickness = 0
    style.ythickness = 0
    self.close.modify_style(style)

    self.show_all()

