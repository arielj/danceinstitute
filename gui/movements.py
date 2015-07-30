#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
import widgets
from settings import Settings
import datetime

class AddMovementDialog(gtk.Dialog):
  def __init__(self,movement):
    self.movement = movement
    self.form = AddMovementForm(movement)
    gtk.Dialog.__init__(self, 'Agregar movimento', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class AddMovementForm(FormFor):
  def __init__(self, movement):
    FormFor.__init__(self, movement)
    
    self.fields = gtk.VBox()
    self.add_field('date', attrs=10)
    self.date_e.set_text(movement.date.strftime(Settings.get_settings().date_format))
    self.date_e.connect('button-press-event', self.show_calendar)
    self.add_field('amount', attrs=6)
    self.add_field('description', attrs=100)
    self.direction = gtk.HBox(True, 2)
    self.incoming_r = gtk.RadioButton(None, 'Entrada')
    self.outgoing_r = gtk.RadioButton(self.incoming_r, 'Salida')
    self.direction.pack_start(self.incoming_r)
    self.direction.pack_start(self.outgoing_r)
    self.fields.pack_start(self.direction,False)

    self.pack_start(self.fields, False)

  def get_direction(self):
    return 'out' if self.outgoing_r.get_active() else 'in'

  def get_values(self):
    return {'date': self.date_e.get_text(), 'amount': self.amount_e.get_text(), 'description': self.description_e.get_text(), 'direction': self.get_direction()}

  def show_calendar(self, widget, event):
    widgets.CalendarPopup(lambda cal, dialog: self.on_date_selected(cal,widget,dialog), widget.get_text()).run()

  def on_date_selected(self, calendar, widget, dialog):
    year, month, day = dialog.get_date_values()
    d = datetime.date(int(year),int(month),int(day))
    widget.set_text(d.strftime(Settings.get_settings().date_format))
    dialog.destroy()
