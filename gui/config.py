#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk

class Config(gtk.ScrolledWindow):
  def __init__(self, settings):
    gtk.ScrolledWindow.__init__(self)
    
    self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    
    self.settings = settings
    
    self.vbox = gtk.VBox()
    
    self.create_form()
    
    self.add_with_viewport(self.vbox)
    
    self.show_all()

  def create_form(self):
    field = gtk.VBox()
    label = gtk.Label('Tamaño incial')
    entry = gtk.Entry(15)
    
    field.pack_start(label, False)
    field.pack_start(entry, False)
    
    self.vbox.pack_start(field, False)

  def get_tab_label(self):
    return "Configuración"
