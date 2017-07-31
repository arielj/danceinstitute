#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
import datetime
import widgets
import exporter
import string
import re
from settings import Settings
from translations import _t

valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def str_to_filename(strng):
  strng = strng.replace(' ','_').lower()
  return ''.join(c for c in strng if c in valid_chars)

class PaymentsReport(gtk.VBox):
  def __init__(self, payments, movements, users, klasses, packages):
    self.payments = payments
    self.movements = movements
    self.users = users
    self.klasses = klasses
    self.packages = packages
    gtk.VBox.__init__(self, False, 5)

    content = gtk.HBox(False, 5)
    self.pack_start(content, True)

    self.from_e = gtk.Entry(10)
    self.from_e.set_text(datetime.date.today().strftime(Settings.get_settings().date_format))
    self.from_e.connect('button-press-event', self.show_calendar)
    self.from_e.set_property("editable", False)
    self.from_e.set_can_focus(False)
    self.to_e = gtk.Entry(10)
    self.to_e.set_text(datetime.date.today().strftime(Settings.get_settings().date_format))
    self.to_e.connect('button-press-event', self.show_calendar)
    self.to_e.set_property("editable", False)
    self.to_e.set_can_focus(False)
    self.done_rb = gtk.RadioButton(None, 'Hechos')
    self.received_rb = gtk.RadioButton(self.done_rb, 'Recibidos')
    self.received_rb.set_active(True)

    users_model = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    users_model.append((None,'Todos los alumnos'))
    for user in self.users:
      users_model.append((user, user.to_label()))

    self.user = gtk.ComboBoxEntry(users_model,1)
    completion = gtk.EntryCompletion()
    completion.set_model(users_model)
    completion.set_text_column(1)
    completion.connect('match-selected', self.on_user_match_selected)
    self.user.child.set_completion(completion)
    self.user.set_active(0)

    k_or_p_model = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    k_or_p_model.append((None,'Todas las clases o paquetes'))
    for klass in self.klasses:
      k_or_p_model.append((klass, klass.name))
    for package in self.packages:
      k_or_p_model.append((package, package.name))

    self.klass_or_package = gtk.ComboBoxEntry(k_or_p_model,1)
    completion = gtk.EntryCompletion()
    completion.set_model(k_or_p_model)
    completion.set_text_column(1)
    completion.connect('match-selected', self.on_klass_match_selected)
    self.klass_or_package.child.set_completion(completion)
    self.klass_or_package.set_active(0)

    self.group_l = gtk.Label('Grupo')
    self.group_e = gtk.Entry(255)

    self.receipt_l = gtk.Label('Recibo')
    self.receipt_e = gtk.Entry(255)

    self.filter_l = gtk.Label('Buscar')
    self.filter_e = gtk.Entry(255)

    self.filter = gtk.Button('Buscar')

    self.include_inactive = gtk.CheckButton('Incluir usuarios inactivos')
    self.include_inactive.set_active(True)

    self.form = gtk.VBox(False, 5)
    label = gtk.Label()
    label.set_markup("<big><b>Filtrar:</b></big>");
    self.form.pack_start(label, False)
    self.form.pack_start(gtk.Label('Desde:'), False)
    self.form.pack_start(self.from_e, False)
    self.form.pack_start(gtk.Label('Hasta:'), False)
    self.form.pack_start(self.to_e, False)
    self.form.pack_start(self.done_rb, False)
    self.form.pack_start(self.received_rb, False)
    self.form.pack_start(self.user, False)
    self.form.pack_start(self.klass_or_package, False)
    self.form.pack_start(self.include_inactive, False)
    self.form.pack_start(self.group_l, False)
    self.form.pack_start(self.group_e, False)
    self.form.pack_start(self.receipt_l, False)
    self.form.pack_start(self.receipt_e, False)
    self.form.pack_start(self.filter_l, False)
    self.form.pack_start(self.filter_e, False)
    self.form.pack_start(self.filter, False)

    content.pack_start(self.form, False)

    self.payments_wrapper = gtk.VBox()

    self.headings = ['Alumno/Profesor', 'Fecha', 'Monto', 'Detalle', 'Recibo N°']

    self.list = PaymentsList(payments, self.headings)
    self.list.connect('row-activated', self.on_row_activated)
    self.list.renderer_checkbox.connect('toggled', self.on_toggle_payment)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)

    self.payments_wrapper.pack_start(self.scroll, True)

    total_hbox = gtk.HBox()
    self.total_label = gtk.Label('Total: $'+self.sum_total(payments))
    total_hbox.pack_start(self.total_label, False)
    self.payments_wrapper.pack_start(total_hbox, False)

    content.pack_start(self.payments_wrapper, True)

    self.movements_wrapper = gtk.VBox()

    self.movement_headings = ['Detalle', 'Fecha', 'Monto']

    self.list_movements = MovementsList(movements, self.movement_headings, to_row = self.movement_to_row)

    self.scroll_movements = gtk.ScrolledWindow()
    self.scroll_movements.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll_movements.add(self.list_movements)

    self.movements_wrapper.pack_start(self.scroll_movements, True)

    total_hbox = gtk.HBox()
    self.total_label_movements = gtk.Label('Total: $'+self.sum_total(movements))
    total_hbox.pack_start(self.total_label_movements, False)
    self.movements_wrapper.pack_start(total_hbox, False)

    content.pack_start(self.movements_wrapper, True)

    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.print_b = gtk.Button('Imprimir')
    self.print_b.set_sensitive(False)
    self.print_b.connect('clicked', self.on_print_b_clicked)
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
    self.actions.pack_start(self.print_b, False)
    self.pack_start(self.actions, False)

    self.show_all()

  def get_tab_label(self):
    return "Pagos"

  def to_html(self):
    done_or_received = 'hechos' if self.done_rb.get_active() else 'recibidos'
    h1_content = "Pagos %s entre %s y %s" % (done_or_received, self.get_from().strftime(Settings.get_settings().date_format), self.get_to().strftime(Settings.get_settings().date_format))

    u = self.get_selected_user()
    k = self.get_selected_klass_or_package()
    if u is not None: h1_content += ' del alumno %s' % u.to_label()
    if k is not None: h1_content += ' de la clase %s' % k.name

    title = '<h1>%s</h1>' % h1_content
    rows = map(lambda p: self.values_for_html(p), self.payments)
    total = sum(map(lambda p: p.amount, self.payments))
    caption = 'Total: <b>$'+str(total)+'</b>'

    return exporter.html_wrapper(title+exporter.html_table(self.headings,rows,caption))

  def values_for_html(self,p):
    return [p.user.to_label(),p.date.strftime(Settings.get_settings().date_format),'$'+str(p.amount),str(p.description), str(p.receipt_number or '')]

  def m_values_for_html(self,m):
    return [m.description,str(m.date),'$'+str(m.amount)]

  def to_csv(self):
    st = ';'.join(self.headings)+"\n"
    st += "\n".join(map(lambda p: ';'.join(self.values_for_html(p)), self.payments))
    st += "\n\n"
    st += ';'.join(self.movement_headings)+"\n"
    st += "\n".join(map(lambda m: ';'.join(self.m_values_for_html(m)), self.movements))
    return st

  def csv_filename(self):
    done_or_received = 'hechos' if self.done_rb.get_active() else 'recibidos'
    name = 'pagos_%s_entre_%s_y_%s' % (done_or_received, self.get_from().strftime(Settings.get_settings().date_format), self.get_to().strftime(Settings.get_settings().date_format))

    u = self.get_selected_user()
    k = self.get_selected_klass_or_package()
    if u is not None: name += '_alumno_%s' % str_to_filename(u.to_label())
    if k is not None: name += '_clase_%s' % str_to_filename(k.name)

    return name+'.csv'

  def get_from(self):
    return datetime.datetime.strptime(self.from_e.get_text(),Settings.get_settings().date_format)

  def get_to(self):
    return datetime.datetime.strptime(self.to_e.get_text(),Settings.get_settings().date_format)

  def get_filter(self):
    return self.filter_e.get_text()

  def get_done_or_received(self):
    return self.done_rb.get_active()

  def should_include_inactive(self):
    return self.include_inactive.get_active()

  def get_selected_user(self):
    itr = self.user.get_active_iter()
    if itr is not None:
      return self.user.get_model().get_value(itr,0)
    else:
      return None

  def get_selected_klass_or_package(self):
    itr = self.klass_or_package.get_active_iter()
    if itr is not None:
      return self.klass_or_package.get_model().get_value(itr,0)
    else:
      return None

  def get_group(self):
    return self.group_e.get_text()

  def get_receipt_number(self):
    return self.receipt_e.get_text()

  def update(self, payments = None, movements = None):
    if payments is not None:
      self.payments = payments
    self.list.update(self.payments)
    self.total_label.set_text('Total: $'+self.sum_total(self.payments))

    if movements is not None:
      self.movements = movements
    self.list_movements.update(self.movements)
    self.total_label_movements.set_text('Total: $'+self.sum_total(self.movements))

  def sum_total(self, payments):
    return str(sum(map(lambda p: p.amount, payments)))

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    payment = model.get_value(itr, 0)
    self.emit('student-edit', payment.user_id, payment)

  def on_user_match_selected(self, completion, model, itr):
    user = model.get_value(itr,0)
    users_model = self.user.get_model()
    found = None

    if user is not None:
      model_iter = users_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_user = users_model.get_value(model_iter,0)
        if iter_user is not None and iter_user.id == user.id:
          found = model_iter
        else:
          model_iter = users_model.iter_next(model_iter)

    if found is not None:
      self.user.set_active_iter(found)
    else:
      self.user.set_active_iter(users_model.get_iter_first())

  def on_klass_match_selected(self, completion, model, itr):
    k_or_p = model.get_value(itr,0)
    k_or_p_model = self.klass_or_package.get_model()
    found = None

    if k_or_p is not None:
      model_iter = k_or_p_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_k_or_p = k_or_p_model.get_value(model_iter,0)
        if iter_k_or_p is not None and iter_k_or_p.id == k_or_p.id and iter_k_or_p.__class__ == k_or_p._class:
          found = model_iter
        else:
          model_iter = k_or_p_model.iter_next(model_iter)

    if found is not None:
      self.klass_or_package.set_active_iter(found)
    else:
      self.klass_or_package.set_active_iter(k_or_p_model.get_iter_first())

  def payments_to_print(self):
    selected = []

    store = self.list.store
    itr = store.get_iter_first()
    while itr is not None:
      if store.get_value(itr,6): selected.append(store.get_value(itr,0))
      itr = store.iter_next(itr)

    return selected

  def on_toggle_payment(self, renderer, path):
    store = self.list.store
    itr = store.get_iter(path)
    current_val = store.get_value(itr,6)
    store.set(itr, 6, not current_val)
    self.print_b.set_sensitive(self.payments_to_print() != [])

  def on_print_b_clicked(self, button):
    self.emit('print-payments', self.payments_to_print())

  def movement_to_row(self, movement):
    return (movement,str(movement.description),str(movement.date),str(movement.amount))

