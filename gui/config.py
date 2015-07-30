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
    self.name_e = self.add_field('Nombre del instituto/academia', attrs=100)
    self.name_e.set_text(str(getattr(self.settings,'name')))
    
    self.opening_e = self.add_field('Horario de apertura', attrs=5)
    self.opening_e.set_text(str(getattr(self.settings,'opening')))
    self.closing_e = self.add_field('Horario de cierre', attrs=5)
    self.closing_e.set_text(str(getattr(self.settings,'closing')))
    self.recharge_after_e = self.add_field('Recargo luego del día', attrs=2)
    self.recharge_after_e.set_text(str(getattr(self.settings,'recharge_after')))
    self.recharge_value_e = self.add_field('Valor del recargo (formato: 10 o 10%)', attrs=10)
    self.recharge_value_e.set_text(str(getattr(self.settings,'recharge_value')))
    
    self.language_e = self.add_field('Idioma', attrs=2)
    self.language_e.set_text(str(getattr(self.settings,'language')))

    self.tabs_position_e = self.add_field('Posición de las pestañas', attrs=4)
    self.tabs_position_e.set_text(str(getattr(self.settings,'tabs_position')))
    self.startup_size_e = self.add_field('Tamaño inicial (formato: 1024x768)', attrs=15)
    self.startup_size_e.set_text(str(getattr(self.settings,'startup_size')))

    self.date_format_e = self.add_field('Formato de fechas', attrs=15)
    self.date_format_e.set_text(str(getattr(self.settings,'date_format')))

    self.submit = gtk.Button('Guardar')
    
    self.vbox.pack_start(self.submit, False)

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

  def get_values(self):
    return {'name': self.name_e.get_text(), 'opening': self.opening_e.get_text(), 'closing': self.closing_e.get_text(), 'tabs_position': self.tabs_position_e.get_text(), 'startup_size': self.startup_size_e.get_text(), 'language': self.language_e.get_text(), 'recharge_after': self.recharge_after_e.get_text(), 'recharge_value': self.recharge_value_e.get_text(), 'date_format': self.date_format_e.get_text()}
