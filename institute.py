#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import gtk
import gobject
from gui import *
from settings import Settings
from models import *

class Controller(gobject.GObject):
  def main(self):
    gtk.main()
  
  #skip delete event so destroy event is triggered
  def delete_event(self, widget, event, data=None):
    return gtk.FALSE
  
  #stop app
  def quit(self, widget, data=None):
    gtk.main_quit()

  def __init__(self):
    gobject.GObject.__init__(self)
    self.settings = Settings.get_settings()

    self.window = MainWindow()
    self.window.connect("delete_event", self.delete_event)
    self.window.connect("destroy", self.quit)
    self.window.connect('close-tab', self.close_tab)
    self.window.set_title(self.settings.name)
    self.bind_main_menu()

    if self.settings.startup_size != '':
      self.window.set_size_request(1000,700)
      self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    else:
      self.window.maximize()
    
    self.connected_signals = {}

  def close_tab(self, window, page):
    self.window.remove_page(page)
    self.remove_signals(page)
    page.destroy()

  def bind_main_menu(self):
    self.window.menu.config.connect('activate', self.show_config)
    self.window.menu.quit.connect('activate',self.quit)
    self.window.menu.add_teacher.connect('activate', self.add_teacher)
    self.window.menu.list_teachers.connect('activate', self.list_teachers)
    self.window.menu.add_klass.connect('activate', self.add_klass)
    self.window.menu.list_klasses.connect('activate', self.list_klasses)
    self.window.menu.show_schedules.connect('activate', self.show_schedules)
    self.window.menu.add_student.connect('activate', self.add_student)
    self.window.menu.search_student.connect('activate', self.search_student)
    self.window.menu.license.connect('activate', self.show_help_dialog, 'License')
    self.window.menu.about.connect('activate', self.show_help_dialog, 'About')

  def show_help_dialog(self, widget, dialog_class):
    dialog = eval(dialog_class)()
    dialog.connect('response', self.on_help_dialog_response)
    dialog.run()

  def on_help_dialog_response(self, dialog, reponse):
    dialog.destroy()

  def show_status(self, status):
    self.window.show_status(status)



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
    page.connect('teacher-remove', self.on_remove_teacher)
    self.window.add_page(page)
    return page

  def show_schedules(self, widget):
    klasses = Klass.by_room_and_time(self.settings.get_opening_h(), self.settings.get_closing_h())
    page = SchedulesTables(klasses)
    self.window.add_page(page)
    page.connect('klass-edit', self.edit_klass)
    page.connect('klass-add', self.add_klass)
    self.save_signal(self.connect('klass-changed', self.refresh_schedules, page), page)

  def list_klasses(self, widget):
    klasses = Klass.all()
    page = KlassesList(klasses)
    self.window.add_page(page)
    page.connect('klass-edit', self.edit_klass)
    page.connect('klass-add', self.add_klass)
    self.save_signal(self.connect('klass-changed', self.refresh_klasses, page), page)

  def refresh_schedules(self, widget, kls, created, page):
    klasses = Klass.by_room_and_time(self.settings.get_opening_h(), self.settings.get_closing_h())
    page.refresh_tables(klasses)
  
  def refresh_klasses(self, widget, kls, created, page):
    klasses = Klass.all()
    page.refresh_list(klasses)
  
  def submit_klass(self, form):
    kls = form.object
    new_record = kls.is_new_record()
    kls.set_attrs(form.get_values())
    if kls.save():
      self.emit('klass-changed', kls, new_record)
      self.window.update_label(form)
      self.show_status('Clase guardada')
    else:
      ErrorMessage("No se puede guardar la clase:", kls.full_errors()).run()

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
        if teacher.id not in map(lambda t: t.id, page.object.get_teachers()):
          page.object.add_teacher(teacher)
          page.update_teachers()

    if destroy_dialog:
      dialog.destroy()

  def on_remove_teacher(self, page, teacher):
    if teacher is not None:
      for t in page.object.get_teachers():
        if teacher.id == t.id:
          page.object.remove_teacher(t)
          page.update_teachers()



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
      if schedule.is_valid():
        if schedule in page.object.get_schedules():
          page.update_schedules()
        else:
          page.add_schedule(schedule)
      else:
        destroy_dialog = False
        ErrorMessage("No se puede guardar el horario:", schedule.full_errors()).run()

    elif response == gtk.RESPONSE_DELETE_EVENT:
      if schedule in page.object.get_schedules():
        page.object.remove_schedule(schedule)
        page.update_schedules()

    if destroy_dialog:
      dialog.destroy()



  #students controls
  def add_student(self, widget):
    student = Student()
    page = self.student_form(student)

  def edit_student(self, widget, student_id):
    student = Student.find(student_id)
    page = self.student_form(student)

  def student_form(self, student):
    page = StudentForm(student)
    page.submit.connect_object('clicked', self.submit_student, page)
    page.memberships_panel.enroll_b.connect_object('clicked', self.new_membership, page)
    page.memberships_panel.connect('ask-delete-membership', self.ask_delete_membership)
    page.memberships_panel.connect('add-installments', self.add_installments)
    self.save_signal(self.connect('membership-deleted', page.on_membership_deleted), page)
    self.window.add_page(page)
    return page

  def submit_student(self, form):
    student = form.object
    new_record = student.is_new_record()
    student.set_attrs(form.get_values())
    if student.save():
      self.emit('student-changed', student, new_record)
      if new_record:
        form.enable_memberships()
    else:
      ErrorMessage("No se puede guardar el alumno:", student.full_errors()).run()

  def search_student(self, widget):
    page = SearchStudent()
    self.window.add_page(page)
    page.connect('search', self.on_student_search)
    page.connect('student-edit', self.edit_student)
    self.save_signal(self.connect('student-changed', page.on_search), page)
  
  def on_student_search(self, page, value):
    students = Student.search(value)
    page.update_results(students)



  # memberships
  def new_membership(self, page):
    membership = Membership()
    klasses = Klass.all()
    for m in page.object.memberships:
      for k in klasses:
        if m.klass_id == k.id:
          klasses.remove(k)

    if klasses:
      dialog = MembershipDialog(membership, klasses)
      dialog.connect('response', self.on_new_membership, page)
      dialog.run()
    else:
      ErrorMessage("No se puede inscribir:", 'El alumno se encuentra inscripto en todas las clases.').run()

  def on_new_membership(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      membership = dialog.form.object
      membership.set_attrs(dialog.form.get_values())
      membership.student_id = page.object.id
      if membership.is_valid():
        membership.build_installments()
        membership.save()
        page.object.add_membership(membership)
        page.object.save()
        page.update_memberships()
      else:
        ErrorMessage("No se puede guardar la inscripción:", membership.full_errors()).run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_membership(self, widget, membership):
    dialog = ConfirmDialog('Vas a borrar la inscripción a la clase '+membership.klass.name+"\n¿Estás seguro?")
    dialog.connect('response', self.delete_membership, membership)
    dialog.run()

  def delete_membership(self, dialog, response, membership):
    if response == gtk.RESPONSE_ACCEPT:
      membership.delete()
      self.show_status('Inscripción eliminada.')
      self.emit('membership-deleted', membership.id)

    dialog.destroy()

  def add_installments(self, widget, membership):
    return True



  #save a reference of signals connected
  def save_signal(self, h_id, obj):
    if obj not in self.connected_signals:
      self.connected_signals[obj] = []
    self.connected_signals[obj].append(h_id)

  def remove_signals(self, obj):
    if obj in self.connected_signals:
      for h_id in self.connected_signals[obj]:
        self.disconnect(h_id)
      del self.connected_signals[obj]

gobject.type_register(Controller)
gobject.signal_new('student-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #student object, creation(True value means the user just got created)

gobject.signal_new('klass-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #klass object, creation(True value means the user just got created)

gobject.signal_new('membership-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #klass object, creation(True value means the user just got created)

if __name__ == "__main__":
  ctrlr = Controller()
  ctrlr.main()
