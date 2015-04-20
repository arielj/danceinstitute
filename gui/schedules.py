#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk

class ScheduleDialog(gtk.Dialog):
  def __init__(self, schedule):
    self.form = SchedulesForm(schedule)
    
    gtk.Dialog.__init__(self, self.form.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

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

class SchedulesTable(gtk.TreeView):
  def __init__(self, schedules):
    #day, room, from_time, to_time
    self.store = gtk.ListStore(int,str,str,str,str)
    
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
      self.store.append([sch.id, sch.get_day_name(), sch.room, sch.from_time, sch.to_time])

