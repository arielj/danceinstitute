#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
import widgets
from settings import Settings
import datetime

class PaymentsTable(gtk.TreeView):
  def __init__(self, payments):
    self.create_store(payments)

    gtk.TreeView.__init__(self,self.store)

    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    self.add_column('Fecha',1)
    self.add_column('Descripción',2)
    self.add_column('Monto',3)
    self.add_column('Recibo N°',4)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, payments):
    # payment, date, description, amount, receipt_number
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)
    self.set_model(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)

  def set_model(self, payments):
    for p in payments:
      self.store.append((p,p.date.strftime(Settings.get_settings().date_format),p.description,'$'+p.amount,str(p.receipt_number or '')))


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

class AddPaymentsDialog(gtk.Dialog):
  def __init__(self,installments):
    gtk.Dialog.__init__(self, 'Agregar pagos', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.selected_payments = []
    self.installments = installments
    self.add_installments_table()
    amount_f = gtk.HBox()
    self.amount_e = gtk.Entry(10)
    amount_f.pack_start(gtk.Label('Cantidad'), False)
    amount_f.pack_start(self.amount_e, True)
    self.vbox.pack_start(amount_f, False)
    self.date_e = gtk.Entry(10)
    self.date_e.set_text(datetime.datetime.today().strftime(Settings.get_settings().date_format))
    self.date_e.connect('button-press-event', self.show_calendar)
    date_f = gtk.HBox()
    date_f.pack_start(gtk.Label('Fecha'), False)
    date_f.pack_start(self.date_e, True)
    self.vbox.pack_start(date_f, False)
    self.update_total()
    self.vbox.show_all()

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()

  def add_installments_table(self):
    scroll = gtk.ScrolledWindow()
    #installment, student label, month, year, total, paid, select, ignore_recharge
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str,bool,bool)
    for i in self.installments:
      do_check = i.year == datetime.date.today().year and i.month == datetime.date.today().month-1
      if do_check: self.selected_payments.append(i)
      self.store.append([i,i.get_student().to_label(),i.month_name(),str(i.year),i.detailed_total(),i.detailed_to_pay(), do_check, False])

    self.table = gtk.TreeView(self.store)
    self.add_column('Alumno', 1)
    self.add_column('Año', 2)
    self.add_column('Mes', 3)
    self.add_column('Monto', 4)
    self.add_column('Saldo', 5)

    check_renderer = gtk.CellRendererToggle()
    check_renderer.set_activatable(True)
    check_renderer.connect('toggled', self.on_payment_toggled)
    col = gtk.TreeViewColumn('Seleccionar', check_renderer)
    col.add_attribute(check_renderer, "active", 6)
    self.table.append_column(col)
    check_renderer = gtk.CellRendererToggle()
    check_renderer.set_activatable(True)
    check_renderer.connect('toggled', self.on_ignore_recharge_toggled)
    col = gtk.TreeViewColumn('Ignorar recargo', check_renderer)
    col.add_attribute(check_renderer, "active", 7)
    self.table.append_column(col)

    scroll.set_size_request(500,400)
    scroll.add(self.table)
    self.vbox.pack_start(scroll, True)

  def on_payment_toggled(self, renderer, path):
    row = self.store[path]
    row[6] = not row[6]
    if row[6]:
      self.selected_payments.append(row[0])
    else:
      self.selected_payments.remove(row[0])

    self.update_total()

  def on_ignore_recharge_toggled(self, renderer, path):
    row = self.store[path]
    row[7] = not row[7]
    row[0].ignore_recharge = row[7]
    row[5] = row[0].detailed_to_pay()
    self.update_total()

  def update_total(self):
    total = 0
    for p in self.selected_payments: total += p.to_pay()
    self.amount_e.set_text(str(total))

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.table.append_column(col)
    return col

  def get_selected_installments(self):
    return self.selected_payments

  def get_amount(self):
    return int(self.amount_e.get_text())

class AddPaymentForm(FormFor):
  def __init__(self, payment):
    FormFor.__init__(self, payment)

    self.fields = gtk.VBox()
    self.add_field('date', attrs=10)
    self.date_e.set_text(payment.date.strftime(Settings.get_settings().date_format))
    self.date_e.connect('button-press-event', self.show_calendar)
    self.add_field('amount', attrs=15)
    self.add_field('receipt_number', attrs=15)
    self.add_field('description', attrs=100, getter='_description')

    if payment.installment is not None:
      if payment.installment.get_recharge() > 0:
        self.ignore_second_recharge = gtk.CheckButton('Ignorar recargo por mes vencido')
        self.ignore_second_recharge.connect('toggled',self.on_ignore_recharge_toggled)
        self.fields.pack_start(self.ignore_second_recharge, False)
        self.ignore_recharge = gtk.CheckButton('Ignorar recargo por fecha')
        self.ignore_recharge.connect('toggled',self.on_ignore_recharge_toggled)
        self.fields.pack_start(self.ignore_recharge, False)
        if Settings.get_settings().recharge_value == '': self.ignore_recharge.set_no_show_all(True)
        if Settings.get_settings().second_recharge_value == '': self.ignore_second_recharge.set_no_show_all(True)

    self.pack_start(self.fields, False)

  def get_values(self):
    data = {'date': self.date_e.get_text(), 'amount': self.amount_e.get_text(), 'receipt_number': self.receipt_number_e.get_text(), 'description': self.description_e.get_text(), 'ignore_recharge': True}
    if ('ignore_recharge' in vars(self)): data['ignore_recharge'] = self.ignore_recharge.get_active()
    if ('ignore_second_recharge' in vars(self)): data['ignore_second_recharge'] = self.ignore_second_recharge.get_active()

    return data

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()

  def on_ignore_recharge_toggled(self, widget):
    self.amount_e.set_text(str(self.object.installment.to_pay(ignore_recharge=self.ignore_recharge.get_active(), ignore_second_recharge=self.ignore_second_recharge.get_active())))

