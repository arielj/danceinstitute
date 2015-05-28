#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject

class Home(gtk.HBox):
  def __init__(self, klasses = [], notes = [], installments = []):
    gtk.HBox.__init__(self, False, 10)
    self.set_border_width(4)
    
    left = gtk.VBox()
    self.klasses = TodayKlasses(klasses)
    left.pack_start(self.klasses)

    self.notes = Notes(notes)
    left.pack_start(self.notes)
    
    
    self.installments = OverdueInstallments(installments)
    self.installments.list.connect('row-activated', self.on_installment_activated)
    
    self.pack_start(left)
    self.pack_start(self.installments)
    
    self.show_all()

  def get_tab_label(self):
    return 'Inicio'

  def on_installment_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    user_id = model.get_value(itr, 1)
    if user_id:
      self.emit('user-edit', user_id)

gobject.type_register(Home)
gobject.signal_new('user-edit', \
                   Home, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class TodayKlasses(gtk.VBox):
  def __init__(self,klasses):
    gtk.VBox.__init__(self)
    self.pack_start(gtk.Label('Clases de hoy'), False)
    self.table = KlassesTable(klasses)
    self.pack_start(self.table, True)

class KlassesTable(gtk.TreeView):
  def __init__(self, klasses):
    self.create_store(klasses)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    col = self.add_column('Horario', 0)
    col.set_expand(False)

    for idx, room in enumerate(klasses[klasses.keys()[0]].keys(),1):
      self.add_column(room, idx)
  
  def add_column(self, label, idx):
    col = gtk.TreeViewColumn(label,gtk.CellRendererText(), text=idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, klasses):
    args = (str,)
    for i in range(0,len(klasses[klasses.keys()[0]].keys())):
      args = args + (str, )
    
    self.store = gtk.ListStore(*args)
    
    self.refresh(klasses)

  def refresh(self, klasses):
    self.store.clear()
    keys = klasses.keys()
    keys.sort()

    for h in keys:
      insert = [h]
      k = klasses[h]
      for r in k.keys():
        insert.append(k[r].name if k[r] else '')
      self.store.append(insert)



class Notes(gtk.VBox):
  def __init__(self,notes):
    gtk.VBox.__init__(self)
    self.pack_start(gtk.Label('Notas'), False)

class OverdueInstallments(gtk.VBox):
  def __init__(self,installments):
    self.installments = installments
    gtk.VBox.__init__(self)
    self.pack_start(gtk.Label('Cuotas atrasadas'), False)

    #installment, user_id, user_label, year, month
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,gobject.TYPE_PYOBJECT,str,str,str)
    
    self.refresh()
    
    self.list = gtk.TreeView(self.store)
    self.list.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
    
    self.add_column('Usuario',2)
    self.add_column('Año',3)
    self.add_column('Mes',4)

    self.scrolled = gtk.ScrolledWindow()
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.list)
    self.scrolled.add(viewport)
    
    self.pack_start(self.scrolled, True)

  def refresh(self):
    self.store.clear()
    
    for ins in self.installments:
      u = ins.get_student()
      self.store.append((ins,u.id,u.to_label(),ins.year,ins.month_name()))

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col
