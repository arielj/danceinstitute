#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import settings

class Config(gtk.ScrolledWindow):
  def __init__(self, settings):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    self.settings = settings.get_settings()
    
    self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
    
    self.vbox = gtk.VBox()
    
    self.create_form()
    
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)
    
    self.show_all()

  def create_form(self):
    self.add_field('Nombre del instituto/academia', attrs=100).set_text(str(getattr(self.settings,'name')))
    self.add_field('Horario de apertura', attrs=5).set_text(str(getattr(self.settings,'opening')))
    self.add_field('Horario de cierre', attrs=5).set_text(str(getattr(self.settings,'closing')))
    self.add_field('Recargo luego del día', attrs=2).set_text(str(getattr(self.settings,'recharge_after')))
    self.add_field('Valor del recargo (formato: 10 o 10%)', attrs=10).set_text(str(getattr(self.settings,'recharge_value')))
    self.add_field('Idioma', attrs=2).set_text(str(getattr(self.settings,'language')))

    self.add_field('Posición de las pestañas', attrs=4).set_text(str(getattr(self.settings,'tab_position')))
    self.add_field('Tamaño inicial (formato: 1024x768)', attrs=15).set_text(str(getattr(self.settings,'startup_size')))
    
    self.submit = gtk.Button('Guardar')

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
