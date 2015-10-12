#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
from datetime import datetime
from settings import Settings
from translations import _a

class ErrorMessage(gtk.MessageDialog):
  def __init__(self, header, message):
    gtk.MessageDialog.__init__(self, None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE, header)
    self.format_secondary_text(message)
    self.connect('response', self.close)

  def close(self, widget, response):
    self.destroy()

class ConfirmDialog(gtk.Dialog):
  def __init__(self, message):
    gtk.Dialog.__init__(self, '', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    
    self.set_border_width(5)
    
    self.vbox.pack_start(gtk.Label(message), False)
    self.vbox.show_all()

class CalendarPopup(gtk.Dialog):
  def __init__(self, callback, date):
    gtk.Dialog.__init__(self,'Elegí una fecha', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       ())
    
    try:
      d = datetime.strptime(date,Settings.get_settings().date_format)
      year, month, day = [d.year, d.month, d.day]
    except Exception:
      year, month, day = [datetime.today().year, datetime.today().month, datetime.today().day]
    self.calendar = gtk.Calendar()
    self.calendar.select_month(int(month)-1, int(year))
    self.calendar.select_day(int(day))
    self.calendar.connect('day-selected-double-click', callback, self)
    
    self.vbox.pack_start(self.calendar)
    self.vbox.show_all()
    
    self.connect('response', self.close)

  def close(self, response, dialog):
    self.destroy()

  def get_date_values(self):
    year, month, day = self.calendar.get_date()
    month += 1
    if month < 10:
      month = "0"+str(month)
    if day < 10:
      day = "0"+str(day)
    return [str(year),str(month),str(day)]

class OrderableColumn(gtk.TreeViewColumn):
  __gsignals__ = {
        "clicked" : "override"
        }
        
  def __init__(self, cls, attr, text_idx):
    label = _a('teacher', attr)
    gtk.TreeViewColumn.__init__(self, label, gtk.CellRendererText(), text=text_idx)
    self.set_expand(True)
    self.attr = attr
    self.direction = 'DESC'

  def do_clicked(self):
    self.direction = 'DESC' if self.direction == 'ASC' else 'ASC'

  def order_text(self):
    return self.attr+' COLLATE SPANISH '+self.direction
