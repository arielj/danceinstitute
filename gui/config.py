#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk

class Config(gtk.ScrolledWindow):
  def __init__(self, settings):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    
    self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    
    self.settings = settings
    
    self.vbox = gtk.VBox()
    
    self.create_form()
    
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)
    
    self.show_all()

  def create_form(self):
    self.add_field('Nombre del instituto/academia', attrs=100)
    self.add_field('Horario de apertura', attrs=5)
    self.add_field('Horario de cierre', attrs=5)


    self.add_field('Tamaño inicial', attrs=15)

  def add_field(self, label, attrs=None, box=None):
    field = gtk.VBox()
    label = gtk.Label(label)
    entry = gtk.Entry(attrs)
    
    field.pack_start(label, False)
    field.pack_start(entry, False)
    
    self.vbox.pack_start(field, False)
    
    return entry

  def get_tab_label(self):
    return "Configuración"
