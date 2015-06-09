#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject

class Home(gtk.HBox):
  def __init__(self, klasses = [], notes = '', installments = [], payments = [], movements = []):
    gtk.HBox.__init__(self, False, 10)
    self.set_border_width(4)
    
    left = gtk.VBox(False, 10)
    self.klasses = TodayKlasses(klasses)
    left.pack_start(self.klasses, False)

    self.notes = Notes(notes)
    left.pack_start(self.notes, True)
    
    self.installments = OverdueInstallments(installments)
    self.installments.list.connect('row-activated', self.on_installment_activated)

    self.daily_cash = DailyCash(payments,movements)
    
    self.pack_start(left)
    self.pack_start(self.installments)
    self.pack_start(self.daily_cash)
    
    self.show_all()

  def get_tab_label(self):
    return 'Inicio'

  def on_installment_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    user_id = model.get_value(itr, 1)
    if user_id:
      self.emit('user-edit', user_id)

  def get_notes(self):
    buff = self.notes.entry.get_buffer()
    return buff.get_text(buff.get_start_iter(), buff.get_end_iter())

  def update_movements(self, movements):
    self.daily_cash.update_movements(movements)

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
    self.entry = gtk.TextView()
    self.entry.set_editable(True)
    self.entry.get_buffer().set_text(notes)
    self.entry.set_wrap_mode(gtk.WRAP_WORD)
    e = gtk.ScrolledWindow()
    e.add(self.entry)
    e.set_shadow_type(gtk.SHADOW_ETCHED_IN)
    e.set_policy(gtk.POLICY_NEVER,gtk.POLICY_AUTOMATIC)
    self.pack_start(e,True)
    
    self.save = gtk.Button('Guardar nota')
    self.pack_start(self.save, False)

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

class DailyCash(gtk.VBox):
  def __init__(self, payments, movements):
    gtk.VBox.__init__(self, False, 5)
    self.payments = payments
    self.movements = movements
    self.payments_l = PaymentsList(self.payments)
    self.movements_l = MovementsList(self.movements)

    self.pack_start(self.payments_l, True)
    self.pack_start(self.movements_l, True)

  def update_movements(self, movements):
    self.movements = movements
    self.movements_l.update_table(movements)

class PaymentsList(gtk.VBox):
  def __init__(self, payments):
    gtk.VBox.__init__(self, False, 5)
    self.headings = ['Alumno/Profesor', 'Entrada', 'Salida', 'Descripción']
    
    self.table = PaymentsTable(payments, self.headings)
    
    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.table)
    self.pack_start(self.scroll, True)
    
    total_in = 0
    total_out = 0
    for p in payments:
      if p.done:
        total_out += p.amount
      else:
        total_in += p.amount
    self.totals = gtk.Label('Entradas: $'+str(total_in)+' ; Salidas: $'+str(total_out))
    self.pack_start(self.totals, False)
    
class PaymentsTable(gtk.TreeView):
  def __init__(self, payments, headings):
    self.create_store(payments)
    
    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, payments):
    # payment, user name, amount in, amount out, description
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)
    self.update(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)
  
  def set_model(self, payments):
    for p in payments:
      if p.done:
        amount_in = ''
        amount_out = p.amount
      else:
        amount_in = p.amount
        amount_out = ''
      self.store.append((p, p.user.to_label(), str(amount_in), str(amount_out), p.description))

class MovementsList(gtk.VBox):
  def __init__(self, movements):
    gtk.VBox.__init__(self, False, 5)
    self.headings = ['Entrada', 'Salida', 'Descripción']
    
    self.table = MovementsTable(movements, self.headings)
    self.table.get_selection().connect('changed', self.on_selection_changed)
    
    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.table)
    
    self.pack_start(self.scroll, True)
    

    self.totals = gtk.Label(self.get_total_text(movements))
    self.pack_start(self.totals, False)

    self.add_b = gtk.Button('Agregar Movimiento')
    self.delete_b = gtk.Button('Eliminar Movimiento')
    self.delete_b.set_sensitive(False)
    self.movement_actions = gtk.HBox(True, 4)
    self.movement_actions.pack_start(self.add_b)
    self.movement_actions.pack_start(self.delete_b)
    self.pack_start(self.movement_actions, False)

  def update_table(self, movements):
    self.table.update(movements)
    self.totals.set_text(self.get_total_text(movements))

  def get_total_text(self, movements):
    total_in = 0
    total_out = 0
    for m in movements:
      if m.is_outgoing():
        total_out += m.amount
      else:
        total_in += m.amount
    return 'Entradas: $'+str(total_in)+' ; Salidas: $'+str(total_out)

  def on_selection_changed(self, selection):
    model, iter = selection.get_selected()
    self.delete_b.set_sensitive(iter is not None)

  def get_selected_movement(self):
    model, iter = self.table.get_selection().get_selected()
    if iter is None:
      return None
    else:
      return model.get_value(iter,0)

class MovementsTable(gtk.TreeView):
  def __init__(self, movements, headings):
    self.create_store(movements)
    
    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, movements):
    # movement, in, out, description
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str)
    self.update(movements)

  def update(self, movements):
    self.store.clear()
    self.set_model(movements)
  
  def set_model(self, movements):
    for m in movements:
      if m.is_incoming():
        amount_in = m.amount
        amount_out = ''
      else:
        amount_out = m.amount
        amount_in = ''
      self.store.append((m, str(amount_in), str(amount_out), m.description))

