#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
import datetime
import widgets
import exporter
import string
from settings import Settings

valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def str_to_filename(strng):
  strng = strng.replace(' ','_').lower()
  return ''.join(c for c in strng if c in valid_chars)

class PaymentsReport(gtk.VBox):
  def __init__(self, payments, users, klasses, packages):
    self.payments = payments
    self.users = users
    self.klasses = klasses
    self.packages = packages
    gtk.VBox.__init__(self, False, 5)
    
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

    self.filter = gtk.Button('Buscar')
    
    self.form = gtk.HBox(False, 5)
    self.form.pack_start(gtk.Label('Desde:'), False)
    self.form.pack_start(self.from_e, False)
    self.form.pack_start(gtk.Label('Hasta:'), False)
    self.form.pack_start(self.to_e, False)
    self.form.pack_start(self.done_rb, False)
    self.form.pack_start(self.received_rb, False)
    self.form.pack_start(self.user, False)
    self.form.pack_start(self.klass_or_package, False)
    self.form.pack_start(self.filter, False)
    
    self.pack_start(self.form, False)
    
    self.headings = ['Alumno/Profesor', 'Fecha', 'Monto', 'Detalle', 'Recibo N°']
    
    self.list = PaymentsList(payments, self.headings)
    self.list.connect('row-activated', self.on_row_activated)
    
    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)
    
    self.pack_start(self.scroll, True)
    
    total_hbox = gtk.HBox()
    self.total_label = gtk.Label('Total: $'+self.sum_total(payments))
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

  def to_csv(self):
    st = ';'.join(self.headings)+"\n"
    st += "\n".join(map(lambda p: ';'.join(self.values_for_html(p)), self.payments))
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

  def get_done_or_received(self):
    return self.done_rb.get_active()

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

  def update(self, payments = None):
    if payments is not None:
      self.payments = payments
    self.list.update(self.payments)
    self.total_label.set_text('Total: $'+self.sum_total(payments))

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
    self.emit('student-edit', payment.user_id)

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

gobject.type_register(PaymentsReport)
gobject.signal_new('student-edit', \
                   PaymentsReport, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class PaymentsList(gtk.TreeView):
  def __init__(self, payments, headings, to_row = None):
    if to_row is not None:
      self.to_row = to_row
    else:
      self.to_row = self.default_to_row

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
    # payment, user name, date, amount, description, receipt_number
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str)
    self.update(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)
  
  def set_model(self, payments):
    for p in payments:
      self.store.append(self.to_row(p))

  def default_to_row(self, p):
    return (p,p.user.to_label(),p.date.strftime(Settings.get_settings().date_format),'$'+str(p.amount), p.description, str(p.receipt_number or ''))



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

    self.date = gtk.Entry(10)
    self.date.set_text(datetime.datetime.today().strftime(Settings.get_settings().date_format))
    self.date.connect('button-press-event', self.show_calendar)
    self.date.set_property("editable", False)
    self.date.set_can_focus(False)
    self.filter = gtk.Button('Buscar')
    
    self.form = gtk.HBox(False, 5)
    self.form.pack_start(gtk.Label('Fecha:'), False)
    self.form.pack_start(self.date, False)
    self.form.pack_start(self.filter, False)
    
    self.pack_start(self.form, False)
    
    self.tables = gtk.HBox(True, 6)
    p_table = gtk.VBox()
    self.payment_headings = ['Detalle', 'Entrada', 'Salida', 'Alumno/Profesor']
    
    self.p_list = PaymentsList(payments, self.payment_headings, self.p_to_row)
    
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

    self.pack_start(self.tables)

    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
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
    return (p,str(p.description),str(amount_in),str(amount_out),p.user.to_label(),str(p.receipt_number or ''))

  def m_to_row(self,m):
    amount_in = m.amount if m.is_incoming() else ''
    amount_out = m.amount if m.is_outgoing() else ''
    return (m,str(m.description),str(amount_in),str(amount_out))

  def to_csv(self):
    st = ';'.join(self.payment_headings)+"\n"
    st += "\n".join(map(lambda p: ';'.join(list(self.p_to_row(p))[1:]), self.payments))
    st += "\n"
    st += "\n".join(map(lambda m: ';'.join(list(self.m_to_row(m))[1:]), self.movements))
    return st

  def csv_filename(self):
    return 'movimientos_%s.csv' % self.get_date().strftime(Settings.get_settings().date_format)

  def get_date(self):
    return datetime.datetime.strptime(self.date.get_text(),Settings.get_settings().date_format)

  def update(self, payments = None, movements = None):
    if payments is not None:
      self.payments = payments
    self.p_list.update(self.payments)
    self.total_p_label.set_text(self.payment_totals(self.payments))
    if movements is not None:
      self.movements = movements
    self.m_list.update(self.movements)
    self.total_m_label.set_text(self.movement_totals(self.movements))

  def payment_totals(self, payments):
    total_in = 0
    total_out = 0
    for p in payments:
      if p.done:
        total_out += p.amount
      else:
        total_in += p.amount
    return "Entradas: $" + str(total_in) + " ; Salidas: $" + str(total_out)
  
  def movement_totals(self, movements):
    total_in = 0
    total_out = 0
    for m in movements:
      if m.is_outgoing():
        total_out += m.amount
      else:
        total_in += m.amount
    return "Entradas: $" + str(total_in) + " ; Salidas: $" + str(total_out)

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()

