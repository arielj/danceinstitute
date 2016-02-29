#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
from translations import _a

class FormFor(gtk.VBox):
  def __init__(self, obj):
    gtk.VBox.__init__(self, False, 4)
    self.object = obj
    self.set_border_width(4)
    
    self.flash = gtk.Label()
    self.flash.set_use_markup(True)
    self.flash_wrapper = gtk.EventBox()
    self.flash_wrapper.add(self.flash)
    self.flash_wrapper.set_no_show_all(True)
    self.flash_wrapper.hide()
    self.flash_wrapper.modify_bg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#a94442"))
    #self.flash_wrapper.modify_fg(gtk.STATE_NORMAL, gtk.gdk.color_parse("#a94442"))
    
    self.data = gtk.HBox(False, 8)
    
    gtk.VBox.pack_start(self, self.flash_wrapper, False)
    gtk.VBox.pack_start(self, self.data, True)

  def pack_start(self, widget, boolean):
    self.data.pack_start(widget, boolean)

  def set_flash(self, message):
    self.flash.set_markup('<span size="15000" weight="bold">' + message + '</span>')
    self.flash_wrapper.show()
    self.flash.show()
  
  def hide_flash(self):
    self.flash_wrapper.hide()
  
  def add_field(self, method, label = None, field_type = 'entry', attrs = None, box = None, list_store = None, getter = None):
    if getter is None: getter = method

    value = getattr(self.object,getter)

    if not label: label = _a(self.object.__class__.__name__.lower(), method)
    l = gtk.Label(label)
    vars(self)[method + "_l"] = l

    if field_type == 'entry':
      e = gtk.Entry(attrs)
      e.set_text(str(value or ''))
      vars(self)[method + "_e"] = e
    elif field_type == 'text':
      entry = gtk.TextView()
      entry.set_editable(True)
      entry.get_buffer().set_text(str(value or ''))
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
      e.get_model().foreach(self.set_active_item_on_combo, (getter, e))
    
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
    if model.get_value(itr,0) == getattr(self.object, method):
      e.set_active_iter(itr)
      return True
    else:
      return False

