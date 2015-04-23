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

    if self.settings.startup_size != '':
      self.window.set_size_request(1000,700)
      self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    else:
      self.window.maximize()

  def close_tab(self, page):
    self.window.remove_page(page)



  #config controls
  def show_config(self, widget):
    page = Config(self.settings)
    self.window.add_page(page)



  #teachers controls
  def add_teacher(self, widget):
    teacher = Teacher()
    page = self.teacher_form(widget, teacher)

  def edit_teacher(self, widget, teacher):
    page = self.teacher_form(widget, teacher)

  def teacher_form(self, widget, teacher = None):
    page = TeacherForm(teacher)
    page.submit.connect_object('clicked',self.submit_teacher, page)
    self.window.add_page(page)
    return page

  def submit_teacher(self, form):
    print form.object.id
    print form.get_values()

  def list_teachers(self, widget):
    teachers = Teacher.all()
    page = TeachersList(teachers)
    self.window.add_page(page)
    page.connect('teacher-edit', self.edit_teacher)
    page.connect('teacher-add', self.add_teacher)



  #klasses controls
  def add_klass(self, widget, room = '', time = '', day_idx = 0):
    klass = Klass()
    if room and time:
      klass.build_schedule({'from_time': time, 'room': room, 'day': day_idx})
    page = self.klass_form(widget, klass)
  
  def edit_klass(self, widget, klass):
    page = self.klass_form(widget, klass)
  
  def klass_form(self, widget, klass = None):
    page = KlassForm(klass)
    page.submit.connect_object('clicked',self.submit_klass, page)
    page.connect('schedule-edit', self.edit_schedule)
    page.connect('schedule-add', self.add_schedule)
    page.connect('teacher-search', self.show_select_teacher_dialog)
    self.window.add_page(page)
    return page

  def list_klasses(self, widget):
    klasses = Klass.by_room_and_time(self.settings.get_opening_h(), self.settings.get_closing_h())
    page = KlassesList(klasses)
    self.window.add_page(page)
    page.connect('klass-edit', self.edit_klass)
    page.connect('klass-add', self.add_klass)
  
  def submit_klass(self, form):
    print form.object.id
    print form.get_values()

  def show_select_teacher_dialog(self, page):
    teachers = Teacher.all()
    dialog = SelectTeacherDialog(teachers)
    dialog.connect('response', self.select_teacher_dialog_response, page)
    dialog.run()

  def select_teacher_dialog_response(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      teacher = dialog.get_selected_teacher()
      if teacher is not None:
        if teacher.id not in map(lambda t: t.id, page.object.teachers):
          page.object.teachers.append(teacher)
          page.update_teachers()

    if destroy_dialog:
      dialog.destroy()

  #schedules controls
  def add_schedule(self, page):
    schedule = Schedule()
    self.show_schedule_dialog(schedule, page)
  
  def edit_schedule(self, page, schedule):
    self.show_schedule_dialog(schedule, page)
  
  def show_schedule_dialog(self, schedule, page):
    dialog = ScheduleDialog(schedule)
    dialog.connect('response', self.schedule_dialog_response, schedule, page)
    dialog.run()

  def schedule_dialog_response(self, dialog, response, schedule, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      schedule.set_attrs(dialog.get_values())
      if schedule in page.object.schedules:
        page.update_schedules()
      else:
        page.add_schedule(schedule)

    elif response == gtk.RESPONSE_DELETE_EVENT:
      if schedule in page.object.schedules:
        page.object.schedules.remove(schedule)
        page.update_schedules()

    if destroy_dialog:
      dialog.destroy()



  #students controls
  def add_student(self, widget):
    student = Student()
    page = self.student_form(student)

  def edit_student(self, widget):
    student = Student.find(1)
    page = self.student_form(student)

  def student_form(self, student):
    page = StudentForm(student)
    page.submit.connect_object('clicked',self.submit_student, page)
    self.window.add_page(page)
    return page

  def submit_student(self, form):
    print form.object.id
    print form.get_values()

  def search_student(self, widget):
    print "buscar alumno..."



if __name__ == "__main__":
  ctrlr = Controller()
  ctrlr.main()
