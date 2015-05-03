import gtk

class ErrorMessage(gtk.MessageDialog):
  def __init__(self, header, message):
    gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, header)
    self.format_secondary_text(message)
    self.connect('response', self.close)

  def close(self, widget, response):
    self.destroy()
