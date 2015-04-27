import gtk

class FormFor(gtk.HBox):
  def __init__(self, obj):
    gtk.HBox.__init__(self, True, 8)
    self.object = obj
    self.set_border_width(4)
    
  def add_field(self, label, method, gtktype = 'entry', attrs = None, box = None):
    l = gtk.Label(label)
    vars(self)[method + "_l"] = l

    e = gtk.Entry(attrs)
    e.set_text(vars(self.object)[method])
    vars(self)[method + "_e"] = e
    
    field = gtk.VBox()
    field.pack_start(l, False)
    field.pack_start(e, False)
    
    if box is not None:
      box.pack_start(field, True)
    else:
      self.fields.pack_start(field, False)

