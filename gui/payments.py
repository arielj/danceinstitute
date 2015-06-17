#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
import widgets

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


class AddPaymentDialog(gtk.Dialog):
  def __init__(self,payment):
    self.payment = payment
    self.form = AddPaymentForm(payment)
    gtk.Dialog.__init__(self, 'Agregar pago', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class AddPaymentForm(FormFor):
  def __init__(self, payment):
    FormFor.__init__(self, payment)
    
    self.fields = gtk.VBox()
    self.add_field('date', attrs=10)
    self.date_e.connect('button-press-event', self.show_calendar)
    self.add_field('amount', attrs=6)
    
    if payment.installment is None:
      self.add_field('description', attrs=100)
    else:
      self.ignore_recharge = gtk.CheckButton('Ignorar recargo')
      self.ignore_recharge.connect('toggled',self.on_ignore_recharge_toggled)
      self.fields.pack_start(self.ignore_recharge, False)
    
    self.pack_start(self.fields, False)

  def get_values(self):
    data = {'date': self.date_e.get_text(), 'amount': self.amount_e.get_text()}
    if self.object.installment is None:
      data['description'] = self.description_e.get_text()
    else:
      data['ignore_recharge'] = self.ignore_recharge.get_active()

    return data

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    widget.set_text("%s-%s-%s" % (year, month, day))
    dialog.destroy()

  def on_ignore_recharge_toggled(self, widget):
    self.amount_e.set_text(str(self.object.installment.to_pay(ignore_recharge=widget.get_active())))

class PaymentsTab(gtk.VBox):
  def __init__(self, user, done = False):
    gtk.VBox.__init__(self)
    
    self.membership = None
    self.user = user
    self.done = done
    
    self.info_vbox =gtk.VBox()
    self.info_vbox.pack_start(gtk.Label('Pagos no relacionados a cuotas'), False)

    self.pack_start(self.info_vbox, False)

    #payment, date, description, amount
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str)
    
    self.refresh()
    
    self.list = gtk.TreeView(self.store)
    self.list.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
    self.selection = self.list.get_selection()
    self.selection.connect('changed', self.on_selection_changed)
    
    self.add_column('Fecha',1)
    self.add_column('Descripción',2)
    self.add_column('Monto',3)

    self.scrolled = gtk.ScrolledWindow()
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.list)
    self.scrolled.add(viewport)
    
    self.pack_start(self.scrolled, True)
    
    self.actions = gtk.HBox(True, 5)
    
    self.add_b = gtk.Button('Agregar Pago')
    self.delete_b = gtk.Button('Eliminar Pago')
    self.delete_b.set_sensitive(False)
    
    self.actions.pack_start(self.add_b, False)
    self.actions.pack_start(self.delete_b, False)
    
    self.pack_start(self.actions, False)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col

  def refresh(self):
    self.store.clear()
    
    if self.user.is_not_new_record():
      for p in self.user.get_payments(include_installments = False, done = self.done):
        self.store.append((p,p.date,p.description, p.amount))

  def on_selection_changed(self, selection):
    model, iter = selection.get_selected()
    self.delete_b.set_sensitive(iter is not None)

  def get_selected_payment(self):
    model, iter = self.selection.get_selected()
    if iter is None:
      return None
    else:
      return model.get_value(iter,0)

