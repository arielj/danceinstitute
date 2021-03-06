#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from payments import *
from liabilities import *
from translations import _t, _m
import datetime

class MembershipsTab(gtk.VBox):
  def __init__(self, user):
    gtk.VBox.__init__(self)
    self.user = user

    self.membership_data = MembershipData(None)
    self.membership_data.connect('edit-package', self.on_edit_package_clicked)
    self.membership_data.connect('add-payment', self.on_add_payment)
    self.membership_data.connect('edit-installment', self.on_edit_installment)
    self.membership_data.connect('edit-installment-payments', self.on_edit_installment_payments)

    self.memberships = gtk.ComboBoxEntry()
    self.memberships.connect('changed', self.on_membership_selected)
    self.completion = gtk.EntryCompletion()

    self.pack_start(self.memberships, False)
    self.pack_start(self.membership_data, True)

    self.actions = gtk.HBox(True, 2)
    self.create_package_b = gtk.Button('Crear Paquete')
    self.enroll_b = gtk.Button('Incribir a una clase')
    self.delete_b = gtk.Button('Eliminar inscripción')

    self.actions.pack_start(self.create_package_b, False)
    self.actions.pack_start(self.enroll_b, False)
    self.actions.pack_start(self.delete_b, False)

    self.pack_start(self.actions, False)

    self.set_model(self.user.memberships)
    m = self.user.memberships[0] if len(self.user.memberships) > 0 else None
    self.membership_data.set_membership(m)

    self.membership_data.add_installments_b.connect('clicked', self.on_add_ins_clicked)
    self.membership_data.add_payments_b.connect('clicked', self.on_add_payments_clicked)
    self.membership_data.add_payment_b.connect('clicked', self.on_add_payment_clicked)
    self.membership_data.delete_installments_b.connect('clicked', self.on_delete_installments_clicked)
    self.membership_data.list.connect('row-activated', self.on_row_activated)

  def set_model(self, memberships):
    current_membership = self.membership_data.membership
    current_present = False

    memberships_model = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    ms = memberships if isinstance(memberships, list) else memberships.order_by('id DESC')
    for m in ms:
      if current_membership is not None and m.id == current_membership.id:
        current_membership = m
        current_present = True
      memberships_model.append((m, m.klass_or_package.name))

    self.memberships.set_model(memberships_model)
    self.memberships.set_text_column(1)
    self.completion.set_model(memberships_model)
    self.completion.set_text_column(1)
    self.completion.connect('match-selected', self.on_memberships_match_selected)
    self.memberships.child.set_completion(self.completion)
    if current_present is True: self.select_membership(current_membership)
    elif len(memberships) > 0: self.memberships.set_active(0)
    else: self.membership_data.set_membership(None)

  def refresh(self):
    self.set_model(self.user.reload_memberships())
    self.membership_data.refresh()

  def on_membership_selected(self, combo):
    model = combo.get_model()
    if combo.get_active_iter() is not None:
      membership = model.get_value(combo.get_active_iter(), 0)
      self.membership_data.set_membership(membership)

  def select_membership(self, membership):
    memberships_model = self.memberships.get_model()
    found = None

    if membership is not None:
      model_iter = memberships_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_m = memberships_model.get_value(model_iter,0)
        if iter_m is not None and iter_m.id == membership.id:
          found = model_iter
        else:
          model_iter = memberships_model.iter_next(model_iter)

    if found is not None:
      self.memberships.set_active_iter(found)
      self.membership_data.set_membership(membership)
    else:
      self.memberships.set_active_iter(memberships_model.get_iter_first())

  def on_membership_deleted(self, m_id):
    self.refresh()

  def on_installment_deleted(self, i_id):
    self.refresh()

  def on_delete_clicked(self, widget, membership):
    self.emit('ask-delete-membership', membership)

  def on_add_ins_clicked(self, widget):
    self.emit('add-installments')

  def on_add_payment_clicked(self, widget):
    self.emit('add-payment', self.membership_data.get_selected_installments(), False)

  def on_add_payments_clicked(self, widget):
    self.emit('add-payments')

  def on_delete_installments_clicked(self, widget):
    self.emit('delete-installments', self.membership_data.get_selected_installments())

  def on_row_activated(self, tree, path, view_column):
    model = tree.get_model()
    itr = model.get_iter(path)
    installment = model.get_value(itr, 0)
    self.emit('add-payment', [installment], False)

  def on_memberships_match_selected(self, completion, model, itr):
    membership = model.get_value(itr,0)
    self.select_membership(membership)

  def get_current_membership(self):
    return self.membership_data.membership

  def on_edit_package_clicked(self, data, package):
    self.emit('edit-package', package)

  def show_installment(self, installment):
    self.select_membership(installment.membership)

  def on_add_payment(self, data, installment):
    self.emit('add-payment', [installment], False)

  def on_edit_installment(self, data, installment):
    self.emit('edit-installment', installment)

  def on_edit_installment_payments(self, data, installment):
    self.emit('edit-installment-payments', installment)

  def on_payment_deleted(self, p_id):
    return

