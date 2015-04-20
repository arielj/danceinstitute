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
    self.name_e = gtk.Entry(30)
    self.name_e.set_text(self.klass.name)
    
    self.fee_l = gtk.Label('Precio completo')
    self.fee_e = gtk.Entry(5)
    self.fee_e.set_text(self.klass.fee)
    
    self.half_fee_l = gtk.Label('Precio mitad')
    self.half_fee_e = gtk.Entry(5)
    self.half_fee_e.set_text(self.klass.half_fee)
    
    self.once_fee_l = gtk.Label('Precio por clase')
    self.once_fee_e = gtk.Entry(5)
    self.once_fee_e.set_text(self.klass.once_fee)
    
    self.min_age_l = gtk.Label('Edad mínima')
    self.min_age_e = gtk.Entry(2)
    self.min_age_e.set_text(self.klass.min_age)
    
    self.max_age_l = gtk.Label('Edad máxima')
    self.max_age_e = gtk.Entry(2)
    self.max_age_e.set_text(self.klass.max_age)
    
    self.quota_l = gtk.Label('Cupo máximo')
    self.quota_e = gtk.Entry(2)
    self.quota_e.set_text(self.klass.quota)
    
    self.info_l = gtk.Label('Información')
    self.info_e = gtk.TextView()
    self.info_e.set_editable(True)
    self.info_e.get_buffer().set_text(self.klass.info)
    self.info_e.set_wrap_mode(gtk.WRAP_WORD)
    scroll_window = gtk.ScrolledWindow()
    scroll_window.add(self.info_e)
    scroll_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll_window.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    
    fields = gtk.VBox()
    fields.pack_start(self.name_l, False)
    fields.pack_start(self.name_e, False)
    fields.pack_start(self.fee_l, False)
    fields.pack_start(self.fee_e, False)
    fields.pack_start(self.half_fee_l, False)
    fields.pack_start(self.half_fee_e, False)
    fields.pack_start(self.once_fee_l, False)
    fields.pack_start(self.once_fee_e, False)
    fields.pack_start(self.min_age_l, False)
    fields.pack_start(self.min_age_e, False)
    fields.pack_start(self.max_age_l, False)
    fields.pack_start(self.max_age_e, False)
    fields.pack_start(self.quota_l, False)
    fields.pack_start(self.quota_e, False)
    fields.pack_start(self.info_l, False)
    fields.pack_start(scroll_window, True)

    return fields
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'fee': self.fee_e.get_text(), 'half_fee': self.half_fee_e.get_text(), 'once_fee': self.once_fee_e.get_text(), 'min_age': self.min_age_e.get_text(), 'max_age': self.max_age_e.get_text(), 'quota': self.quota_e.get_text(), 'info': self.info_e.get_buffer().get_text(), 'schedules': self.schedules_t.get_values()}

  def add_schedules_table(self):
    self.schedules_l = gtk.Label('Horarios')
    self.schedules_t = SchedulesTable(self.klass.schedules)
    
    self.add_schedule_b = gtk.Button('Agregar horario')
    
    self.fields.pack_start(self.schedules_l, False)
    self.fields.pack_start(self.schedules_t, False)
    self.fields.pack_start(self.add_schedule_b, False)
  
  def add_schedule(self, schedule):
    self.klass.schedules.append(schedule)
    self.update_schedules()

  def update_schedules(self):
    self.schedules_t.update(self.klass.schedules)
