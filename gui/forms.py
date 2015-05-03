import gtk
from translations import _a

class FormFor(gtk.HBox):
  def __init__(self, obj):
    gtk.HBox.__init__(self, True, 8)
    self.object = obj
    self.set_border_width(4)
    
  def add_field(self, method, label = None, field_type = 'entry', attrs = None, box = None, list_store = None):
    if not label:
      label = _a(self.object.__class__.__name__.lower(), method)
    l = gtk.Label(label)
    vars(self)[method + "_l"] = l

    if field_type == 'entry':
      e = gtk.Entry(attrs)
      e.set_text(str(vars(self.object)[method] or ''))
      vars(self)[method + "_e"] = e
    elif field_type == 'text':
      entry = gtk.TextView()
      entry.set_editable(True)
      entry.get_buffer().set_text(vars(self.object)[method])
      entry.set_wrap_mode(gtk.WRAP_WORD)
      e = gtk.ScrolledWindow()
      e.add(entry)
      e.set_shadow_type(gtk.SHADOW_ETCHED_IN)
      e.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
      vars(self)[method + "_e"] = entry
    elif field_type == 'combo':
      e = gtk.ComboBox(list_store)
      cell = gtk.CellRendererText()
      e.pack_start(cell, True)
      e.add_attribute(cell, 'text', 1)
      vars(self)[method + "_e"] = e
      e.get_model().foreach(self.set_active_item_on_combo, (method, e))
    
    field = gtk.VBox()
    field.pack_start(l, False)
    field.pack_start(e, False)
    vars(self)[method + "_field"] = field
    
    if box is not None:
      box.pack_start(field, True)
    else:
      self.fields.pack_start(field, False)
    
    return [field, l, e]

  def set_active_item_on_combo(self, model, path, itr, data):
    method, e = data
    if model.get_value(itr,0) == vars(self.object)[method]:
      e.set_active_iter(itr)
      return True
    else:
      return False

