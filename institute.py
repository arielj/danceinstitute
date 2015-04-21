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
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.quit)
    
    #self.window.set_size_request(1000,700)
    #self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    self.window.maximize()

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
  def add_klass(self, widget, room = '', time = '', day_idx = 0):
    klass = Klass()
    if room or time or day:
      schedule = Schedule({'from_time': time, 'room': room, 'day': day_idx})
      klass.schedules = [schedule]
    page = self.klass_form(widget, klass)
  
  def edit_klass(self, widget, klass_id):
    klass = Klass.find(klass_id)
    page = self.klass_form(widget, klass)
    page.add_schedule_b.connect('clicked', self.add_schedule, page)
    page.connect('row-activated', self.edit_schedule)
    return page
  
  def klass_form(self, widget, klass = None):
    page = KlassForm(klass)
    page.submit.connect('clicked',self.submit_klass, page)
    self.window.add_page(page)
    return page

  def list_klasses(self, widget):
    klasses = Klass.by_room_and_time()
    page = KlassesList(klasses)
    self.window.add_page(page)
    page.connect('dclick-klass-edit', self.edit_klass)
    page.connect('dclick-klass-add', self.add_klass)
  
  def submit_klass(self, widget, form):
    print form.klass.id
    print form.get_values()
  
  #schedules controls
  def add_schedule(self, widget, page):
    schedule = Schedule()
    self.show_schedule_dialog(schedule, page)
  
  def edit_schedule(self, page, schedule):
    self.show_schedule_dialog(schedule, page)
  
  def show_schedule_dialog(self, schedule, page):
    dialog = ScheduleDialog(schedule)
    dialog.connect('response', self.schedule_dialog_response, schedule, page)
    dialog.run()

  def schedule_dialog_response(self, dialog, response, schedule, page):
    if response == gtk.RESPONSE_ACCEPT:
      schedule.set_attrs(dialog.get_values())
      if schedule.id:
        page.update_schedules()
      else:
        page.add_schedule(schedule)
      dialog.destroy()
    elif response == gtk.RESPONSE_REJECT:
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