gobject.type_register(PaymentsReport)
gobject.signal_new('student-edit', \
                   PaymentsReport, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
gobject.signal_new('print-payments', \
                   PaymentsReport, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class PaymentsList(gtk.TreeView):
  def __init__(self, payments, headings, to_row = None, printable = True):
    self.printable = printable
    if to_row is not None:
      self.to_row = to_row
    else:
      self.to_row = self.default_to_row

    self.create_store(payments)

    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

    if printable:
      self.renderer_checkbox = gtk.CellRendererToggle()
      self.append_column(gtk.TreeViewColumn("Impr?", self.renderer_checkbox, active = 6))

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, payments):
    # payment, user name, date, amount, description, receipt_number, print
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str,bool)
    self.update(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)

  def set_model(self, payments):
    for p in payments:
      self.store.append(self.to_row(p))

  def default_to_row(self, p):
    return (p,p.user.to_label(),p.date.strftime(Settings.get_settings().date_format),'$'+str(p.amount), p.description, str(p.receipt_number or ''), False)

class KlassStudents(gtk.VBox):
  def __init__(self, klass, students = {}):
    self.klass = klass
    self.students = students
    gtk.VBox.__init__(self)




class DailyCashReport(gtk.VBox):
  def __init__(self, payments, movements):
    self.movements = movements
    self.payments = payments
    gtk.VBox.__init__(self, False, 5)

    content = gtk.HBox()
    self.pack_start(content, True)

    self.date = gtk.Entry(10)
    self.date.set_text(datetime.datetime.today().strftime(Settings.get_settings().date_format))
    self.date.connect('button-press-event', self.show_calendar)
    self.date.set_property("editable", False)
    self.date.set_can_focus(False)
    self.filter = gtk.Button('Buscar')

    self.desc_filter = gtk.Entry(100)
    self.desc_filter.connect('changed', self.on_desc_filter_changed)

    self.form = gtk.VBox(False, 5)
    label = gtk.Label()
    label.set_markup('<big><b>Filtrar:</b></big>')
    self.form.pack_start(label, False)
    self.form.pack_start(gtk.Label('Fecha:'), False)
    self.form.pack_start(self.date, False)
    self.form.pack_start(gtk.Label('Buscar:'), False)
    self.form.pack_start(self.desc_filter, False)
    self.form.pack_start(self.filter, False)

    self.since_closer = gtk.CheckButton('Sólo desde cierre')

    self.mark_closers = gtk.Button('Marcar cierre')

    self.form.pack_start(self.since_closer, False)
    self.form.pack_start(self.mark_closers, False)
    content.pack_start(self.form, False)

    self.tables = gtk.HBox(True, 6)
    p_table = gtk.VBox()
    self.payment_headings = ['Detalle', 'Entrada', 'Salida', 'Alumno/Profesor']

    self.p_list = PaymentsList(payments, self.payment_headings, self.p_to_row, False)
    self.p_list.connect('row-activated', self.on_payment_row_activated)

    self.p_scroll = gtk.ScrolledWindow()
    self.p_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.p_scroll.add(self.p_list)

    p_table.pack_start(self.p_scroll, True)

    total_p_hbox = gtk.HBox()
    self.total_p_label = gtk.Label(self.payment_totals(payments))
    total_p_hbox.pack_start(self.total_p_label, False)
    p_table.pack_start(total_p_hbox, False)
    self.tables.pack_start(p_table)

    m_table = gtk.VBox()
    self.movement_headings = ['Detalle', 'Entrada', 'Salida']

    self.m_list = MovementsList(movements, self.movement_headings, self.m_to_row)

    self.m_scroll = gtk.ScrolledWindow()
    self.m_scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.m_scroll.add(self.m_list)

    m_table.pack_start(self.m_scroll, True)

    total_m_hbox = gtk.HBox()
    self.total_m_label = gtk.Label(self.movement_totals(movements))
    total_m_hbox.pack_start(self.total_m_label, False)
    m_table.pack_start(total_m_hbox, False)

    self.tables.pack_start(m_table)

    content.pack_start(self.tables)

    total_hbox = gtk.HBox()
    self.total_label = gtk.Label(self.totals(payments,movements))

    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
    self.actions.pack_start(gtk.HBox(), True)
    self.actions.pack_start(self.total_label, False)
    self.pack_start(self.actions, False)

    self.show_all()

  def get_tab_label(self):
    return "Caja diaria"

  def to_html(self):
    title = "<h1>Movimientos del día %s</h1>" % self.get_date().strftime(Settings.get_settings().date_format)

    rows = map(lambda p: list(self.p_to_row(p))[1:-1], self.payments)
    caption = self.payment_totals(self.payments)

    p_table = exporter.html_table(self.payment_headings,rows,caption)

    rows = map(lambda m: list(self.m_to_row(m))[1:], self.movements)
    caption = self.movement_totals(self.movements)

    m_table = exporter.html_table(self.movement_headings,rows,caption)

    return exporter.html_wrapper(title+"<div style='float:left;width:49%;min_width:400px;'>Pagos:"+p_table+"</div><div style='float:right;width:49%;min_width:400px;'>Movimientos:"+m_table+"</div><div class='clear'></div>")

  def p_to_row(self,p):
    amount_in = p.amount if not p.done else ''
    amount_out = p.amount if p.done else ''
    return (p,str(p.description),str(amount_in),str(amount_out),p.user.to_label(),str(p.receipt_number or ''), False)

  def m_to_row(self,m):
    amount_in = m.amount if m.is_incoming() else ''
    amount_out = m.amount if m.is_outgoing() else ''
    return (m,str(m.description),str(amount_in),str(amount_out))

  def to_csv(self):
    st = ';'.join(self.payment_headings)+"\n"
    st += "\n".join(map(lambda p: ';'.join(list(self.p_to_row(p))[1:]), self.get_filtered_payments()))
    st += "\n"
    st += "\n".join(map(lambda m: ';'.join(list(self.m_to_row(m))[1:]), self.get_filtered_movements()))
    return st

  def csv_filename(self):
    return 'movimientos_%s.csv' % self.get_date().strftime(Settings.get_settings().date_format)

  def get_date(self):
    return datetime.datetime.strptime(self.date.get_text(),Settings.get_settings().date_format)

  def get_desc_filter(self):
    return self.desc_filter.get_text()

  def update(self, payments = None, movements = None):
    if payments is not None:
      self.payments = payments
    f_p = self.get_filtered_payments()
    self.p_list.update(f_p)
    self.total_p_label.set_text(self.payment_totals(f_p))

    if movements is not None:
      self.movements = movements
    f_m = self.get_filtered_movements()
    self.m_list.update(f_m)
    self.total_m_label.set_text(self.movement_totals(f_m))
    self.total_label.set_text(self.totals(f_p, f_m))

  def _payment_totals(self, payments):
    total_in = 0
    total_out = 0
    for p in payments:
      if p.done:
        total_out += p.amount
      else:
        total_in += p.amount
    return [total_in, total_out]


  def payment_totals(self, payments):
    total_in, total_out = self._payment_totals(payments)
    return "Entradas: $" + str(total_in) + " ; Salidas: $" + str(total_out)

  def _movement_totals(self, movements):
    total_in = 0
    total_out = 0
    for m in movements:
      if m.is_outgoing():
        total_out += m.amount
      else:
        total_in += m.amount
    return [total_in, total_out]

  def movement_totals(self, movements):
    total_in, total_out = self._movement_totals(movements)
    return "Entradas: $" + str(total_in) + " ; Salidas: $" + str(total_out)

  def totals(self, payments, movements):
    total_in_p, total_out_p = self._payment_totals(payments)
    total_in_m, total_out_m = self._movement_totals(movements)
    return "Entradas: $" + str(total_in_p+total_in_m) + " ; Salidas: $" + str(total_out_p+total_out_m) + " ; Total: $" + str(total_in_p+total_in_m - total_out_p -total_out_m)


  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()

  def on_desc_filter_changed(self, entry):
    self.update()

  def get_filtered_movements(self):
    ms = []
    for m in self.movements:
      if re.search(self.get_desc_filter(), self.m_to_row(m)[1], flags=re.I): ms.append(m)
    return ms

  def get_filtered_payments(self):
    ps = []
    for p in self.payments:
      if re.search(self.get_desc_filter(), self.p_to_row(p)[1], flags=re.I): ps.append(p)
    return ps

  def on_payment_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    payment = model.get_value(itr, 0)
    self.emit('student-edit', payment.user_id, payment)