gobject.type_register(MembershipsTab)
gobject.signal_new('add-installments', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('add-payment', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool))
gobject.signal_new('add-payments', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('delete-installments', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-package', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-installment', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-installment-payments', \
                   MembershipsTab, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class MembershipData(gtk.VBox):
  def __init__(self, membership):
    gtk.VBox.__init__(self)

    self.info_vbox = gtk.VBox()
    self.pack_start(self.info_vbox, False)

    #installment, year, month, base, status, payments
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,int,str,str,str,str)

    self.list = gtk.TreeView(self.store)
    self.list.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
    self.selection = self.list.get_selection()
    self.selection.connect('changed', self.on_selection_changed)

    self.list.set_rubber_banding(True)
    self.selection.set_mode(gtk.SELECTION_MULTIPLE)

    self.list.connect('button-press-event', self.on_list_row_clicked)

    self.add_column('Año',1)
    self.add_column('Mes',2)
    self.add_column('Monto',3)
    self.add_column('Estado',4)
    self.add_column('Pagos',5)

    self.scrolled = gtk.ScrolledWindow()
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.list)
    self.scrolled.add(viewport)

    self.pack_start(self.scrolled, True)

    self.actions = gtk.HBox(True, 2)

    self.add_installments_b = gtk.Button('Agregar Cuotas')
    self.add_payments_b = gtk.Button('Agregar Pagos')
    self.add_payment_b = gtk.Button('Agregar Pago')
    self.add_payment_b.set_sensitive(False)
    self.delete_installments_b = gtk.Button('Eliminar Cuota(s)')
    self.delete_installments_b.set_sensitive(False)

    self.actions.pack_start(self.add_payment_b, False)
    self.actions.pack_start(self.add_payments_b, False)
    self.actions.pack_start(self.add_installments_b, False)
    self.actions.pack_start(self.delete_installments_b, False)

    self.pack_start(self.actions, False)

    self.membership = None
    self.set_membership(membership)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col

  def set_membership_info(self):
    for c in self.info_vbox.get_children(): self.info_vbox.remove(c)

    if self.membership is not None:
      if self.membership.info:
        self.info_vbox.pack_start(gtk.Label(self.membership.info), False)
      if self.membership.is_package():
        includes = gtk.HBox(False, 5)
        includes.pack_start(gtk.Label("El paquete incluye las clases:\n"), False)
        edit_package_button = gtk.Button(None, gtk.STOCK_EDIT)
        edit_package_button.connect('clicked', self.on_edit_package_clicked)
        includes.pack_start(edit_package_button, False)
        includes.pack_start(gtk.Label(self.membership.klass_or_package.klasses_names("\n")), False)
        self.info_vbox.pack_start(includes, False)
      self.info_vbox.show_all()

  def refresh(self):
    self.set_membership_info()
    self.store.clear()

    if self.membership is not None:
      for ins in self.membership.installments:
        self.store.append((ins,ins.year,ins.month_name(),ins.detailed_total(), ins.status, ins.payments_details()))
      self.add_installments_b.set_sensitive(True)
      self.add_payments_b.set_sensitive(True)
    else:
      self.add_installments_b.set_sensitive(False)
      self.add_payments_b.set_sensitive(False)

  def on_selection_changed(self, selection):
    model, pathlist = selection.get_selected_rows()
    self.delete_installments_b.set_sensitive(pathlist != False)
    self.add_payment_b.set_sensitive(len(pathlist) == 1)

  def get_selected_installments(self):
    model, pathlist = self.selection.get_selected_rows()
    items = []
    for path in pathlist:
      iter = model.get_iter(path)
      items.append(model.get_value(iter, 0))
    return items

  def set_membership(self, membership):
    self.membership = membership
    self.refresh()

  def on_edit_package_clicked(self, button):
    if self.membership.is_package() is True: self.emit('edit-package', self.membership.klass_or_package)

  def on_list_row_clicked(self, treeview, event):
    if event.button == 3:
      pthinfo = treeview.get_path_at_pos(int(event.x), int(event.y))
      if pthinfo is not None:
        path, col, cellx, celly = pthinfo
        model = treeview.get_model()
        itr = model.get_iter(path)
        installment = model.get_value(itr,0)

        popup = gtk.Menu()

        edit_ins = gtk.MenuItem('Editar cuota')
        popup.append(edit_ins)
        edit_ins.show()
        edit_ins.connect('activate', self.on_installment_popup_edit, installment)

        if not installment.is_paid():
          add_pay = gtk.MenuItem('Agregar pago')
          popup.append(add_pay)
          add_pay.show()
          add_pay.connect('activate', self.on_installment_popup_add_payment, installment)

        if installment.payments:
          edit_pay = gtk.MenuItem('Editar pagos')
          popup.append(edit_pay)
          edit_pay.show()
          edit_pay.connect('activate', self.on_installment_popup_edit_payments, installment)

        popup.popup(None, None, None, event.button, event.time)

      return True

  def on_installment_popup_add_payment(self, menu_item, installment):
    self.emit('add-payment', installment)

  def on_installment_popup_edit(self, menu_item, installment):
    self.emit('edit-installment', installment)

  def on_installment_popup_edit_payments(self, menu_item, installment):
    self.emit('edit-installment-payments', installment)

