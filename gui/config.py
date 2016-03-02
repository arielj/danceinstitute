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
    
    self.vbox = gtk.VBox(False, 5)
    self.hbox = gtk.HBox(False, 8)
    
    self.vbox.pack_start(self.hbox, True)
    
    self.left = gtk.VBox()
    self.right = gtk.VBox()
    
    self.hbox.pack_start(self.left, True)
    self.hbox.pack_start(self.right, True)
    
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
    
    self.hour_fees_l = gtk.Label('Precio por hora')
    self.hour_fees_ls = HourFeesList(self.settings.hour_fees)
    #self.hour_fees_ls.connect('hour-fees-add', self.on_hour_fees_add)
    #self.hour_fees_ls.connect('hour-fees-edit', self.on_hour_fees_edit)
    #self.hour_fees_ls.connect('hour-fees-remove', self.on_hour_fees_delete)

    field = gtk.VBox()
    field.pack_start(self.hour_fees_l, False)
    field.pack_start(self.hour_fees_ls, True)
    self.right.pack_start(field, False)

    self.submit = gtk.Button('Guardar')
    
    self.vbox.pack_start(self.submit, False)

  def add_field(self, label, attrs=None, box=None):
    field = gtk.VBox()
    label = gtk.Label(label)
    entry = gtk.Entry(attrs)
    
    field.pack_start(label, False)
    field.pack_start(entry, False)
    
    self.left.pack_start(field, False)
    
    return entry

  def get_tab_label(self):
    return "Configuración"

  def get_values(self):
    return {'name': self.name_e.get_text(), 'opening': self.opening_e.get_text(), 'closing': self.closing_e.get_text(), 'tabs_position': self.tabs_position_e.get_text(), 'startup_size': self.startup_size_e.get_text(), 'language': self.language_e.get_text(), 'recharge_after': self.recharge_after_e.get_text(), 'recharge_value': self.recharge_value_e.get_text(), 'date_format': self.date_format_e.get_text(), 'hour_fees': self.hour_fees_ls.get_hour_fees()}


class HourFeesList(gtk.TreeView):
  def __init__(self, fees):
    self.create_store(fees)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Horas', 0)
    self.add_column('Precio', 1)

  def add_column(self, label, text_idx):
    renderer = gtk.CellRendererText()
    renderer.set_property('editable', True)
    renderer.connect('edited', self.edited_cb, (self.store, text_idx))
    col = gtk.TreeViewColumn(label, renderer, text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def edited_cb(self, cell, path, new_text, user_data):
    liststore, column = user_data
    liststore[path][column] = new_text
    self.compact_and_add_new()

  def compact_and_add_new(self):
    self.update(self.get_values())
  
  def create_store(self, fees):
    # hours, fee
    self.store = gtk.ListStore(str, str)
    self.update(fees)

  def update(self, fees):
    self.store.clear()
    self.set_model(fees)
  
  def set_model(self, fees):
    for k in sorted(fees.keys()):
      self.store.append((k,str(fees[k])))
    self.store.append(('',''))
  
  def get_values(self):
    d = {}
    for row in self.store:
      if row[0].strip() != "" or row[1].strip() != "": d[row[0].strip()] = row[1].strip()
    return d

  def get_hour_fees(self):
    d = {}
    for row in self.store:
      if row[0].strip() != "" and row[1].strip() != "": d[row[0].strip()] = int(row[1].strip())
    return d
