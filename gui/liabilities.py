#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
import widgets
from settings import Settings
import datetime

class LiabilitiesTab(gtk.VBox):
  def __init__(self, user, done = False):
    gtk.VBox.__init__(self)
    
    self.user = user
    
    self.info_vbox =gtk.VBox()
    self.info_vbox.pack_start(gtk.Label('Deudas'), False)

    self.pack_start(self.info_vbox, False)

    #liability, date, description, amount
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str)
    
    self.refresh()
    
    self.list = gtk.TreeView(self.store)
    self.list.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_HORIZONTAL)
    self.selection = self.list.get_selection()
    self.selection.connect('changed', self.on_selection_changed)
    
    #self.list.set_rubber_banding(True)
    #self.selection.set_mode(gtk.SELECTION_MULTIPLE)
    
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
    
    self.add_b = gtk.Button('Agregar Deuda')
    self.delete_b = gtk.Button('Eliminar Deuda')
    self.delete_b.set_sensitive(False)
    self.add_payment_b = gtk.Button('Agregar Pago')
    self.add_payment_b.set_sensitive(False)
    
    self.actions.pack_start(self.add_b, False)
    self.actions.pack_start(self.delete_b, False)
    self.actions.pack_start(self.add_payment_b, False)
    
    self.pack_start(self.actions, False)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col

  def refresh(self):
    self.store.clear()
    
    if self.user.is_not_new_record():
      for l in self.user.get_liabilities():
        self.store.append((l,l.date.strftime(Settings.get_settings().date_format), l.description, l.detailed_amount()))

  def on_selection_changed(self, selection):
    model, pathlist = selection.get_selected_rows()
    self.delete_b.set_sensitive(pathlist != False)
    self.add_payment_b.set_sensitive(pathlist != False)

  def get_selected_liabilities(self):
    model, pathlist = self.selection.get_selected_rows()
    items = []
    for path in pathlist:
      iter = model.get_iter(path)
      items.append(model.get_value(iter, 0))
    print items
    return items

class AddLiabilityDialog(gtk.Dialog):
  def __init__(self, liability):
    self.liability = liability
    self.form = AddLiabilityForm(liability)
    gtk.Dialog.__init__(self, 'Agregar deuda', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class AddLiabilityForm(FormFor):
  def __init__(self, liability):
    FormFor.__init__(self, liability)
    
    self.fields = gtk.VBox()
    self.add_field('date', attrs=10)
    self.date_e.set_text(liability.date.strftime(Settings.get_settings().date_format))
    self.date_e.connect('button-press-event', self.show_calendar)
    self.add_field('amount', attrs=15)
    self.add_field('description', attrs=100)

    self.pack_start(self.fields, False)

  def get_values(self):
    data = {'date': self.date_e.get_text(), 'amount': self.amount_e.get_text(), 'description': self.description_e.get_text()}

    return data

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()

