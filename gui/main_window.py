import gtk
import gobject
from main_menu import *
from settings import Settings

class MainWindow(gtk.Window):
  def __init__(self):
    gtk.Window.__init__(self,gtk.WINDOW_TOPLEVEL)
    
    self.menu = MainMenu()
    self.v_box = gtk.VBox()
    self.add(self.v_box)
    self.v_box.pack_start(self.menu, False)
    
    self.notebook = gtk.Notebook()
    settings = Settings.get_settings()
    pos = gtk.POS_TOP if settings.tabs_position == 'top' else gtk.POS_LEFT
    self.notebook.set_tab_pos(pos)
    self.v_box.pack_start(self.notebook, True)
    
    self.statusbar = gtk.Statusbar()
    self.v_box.pack_end(self.statusbar, False)

    self.show_all()

  def add_page(self, page):
    label = NotebookTabLabel(page)
    num = self.notebook.append_page(page,label)
    self.notebook.set_current_page(num)
    label.close.connect('clicked', self.on_close_tab, page)
  
  def remove_page(self, page):
    label = self.notebook.get_tab_label(page)
    num = self.notebook.page_num(page)
    self.notebook.remove_page(num)

  def on_close_tab(self, widget, page):
    self.emit('close-tab', page)

  def update_label(self, page):
    label = NotebookTabLabel(page)
    self.notebook.set_tab_label(page,label)
    label.close.connect('clicked', self.on_close_tab, page)

  def show_status(self, status):
    self.statusbar.push(1, status)

gobject.type_register(MainWindow)
gobject.signal_new('close-tab', \
                   MainWindow, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

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
    self.set_size_request(150,-1)

    self.show_all()

