#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
from schedules import *

class KlassForm(gtk.Frame):
  def __init__(self, klass):
    gtk.Frame.__init__(self)
    self.klass = klass

    self.fields = self.get_form_fields()

    if self.klass.id:
      self.add_schedules_table()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    return 'Editar Clase' if self.klass.id else 'Agregar Clase'
  
  def get_form_fields(self):
    self.name_l = gtk.Label('Nombre')
    self.name_e = gtk.Entry(100)
    self.name_e.set_text(self.klass.name)
    
    fields = gtk.VBox()
    fields.pack_start(self.name_l,False)
    fields.pack_start(self.name_e,False)
      
    return fields
  
  def get_values(self):
    return {'name': self.name_e.get_text()}

  def add_schedules_table(self):
    self.schedules_l = gtk.Label('Horarios')
    self.schedules_t = SchedulesTable(self.klass.schedules)
    
    self.add_schedule = gtk.Button('Agregar horario')
    
    self.fields.pack_start(self.schedules_l, False)
    self.fields.pack_start(self.schedules_t, False)
    self.fields.pack_start(self.add_schedule, False)

