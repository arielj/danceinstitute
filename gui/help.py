import gtk

class License(gtk.Dialog):
  def __init__(self):
    gtk.Dialog.__init__(self, self.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_NEVER,gtk.POLICY_ALWAYS)
    self.scroll.set_size_request(500,400)
    
    self.text_view = gtk.TextView()
    buf = self.text_view.get_buffer()
    buf.set_text(self.read_license_file())
    
    self.scroll.add_with_viewport(self.text_view)
    
    self.vbox.pack_start(self.scroll, True)
    
    self.vbox.show_all()

  def get_tab_label(self):
    return 'Licencia'

  def read_license_file(self):
    try:
      return open('LICENSE').read()
    except:
      return 'No se pudo leer el archivo de licensia'

class About(gtk.Dialog):
  def __init__(self):
    gtk.Dialog.__init__(self, self.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       ())

  def get_tab_label(self):
    return 'Acerca de'
