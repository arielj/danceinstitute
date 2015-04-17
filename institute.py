#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from gui import *
from settings import Settings
from teacher import Teacher
from klass import Klass

class Controller:
  def main(self):
    gtk.main()
  
  #skip delete event so destroy event is triggered
  def delete_event(self, widget, event, data=None):
    return gtk.FALSE
  
  #stop app
  def quit(self, widget, data=None):
    gtk.main_quit()

  def __init__(self):
    self.settings = Settings.get_settings()

    self.window = MainWindow(self)
    
    self.window.set_size_request(1000,700)

  def close_tab(self, page):
    self.window.remove_page(page)

  #teachers controls
  def add_teacher(self, widget):
    teacher = Teacher()
    page = TeacherForm(self, teacher)
    self.window.add_page(page)
  
  def edit_teacher(self, widget):
    teacher = Teacher.find(1)
    page = TeacherForm(self, teacher)
    self.window.add_page(page)
  
  def submit_teacher(self, widget, form):
    print form.teacher.id
    print form.get_values()

  #klasses controls
  def add_klass(self, widget):
    klass = Klass()
    page = KlassForm(self, klass)
    self.window.add_page(page)
  
  def edit_klass(self, widget):
    klass = Klass.find(1)
    page = KlassForm(self, klass)
    self.window.add_page(page)
  
  def submit_klass(self, widget, form):
    print form.klass.id
    
if __name__ == "__main__":
  ctrlr = Controller()
  ctrlr.main()
