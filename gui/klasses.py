#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from schedules import *
from teachers import *
from translations import _t

class KlassForm(FormFor):
  def __init__(self, klass):
    FormFor.__init__(self, klass)

    self.create_form_fields()

    self.relationships_hbox = gtk.HBox(False, 8)
    self.fields.pack_start(self.relationships_hbox, True)
    self.add_schedules_table()
    self.add_teachers_table()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit, False)
    
    self.pack_start(self.fields, True)
    
    self.show_all()

  def get_tab_label(self):
    return 'Editar Clase:\n' + self.object.name if self.object.id else 'Agregar Clase'
  
  def create_form_fields(self):
    self.fields = gtk.VBox(False, 5)
    self.add_field('name', attrs=30)
    prices_hbox = gtk.HBox(True, 8)
    self.add_field('normal_fee', attrs=5, box=prices_hbox)
    self.add_field('half_fee', attrs=5, box=prices_hbox)
    self.add_field('once_fee', attrs=5, box=prices_hbox)
    self.add_field('inscription_fee', attrs=5, box=prices_hbox)
    self.fields.pack_start(prices_hbox, False)

    students_hbox = gtk.HBox(True, 8)
    self.add_field('min_age', attrs=2, box=students_hbox)
    self.add_field('max_age', attrs=2, box=students_hbox)
    self.add_field('quota', attrs=2, box=students_hbox)
    self.fields.pack_start(students_hbox, False)
    
    f, l, e = self.add_field('info', field_type = 'text')
    e.set_size_request(-1,200)
    f.set_child_packing(e,True,True,0,gtk.PACK_START)
  
  def get_info_text(self):
    buff = self.info_e.get_buffer()
    return buff.get_text(buff.get_start_iter(), buff.get_end_iter())
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'normal_fee': self.normal_fee_e.get_text(), 'half_fee': self.half_fee_e.get_text(), 'once_fee': self.once_fee_e.get_text(), 'min_age': self.min_age_e.get_text(), 'max_age': self.max_age_e.get_text(), 'quota': self.quota_e.get_text(), 'info': self.get_info_text()}

  def add_schedules_table(self):
    self.schedules_l = gtk.Label('Horarios')
    self.schedules_ls = SchedulesList(self.object.get_schedules())
    self.schedules_ls.connect('schedule-add', self.on_schedule_add)
    self.schedules_ls.connect('schedule-edit', self.on_schedule_edit)
    self.schedules_ls.connect('schedule-delete', self.on_schedule_delete)

    field = gtk.VBox()
    field.pack_start(self.schedules_l, False)
    field.pack_start(self.schedules_ls, True)
    self.relationships_hbox.pack_start(field, True)
    
  def add_teachers_table(self):
    self.teachers_l = gtk.Label('Profesores/as')
    self.teachers_ls = TeachersList(self.object.get_teachers(), with_actions=False)
    self.teachers_ls.connect('selection-changed', self.on_selection_changed)
    
    actions = gtk.HBox()
    self.assign_b = gtk.Button('Asignar')
    self.assign_b.connect('clicked', self.on_assign_clicked)
    actions.pack_start(self.assign_b, False)
    
    self.remove_b = gtk.Button('Quitar')
    self.remove_b.connect('clicked', self.on_remove_clicked)
    self.remove_b.set_sensitive(False)
    actions.pack_start(self.remove_b, False)
    
    self.teachers_ls.vbox.pack_start(actions, False)

    frame = gtk.Frame()
    field = gtk.VBox()
    field.set_size_request(650,-1)
    field.pack_start(self.teachers_l, False)
    frame.add(self.teachers_ls)
    field.pack_start(frame, True)
    self.relationships_hbox.pack_start(field, True)
  
  def add_schedule(self, schedule):
    self.object.add_schedule(schedule)
    self.update_schedules()

  def update_schedules(self):
    self.schedules_ls.update_table(self.object.get_schedules())

  def update_teachers(self):
    self.teachers_ls.update_table(self.object.get_teachers())

  def on_schedule_add(self, widget):
    self.emit('schedule-add')
  
  def on_schedule_edit(self, widget, schedule):
    self.emit('schedule-edit', schedule)

  def on_schedule_delete(self, widget, schedule):
    print 'borrar....'

  def on_assign_clicked(self, widget):
    self.emit('teacher-search')

  def on_remove_clicked(self, widget):
    self.emit('teacher-remove', self.teachers_ls.get_selected())

  def on_selection_changed(self, widget, selection):
    model, iter = selection.get_selected()
    self.remove_b.set_sensitive(iter is not None)

