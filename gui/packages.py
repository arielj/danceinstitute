#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor

class PackagesList(gtk.ScrolledWindow):
  def __init__(self, packages, with_actions = True):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.packages = packages
    self.with_actions = with_actions
    
    self.vbox = gtk.VBox()
    
    self.packages_t = PackagesTable(packages)
    self.packages_t.connect('row-activated', self.on_row_activated)
    self.t_selection = self.packages_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)
    
    self.vbox.pack_start(self.packages_t, True)
    
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
    return 'Paquetes'

  def refresh_list(self, packages):
    self.packages_t.update(packages)

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
    self.emit('package-add')

  def on_edit_clicked(self, btn):
    package = self.get_selected()
    if package is not None:
      self.emit('package-edit', package)

  def on_delete_clicked(self, btn):
    package = self.get_selected()
    if package is not None:
      self.emit('klass-delete', package)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

gobject.type_register(PackagesList)
gobject.signal_new('package-edit', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('package-delete', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('package-add', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('selection-changed', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class PackagesTable(gtk.TreeView):
  def __init__(self, packages):
    self.create_store(packages)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Nombre', 1)
    self.add_column('Clases', 2)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, packages):
    # package, name, klasses names
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str)
    self.update(packages)

  def update(self, packages):
    self.store.clear()
    self.set_model(packages)
  
  def set_model(self, packages):
    for p in packages:
      self.store.append((p,p.name,p.klasses_names()))

