import gtk

class ErrorMessage(gtk.MessageDialog):
  def __init__(self, header, message):
    gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, header)
    self.format_secondary_text(message)
    self.connect('response', self.close)

  def close(self, widget, response):
    self.destroy()

class ConfirmDialog(gtk.Dialog):
  def __init__(self, message):
    gtk.Dialog.__init__(self, '', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    
    self.set_border_width(5)
    
    self.vbox.pack_start(gtk.Label(message), False)
    self.vbox.show_all()
