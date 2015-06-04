#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
import datetime
import widgets
import exporter

class DailyPayments(gtk.VBox):
  def __init__(self, payments):
    self.payments = payments
    gtk.VBox.__init__(self, False, 5)
    
    self.from_e = gtk.Entry(10)
    self.from_e.set_text(str(datetime.datetime.today()))
    self.from_e.connect('button-press-event', self.show_calendar)
    self.from_e.set_property("editable", False)
    self.from_e.set_can_focus(False)
    self.to_e = gtk.Entry(10)
    self.to_e.set_text(str(datetime.datetime.today()))
    self.to_e.connect('button-press-event', self.show_calendar)
    self.to_e.set_property("editable", False)
    self.to_e.set_can_focus(False)
    self.done_rb = gtk.RadioButton(None, 'Hechos')
    self.received_rb = gtk.RadioButton(self.done_rb, 'Recibidos')
    self.received_rb.set_active(True)
    self.filter = gtk.Button('Buscar')
    
    self.form = gtk.HBox(False, 5)
    self.form.pack_start(gtk.Label('Desde:'), False)
    self.form.pack_start(self.from_e, False)
    self.form.pack_start(gtk.Label('Hasta:'), False)
    self.form.pack_start(self.to_e, False)
    self.form.pack_start(self.done_rb, False)
    self.form.pack_start(self.received_rb, False)
    self.form.pack_start(self.filter, False)
    
    self.pack_start(self.form, False)
    
    self.headings = ['Alumno/Profesor', 'Fecha', 'Monto', 'Detalle']
    
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
    
    self.export = gtk.Button('Exportar')
    self.pack_start(self.export, False)
    
    self.show_all()

  def get_tab_label(self):
    return "Pagos"

  def to_html(self):
    done_or_received = 'hechos' if self.done_rb.get_active() else 'recibidos'
    title = "<h1>Pagos %s entre %s y %s</h1>" % (done_or_received, str(self.get_from()), str(self.get_to()))

    rows = map(lambda p: self.values_for_html(p), self.payments)
    total = sum(map(lambda p: p.amount, self.payments))
    caption = 'Total: <b>$'+str(total)+'</b>'

    return exporter.html_wrapper(title+exporter.html_table(self.headings,rows,caption))
    
  def values_for_html(self,p):
    return [p.user.to_label(),str(p.date),str(p.amount),str(p.description)]
    

  def get_from(self):
    return self.from_e.get_text()

  def get_to(self):
    return self.to_e.get_text()

  def get_done_or_received(self):
    return self.done_rb.get_active()

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
    widget.set_text("%s-%s-%s" % (year, month, day))
    dialog.destroy()

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    payment = model.get_value(itr, 0)
    self.emit('student-edit', payment.user_id)

gobject.type_register(DailyPayments)
gobject.signal_new('student-edit', \
                   DailyPayments, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class PaymentsList(gtk.TreeView):
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
    # payment, user name, date, amount, description
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)
    self.update(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)
  
  def set_model(self, payments):
    for p in payments:
      self.store.append((p,p.user.to_label(),str(p.date),str(p.amount), p.description))

class KlassStudents(gtk.VBox):
  def __init__(self, klass, students = {}):
    self.klass = klass
    self.students = students
    gtk.VBox.__init__(self)