gobject.type_register(DailyCashReport)
gobject.signal_new('student-edit', \
                   DailyCashReport, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))


class MovementsList(gtk.TreeView):
  def __init__(self, movements, headings, to_row = None, printable = False):
    if to_row is not None:
      self.to_row = to_row
    else:
      self.to_row = self.default_to_row

    self.create_store(movements)

    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

    if printable:
      self.renderer_checkbox = gtk.CellRendererToggle()
      self.append_column(gtk.TreeViewColumn("Impr?", self.renderer_checkbox, active = 6))

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, movements):
    # movement, date, amount, description
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str)
    self.update(movements)

  def update(self, movements):
    self.store.clear()
    self.set_model(movements)

  def set_model(self, movements):
    for m in movements:
      self.store.append(self.to_row(m))

  def default_to_row(self, m):
    return (m,str(m.date),str(m.amount), m.description)



class InstallmentsReport(gtk.VBox):
  def __init__(self, installments, klasses):
    self.installments = installments
    gtk.VBox.__init__(self, False, 5)

    content = gtk.HBox()
    self.pack_start(content, True)

    klasses_model = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    klasses_model.append((None,'Todas'))
    for klass in klasses:
      klasses_model.append((klass, klass.name))

    self.klass = gtk.ComboBoxEntry(klasses_model,1)
    completion = gtk.EntryCompletion()
    completion.set_model(klasses_model)
    completion.set_text_column(1)
    completion.connect('match-selected', self.on_klass_match_selected)
    self.klass.child.set_completion(completion)
    self.klass.set_active(0)

    self.year_e = gtk.Entry(4)

    store = gtk.ListStore(int, str)
    store.append((-1,''))
    for i,m in enumerate(_t('months')):
      store.append((i,m))
    self.month_e = gtk.ComboBox(store)
    cell = gtk.CellRendererText()
    self.month_e.pack_start(cell, True)
    self.month_e.add_attribute(cell, 'text', 1)

    self.only_active = gtk.CheckButton('Mostrar sólo de usuarios activos')

    self.include_paid = gtk.CheckButton('Incluir cuotas pagadas')

    self.only_overdue = gtk.CheckButton('Mostrar sólo cuotas con recargo')

    self.filter = gtk.Button('Buscar')

    self.form = gtk.VBox(False, 5)
    label = gtk.Label()
    label.set_markup('<big><b>Filtrar:</b></big>')
    self.form.pack_start(label, False)
    self.form.pack_start(gtk.Label('Clase:'), False)
    self.form.pack_start(self.klass, False)
    self.form.pack_start(gtk.Label('Año:'), False)
    self.form.pack_start(self.year_e, False)
    self.form.pack_start(gtk.Label('Mes:'), False)
    self.form.pack_start(self.month_e, False)

    self.form.pack_start(self.only_active, False)
    self.form.pack_start(self.include_paid, False)
    self.form.pack_start(self.only_overdue, False)
    self.form.pack_start(self.filter, False)

    content.pack_start(self.form, False)

    self.headings = ['Alumno', 'Año', 'Mes', 'Clase', 'A pagar']

    self.list = InstallmentsList(installments, self.headings)
    self.list.connect('row-activated', self.on_row_activated)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)

    content.pack_start(self.scroll, True)

    total_hbox = gtk.HBox()
    self.total_label = gtk.Label('Total: $'+self.sum_total(installments))
    total_hbox.pack_start(self.total_label, False)
    self.pack_start(total_hbox, False)

    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
    self.pack_start(self.actions, False)

    self.show_all()

  def get_tab_label(self):
    return "Cuotas"

  def sum_total(self, installments):
    return str(sum(map(lambda i: i.to_pay(), installments)))

  def to_html(self):
    h1_content = "Cuotas"
    k = self.get_selected_klass()
    if k is not None: h1_content += ' de la clase %s' % k.name

    title = "<h1>%s</h1>" % h1_content
    rows = map(lambda i: self.values_for_html(i), self.installments)

    return exporter.html_wrapper(title+exporter.html_table(self.headings,rows))

  def to_csv(self):
    st = ';'.join(self.headings)+"\n"
    st += "\n".join(map(lambda i: ';'.join(self.values_for_html(i)), self.installments))
    return st

  def csv_filename(self):
    f = 'cuotas'
    k = self.get_selected_klass()
    if k is not None: f += '_clase_%s' % str_to_filename(k.name)
    return f+'.csv'

  def values_for_html(self,i):
    return [i.membership.student.to_label(),str(i.year),i.month_name(),i.membership.klass_or_package.name, str(i.to_pay())]

  def update(self, installments = None):
    if installments is not None:
      self.installments = installments
    self.list.update(self.installments)
    self.total_label.set_text('Total: $'+self.sum_total(self.installments))

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    installment = model.get_value(itr, 0)
    self.emit('student-edit', installment.membership.student_id, installment)

  def get_selected_klass(self):
    itr = self.klass.get_active_iter()
    if itr is not None:
      return self.klass.get_model().get_value(itr,0)
    else:
      return None

  def get_selected_month(self):
    itr = self.month_e.get_active_iter()
    if itr is not None:
      m = self.month_e.get_model().get_value(itr,0)
      return m if m != -1 else None
    else:
      return None

  def get_year(self):
    return self.year_e.get_text()

  def is_only_active(self):
    return self.only_active.get_active()

  def is_only_overdue(self):
    return self.only_overdue.get_active()

  def on_klass_match_selected(self, completion, model, itr):
    klass = model.get_value(itr,0)
    klasses_model = self.klass.get_model()
    found = None

    if klass is not None:
      model_iter = klasses_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_klass = klasses_model.get_value(model_iter,0)
        if iter_klass is not None and iter_klass.id == klass.id:
          found = model_iter
        else:
          model_iter = klasses_model.iter_next(model_iter)

    if found is not None:
      self.klass.set_active_iter(found)
    else:
      self.klass.set_active_iter(klasses_model.get_iter_first())

