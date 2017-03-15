#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import datetime
import pango

class Receipt(gtk.DrawingArea):
  def __init__(self, payments):
    gtk.DrawingArea.__init__(self)
    self.user = payments[0].user
    self.set_size_request(600, 300)

    self.connect("expose-event", self.area_expose_cb, payments)

    self.items_offset = 40


  def area_expose_cb(self, area, event, payments):
    self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
    self.add_header()
    self.add_payments(payments)
    self.add_footer()
    return True

  def do_print(self):
    print_op = gtk.PrintOperation()
    print_op.set_n_pages(1)
    print_op.connect("draw_page", self.print_text)
    res = print_op.run(gtk.PRINT_OPERATION_ACTION_PRINT_DIALOG, None)

  def add_header(self):
    user_name = self.create_pango_layout(self.user.to_label())
    self.window.draw_layout(self.gc, 10, 10, user_name)

    number = self.create_pango_layout('2')
    number.set_width(20)
    number.set_alignment(pango.ALIGN_CENTER)
    self.window.draw_layout(self.gc, 290, 10, number)

    date = self.create_pango_layout(str(datetime.date.today()))
    date.set_alignment(pango.ALIGN_RIGHT)
    date.set_width(100)
    self.window.draw_layout(self.gc, 500, 10, date)

  def add_payments(self, payments):
    summ = None
    for p in payments:
      desc = self.create_pango_layout(p.description)
      self.window.draw_layout(self.gc, 30, self.items_offset, desc)
      summ = p.amount if summ is None else summ + p.amount
      amount = self.create_pango_layout(str(p.amount))
      self.window.draw_layout(self.gc, 400, self.items_offset, amount)
      self.items_offset += 18

    total_label = self.create_pango_layout("Total:")
    self.window.draw_layout(self.gc, 350, self.items_offset+18, total_label)
    total = self.create_pango_layout(str(summ))
    self.window.draw_layout(self.gc, 400, self.items_offset+18, total)

  def add_footer(self):
    mara = self.create_pango_layout('Instituto de danzas Mara Micolich')
    self.window.draw_layout(self.gc, 10, self.items_offset+80, mara)

    sign = self.create_pango_layout('.............')
    sign.set_alignment(pango.ALIGN_RIGHT)
    self.window.draw_layout(self.gc, 400, self.items_offset+80, sign)

  def print_text(self, operation=None, context=None, page_nr=None):
    self.pangolayout = context.create_pango_layout()
    self.format_text()
    cairo_context = context.get_cairo_context()
    cairo_context.show_layout(self.pangolayout)
