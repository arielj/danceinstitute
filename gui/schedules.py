#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk

class SchedulesForm():
  def __init__(self, controller, schedule):
    gtk.Frame.__init__(self)
    self.schedule = schedule
    self.controller = controller

    self.fields = self.get_form_fields()
    
    self.submit = gtk.Button('Aceptar')
    #self.submit.connect('clicked',self.controller.submit_schedule, self)
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    return 'Editar Horario' if self.teacher.id else 'Agregar Horario'
  
  def get_form_fields(self):
    self.room_l = gtk.Label('Sala')
    fields.pack_start(self.room_l,False)

    self.rooms = {}

    radio_group = None
    rooms = self.klass.__class__.possible_rooms()
    rooms_hbox = gtk.HBox()
    for r in rooms:
      self.rooms[r] = gtk.RadioButton(radio_group, r)
      if radio_group is None:
        radio_group = self.rooms[r]
      rooms_hbox.pack_start(self.rooms[r], False)
    fields.pack_start(self.rooms[r], False)

    self.day_l = gtk.Label('Día')
    fields.pack_start(self.day_l, False)

    self.days= {}
    days = self.klass.__class__.get_days()
    days_hbox = gtk.HBox()
    for day in days:
      self.days[day] = gtk.RadioButton(radio_group, day)
      if radio_group is None:
        radio_group = self.days[day]
      days_hbox.pack_start(self.days[day], False)

    fields.pack_start(days_hbox, False)
  
    self.from_time_l = gtk.Label('Desde')
    self.from_time_e = gtk.Entry(5)
    fields.pack_start(self.from_time_l,False)
    fields.pack_start(self.from_time_e,False)


    self.to_time_l = gtk.Label('Hasta')
    self.to_time_e = gtk.Entry(5)
    fields.pack_start(self.to_time_l,False)
    fields.pack_start(self.to_time_e,False)

        
    self.from_time_e.set_text(self.schedule.from_time)
    self.to_time_e.set_text(self.schedule.to_time)
    for r in rooms:
      self.rooms[r].set_active(self.schedule.room == r)
    for d in days:
      self.days[d].set_active(self.schedule.get_name_day() == d)
    
    return fields

  def get_selected_room(self):
    for r in self.schedule.__class__.possible_rooms():
      if self.rooms[r].get_active() is True:
        return r
    return ''
  
  def get_values(self):
    return {'room': self.get_selected_room(), 'day': self.day_e.get_text(), 'from_time': self.from_time_e.get_text(), 'to_time': self.time_time_e.get_text()}

class SchedulesTable(gtk.TreeView):
  def __init__(self, schedules):
    #day, room, from_time, to_time
    self.store = gtk.ListStore(str,str,str,str)
    self.schedules = schedules
    for sch in self.schedules:
      self.store.append([sch.get_day_name(), sch.room, sch.from_time, sch.to_time])
    
    gtk.TreeView.__init__(self,self.store)

    self.day_col = gtk.TreeViewColumn('Día', gtk.CellRendererText(), text=0)
    self.room_col = gtk.TreeViewColumn('Sala', gtk.CellRendererText(), text=1)
    self.from_col = gtk.TreeViewColumn('Desde', gtk.CellRendererText(), text=2)
    self.to_col = gtk.TreeViewColumn('Hasta', gtk.CellRendererText(), text=3)
    
    self.append_column(self.day_col)
    self.append_column(self.room_col)
    self.append_column(self.from_col)
    self.append_column(self.to_col)

