import gtk

class FormFor(gtk.Frame):
  def __init__(self, obj):
    gtk.Frame.__init__(self)
    self.object = obj
    
  def add_field(self, label, method, gtktype = 'entry', attrs = None):
    l = gtk.Label(label)
    vars(self)[method + "_l"] = l

    e = gtk.Entry(attrs)
    e.set_text(vars(self.object)[method])
    vars(self)[method + "_e"] = e
    
    self.fields.pack_start(l, False)
    self.fields.pack_start(e, False)