gobject.type_register(InstallmentsReport)
gobject.signal_new('student-edit', \
                   InstallmentsReport, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))

class InstallmentsList(gtk.TreeView):
  def __init__(self, installments, headings, to_row = None):
    if to_row is not None:
      self.to_row = to_row
    else:
      self.to_row = self.default_to_row

    self.create_store(installments)

    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, installments):
    # installments, user name, year, month name, klass
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str)
    self.update(installments)

  def update(self, installments):
    self.store.clear()
    self.set_model(installments)

  def set_model(self, installments):
    for i in installments:
      if i.membership: self.store.append(self.to_row(i))

  def default_to_row(self, i):
    return (i,i.membership.student.to_label(),str(i.year),i.month_name(), i.membership.klass_or_package.name, i.to_pay())


class Debts(gtk.VBox):
  def __init__(self, debts):
    self.debts = debts
    gtk.VBox.__init__(self, False, 5)

    content = gtk.HBox()
    self.pack_start(content, True)

    self.filter = gtk.Button('Buscar')

    self.filter_l = gtk.Label('Buscar:')
    self.filter_e = gtk.Entry(100)

    self.include_inactive = gtk.CheckButton('Incluir usuarios inactivos')

    self.form = gtk.VBox(False, 5)
    label = gtk.Label()
    label.set_markup('<big><b>Filtrar:</b></big>')
    self.form.pack_start(label, False)
    self.form.pack_start(self.filter_l, False)
    self.form.pack_start(self.filter_e, False)
    self.form.pack_start(self.filter, False)

    content.pack_start(self.form, False)

    self.headings = ['Alumno', 'Detalle', 'Monto']

    self.list = DebtsList(debts, self.headings)
    self.list.connect('row-activated', self.on_row_activated)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)

    content.pack_start(self.scroll, True)

    total_hbox = gtk.HBox()
    self.total_label = gtk.Label('Total: $'+self.sum_total(debts))
    total_hbox.pack_start(self.total_label, False)
    self.pack_start(total_hbox, False)

    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
    self.pack_start(self.actions, False)

    self.show_all()

  def get_tab_label(self):
    return "Deudas"

  def sum_total(self, debts):
    return str(sum(map(lambda d: d.to_pay(), debts)))

  def to_html(self):
    h1_content = "Deudas"
    #k = self.get_selected_klass()
    #if k is not None: h1_content += ' de la clase %s' % k.name

    title = "<h1>%s</h1>" % h1_content
    rows = map(lambda d: self.values_for_html(d), self.debts)

    return exporter.html_wrapper(title+exporter.html_table(self.headings,rows))

  def to_csv(self):
    st = ';'.join(self.headings)+"\n"
    st += "\n".join(map(lambda d: ';'.join(self.values_for_html(d)), self.debts))
    return st

  def csv_filename(self):
    f = 'deudas'
    k = self.get_selected_klass()
    if k is not None: f += '_clase_%s' % str_to_filename(k.name)
    return f+'.csv'

  def values_for_html(self,d):
    return [d.user.to_label(), d.description, str(d.to_pay())]

  def update(self, debts = None):
    if debts is not None:
      self.debts = debts
    self.list.update(self.debts)
    self.total_label.set_text('Total: $'+self.sum_total(debts))

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    liability = model.get_value(itr, 0)
    self.emit('student-edit', liability.user_id)

  def get_filter(self):
    return self.filter_e.get_text()

  def get_selected_klass(self):
    itr = self.klass.get_active_iter()
    if itr is not None:
      return self.klass.get_model().get_value(itr,0)
    else:
      return None

  def should_include_inactive_users(self):
    return self.include_inactive.get_active()

  def on_klass_match_selected(self, completion, model, itr):
    klass = model.get_value(itr,0)
    klasses_model = self.klass.get_model()
    found = None

    if klass is not None:
      model_iter = klasses_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_klass = klasses_model.get_value(model_iter,0)
        if iter_klass is not None and iter_klass.id == klass.id:
          found = model_iter
        else:
          model_iter = klasses_model.iter_next(model_iter)

    if found is not None:
      self.klass.set_active_iter(found)
    else:
      self.klass.set_active_iter(klasses_model.get_iter_first())