gobject.type_register(MembershipData)
gobject.signal_new('edit-package', \
                   MembershipData, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('add-payment', \
                   MembershipData, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-installment', \
                   MembershipData, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-installment-payments', \
                   MembershipData, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class MembershipDialog(gtk.Dialog):
  def __init__(self, membership, options):
    self.form = MembershipForm(membership, options)
    gtk.Dialog.__init__(self, self.form.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class MembershipForm(FormFor):
  def __init__(self, membership, options):
    FormFor.__init__(self, membership)

    self.fields = gtk.VBox()

    store = gtk.ListStore(int, str, gobject.TYPE_PYOBJECT)
    for o in options:
      store.append((o.id,o.name,o))
    self.klass_or_package_e = gtk.ComboBoxEntry(store,1)
    completion = gtk.EntryCompletion()
    completion.set_model(store)
    completion.set_text_column(1)
    completion.connect('match-selected', self.on_klass_match_selected)
    self.klass_or_package_e.child.set_completion(completion)
    self.klass_or_package_e.set_active(0)
    self.fields.pack_start(self.klass_or_package_e, False)

    self.add_field('info', attrs = 250)

    self.pack_start(self.fields, False)

  def get_values(self):
    return {'klass_or_package': self.get_selected_klass_or_package(),'info': self.info_e.get_text()}

  def get_tab_label(self):
    if self.object.id:
      return "Editar inscripción:\n" + self.object.klass_or_package.name
    else:
      return 'Agregar nueva inscripción'

  def get_selected_klass_or_package(self):
    m = self.klass_or_package_e.get_model()
    itr = self.klass_or_package_e.get_active_iter()
    if itr is not None:
      return m.get_value(itr,2)

  def on_klass_match_selected(self, completion, model, itr):
    klass = model.get_value(itr,0)
    klasses_model = self.klass_or_package_e.get_model()
    found = None

    if klass is not None:
      model_iter = klasses_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_klass = klasses_model.get_value(model_iter,0)
        if iter_klass is not None and iter_klass == klass:
          found = model_iter
        else:
          model_iter = klasses_model.iter_next(model_iter)

    if found is not None:
      self.klass_or_package_e.set_active_iter(found)
    else:
      self.klass_or_package_e.set_active_iter(klasses_model.get_iter_first())


class AddInstallmentsDialog(gtk.Dialog):
  def __init__(self,membership):
    self.membership = membership
    self.form = AddInstallmentsForm()
    self.form.fee_e.set_text(str(membership.get_fee()))
    gtk.Dialog.__init__(self, 'Agregar cuotas', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class AddInstallmentsForm(gtk.VBox):
  def __init__(self):
    gtk.VBox.__init__(self, True, 8)
    self.set_border_width(4)

    field = gtk.VBox()
    self.year_l = gtk.Label('Año')
    self.year_e = gtk.Entry(4)
    self.year_e.set_text(str(datetime.datetime.today().year))
    field.pack_start(self.year_l, False)
    field.pack_start(self.year_e, False)
    self.pack_start(field, False)

    field = gtk.VBox()
    self.initial_month_l = gtk.Label('Mes inicial')
    store = gtk.ListStore(int, str)
    for i,m in enumerate(_t('months')):
      store.append((i,m))
    self.initial_month_e = gtk.ComboBox(store)
    cell = gtk.CellRendererText()
    self.initial_month_e.pack_start(cell, True)
    self.initial_month_e.add_attribute(cell, 'text', 1)
    start_m = datetime.datetime.today().month
    if datetime.datetime.today().day <= 25: start_m = start_m-1
    if start_m < 0: start_m = 0
    if Settings.get_settings().installments_from > start_m: start_m = Settings.get_settings().installments_from
    self.initial_month_e.set_active(start_m)
    field.pack_start(self.initial_month_l, False)
    field.pack_start(self.initial_month_e, False)
    self.pack_start(field, False)

    field = gtk.VBox()
    self.final_month_l = gtk.Label('Mes final')
    store = gtk.ListStore(int, str)
    for i,m in enumerate(_t('months')):
      store.append((i,m))
    self.final_month_e = gtk.ComboBox(store)
    cell = gtk.CellRendererText()
    self.final_month_e.pack_start(cell, True)
    self.final_month_e.add_attribute(cell, 'text', 1)
    end_m = Settings.get_settings().installments_to
    if end_m <= start_m: end_m = start_m + 3
    if end_m > 11: end_m = 11
    self.final_month_e.set_active(end_m)
    field.pack_start(self.final_month_l, False)
    field.pack_start(self.final_month_e, False)
    self.pack_start(field, False)

    field = gtk.VBox()
    self.fee_l = gtk.Label('Precio')
    self.fee_e = gtk.Entry(4)
    field.pack_start(self.fee_l, False)
    field.pack_start(self.fee_e, False)
    self.pack_start(field, False)

  def get_selected_initial_month(self):
    itr = self.initial_month_e.get_active_iter()
    return self.initial_month_e.get_model().get_value(itr,0)

  def get_selected_final_month(self):
    itr = self.final_month_e.get_active_iter()
    return self.final_month_e.get_model().get_value(itr,0)

  def get_values(self):
    return {'year': self.year_e.get_text(), 'initial_month': self.get_selected_initial_month(), 'final_month': self.get_selected_final_month(), 'fee': self.fee_e.get_text()}

class DeleteInstallmentDialog(gtk.Dialog):
  def __init__(self, installments):
    gtk.Dialog.__init__(self, '', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.set_border_width(5)

    desc = "\n".join(map(lambda i: i.to_label(), installments))

    message = "Vas a borrar la(s) cuota(s) de:\n"+desc+"\n\n¿Estás seguro?"

    self.vbox.pack_start(gtk.Label(message), False)

    self.payments_check = gtk.CheckButton('¿Borrar también los pagos de la cuota?')

    self.vbox.pack_start(self.payments_check, False)

    self.vbox.show_all()

  def delete_payments(self):
    return self.payments_check.get_active();

class DeleteLiabilitiesDialog(gtk.Dialog):
  def __init__(self, liabilities):
    gtk.Dialog.__init__(self, '', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.set_border_width(5)

    desc = "\n".join(map(lambda l: l.to_label(), liabilities))

    message = "Vas a borrar la(s) deuda(s):\n"+desc+"\n\n¿Estás seguro?"

    self.vbox.pack_start(gtk.Label(message), False)

    self.payments_check = gtk.CheckButton('¿Borrar también los pagos de cada deuda?')

    self.vbox.pack_start(self.payments_check, False)

    self.vbox.show_all()

  def delete_payments(self):
    return self.payments_check.get_active();

class EditInstallmentDialog(gtk.Dialog):
  def __init__(self, installment):
    gtk.Dialog.__init__(self, 'Editar cuota', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.installment = installment

    self.vbox.pack_start(gtk.Label('Monto'))
    self.amount_e = gtk.Entry(10)
    self.amount_e.set_text(str(installment.amount))
    self.vbox.pack_start(self.amount_e)

    self.show_all()

  def get_amount(self):
    return self.amount_e.get_text()