class PaymentsTab(gtk.VBox):
  def __init__(self, user, done = False):
    gtk.VBox.__init__(self)

    self.user = user
    self.done = done

    self.info_vbox =gtk.VBox()
    self.info_vbox.pack_start(gtk.Label('Pagos no relacionados a cuotas'), False)

    self.pack_start(self.info_vbox, False)

    #payment, date, description, amount, receipt_number
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)

    self.refresh()

    self.list = gtk.TreeView(self.store)
    self.list.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
    self.selection = self.list.get_selection()
    self.selection.connect('changed', self.on_selection_changed)

    self.list.set_rubber_banding(True)
    self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    self.add_column('Fecha',1)
    self.add_column('Descripción',2)
    self.add_column('Monto',3)
    self.add_column('Recibo N°',4)

    self.scrolled = gtk.ScrolledWindow()
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.list)
    self.scrolled.add(viewport)

    self.pack_start(self.scrolled, True)

    self.actions = gtk.HBox(True, 5)

    self.add_b = gtk.Button('Agregar Pago')
    self.delete_b = gtk.Button('Eliminar Pago(s)')
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
      for p in self.user.get_payments(include_installments = False, done = self.done).order_by('date DESC, id DESC'):
        self.store.append((p,p.date.strftime(Settings.get_settings().date_format),p.description, '$'+p.amount, str(p.receipt_number or '')))

  def on_selection_changed(self, selection):
    model, pathlist = selection.get_selected_rows()
    self.delete_b.set_sensitive(pathlist != False)

  def get_selected_payments(self):
    model, pathlist = self.selection.get_selected_rows()
    items = []
    for path in pathlist:
      iter = model.get_iter(path)
      items.append(model.get_value(iter, 0))
    return items

  def on_payment_deleted(self, p_id):
    self.refresh()

class EditInstallmentPaymentsDialog(gtk.Dialog):
  def __init__(self, installment):
    gtk.Dialog.__init__(self, 'Editar pagos de cuota', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.installment = installment

    self.payments = {}

    hbox = gtk.HBox()
    self.vbox.pack_start(hbox)

    dates_vbox = gtk.VBox()
    hbox.pack_start(dates_vbox)
    dates_vbox.pack_start(gtk.Label('Fecha'))

    descs_vbox = gtk.VBox()
    hbox.pack_start(descs_vbox)
    descs_vbox.pack_start(gtk.Label('Descripción'))

    amounts_vbox = gtk.VBox()
    hbox.pack_start(amounts_vbox)
    amounts_vbox.pack_start(gtk.Label('Monto'))

    removes_vbox = gtk.VBox()
    hbox.pack_start(removes_vbox)
    removes_vbox.pack_start(gtk.Label('Eliminar'))

    for p in installment.payments:
      hbox = gtk.HBox()
      date_e = gtk.Entry(10)
      date_e.set_text(p.date.strftime(Settings.get_settings().date_format))
      dates_vbox.pack_start(date_e)

      desc_e = gtk.Entry(100)
      if p._description: desc_e.set_text(p._description)
      descs_vbox.pack_start(desc_e)

      amount_e = gtk.Entry(10)
      amount_e.set_text(str(p.amount))
      amounts_vbox.pack_start(amount_e)

      receipt_e = gtk.Entry(10)
      if p._receipt_number: receipt_e.set_text(str(p._receipt_number))
      #hbox.pack_start(receipt_e)

      remove_e = gtk.CheckButton()
      removes_vbox.pack_start(remove_e)

      self.payments[p.id] = {'date': date_e, 'desc': desc_e, 'amount': amount_e, 'receipt': receipt_e, 'remove': remove_e}

    self.show_all()

  def get_payments_data(self):
    data = {}
    for p_id, p_data in self.payments.iteritems():
      data[p_id] = {'date': p_data['date'].get_text(), 'description': p_data['desc'].get_text(), 'amount': p_data['amount'].get_text(), 'receipt_number': p_data['receipt'].get_text(), 'remove': p_data['remove'].get_active()}

    return data
