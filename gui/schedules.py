#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from translations import _t

class ScheduleDialog(gtk.Dialog):
  def __init__(self, schedule):
    self.form = SchedulesForm(schedule)
    
    gtk.Dialog.__init__(self, self.form.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                        gtk.STOCK_DELETE, gtk.RESPONSE_DELETE_EVENT))

    self.schedule = schedule
    
    self.vbox.pack_start(self.form)
    self.form.show_all()
  
  def get_values(self):
    return self.form.get_values()

class SchedulesPage(gtk.Frame):
  def __init__(self, schedule):
    gtk.Frame.__init__(self)
    self.schedule = schedule

    self.fields = SchedulesForm(schedule)
    
    self.submit = gtk.Button('Aceptar')
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    return self.fields.get_tab_label()

class SchedulesForm(gtk.VBox):
  def __init__(self, schedule):
    gtk.VBox.__init__(self)
    self.schedule = schedule

    self.room_l = gtk.Label('Sala')
    self.pack_start(self.room_l,False)

    # create rooms radios
    self.rooms = {}
    rooms = self.schedule.__class__.possible_rooms()
    rooms_hbox = gtk.HBox()
    radio_group = None
    for r in rooms:
      self.rooms[r] = gtk.RadioButton(radio_group, r)
      if radio_group is None:
        radio_group = self.rooms[r]
      rooms_hbox.pack_start(self.rooms[r], False)
    self.pack_start(rooms_hbox, False)

    self.day_l = gtk.Label('Día')
    self.pack_start(self.day_l, False)

    # create days radios
    self.days= {}
    days = _t('days')
    days_hbox = gtk.HBox()
    days_group = None
    for idx, day in enumerate(days):
      self.days[day] = {'btn': gtk.RadioButton(days_group, day), 'idx': idx}
      if days_group is None:
        days_group = self.days[day]['btn']
      days_hbox.pack_start(self.days[day]['btn'], False)

    self.pack_start(days_hbox, False)
  
    self.from_time_l = gtk.Label('Desde')
    self.from_time_e = gtk.Entry(5)
    self.pack_start(self.from_time_l,False)
    self.pack_start(self.from_time_e,False)

    self.to_time_l = gtk.Label('Hasta')
    self.to_time_e = gtk.Entry(5)
    self.pack_start(self.to_time_l,False)
    self.pack_start(self.to_time_e,False)
        
    self.from_time_e.set_text(self.schedule.str_from_time())
    self.to_time_e.set_text(self.schedule.str_to_time())
    for r in rooms:
      self.rooms[r].set_active(self.schedule.room == r)
    for d in days:
      self.days[d]['btn'].set_active(self.schedule.day_name() == d)

  def get_tab_label(self):
    return 'Editar Horario' if self.schedule.id else 'Agregar Horario'

  def get_selected_room(self):
    for r in self.rooms.iterkeys():
      if self.rooms[r].get_active() is True:
        return r
    return ''

  def get_selected_day(self):
    for key in self.days.iterkeys():
      if self.days[key]['btn'].get_active() is True:
        return self.days[key]['idx']
  
  def get_values(self):
    return {'room_name': self.get_selected_room(), 'day': self.get_selected_day(), 'from_time': self.from_time_e.get_text(), 'to_time': self.to_time_e.get_text()}

class SchedulesList(gtk.ScrolledWindow):
  def __init__(self, schedules, with_actions = True):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.vbox = gtk.VBox()
    self.with_actions = with_actions
    
    self.table = SchedulesTable(schedules)
    self.table.connect('row-activated', self.on_row_activated)
    
    self.vbox.pack_start(self.table, True)
    
    if self.with_actions:
      self.add_b = gtk.Button('Agregar')
      self.add_b.connect('clicked', self.on_add_clicked)
      self.edit_b = gtk.Button('Editar')
      self.edit_b.connect('clicked', self.on_edit_clicked)
      self.delete_b = gtk.Button('Eliminar')
      self.delete_b.connect('clicked', self.on_delete_clicked)
      self.edit_b.set_sensitive(False)
      self.delete_b.set_sensitive(False)
      self.table.get_selection().connect('changed', self.on_selection_change)
      
      self.actions = gtk.HBox()
      self.actions.pack_start(self.add_b, False)
      self.actions.pack_start(self.edit_b, False)
      self.actions.pack_start(self.delete_b, False)
      self.vbox.pack_start(self.actions, False)
    
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)

  def update_table(self, schedules):
    self.table.update(schedules)

  def on_selection_change(self, selection):
    if self.with_actions:
      model, iter = selection.get_selected()
      self.edit_b.set_sensitive(iter is not None)
      self.delete_b.set_sensitive(iter is not None)

  def on_add_clicked(self, btn):
    self.emit('schedule-add')

  def on_edit_clicked(self, btn):
    model, iter = self.table.get_selection().get_selected()
    if iter is not None:
      schedule = model.get_value(iter,0)
      self.emit('schedule-edit', schedule)

  def on_delete_clicked(self, btn):
    model, iter = self.table.get_selection().get_selected()
    if iter is not None:
      schedule = model.get_value(iter,0)
      self.emit('schedule-remove', schedule)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    schedule = model.get_value(itr, 0)
    if schedule:
      self.emit('schedule-edit', schedule)
    else:
      self.emit('schedule-add')

gobject.type_register(SchedulesList)
gobject.signal_new('schedule-edit', \
                   SchedulesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('schedule-remove', \
                   SchedulesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('schedule-add', \
                   SchedulesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())

class SchedulesTable(gtk.TreeView):
  def __init__(self, schedules):
    #day, room, from_time, to_time
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)
    self.set_model(schedules)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    self.add_column('Día', 1)
    self.add_column('Sala', 2)
    self.add_column('Desde', 3)
    self.add_column('Hasta', 4)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def get_values(self):
    return self.schedules
    
  def update(self, schedules):
    self.store.clear()
    self.set_model(schedules)

  def set_model(self, schedules):
    self.schedules = schedules
    for sch in self.schedules:
      self.store.append([sch, sch.day_name(), sch.room.name, sch.str_from_time(), sch.str_to_time()])

