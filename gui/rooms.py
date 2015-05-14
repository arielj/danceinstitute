#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor

class RoomsList(gtk.ScrolledWindow):
  def __init__(self, rooms, with_actions = True):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.rooms = rooms
    self.with_actions = with_actions
    
    self.vbox = gtk.VBox()
    
    self.rooms_t = RoomsTable(rooms)
    self.rooms_t.connect('row-activated', self.on_row_activated)
    self.t_selection = self.rooms_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)
    
    self.vbox.pack_start(self.rooms_t, True)
    
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
    return 'Salas'

  def refresh_list(self, rooms):
    self.rooms_t.update(rooms)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    room = model.get_value(itr, 0)
    self.emit('room-edit', room)

  def on_selection_changed(self, selection):
    if self.with_actions:
      model, iter = selection.get_selected()
      self.edit_b.set_sensitive(iter is not None)
      self.delete_b.set_sensitive(iter is not None)
    self.emit('selection-changed', selection)

  def on_add_clicked(self, btn):
    self.emit('room-add')

  def on_edit_clicked(self, btn):
    room = self.get_selected()
    if room is not None:
      self.emit('room-edit', room)

  def on_delete_clicked(self, btn):
    room = self.get_selected()
    if room is not None:
      self.emit('room-delete', room)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

gobject.type_register(RoomsList)
gobject.signal_new('room-edit', \
                   RoomsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('room-delete', \
                   RoomsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('room-add', \
                   RoomsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('selection-changed', \
                   RoomsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class RoomsTable(gtk.TreeView):
  def __init__(self, rooms):
    self.create_store(rooms)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Nombre', 1)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, rooms):
    # room, name, klasses names
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    self.update(rooms)

  def update(self, rooms):
    self.store.clear()
    self.set_model(rooms)
  
  def set_model(self, rooms):
    for r in rooms:
      self.store.append((r,r.name))

class RoomForm(FormFor):
  def __init__(self, room):
    FormFor.__init__(self, room)

    self.room = room

    self.create_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.pack_start(self.fields, True)
    
    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      return "Editar sala:\n" + self.object.name
    else:
      return 'Agregar sala'
  
  def create_form_fields(self):
    self.fields = gtk.VBox()
    self.add_field('name', attrs=20)
  
  def get_values(self):
    return {'name': self.name_e.get_text()}

