#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from gui import *
from settings import Settings
from models import *

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
    self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

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
    page = KlassForm(klass)
    page.submit.connect('clicked',self.submit_klass, page)
    self.window.add_page(page)
  
  def edit_klass(self, widget):
    klass = Klass.find(1)
    page = KlassForm(klass)
    page.add_schedule.connect('clicked', self.add_schedule)
    page.submit.connect('clicked',self.submit_klass, page)
    self.window.add_page(page)
  
  def submit_klass(self, widget, form):
    print form.klass.id
    print form.get_values()
  
  #schedules controls
  def add_schedule(self, widget):
    schedule = Schedule()
    dialog = ScheduleDialog(schedule)
    dialog.connect('response', self.schedule_dialog_response, schedule)
    dialog.run()
  
  def schedule_dialog_response(self, dialog, response, schedule):
    if response == gtk.RESPONSE_ACCEPT:
      print "bien"
      print dialog.get_values()
    elif response == gtk.RESPONSE_REJECT:
      print "no!"
      dialog.destroy()

  #students controls
  def add_student(self, widget):
    student = Student()
    page = StudentForm(student)
    page.submit.connect('clicked',self.submit_student, page)
    self.window.add_page(page)
  
  def edit_student(self, widget):
    student = Student.find(1)
    page = StudentForm(student)
    page.submit.connect('clicked',self.submit_student, page)
    self.window.add_page(page)
  
  def submit_student(self, widget, form):
    print form.student.id
    print form.get_values()

  def search_student(self, widget):
    print "buscar usuarios..."
    
if __name__ == "__main__":
  ctrlr = Controller()
  ctrlr.main()
