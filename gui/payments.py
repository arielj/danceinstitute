#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject

class PaymentsPanel(gtk.VBox):
  def __init__(self,teacher):
    gtk.VBox.__init__(self)
    
    self.teacher = teacher
    
    self.pack_start(gtk.Label('Pagos'),False)
    
    self.payments_t = PaymentsList(teacher.get_payments())
    self.pack_start(self.payments_t, True)

  def update(self):
    self.payments_t.update_table(self.teacher.get_payments())
    
class PaymentsList(gtk.ScrolledWindow):
  def __init__(self, payments, with_actions = True):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.payments = payments
    self.with_actions = with_actions
    
    self.vbox = gtk.VBox()
    
    self.payments_t = PaymentsTable(payments)
    self.t_selection = self.payments_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)
    
    self.vbox.pack_start(self.payments_t, True)
    
    if self.with_actions:
      self.add_b = gtk.Button('Agregar')
      self.delete_b = gtk.Button('Borrar')
      self.delete_b.set_sensitive(False)
      self.add_b.connect('clicked', self.on_add_clicked)
      self.delete_b.connect('clicked', self.on_delete_clicked)
      
      self.actions = gtk.HBox()
      self.actions.pack_start(self.add_b, False)
      self.actions.pack_start(self.delete_b, False)
      
      self.vbox.pack_start(self.actions, False)
    
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)
    
    self.show_all()

  def get_tab_label(self):
    return 'Pagos'

  def update_table(self, payments):
    self.payments_t.update(payments)

  def on_selection_changed(self, selection):
    if self.with_actions:
      model, iter = selection.get_selected()
      self.delete_b.set_sensitive(iter is not None)
    self.emit('selection-changed', selection)

  def on_add_clicked(self, btn):
    self.emit('payment-add')

  def on_delete_clicked(self, btn):
    payment = self.get_selected()
    if payment is not None:
      self.emit('payment-delete', payment)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

  def refresh_list(self, payments):
    self.payments_t.update(payments)

gobject.type_register(PaymentsList)
gobject.signal_new('payment-delete', \
                   PaymentsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('payment-add', \
                   PaymentsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('selection-changed', \
                   PaymentsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class PaymentsTable(gtk.TreeView):
  def __init__(self, payments):
    self.create_store(payments)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Fecha',1)
    self.add_column('Descripción',2)
    self.add_column('Monto',3)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, payments):
    # payment, name, lastname, dni, email, address, cellphone
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str)
    self.set_model(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)
  
  def set_model(self, payments):
    for p in payments:
      self.store.append((p,p.date,p.description,'$'+str(p.amount)))
