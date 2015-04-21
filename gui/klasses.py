#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from schedules import *

class KlassForm(gtk.Frame):
  def __init__(self, klass):
    gtk.Frame.__init__(self)

    self.klass = klass

    self.fields = self.get_form_fields()

    self.add_schedules_table()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    return 'Editar Clase' if self.klass.id else 'Agregar Clase'
  
  def get_form_fields(self):
    self.name_l = gtk.Label('Clase')
    self.name_e = gtk.Entry(30)
    self.name_e.set_text(self.klass.name)
    
    self.fee_l = gtk.Label('Precio')
    self.fee_e = gtk.Entry(5)
    self.fee_e.set_text(self.klass.fee)
    
    self.half_fee_l = gtk.Label('Precio alternativo')
    self.half_fee_e = gtk.Entry(5)
    self.half_fee_e.set_text(self.klass.half_fee)
    
    self.once_fee_l = gtk.Label('Precio por clase individual')
    self.once_fee_e = gtk.Entry(5)
    self.once_fee_e.set_text(self.klass.once_fee)
    
    self.inscription_fee_l = gtk.Label('Inscripción')
    self.inscription_fee_e = gtk.Entry(5)
    self.inscription_fee_e.set_text(self.klass.inscription_fee)
    
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
    fields.pack_start(self.inscription_fee_l, False)
    fields.pack_start(self.inscription_fee_e, False)
    fields.pack_start(self.min_age_l, False)
    fields.pack_start(self.min_age_e, False)
    fields.pack_start(self.max_age_l, False)
    fields.pack_start(self.max_age_e, False)
    fields.pack_start(self.quota_l, False)
    fields.pack_start(self.quota_e, False)
    fields.pack_start(self.info_l, False)
    fields.pack_start(scroll_window, True)

    return fields
  
  def get_info_text(self):
    buff = self.info_e.get_buffer()
    return buff.get_text(buff.get_start_iter(), buff.get_end_iter())
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'fee': self.fee_e.get_text(), 'half_fee': self.half_fee_e.get_text(), 'once_fee': self.once_fee_e.get_text(), 'min_age': self.min_age_e.get_text(), 'max_age': self.max_age_e.get_text(), 'quota': self.quota_e.get_text(), 'info': self.get_info_text()}

  def add_schedules_table(self):
    self.schedules_l = gtk.Label('Horarios')
    self.schedules_t = SchedulesTable(self.klass.schedules)
    self.schedules_t.connect('row-activated', self.on_row_activated)
    
    self.add_schedule_b = gtk.Button('Agregar horario')
    
    self.fields.pack_start(self.schedules_l, False)
    self.fields.pack_start(self.schedules_t, False)
    self.fields.pack_start(self.add_schedule_b, False)
  
  def add_schedule(self, schedule):
    self.klass.schedules.append(schedule)
    self.update_schedules()

  def update_schedules(self):
    self.schedules_t.update(self.klass.schedules)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    sch_id = model.get_value(itr, 0)
    schedule = self.klass.find_schedule(sch_id)
    self.emit('row-activated', schedule)
    
gobject.type_register(KlassForm)
gobject.signal_new('row-activated', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class KlassesList(gtk.ScrolledWindow):
  def __init__(self, klasses):
    gtk.ScrolledWindow.__init__(self)
    self.klasses = klasses
    
    self.vbox = gtk.VBox()
    
    self.room_table = {}
    for room in klasses.iterkeys():
      label = gtk.Label('Horarios en sala: ' + room)
      self.room_table[room] = RoomKlassesTable(room, self.klasses[room])
      self.room_table[room].connect('row-activated', self.on_row_activated)
      self.vbox.pack_start(label, False)
      self.vbox.pack_start(self.room_table[room], False)
    
    self.add_with_viewport(self.vbox)
    
    self.show_all()

  def get_tab_label(self):
    return 'Clases'

  def on_row_activated(self, tree, path, column):
    if column.day_idx != -1:
      model = tree.get_model()
      itr = model.get_iter(path)
      time = model.get_value(itr, 0)
      day = column.day_name
      room = tree.room
      klass_id = self.klasses[room][time][day][0]
      if klass_id:
        self.emit('dclick-klass-edit', klass_id)
      else:
        self.emit('dclick-klass-add', room, time, column.day_idx)
    
gobject.type_register(KlassesList)
gobject.signal_new('dclick-klass-edit', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
                   
gobject.type_register(KlassesList)
gobject.signal_new('dclick-klass-add', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT))

class RoomKlassesTable(gtk.TreeView):
  def __init__(self, room, klasses):
    self.room = room
    self.create_store(klasses)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.hour_col = ListColumn('Horario', 0, 'hour',-1)
    self.mon_col = ListColumn('Lunes', 1, 'mon',0)
    self.tue_col = ListColumn('Martes', 2, 'tue',1)
    self.wed_col = ListColumn('Miércoles', 3, 'wed',2)
    self.thu_col = ListColumn('Jueves', 4, 'thu',3)
    self.fri_col = ListColumn('Viernes', 5, 'fri',4)
    self.sat_col = ListColumn('Sábado', 6, 'sat',5)
    self.sun_col = ListColumn('Domingo', 7, 'sun',6)
    self.mon_col.set_expand(True)
    self.tue_col.set_expand(True)
    self.wed_col.set_expand(True)
    self.thu_col.set_expand(True)
    self.fri_col.set_expand(True)
    self.sat_col.set_expand(True)
    self.sun_col.set_expand(True)
    
    self.append_column(self.hour_col)
    self.append_column(self.mon_col)
    self.append_column(self.tue_col)
    self.append_column(self.wed_col)
    self.append_column(self.thu_col)
    self.append_column(self.fri_col)
    self.append_column(self.sat_col)
    self.append_column(self.sun_col)
  
  def create_store(self, klasses):
    # hour, monday, tuesdat, wednesday, thursday, friday, saturday, sunday
    self.store = gtk.ListStore(str,str,str,str,str,str,str,str)
    
    for h in range(14,23,1):
      k = klasses[str(h)+':00']
      self.store.append((str(h)+':00',k['mon'][1],k['tue'][1],k['wed'][1],k['thu'][1],k['fri'][1],k['sat'][1],k['sun'][1]))
      k = klasses[str(h)+':30']
      self.store.append((str(h)+':30',k['mon'][1],k['tue'][1],k['wed'][1],k['thu'][1],k['fri'][1],k['sat'][1],k['sun'][1]))

class ListColumn(gtk.TreeViewColumn):
  def __init__(self, label, idx, name, day_idx):
    gtk.TreeViewColumn.__init__(self,label,gtk.CellRendererText(), text=idx)
    self.day_name = name
    self.day_idx = day_idx
