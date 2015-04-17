#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from gui import *
from settings import Settings
from teacher import Teacher

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

  def add_teacher(self, widget):
    teacher = Teacher()
    page = TeacherForm(teacher)
    self.window.add_page(page)
  
  def edit_teacher(self, widget):
    teacher = Teacher.find(1)
    page = TeacherForm(teacher)
    self.window.add_page(page)

  def close_tab(self, page):
    self.window.remove_page(page)
    
if __name__ == "__main__":
  ctrlr = Controller()
  ctrlr.main()
