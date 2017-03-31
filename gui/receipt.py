#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import datetime
import pango
from translations import _l

class Receipt():
  def __init__(self, payments):
    self.user = payments[0].user
    self.items_offset = 0.03
    self.payments = payments
    self.context = None
    self.width = 0
    self.height = 0

  def default_page_setup(self):
    setup = gtk.PageSetup()
    setup.set_orientation(gtk.PAGE_ORIENTATION_LANDSCAPE)
    setup.set_paper_size(gtk.PaperSize('iso_a6_105x148mm'))
    setup.set_top_margin(6, gtk.UNIT_MM)
    setup.set_bottom_margin(6, gtk.UNIT_MM)
    setup.set_left_margin(6, gtk.UNIT_MM)
    setup.set_right_margin(6, gtk.UNIT_MM)
    return setup

  def print_settings(self):
    settings = gtk.PrintSettings()
    settings.set_orientation(gtk.PAGE_ORIENTATION_LANDSCAPE)
    settings.set_paper_size(gtk.PaperSize('iso_a6_105x148mm'))
    return settings

  def do_print(self):
    print_op = gtk.PrintOperation()
    print_op.set_print_settings(self.print_settings())
    print_op.set_default_page_setup(self.default_page_setup())
    print_op.set_n_pages(1)
    print_op.set_job_name("Recibo #...")
    print_op.connect("draw_page", self.print_text)
    res = print_op.run(gtk.PRINT_OPERATION_ACTION_PRINT, None)

  def add_header(self):
    cr = self.context.get_cairo_context()
    user_name = self.context.create_pango_layout()
    user_name.set_text(self.user.to_label())
    cr.move_to(0,0)
    cr.show_layout(user_name)

    number = self.context.create_pango_layout()
    number.set_text('2')
    number.set_alignment(pango.ALIGN_CENTER)
    w, h = number.get_size()
    cr.move_to(int((self.width+w/pango.SCALE)/2),0)
    cr.show_layout(number)

    date = self.context.create_pango_layout()
    date.set_text(_l(datetime.date.today()))
    w, h = date.get_size()
    cr.move_to(int(self.width-w/pango.SCALE),0)
    cr.show_layout(date)

  def add_payments(self):
    cr = self.context.get_cairo_context()

    h_font_desc = pango.FontDescription()
    h_font_desc.set_weight(pango.WEIGHT_BOLD)

    h_desc = self.context.create_pango_layout()
    h_desc.set_text('DESCRIPCIÓN')
    h_desc.set_font_description(h_font_desc)
    cr.move_to(int(self.width*0.06), int(self.height*(0.1+self.items_offset)))
    cr.show_layout(h_desc)

    h_amount = self.context.create_pango_layout()
    h_amount.set_text('MONTO')
    h_amount.set_font_description(h_font_desc)
    cr.move_to(int(self.width*0.8), int(self.height*(0.1+self.items_offset)))
    cr.show_layout(h_amount)

    self.items_offset += 0.07
    cr.set_source_rgb(0, 0, 0)
    cr.set_line_width(0.7)
    cr.move_to(int(self.width*0.05), int(self.height*(0.1+self.items_offset)))
    cr.line_to(int(self.width*0.95), int(self.height*(0.1+self.items_offset)))
    cr.stroke()

    cr.set_line_width(0.3)

    self.items_offset += 0.01

    summ = None
    for p in self.payments:
      desc = self.context.create_pango_layout()
      desc.set_text(p.description)
      cr.move_to(int(self.width*0.09), int(self.height*(0.1+self.items_offset)))
      cr.show_layout(desc)

      summ = p.amount if summ is None else summ + p.amount

      amount = self.context.create_pango_layout()
      amount.set_text(str(p.amount))
      w, h = amount.get_size()
      cr.move_to(int(self.width*0.9-w/pango.SCALE), int(self.height*(0.1+self.items_offset)))
      cr.show_layout(amount)

      self.items_offset += 0.06
      cr.move_to(int(self.width*0.05), int(self.height*(0.1+self.items_offset)))
      cr.line_to(int(self.width*0.95), int(self.height*(0.1+self.items_offset)))
      cr.stroke()

      self.items_offset += 0.02

    cr.set_line_width(0.5)
    cr.move_to(int(self.width*0.65), int(self.height*0.76))
    cr.line_to(int(self.width*0.95), int(self.height*0.76))
    cr.stroke()

    total_label = self.context.create_pango_layout()
    total_label.set_text("Total:")
    cr.move_to(int(self.width*0.7), int(self.height*0.76))
    cr.show_layout(total_label)

    total = self.context.create_pango_layout()
    total.set_text(str(summ))
    w, h = total.get_size()
    cr.move_to(int(self.width*0.9-w/pango.SCALE), int(self.height*0.76))
    cr.show_layout(total)

  def add_footer(self):
    cr = self.context.get_cairo_context()
    mara = self.context.create_pango_layout()
    mara.set_text('Instituto de danzas Mara Micolich')
    cr.move_to(0, int(self.height*0.95))
    cr.show_layout(mara)

    sign = self.context.create_pango_layout()
    sign.set_text('.............')
    sign.set_alignment(pango.ALIGN_RIGHT)
    w, h = sign.get_size()
    cr.move_to(int(self.width-w/pango.SCALE), int(self.height*0.95))
    cr.show_layout(sign)

  def print_text(self, operation=None, context=None, page_nr=None):
    self.context = context
    self.width = context.get_width()
    self.height = context.get_height()
    self.add_header()
    self.add_payments()
    self.add_footer()