gobject.type_register(KlassForm)
gobject.signal_new('schedule-edit', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('schedule-add', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
#gobject.signal_new('teacher-edit', \
#                   KlassForm, \
#                   gobject.SIGNAL_RUN_FIRST, \
#                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
#gobject.signal_new('teacher-add', \
#                   KlassForm, \
#                   gobject.SIGNAL_RUN_FIRST, \
#                   gobject.TYPE_NONE, ())
gobject.signal_new('teacher-search', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('teacher-remove', \
                   KlassForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class SchedulesTables(gtk.ScrolledWindow):
  def __init__(self, klasses):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
    self.set_shadow_type(gtk.SHADOW_NONE)
    self.set_border_width(4)
    
    self.klasses = klasses
    
    self.vbox = gtk.VBox(False, 10)
    
    self.room_table = {}
    for room in klasses.iterkeys():
      vbox = gtk.VBox(False, 3)
      label = gtk.Label('Horarios en sala: ' + room)
      self.room_table[room] = RoomKlassesTable(room, self.klasses[room])
      self.room_table[room].connect('row-activated', self.on_row_activated)
      vbox.pack_start(label, False)
      vbox.pack_start(self.room_table[room], False)
      self.vbox.pack_start(vbox, False)

    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)
    
    self.show_all()

  def get_tab_label(self):
    return 'Horarios'

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

  def refresh_tables(self,klasses):
    self.klasses = klasses
    for room in self.klasses:
      self.room_table[room].refresh(self.klasses[room])
    
gobject.type_register(SchedulesTables)
gobject.signal_new('klass-edit', \
                   SchedulesTables, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
                   
gobject.signal_new('klass-add', \
                   SchedulesTables, \
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
    
    self.refresh(klasses)

  def refresh(self, klasses):
    self.store.clear()
    keys = klasses.keys()
    keys.sort()
    for h in keys:
      k = klasses[h]
      insert = [h]
      for d in _t('abbr_days','en'):
        insert.append(k[d].name if k[d] else '')
      self.store.append(insert)

class ListColumn(gtk.TreeViewColumn):
  def __init__(self, label, idx, name, day_idx):
    gtk.TreeViewColumn.__init__(self,label,gtk.CellRendererText(), text=idx)
    self.day_name = name
    self.day_idx = day_idx
    self.set_expand(True)


class KlassesList(gtk.ScrolledWindow):
  def __init__(self, klasses, with_actions = True):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.klasses = klasses
    self.with_actions = with_actions
    
    self.vbox = gtk.VBox()
    
    self.klasses_t = KlassesTable(klasses)
    self.klasses_t.connect('row-activated', self.on_row_activated)
    self.t_selection = self.klasses_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)
    
    self.vbox.pack_start(self.klasses_t, True)
    
    if self.with_actions:
      self.add_b = gtk.Button('Agregar')
      self.edit_b = gtk.Button('Editar')
      self.edit_b.set_sensitive(False)
      self.delete_b = gtk.Button('Borrar')
      self.delete_b.set_sensitive(False)
      self.add_b.connect('clicked', self.on_add_clicked)
      self.edit_b.connect('clicked', self.on_edit_clicked)
      self.delete_b.connect('clicked', self.on_delete_clicked)
      
      self.actions = gtk.HBox()
      self.actions.pack_start(self.add_b, False)
      self.actions.pack_start(self.edit_b, False)
      self.actions.pack_start(self.delete_b, False)
      
      self.vbox.pack_start(self.actions, False)
    
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)
    
    self.show_all()

  def get_tab_label(self):
    return 'Clases'

  def refresh_list(self, klasses):
    self.klasses_t.update(klasses)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    klass = model.get_value(itr, 0)
    self.emit('klass-edit', klass)

  def on_selection_changed(self, selection):
    if self.with_actions:
      model, iter = selection.get_selected()
      self.edit_b.set_sensitive(iter is not None)
      self.delete_b.set_sensitive(iter is not None)
    self.emit('selection-changed', selection)

  def on_add_clicked(self, btn):
    self.emit('klass-add')

  def on_edit_clicked(self, btn):
    klass = self.get_selected()
    if klass is not None:
      self.emit('klass-edit', klass)

  def on_delete_clicked(self, btn):
    klass = self.get_selected()
    if klass is not None:
      self.emit('klass-delete', klass)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

gobject.type_register(KlassesList)
gobject.signal_new('klass-edit', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('klass-delete', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('klass-add', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('selection-changed', \
                   KlassesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class KlassesTable(gtk.TreeView):
  def __init__(self, klasses):
    self.create_store(klasses)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Nombre', 1)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, klasses):
    # klass, name
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    self.update(klasses)

  def update(self, klasses):
    self.store.clear()
    self.set_model(klasses)
  
  def set_model(self, klasses):
    for k in klasses:
      self.store.append((k,k.name))