gobject.type_register(Debts)
gobject.signal_new('student-edit', \
                   Debts, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class DebtsList(gtk.TreeView):
  def __init__(self, debts, headings, to_row = None):
    if to_row is not None:
      self.to_row = to_row
    else:
      self.to_row = self.default_to_row

    self.create_store(debts)

    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, debts):
    # liability, user name, description, amount
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str)
    self.update(debts)

  def update(self, debts):
    self.store.clear()
    self.set_model(debts)

  def set_model(self, debts):
    for d in debts: self.store.append(self.to_row(d))

  def default_to_row(self, d):
    return (d,d.user.to_label(), d.description, d.to_pay())


class Receipts(gtk.VBox):
  def __init__(self):
    self.payments = []
    gtk.VBox.__init__(self, False, 5)

    content = gtk.HBox()
    self.pack_start(content, True)

    self.filter = gtk.Button('Buscar')

    self.filter_l = gtk.Label('Número:')
    self.filter_e = gtk.Entry(100)

    self.form = gtk.VBox(False, 5)
    label = gtk.Label()
    label.set_markup('<big><b>Filtrar:</b></big>')
    self.form.pack_start(label, False)
    self.form.pack_start(self.filter_l, False)
    self.form.pack_start(self.filter_e, False)
    self.form.pack_start(self.filter, False)

    content.pack_start(self.form, False)

    self.headings = ['Alumno/Profesor', 'Fecha', 'Monto', 'Detalle', 'Recibo N°']

    self.list = PaymentsList(self.payments, self.headings, None, False)
    self.list.connect('row-activated', self.on_row_activated)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)

    content.pack_start(self.scroll, True)

    total_hbox = gtk.HBox()
    self.total_label = gtk.Label('Total: $'+self.sum_total(self.payments))
    total_hbox.pack_start(self.total_label, False)
    self.pack_start(total_hbox, False)

    self.actions = gtk.HBox(False, 5)
    self.reprint = gtk.Button('Volver a imprimir')
    self.reprint.set_sensitive(False)
    self.actions.pack_start(self.reprint, False)
    self.pack_start(self.actions, False)

    self.show_all()

  def get_tab_label(self):
    return "Recibos"

  def sum_total(self, payments):
    return str(sum(map(lambda p: p.amount, payments)))

  def update(self, payments = None):
    if payments is not None:
      self.payments = payments
    self.list.update(self.payments)
    self.total_label.set_text('Total: $'+self.sum_total(payments))
    self.reprint.set_sensitive(len(self.payments) > 0)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    payment = model.get_value(itr, 0)
    self.emit('student-edit', payment.user_id)

  def receipt_value(self):
    return self.filter_e.get_text()

