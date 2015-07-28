#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import tempfile
import webbrowser
import re
import datetime
from database import Conn
from gui import *
from settings import Settings
from models import *
import translations
import exporter

class Controller(gobject.GObject):
  def main(self):
    gtk.main()
  
  #skip delete event so destroy event is triggered
  def delete_event(self, widget, event, data=None):
    return gtk.FALSE
  
  #stop app
  def quit(self, widget, data=None):
    Conn.close()
    gtk.main_quit()

  def __init__(self, env):
    Conn.start_connection(env)
    gobject.GObject.__init__(self)
    self.settings = Settings.get_settings()

    self.window = MainWindow()
    if env != 'test':
      self.window.show_all()
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
    
    self.bind_status_signals()
    self.connected_signals = {}
    
    self.connect('settings-changed', self.on_settings_changed)
    
    self.home(None)

  def close_tab(self, window, page):
    self.window.remove_page(page)
    self.remove_signals(page)
    page.destroy()

  def bind_main_menu(self):
    self.window.menu.show_home.connect('activate', self.home)
    self.window.menu.config.connect('activate', self.show_config)
    self.window.menu.quit.connect('activate',self.quit)
    self.window.menu.list_rooms.connect('activate',self.list_rooms)
    self.window.menu.add_teacher.connect('activate', self.add_teacher)
    self.window.menu.list_teachers.connect('activate', self.list_teachers)
    self.window.menu.add_klass.connect('activate', self.add_klass)
    self.window.menu.list_klasses.connect('activate', self.list_klasses)
    self.window.menu.show_schedules.connect('activate', self.show_schedules)
    self.window.menu.show_packages.connect('activate', self.show_packages)
    self.window.menu.add_student.connect('activate', self.add_student)
    self.window.menu.search_student.connect('activate', self.search_student)
    self.window.menu.payments.connect('activate', self.payments_report)
    self.window.menu.daily_cash.connect('activate', self.daily_cash)
    self.window.menu.overdue_installments.connect('activate', self.overdue_installments)
    self.window.menu.license.connect('activate', self.show_help_dialog, 'License')
    self.window.menu.about.connect('activate', self.show_help_dialog, 'About')

  def bind_status_signals(self):
    self.connect_object('membership-deleted', self.show_status, 'Inscripción eliminada.')
    self.connect_object('klass-changed', self.show_status, 'Clase guardada.')
    self.connect('user-changed', self.on_user_changed)
    self.connect_object('settings-changed', self.show_status, 'Configuración guardada.')
    self.connect_object('payment-deleted', self.show_status, 'Pago eliminado.')
    self.connect_object('installment-deleted', self.show_status, 'Cuota eliminada.')
    self.connect_object('package-changed', self.show_status, 'Paquete guardado.')
    self.connect_object('klass-deleted', self.show_status, 'Clase borrada.')

  def on_user_changed(self, widget, user, new_record):
    self.show_status(translations._m(user.cls_name())+' guardado.')

  def show_help_dialog(self, widget, dialog_class):
    dialog = eval(dialog_class)()
    dialog.connect('response', self.on_help_dialog_response)
    dialog.run()

  def on_help_dialog_response(self, dialog, reponse):
    dialog.destroy()

  def show_status(self, status, *data):
    self.window.show_status(status)

  def home(self, widget):
    current = self.window.get_page_by_label(Home.tab_label())
    if current:
      self.window.focus_page(current)
      return current

    today = datetime.datetime.today().date()
    klasses = klass.Klass.for_day(self.settings.get_opening_h(), self.settings.get_closing_h(),today.weekday())
    installments = installment.Installment.overdues()
    notes = self.settings.notes
    payments = payment.Payment.filter(today,today)
    movements = movement.Movement.by_date(today)
    page = Home(klasses, notes, installments, payments, movements)
    page.connect('user-edit', self.edit_student)
    page.notes.save.connect_object('clicked',self.save_notes, page)
    page.daily_cash.movements_l.add_b.connect_object('clicked', self.add_movement_dialog, page)
    page.daily_cash.movements_l.delete_b.connect_object('clicked', self.ask_delete_movement, page)
    self.save_signal(self.connect_object('movement-deleted', self.update_home_movements, page), page)
    self.save_signal(self.connect_object('payment-deleted', self.update_home_payments, page), page)
    self.save_signal(self.connect_object('payment-changed', self.update_home_payments, page), page)
    self.window.add_page(page)
    return page

  def add_movement_dialog(self, page):
    movement = Movement()
    dialog = AddMovementDialog(movement)
    dialog.connect('response', self.on_add_movement, page)
    dialog.run()
  
  def on_add_movement(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      data = dialog.form.get_values()
      movement = dialog.movement
      movement.set_attrs(data)
      added = movement.save()
      if added is False:
        added = movement.full_errors()
      if added is True:
        self.update_movements(page)
      else:
        ErrorMessage('No se pudo cargar el movimiento:', added).run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_movement(self, page):
    mov = page.daily_cash.movements_l.get_selected_movement()
    if mov:
      dialog = ConfirmDialog('Vas a borrar el movimiento: '+mov.description+"\n¿Estás seguro?")
      dialog.connect('response', self.delete_movement, mov)
      dialog.run()

  def delete_movement(self, dialog, response, movement):
    if response == gtk.RESPONSE_ACCEPT:
      movement.delete()
      self.emit('movement-deleted', movement.id)

    dialog.destroy()

  def update_home_movements(self, page, *args):
    page.update_movements(movement.Movement.by_date(datetime.datetime.today().date()))

  def update_home_payments(self, page, *args):
    today = datetime.datetime.today().date()
    payments = payment.Payment.filter(today,today)
    page.update_payments(payments)

  def save_notes(self, page):
    self.settings.notes = page.get_notes()
    if self.settings.save():
      self.emit('settings-changed')

  #config controls
  def show_config(self, widget):
    page = Config(self.settings)
    current = self.window.get_page_by_label(page.get_tab_label())
    if current:
      self.window.focus_page(current)
      return current
    else:
      page.submit.connect('clicked', self.save_config, page)
      self.window.add_page(page)
      return page

  def save_config(self, button, page):
    self.settings.set_values(page.get_values())
    if self.settings.save():
      self.emit('settings-changed')

  def on_settings_changed(self, *data):
    translations.I18n.set_lang(self.settings.language)
    pos = gtk.POS_TOP if self.settings.tabs_position == 'top' else gtk.POS_LEFT
    if self.window.notebook.get_tab_pos() != pos:
      self.window.notebook.set_tab_pos(pos)



  #rooms controls
  def list_rooms(self, widget):
    current = self.window.get_page_by_label(RoomsList.tab_label())
    if current:
      self.window.focus_page(current)
      return current
    else:
      rooms = Room.all()
      page = RoomsList(rooms)
      self.window.add_page(page)
      page.connect('room-edit', self.edit_room)
      page.connect('room-add', self.add_room)
      self.save_signal(self.connect('room-changed', self.refresh_rooms, page), page)
      return page

  def add_room(self, widget):
    room = Room()
    page = self.room_form(widget, room)

  def edit_room(self, widget, room):
    page = self.room_form(widget, room)

  def room_form(self, widget, room):
    if room.is_not_new_record():
      current = self.window.get_page_by_object(room)
      if current:
        self.window.focus_page(current)
        return current

    page = RoomForm(room)
    page.submit.connect_object('clicked',self.submit_room, page)
    self.window.add_page(page)
    return page

  def submit_room(self, form):
    room = form.object
    new_record = room.is_new_record()
    room.set_attrs(form.get_values())
    if room.save():
      self.emit('room-changed', room, new_record)
      self.window.update_label(form)
    else:
      ErrorMessage("No se puede guardar la clase:", room.full_errors()).run()

  def refresh_rooms(self, widget, room, created, page):
    rooms = Room.all()
    page.refresh_list(rooms)
    


  #teachers controls
  def add_teacher(self, widget):
    teacher = Teacher()
    page = self.user_form(teacher)

  def edit_teacher(self, widget, teacher):
    page = self.user_form(teacher)

  def list_teachers(self, widget):
    current = self.window.get_page_by_label(TeachersList.tab_label())
    if current:
      self.window.focus_page(current)
      return current

    teachers = Teacher.get()
    page = TeachersList(teachers)
    self.window.add_page(page)
    page.connect('teacher-edit', self.edit_teacher)
    page.connect('teacher-add', self.add_teacher)
    page.connect('teacher-delete', self.ask_delete_teacher)
    self.save_signal(self.connect('user-changed', self.refresh_teachers, page), page)
    self.save_signal(self.connect('teacher-deleted', self.refresh_teachers, None, page), page)
    return page

  def ask_delete_teacher(self, page, teacher_id):
    teacher = Teacher.find(teacher_id)
    if teacher:
      can_delete = teacher.can_delete()
      if can_delete is True:
        dialog = ConfirmDialog('Vas a borrar a '+teacher.to_label()+":\n¿Estás seguro?")
        dialog.connect('response', self.delete_teacher, teacher)
        dialog.run()
      else:
        ErrorMessage("No se puede borrar al profesor:", can_delete).run()

  def delete_teacher(self, dialog, response, teacher):
    if response == gtk.RESPONSE_ACCEPT:
      deleted = teacher.delete()
      if deleted is True:
        self.emit('teacher-deleted', teacher.id)
      else:
        print deleted
        ErrorMessage("No se puede borrar al profesor:", deleted).run()
    dialog.destroy()

  def refresh_teachers(self, widget, teacher, created, page):
    teachers = Teacher.get()
    page.refresh_list(teachers)

  def add_teacher_payment(self, page):
    payment = Payment()
    payment.user = page.object
    
    dialog = AddPaymentDialog(payment)
    dialog.connect('response', self.on_add_payment, page, True)
    dialog.run()


  #students controls
  def add_student(self, widget):
    student = Student()
    page = self.user_form(student)

  def edit_student(self, widget, student_id):
    student = Student.find(student_id)
    page = self.user_form(student)

  def user_form(self, user):
    if user.is_not_new_record():
      current = self.window.get_page_by_object(user)
      if current:
        self.window.focus_page(current)
        return current

    page = UserForm(user)
    page.submit.connect_object('clicked', self.submit_user, page)
    page.open_fb.connect_object('clicked', self.open_fb, page)
    page.memberships_panel.enroll_b.connect_object('clicked', self.new_membership, page)
    page.memberships_panel.connect('ask-delete-membership', self.ask_delete_membership)
    page.memberships_panel.connect('add-installments', self.add_installments, page)
    page.memberships_panel.connect('add-payment', self.add_payment, page)
    page.memberships_panel.connect('delete-payment', self.ask_delete_payment, page)
    page.memberships_panel.connect('delete-installment', self.ask_delete_installment, page)
    self.save_signal(self.connect('membership-deleted', page.on_membership_deleted), page)
    self.save_signal(self.connect('payment-deleted', page.on_payment_deleted), page)
    self.save_signal(self.connect('installment-deleted', page.on_installment_deleted), page)
    self.window.add_page(page)
    return page

  def submit_user(self, form):
    user = form.object
    new_record = user.is_new_record()
    user.set_attrs(form.get_values())
    if user.save():
      self.emit('user-changed', user, new_record)
      self.window.update_label(form)
      if new_record:
        form.enable_memberships()
    else:
      ErrorMessage("No se puede guardar el " + translations._m(user.cls_name()) + ":", user.full_errors()).run()

  def search_student(self, widget):
    page = SearchStudent()
    self.window.add_page(page)
    page.connect('search', self.on_student_search)
    page.connect('student-edit', self.edit_student)
    page.connect('student-add', self.add_student)
    page.connect('student-delete', self.ask_delete_student)
    self.save_signal(self.connect('user-changed', page.on_search), page)
    self.save_signal(self.connect('student-deleted', page.on_search, None), page)
  
  def on_student_search(self, page, value):
    students = Student.search(value)
    page.update_results(students)

  def open_fb(self, page):
    facebook_uid = page.facebook_uid_e.get_text()
    if facebook_uid:
      if not re.match('https://www.facebook.com/',facebook_uid):
        facebook_uid = 'https://www.facebook.com/'+facebook_uid
      webbrowser.open_new_tab(facebook_uid)
    else:
      ErrorMessage('No se puede abrir la página de Facebook de la persona:', 'No se cargó una ID de facebook').run()

  def ask_delete_student(self, page, student):
    student = Student.find(student.id)
    if student:
      can_delete = student.can_delete()
      if can_delete is True:
        dialog = ConfirmDialog('Vas a borrar al alumno: '+student.to_label()+":\n¿Estás seguro?")
        dialog.connect('response', self.delete_student, student)
        dialog.run()
      else:
        ErrorMessage("No se puede borrar al alumno:", can_delete).run()

  def delete_student(self, dialog, response, student):
    if response == gtk.RESPONSE_ACCEPT:
      deleted = student.delete()
      if deleted is True:
        self.emit('student-deleted', student.id)
      else:
        ErrorMessage("No se puede borrar al alumno:", deleted).run()
    dialog.destroy()


  #klasses controls
  def add_klass(self, widget, room = '', time = '', day_idx = 0):
    klass = Klass()
    room = Room.find_by('name',room)
    if room and time:
      klass.build_schedule({'from_time': time, 'room': room, 'day': day_idx})
    page = self.klass_form(widget, klass)
  
  def edit_klass(self, widget, klass_id):
    klass = Klass.find(klass_id)
    page = self.klass_form(widget, klass)
  
  def klass_form(self, widget, klass):
    if klass.is_not_new_record():
      current = self.window.get_page_by_object(klass)
      if current:
        self.window.focus_page(current)
        return current

    page = KlassForm(klass)
    page.submit.connect_object('clicked',self.submit_klass, page)
    page.connect('schedule-edit', self.edit_schedule)
    page.connect('schedule-add', self.add_schedule)
    page.connect('schedule-remove', self.remove_schedule)
    page.connect('teacher-search', self.show_select_teacher_dialog)
    page.connect('teacher-remove', self.on_remove_teacher)
    page.connect('list-students', self.on_list_students)
    self.window.add_page(page)
    return page

  def show_schedules(self, widget):
    current = self.window.get_page_by_label(SchedulesTables.tab_label())
    if current:
      self.window.focus_page(current)
      return current

    klasses = Klass.by_room_and_time(self.settings.get_opening_h(), self.settings.get_closing_h())
    page = SchedulesTables(klasses)
    self.window.add_page(page)
    page.connect('klass-edit', self.edit_klass)
    page.connect('klass-add', self.add_klass)
    self.save_signal(self.connect('klass-changed', self.refresh_schedules, page), page)
    return page

  def list_klasses(self, widget):
    current = self.window.get_page_by_label(KlassesList.tab_label())
    if current:
      self.window.focus_page(current)
      return current

    klasses = Klass.all()
    page = KlassesList(klasses)
    self.window.add_page(page)
    page.connect('klass-edit', self.edit_klass)
    page.connect('klass-add', self.add_klass)
    page.connect('klass-delete', self.ask_delete_klass)
    self.save_signal(self.connect('klass-changed', self.refresh_klasses, page), page)
    self.save_signal(self.connect('klass-deleted', self.refresh_klasses, None, page), page)
    return page

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
    else:
      ErrorMessage("No se puede guardar la clase:", kls.full_errors()).run()

  def ask_delete_klass(self, page, klass):
    klass = Klass.find(klass.id)
    if klass:
      can_delete = klass.can_delete()
      if can_delete is True:
        dialog = ConfirmDialog('Vas a borrar la clase: '+klass.name+":\n¿Estás seguro?")
        dialog.connect('response', self.delete_klass, klass)
        dialog.run()
      else:
        ErrorMessage("No se puede borrar la clase:", can_delete).run()

  def delete_klass(self, dialog, response, klass):
    if response == gtk.RESPONSE_ACCEPT:
      deleted = klass.delete()
      if deleted is True:
        self.emit('klass-deleted', klass.id)
      else:
        ErrorMessage("No se puede borrar la clase:", deleted).run()
    dialog.destroy()

  def show_select_teacher_dialog(self, page):
    teachers = Teacher.get(exclude = page.object.teacher_ids())
    dialog = SelectTeacherDialog(teachers)
    dialog.connect('response', self.select_teacher_dialog_response, page)
    dialog.run()

  def select_teacher_dialog_response(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      teacher = dialog.get_selected_teacher()
      if teacher is not None:
        page.object.add_teacher(teacher)
        page.update_teachers()

    if destroy_dialog:
      dialog.destroy()

  def on_remove_teacher(self, page, teacher):
    if teacher is not None:
      for t in page.object.teachers:
        if teacher.id == t.id:
          page.object.remove_teacher(t)
          page.update_teachers()

  def on_list_students(self, page):
    dialog = StudentsListDialog(page.object)
    dialog.list.connect_object('student-activated', self.on_student_activated, dialog)
    dialog.export.connect_object('clicked', self.export_klass_students, dialog, page.object)
    dialog.connect('response', self.students_list_dialog_response)
    dialog.run()

  def students_list_dialog_response(self, dialog, response):
    dialog.destroy()

  def on_student_activated(self,dialog,student):
    dialog.destroy()
    self.edit_student(dialog,student.id)

  def export_klass_students(self, dialog, klass):
    table_html = dialog.list.to_html()
    title = '<h1>Alumnos de la clase: '+klass.name+'</h1>'
    self.export(exporter.html_wrapper(title+table_html))



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
        if schedule in page.object.schedules:
          page.update_schedules()
        else:
          page.add_schedule(schedule)
      else:
        destroy_dialog = False
        ErrorMessage("No se puede guardar el horario:", schedule.full_errors()).run()

    elif response == gtk.RESPONSE_DELETE_EVENT:
      self.remove_schedule(page,schedule)

    if destroy_dialog:
      dialog.destroy()

  def remove_schedule(self, page, schedule):
    page.object.remove_schedule(schedule)
    page.update_schedules()




  #packages controls
  def show_packages(self, widget):
    current = self.window.get_page_by_label(PackagesList.tab_label())
    if current:
      self.window.focus_page(current)
      return current

    page = PackagesList(Package.all())
    self.window.add_page(page)
    page.connect('package-add',self.add_package)
    page.connect('package-edit', self.edit_package)
    page.connect('package-delete', self.ask_delete_package)
    self.save_signal(self.connect('package-changed', self.refresh_packages, page), page)
    self.save_signal(self.connect('package-deleted', self.refresh_packages, None, page), page)
    return page

  def add_package(self, widget):
    package = Package()
    klasses = Klass.all()
    return self.package_form(package, klasses)
  
  def edit_package(self, widget, package_id):
    package = Package.find(package_id)
    return self.package_form(package)

  def package_form(self, package, klasses = None):
    if package.is_not_new_record():
      current = self.window.get_page_by_object(package)
      if current:
        self.window.focus_page(current)
        return current

    page = PackageForm(package, klasses)
    page.submit.connect_object('clicked', self.submit_package, page)
    self.window.add_page(page)
    return page

  def submit_package(self, form):
    package = form.object
    new_record = package.is_new_record()
    package.set_attrs(form.get_values())
    if package.save():
      self.close_tab(None, form)
      self.emit('package-changed', package, new_record)
    else:
      ErrorMessage("No se puede guardar el paquete:", package.full_errors()).run()

  def refresh_packages(self, widget, package, created, page):
    packages = Package.all()
    page.refresh_list(packages)

  def ask_delete_package(self, page, package):
    package = Package.find(package.id)
    if package:
      can_delete = package.can_delete()
      if can_delete is True:
        dialog = ConfirmDialog('Vas a borrar el paquete: '+package.name+":\n¿Estás seguro?")
        dialog.connect('response', self.delete_package, package)
        dialog.run()
      else:
        ErrorMessage("No se puede borrar el paquete:", can_delete).run()

  def delete_package(self, dialog, response, package):
    if response == gtk.RESPONSE_ACCEPT:
      deleted = package.delete()
      if deleted is True:
        self.emit('package-deleted', package.id)
      else:
        ErrorMessage("No se puede borrar el paquete:", deleted).run()
    dialog.destroy()




  # memberships
  def new_membership(self, page):
    membership = Membership()
    klasses = Klass.all()
    packages = Package.all()
    
    options = klasses.do_get() + packages.do_get()

    for m in page.object.memberships:
      for o in options:
        if m.for_id == o.id and m.for_type == o.cls_name():
          options.remove(o)

    if options:
      dialog = MembershipDialog(membership, options)
      dialog.connect('response', self.on_new_membership, page)
      dialog.run()
    else:
      ErrorMessage("No se puede inscribir:", 'El alumno se encuentra inscripto en todas las clases.').run()

  def on_new_membership(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      if dialog.form.get_selected_klass_or_package() is None:
        ErrorMessage("No se puede guardar la inscripción:", "La clase (o paquete) ingresada no es válida.").run()
        destroy_dialog = False
      else:
        membership = dialog.form.object
        membership.set_attrs(dialog.form.get_values())
        membership.student_id = page.object.id
        if membership.save():
          page.object.reload_memberships()
          page.update()
        else:
          ErrorMessage("No se puede guardar la inscripción:", membership.full_errors()).run()
          destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_membership(self, widget, membership):
    dialog = ConfirmDialog('Vas a borrar la inscripción a '+membership.klass_or_package.name+"\n¿Estás seguro?")
    dialog.connect('response', self.delete_membership, membership)
    dialog.run()

  def delete_membership(self, dialog, response, membership):
    if response == gtk.RESPONSE_ACCEPT:
      membership.student.reload_memberships()
      membership.delete()
      self.emit('membership-deleted', membership.id)

    dialog.destroy()

  def add_installments(self, widget, membership, page):
    dialog = AddInstallmentsDialog(membership)
    dialog.connect('response', self.on_add_installments, page)
    dialog.run()
  
  def on_add_installments(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      membership = dialog.membership
      data = dialog.form.get_values()
      created = membership.create_installments(data['year'],data['initial_month'],data['final_month'],data['fee'])
      if created is True:
        page.update()
      else:
        ErrorMessage('No se pudieron agrega las cuotas:', created).run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_installment(self, widget, installment, page):
    dialog = ConfirmDialog('Vas a borrar la cuota de '+installment.to_label()+"\n¿Estás seguro?")
    dialog.connect('response', self.delete_installment, installment)
    dialog.run()

  def delete_installment(self, dialog, response, installment):
    if response == gtk.RESPONSE_ACCEPT:
      installment.delete()
      self.emit('installment-deleted', installment.id)

    dialog.destroy()





  #payments controls
  def add_payment(self, widget, installment, done, page):
    payment = Payment()
    if installment:
      payment.amount = installment.to_pay()
      payment.installment = installment
    payment.user = page.object
    payment.done = done

    dialog = AddPaymentDialog(payment)
    dialog.connect('response', self.on_add_payment, page, installment)
    dialog.run()
  
  def on_add_payment(self, dialog, response, page, installment = None):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      data = dialog.form.get_values()
      if installment is not None:
        added = installment.add_payment(data)
      else:
        payment = dialog.payment
        payment.set_attrs(data)
        added = payment.save()
        if added is False:
          added = payment.full_errors()
        else:
          added = payment
      if added:
        if isinstance(added, Payment): self.emit('payment-changed', added, True)
        page.update()
      else:
        ErrorMessage('No se pudo cargar el pago:', added).run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_payment(self, widget, payment, page):
    dialog = ConfirmDialog('Vas a borrar el pago: '+payment.description+"\n¿Estás seguro?")
    dialog.connect('response', self.delete_payment, payment)
    dialog.run()

  def delete_payment(self, dialog, response, payment):
    if response == gtk.RESPONSE_ACCEPT:
      payment.delete()
      self.emit('payment-deleted', payment.id)

    dialog.destroy()



  #resports
  def payments_report(self, menu_item):
    today = datetime.datetime.today().date()
    page = PaymentsReport(Payment.filter(today,today,False),User.all(), Klass.all(), Package.all())
    page.export_html.connect_object('clicked', self.export_payments_report_html, page)
    page.export_csv.connect_object('clicked', self.export_payments_report_csv, page)
    page.filter.connect_object('clicked', self.filter_payments, page)
    page.connect('student-edit', self.edit_student)
    self.window.add_page(page)
    return page

  def filter_payments(self, page):
    f = page.get_from()
    t = page.get_to()
    received = page.get_done_or_received()
    user = page.get_selected_user()
    k_or_p = page.get_selected_klass_or_package()
    payments = Payment.filter(f,t,received,user,k_or_p)
    page.update(payments)

  def export_payments_report_html(self, page):
    self.export_html(page.to_html())
    
  def export_payments_report_csv(self, page):
    self.export_csv(page.to_csv(), page.csv_filename())
      

  def daily_cash(self, menu_item):
    today = datetime.datetime.today().date()
    page = DailyCashReport(Payment.filter(today,today,None), Movement.by_date(today))
    page.export_html.connect_object('clicked', self.export_daily_cash_html, page)
    page.export_csv.connect_object('clicked', self.export_daily_cash_csv, page)
    page.filter.connect_object('clicked', self.filter_daily_cash, page)
    self.window.add_page(page)
    return page

  def filter_daily_cash(self, page):
    date = page.get_date()
    payments = Payment.filter(date,date,None)
    movements = Movement.by_date(date)
    page.update(payments = payments, movements = movements)

  def export_daily_cash_html(self, page):
    self.export_html(page.to_html())

  def export_daily_cash_csv(self, page):
    self.export_csv(page.to_csv(),page.csv_filename())


  def overdue_installments(self, menu_item):
    page = OverdueInstallments(Installment.overdues(), Klass.all())
    page.filter.connect_object('clicked', self.filter_overdues, page)
    page.export_html.connect_object('clicked', self.export_overdue_installments_report_html, page)
    page.export_csv.connect_object('clicked', self.export_overdue_installments_report_csv, page)
    page.connect('student-edit', self.edit_student)
    self.window.add_page(page)
    return page

  def filter_overdues(self, page):
    klass = page.get_selected_klass()
    installments = Installment.overdues(klass=klass)
    page.update(installments)

  def export_overdue_installments_report_html(self, page):
    self.export_html(page.to_html())

  def export_overdue_installments_report_csv(self, page):
    self.export_csv(page.to_csv(), page.csv_filename())

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

  def export_html(self, html):
    f, path = tempfile.mkstemp('.html')
    f = open(path,'w')
    f.write(html)
    f.close
    webbrowser.open_new_tab(path)

  def export_csv(self, csv_content, csv_filename = None):
    dialog = gtk.FileChooserDialog(title='Guardar como...', action=gtk.FILE_CHOOSER_ACTION_SAVE, buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
    if csv_filename is not None: dialog.set_current_name(csv_filename)
    if self.settings.export_path is not None: dialog.set_current_folder(self.settings.export_path)
    dialog.connect('response', self.on_export_csv_file, csv_content)
    dialog.set_do_overwrite_confirmation(True)
    dialog.run()
  
  def on_export_csv_file(self, dialog, response, csv_content):
    if response == gtk.RESPONSE_OK:
      self.settings.export_path = dialog.get_current_folder()
      self.settings.save()
      path = dialog.get_filename()
      f = open(path, 'w')
      f.write(csv_content)
      f.close()
    
    dialog.destroy()


  def current_page(self):
    return self.window.current_page()

gobject.type_register(Controller)
gobject.signal_new('user-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #user object, creation(True value means the user just got created)

gobject.signal_new('klass-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #klass object, creation(True value means the klass just got created)
                   
gobject.signal_new('package-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #package object, creation(True value means the package just got created)

gobject.signal_new('room-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #room object, creation(True value means the room just got created)

gobject.signal_new('payment-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool ))
                   #payment object, creation(True value means the payment just got created)

gobject.signal_new('klass-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #klass id

gobject.signal_new('teacher-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #teacher id

gobject.signal_new('student-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #student id

gobject.signal_new('installment-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #installment id

gobject.signal_new('membership-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #membership id

gobject.signal_new('package-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #package id

gobject.signal_new('payment-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #payment id

gobject.signal_new('movement-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int,))
                   #payment id


gobject.signal_new('settings-changed', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())

def main(argv):
  env = 'dev'
  try:
    opts, args = getopt.getopt(argv,"e:",["env="])
    for opt, arg in opts:
      if opt in ('-e', '--env'):
        env = arg
  except getopt.GetoptError:
    print "args error"
  ctrlr = Controller(env = env)
  ctrlr.main()

if __name__ == "__main__":
  main(sys.argv[1:])