class MovementsList(gtk.TreeView):
  def __init__(self, movements, headings, to_row = None):
    if to_row is not None:
      self.to_row = to_row
    else:
      self.to_row = self.default_to_row

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



class OverdueInstallments(gtk.VBox):
  def __init__(self, installments, klasses):
    self.installments = installments
    gtk.VBox.__init__(self, False, 5)
    
    klasses_model = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    klasses_model.append((None,'Todas las clases'))
    for klass in klasses:
      klasses_model.append((klass, klass.name))
    
    self.klass = gtk.ComboBoxEntry(klasses_model,1)
    completion = gtk.EntryCompletion()
    completion.set_model(klasses_model)
    completion.set_text_column(1)
    completion.connect('match-selected', self.on_klass_match_selected)
    self.klass.child.set_completion(completion)
    self.klass.set_active(0)

    self.filter = gtk.Button('Buscar')
    
    self.form = gtk.HBox(False, 5)
    self.form.pack_start(self.klass, False)
    self.form.pack_start(self.filter, False)
    
    self.pack_start(self.form, False)
    
    self.headings = ['Alumno', 'Año', 'Mes', 'Clase']
    
    self.list = InstallmentsList(installments, self.headings)
    self.list.connect('row-activated', self.on_row_activated)
    
    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.list)
    
    self.pack_start(self.scroll, True)
    
    self.actions = gtk.HBox(False, 5)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_csv = gtk.Button('Exportar CSV')
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)
    self.pack_start(self.actions, False)
    
    self.show_all()

  def get_tab_label(self):
    return "Cuotas atrasadas"

  def to_html(self):
    h1_content = "Cuotas atrasadas"
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
    f = 'cuotas_atrasadas'
    k = self.get_selected_klass()
    if k is not None: f += '_clase_%s' % str_to_filename(k.name)
    return f+'.csv'

  def values_for_html(self,i):
    return [i.membership.student.to_label(),str(i.year),i.month_name(),i.membership.klass_or_package.name]

  def update(self, installments = None):
    if installments is not None:
      self.installments = installments
    self.list.update(self.installments)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    installment = model.get_value(itr, 0)
    self.emit('student-edit', installment.membership.student_id)

  def get_selected_klass(self):
    itr = self.klass.get_active_iter()
    if itr is not None:
      return self.klass.get_model().get_value(itr,0)
    else:
      return None

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

gobject.type_register(OverdueInstallments)
gobject.signal_new('student-edit', \
                   OverdueInstallments, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

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
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)
    self.update(installments)

  def update(self, installments):
    self.store.clear()
    self.set_model(installments)
  
  def set_model(self, installments):
    for i in installments: self.store.append(self.to_row(i))

  def default_to_row(self, i):
    return (i,i.membership.student.to_label(),str(i.year),i.month_name(), i.membership.klass_or_package.name)
