#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from schedules import *

class KlassForm(FormFor):
  def __init__(self, klass):
    FormFor.__init__(self, klass)

    self.create_form_fields()

    self.add_schedules_table()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit, False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    return 'Editar Clase:\n' + self.object.name if self.object.id else 'Agregar Clase'
  
  def create_form_fields(self):
    self.fields = gtk.VBox()
    self.add_field('Clase', 'name', attrs=30)
    self.add_field('Precio', 'fee', attrs=5)
    self.add_field('Precio alternativo', 'half_fee', attrs=5)
    self.add_field('Precio por clase individual', 'once_fee', attrs=5)
    self.add_field('Inscripción', 'inscription_fee', attrs=5)
    self.add_field('Edad mínima', 'min_age', attrs=2)
    self.add_field('Edad máxima', 'max_age', attrs=2)
    self.add_field('Cupo máximo', 'quota', attrs=2)
    
    self.info_l = gtk.Label('Información')
    self.info_e = gtk.TextView()
    self.info_e.set_editable(True)
    self.info_e.get_buffer().set_text(self.object.info)
    self.info_e.set_wrap_mode(gtk.WRAP_WORD)
    scroll_window = gtk.ScrolledWindow()
    scroll_window.add(self.info_e)
    scroll_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    scroll_window.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    
    self.fields.pack_start(self.info_l, False)
    self.fields.pack_start(scroll_window, True)
  
  def get_info_text(self):
    buff = self.info_e.get_buffer()
    return buff.get_text(buff.get_start_iter(), buff.get_end_iter())
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'fee': self.fee_e.get_text(), 'half_fee': self.half_fee_e.get_text(), 'once_fee': self.once_fee_e.get_text(), 'min_age': self.min_age_e.get_text(), 'max_age': self.max_age_e.get_text(), 'quota': self.quota_e.get_text(), 'info': self.get_info_text()}

  def add_schedules_table(self):
    self.schedules_l = gtk.Label('Horarios')
    self.schedules_ls = SchedulesList(self.object.schedules)
    self.schedules_ls.connect('schedule-add', self.on_schedule_add)
    self.schedules_ls.connect('schedule-edit', self.on_schedule_edit)
    self.schedules_ls.connect('schedule-delete', self.on_schedule_delete)
        
    self.fields.pack_start(self.schedules_l, False)
    self.fields.pack_start(self.schedules_ls, True)
  
  def add_schedule(self, schedule):
    self.object.schedules.append(schedule)
    self.update_schedules()

  def update_schedules(self):
    self.schedules_ls.update_table(self.object.schedules)

  def on_schedule_add(self, widget):
    self.emit('schedule-add')
  
  def on_schedule_edit(self, widget, schedule):
    self.emit('schedule-edit', schedule)

  def on_schedule_delete(self, widget, schedule):
    print 'borrar....'

gobject.type_register(KlassForm)
gobject.signal_new('schedule-edit', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

gobject.signal_new('schedule-add', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
                   


class KlassesList(gtk.ScrolledWindow):
  def __init__(self, klasses):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
    
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
      klass = self.klasses[room][time][day]
      if klass:
        self.emit('klass-edit', klass)
      else:
        self.emit('klass-add', room, time, column.day_idx)
    
gobject.type_register(KlassesList)
gobject.signal_new('klass-edit', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
                   
gobject.signal_new('klass-add', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_INT))

class RoomKlassesTable(gtk.TreeView):
  def __init__(self, room, klasses):
    self.room = room
    self.create_store(klasses)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    col = self.add_column('Horario', 0, 'hour',-1)
    col.set_expand(False)

    self.add_column('Lunes', 1, 'mon',0)
    self.add_column('Martes', 2, 'tue',1)
    self.add_column('Miércoles', 3, 'wed',2)
    self.add_column('Jueves', 4, 'thu',3)
    self.add_column('Viernes', 5, 'fri',4)
    self.add_column('Sábado', 6, 'sat',5)
    self.add_column('Domingo', 7, 'sun',6)
  
  def add_column(self, label, idx, name, day_idx):
    col = ListColumn(label, idx, name, day_idx)
    self.append_column(col)
    return col
  
  def create_store(self, klasses):
    # hour, monday, tuesday, wednesday, thursday, friday, saturday, sunday
    self.store = gtk.ListStore(str,str,str,str,str,str,str,str)
    
    for h in range(14,23,1):
      for h2 in [str(h)+':00', str(h)+':30']:
        k = klasses[h2]
        insert = [h2]
        for d in ['mon','tue','wed','thu','fri','sat','sun']:
          insert.append(k[d].name if k[d] else '')
        self.store.append(insert)

class ListColumn(gtk.TreeViewColumn):
  def __init__(self, label, idx, name, day_idx):
    gtk.TreeViewColumn.__init__(self,label,gtk.CellRendererText(), text=idx)
    self.day_name = name
    self.day_idx = day_idx
    self.set_expand(True)