gobject.type_register(Receipts)
gobject.signal_new('student-edit', \
                   Receipts, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))


class StudentsHoursReport(gtk.VBox):
  def __init__(self, students, klasses):
    gtk.VBox.__init__(self, False, 5)


    content = gtk.HBox()
    self.pack_start(content, True)

    self.students = students
    self.klasses = klasses
    self.klass_index = {}
    self.headings = ['Alumno/a']

    list_store_fields = [int, str] #user_id, user label
    i = 2
    for k in klasses:
      self.klass_index[k.id] = i
      try:
        n = k.get_full_name()
        idx = n.find('(')
        n = n[:idx]+"\n"+n[idx:]
        self.headings.append(n)
      except IndexError:
        self.headings.append(k.name)
      list_store_fields.append(str) #klass hours
      i += 1
    list_store_fields.append(str) #total hours
    self.headings.append("Total")

    store = gtk.ListStore(*tuple(list_store_fields))

    self.list = StudentsHoursList(students, self.headings, self.klass_index)
    #self.list.connect('row-activated', self.on_row_activated)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)

    content.pack_start(self.scroll, True)

    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
    self.pack_start(self.actions, False)

    self.show_all()

  def get_tab_label(self):
    return "Alumnos (Horas/Clase)"

  def to_html(self):
    h1_content = "Alumnos (Horas/Clase)"

    title = "<h1>%s</h1>" % h1_content
    rows = map(lambda i: self.values_for_html(i), self.students)

    return exporter.html_wrapper(title+exporter.html_table(self.headings, rows))

  def to_csv(self):
    st = '"'+'";"'.join(self.headings)+'"'+"\n"
    st += "\n".join(map(lambda i: ';'.join(self.values_for_html(i)), self.students))
    return st

  def csv_filename(self):
    f = 'alumnos: horas por clase'
    return f+'.csv'

  def values_for_html(self, s):
    row = [s.to_label()]
    for k in self.klass_index: row.append('')
    total = 0

    for m in s.memberships.where('inactive', False):
      for k in m.klasses():
        row[self.klass_index[k.id]-1] = str(k.get_duration())
        total += k.get_duration()

    row.append(str(total))
    return row

class StudentsHoursList(gtk.TreeView):
  def __init__(self, students, headings, indexes):
    self.students = students
    self.indexes = indexes
    self.create_store(students)

    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, students):
    fields = [int, str] #user_id, user label
    for k in self.indexes: fields.append(str) #klass hours
    fields.append(str) #total hours
    self.store = gtk.ListStore(*tuple(fields))
    self.update(students)

  def update(self, students):
    self.store.clear()
    self.students = students
    self.set_model()

  def set_model(self):
    for s in self.students: self.store.append(self.to_row(s))

  def to_row(self, student):
    s = student
    row = [s.id, s.to_label()]

    for k in self.indexes: row.append('')
    total = 0

    for m in s.memberships.where('inactive', False):
      for k in m.klasses():
        row[self.indexes[k.id]] = str(k.get_duration())
        total += k.get_duration()

    row.append(str(total))

    return tuple(row)
