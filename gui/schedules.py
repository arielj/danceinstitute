#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject

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
    radio_group = None
    rooms = self.schedule.__class__.possible_rooms()
    rooms_hbox = gtk.HBox()
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
    days_group = None
    days = self.schedule.__class__.get_days()
    days_hbox = gtk.HBox()
    idx = 0
    for day in days:
      self.days[day] = {'btn': gtk.RadioButton(days_group, day), 'idx': idx}
      if days_group is None:
        days_group = self.days[day]['btn']
      days_hbox.pack_start(self.days[day]['btn'], False)
      idx += 1

    self.pack_start(days_hbox, False)
  
    self.from_time_l = gtk.Label('Desde')
    self.from_time_e = gtk.Entry(5)
    self.pack_start(self.from_time_l,False)
    self.pack_start(self.from_time_e,False)

    self.to_time_l = gtk.Label('Hasta')
    self.to_time_e = gtk.Entry(5)
    self.pack_start(self.to_time_l,False)
    self.pack_start(self.to_time_e,False)
        
    self.from_time_e.set_text(self.schedule.from_time)
    self.to_time_e.set_text(self.schedule.to_time)
    for r in rooms:
      self.rooms[r].set_active(self.schedule.room == r)
    for d in days:
      self.days[d]['btn'].set_active(self.schedule.get_day_name() == d)

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
    return 0
  
  def get_values(self):
    return {'room': self.get_selected_room(), 'day': self.get_selected_day(), 'from_time': self.from_time_e.get_text(), 'to_time': self.to_time_e.get_text()}

class SchedulesList(gtk.Frame):
  def __init__(self, schedules, with_actions = True):
    gtk.Frame.__init__(self)
    self.vbox = gtk.VBox()
    
    self.table = SchedulesTable(schedules)
    self.table.connect('row-activated', self.on_row_activated)
    
    self.vbox.pack_start(self.table, True)
    
    if with_actions:
      self.add_b = gtk.Button('Agregar horario')
      self.add_b.connect('clicked', self.on_add_clicked)
      self.edit_b = gtk.Button('Editar horario')
      self.edit_b.connect('clicked', self.on_edit_clicked)
      self.delete_b = gtk.Button('Eliminar horario')
      self.delete_b.connect('clicked', self.on_delete_clicked)
      self.edit_b.set_sensitive(False)
      self.delete_b.set_sensitive(False)
      self.table.get_selection().connect('changed', self.on_selection_change)
      
      self.actions = gtk.HBox()
      self.actions.pack_start(self.add_b, False)
      self.actions.pack_start(self.edit_b, False)
      self.actions.pack_start(self.delete_b, False)
      self.vbox.pack_start(self.actions, False)
    
    self.add(self.vbox)

  def update_table(self, schedules):
    self.table.update(schedules)

  def on_selection_change(self, selection):
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
      self.emit('schedule-delete', schedule)

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
gobject.signal_new('schedule-delete', \
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

    self.day_col = gtk.TreeViewColumn('Día', gtk.CellRendererText(), text=1)
    self.room_col = gtk.TreeViewColumn('Sala', gtk.CellRendererText(), text=2)
    self.from_col = gtk.TreeViewColumn('Desde', gtk.CellRendererText(), text=3)
    self.to_col = gtk.TreeViewColumn('Hasta', gtk.CellRendererText(), text=4)
    
    self.append_column(self.day_col)
    self.append_column(self.room_col)
    self.append_column(self.from_col)
    self.append_column(self.to_col)
  
  def get_values(self):
    return self.schedules
    
  def update(self, schedules):
    self.store.clear()
    self.set_model(schedules)

  def set_model(self, schedules):
    self.schedules = schedules
    for sch in self.schedules:
      self.store.append([sch, sch.get_day_name(), sch.room, sch.from_time, sch.to_time])
    self.store.append([None,'','','',''])

