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
import constants
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
    self.window.menu.installments.connect('activate', self.installments_report)
    self.window.menu.debts.connect('activate', self.debts)
    self.window.menu.receipts.connect('activate', self.receipts)
    self.window.menu.students_hours.connect('activate', self.students_hours_report)
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
    self.connect_object('klass-deactivated', self.show_status, 'Clase desactivada.')
    self.connect_object('klass-reactivated', self.show_status, 'Clase reactivada.')

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
    today_birthdays = user.User.birthday_today()
    page = Home(klasses, notes, installments, payments, movements, today_birthdays)
    page.connect('student-edit', self.edit_student)
    page.notes.save.connect_object('clicked',self.save_notes, page)
    page.daily_cash.movements_l.add_b.connect_object('clicked', self.add_movement_dialog, page)
    page.daily_cash.movements_l.delete_b.connect_object('clicked', self.ask_delete_movement, page)
    page.daily_cash.movements_l.mark_closers.connect_object('clicked', self.mark_closers, page)
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
        self.update_home_movements(page)
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
      self.emit('movement-deleted', movement)

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
      page.refresh_installment_fees.connect('clicked', self.refresh_installment_fees, page)
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

  def refresh_installment_fees(self, button, page):
    #for p in Package.all():
    #  if int(p.fee) != int(p.get_hours_fee()):
    #    p.fee = p.get_hours_fee()
    #    p.save()

    for i in Installment.where('status','waiting'):
      m = i.membership
      if m:
        a1 = i.amount
        a2 = 0
        if m.for_type == 'Package':
          a2 = m.klass_or_package.get_hours_fee()
        else:
          a2 = m.klass_or_package.get_hours_fee('normal')
        if a1 < int(a2):
          i.amount = a2
          i.save()


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

  def edit_teacher(self, widget, teacher_id):
    teacher = Teacher.find(teacher_id)
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
    page.connect('query-reorder', self.reorder_teachers)
    self.save_signal(self.connect('user-changed', self.refresh_teachers, page), page)
    self.save_signal(self.connect('teacher-deleted', self.refresh_teachers, None, page), page)
    return page

  def reorder_teachers(self, page, attr):
    teachers = Teacher.get().order_by(attr)
    page.refresh_list(teachers)

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
        self.emit('teacher-deleted', teacher)
      else:
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

  def edit_student(self, widget, student_id, extra = None):
    student = Student.find(student_id)
    page = self.user_form(student)
    if isinstance(extra, Payment):
      if extra.installment is not None: page.show_installment(extra.installment)
    if isinstance(extra, Installment): page.show_installment(extra)

  def user_form(self, user):
    if user.is_not_new_record():
      current = self.window.get_page_by_object(user)
      if current:
        self.window.focus_page(current)
        return current

    page = UserForm(user)
    page.submit.connect_object('clicked', self.submit_user, page)
    page.inactivate.connect_object('clicked', self.inactivate_user, page)
    page.activate.connect_object('clicked', self.reactivate_user, page)
    page.open_fb.connect_object('clicked', self.open_fb, page)
    page.connect('create-user-package', self.new_user_package)
    page.connect('add-membership', self.new_membership)
    page.connect('ask-delete-membership', self.ask_delete_membership)
    page.connect('add-installments', self.add_installments)
    page.connect('add-payment', self.add_payment)
    page.connect('add-payments', self.add_payments)
    page.connect('add-liability', self.add_liability)
    page.connect('delete-payments', self.ask_delete_payments)
    page.connect('delete-installments', self.ask_delete_installments)
    page.connect('delete-liabilities', self.ask_delete_liabilities)
    page.connect('edit-package', self.edit_user_package)
    page.connect('print-payments', self.print_payments)
    page.connect('edit-installment', self.edit_installment)
    page.connect('edit-installment-payments', self.edit_installment_payments)
    page.connect('edit-payment', self.edit_payment)
    page.add_family.connect('clicked', self.on_add_family_clicked, page)
    page.remove_family.connect('clicked', self.on_remove_family_clicked, page)
    self.save_signal(self.connect('membership-deleted', page.on_membership_deleted), page)
    self.save_signal(self.connect('payment-deleted', page.on_payment_deleted), page)
    self.save_signal(self.connect('installment-deleted', page.on_installment_deleted), page)
    self.save_signal(self.connect('liability-deleted', page.on_liability_deleted), page)
    self.window.add_page(page)
    return page

  def on_add_family_clicked(self, widget, page):
    dialog = AddFamilyDialog(User.where('(family IS NULL OR family != :family) AND id != :id', {'family': page.object.family, 'id': page.object.id}))
    dialog.connect('response', self.on_add_family_response, page)
    dialog.run()

  def on_add_family_response(self, dialog, response, page):
    if response == gtk.RESPONSE_ACCEPT:
      page.object.add_family_member(dialog.get_selected_user())
      page.refresh_family()
    dialog.destroy()

  def on_remove_family_clicked(self, widget, page):
    page.object.remove_family_member(page.get_selected_family_member())
    page.refresh_family()

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
    page.connect('students-export-html', self.students_export_html, page)
    page.connect('students-export-csv', self.students_export_csv, page)
    page.results.connect('query-reorder', self.reorder_students, page)
    self.save_signal(self.connect('user-changed', page.on_search), page)
    self.save_signal(self.connect('student-deleted', page.on_search, None), page)

  def students_export_html(self, button, page):
    self.export_html(page.to_html())

  def students_export_csv(self, button, page):
    self.export_csv(page.to_csv(), page.csv_filename())

  def reorder_students(self, table, attr, page):
    value = page.form.get_value()
    group = page.form.get_group()
    students = Student.search(value, group).order_by(attr)
    page.update_results(students)

  def on_student_search(self, page, value, group = None, active_status = None):
    students = Student.search(value, group)
    if active_status != 2:
      students = students.where('inactive', active_status)
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
        self.emit('student-deleted', student)
      else:
        ErrorMessage("No se puede borrar al alumno:", deleted).run()
    dialog.destroy()

  def inactivate_user(self, form):
    form.user.inactivate()
    form.update_user_status()

  def reactivate_user(self, form):
    form.user.reactivate()
    form.update_user_status()


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

    klasses = Klass.active()
    page = KlassesList(klasses)
    self.window.add_page(page)
    page.connect('klass-edit', self.edit_klass)
    page.connect('klass-add', self.add_klass)
    page.connect('klass-delete', self.ask_delete_klass)
    page.connect('klass-deactivate', self.deactivate_klass)
    page.connect('klass-reactivate', self.reactivate_klass)
    page.klass_e.connect('changed',self.filter_klasses, page)
    page.include_inactive_cb.connect('toggled', self.filter_klasses, page)
    self.save_signal(self.connect('klass-changed', self.refresh_klasses, page), page)
    self.save_signal(self.connect('klass-reactivated', self.refresh_klasses, None, page), page)
    self.save_signal(self.connect('klass-deactivated', self.refresh_klasses, None, page), page)
    self.save_signal(self.connect('klass-deleted', self.refresh_klasses, None, page), page)
    return page

  def filter_klasses(self, entry, page):
    t = page.klass_e.get_text().strip()
    klasses = Klass.all() if page.include_inactive() else Klass.active()
    if t != '':
      klasses = klasses.where('name LIKE :name',{'name': '%'+page.klass_e.get_text()+'%'})
    page.refresh_list(klasses)

  def refresh_schedules(self, widget, kls, created, page):
    klasses = Klass.by_room_and_time(self.settings.get_opening_h(), self.settings.get_closing_h())
    page.refresh_tables(klasses)

  def refresh_klasses(self, widget, kls, created, page):
    klasses = Klass.all() if page.include_inactive() else Klass.active()
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
        self.emit('klass-deleted', klass)
      else:
        ErrorMessage("No se puede borrar la clase:", deleted).run()
    dialog.destroy()

  def deactivate_klass(self, widget, klass):
    klass.inactivate()
    self.emit('klass-deactivated', klass)

  def reactivate_klass(self, widget, klass):
    klass.reactivate()
    self.emit('klass-reactivated', klass)


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
    dialog.list.connect('query-reorder', self.reorder_klass_students, page.object)
    dialog.export_csv.connect_object('clicked', self.export_klass_students_csv, dialog, page.object)
    dialog.export_html.connect_object('clicked', self.export_klass_students_html, dialog, page.object)
    dialog.connect('response', self.students_list_dialog_response)
    dialog.run()

  def reorder_klass_students(self, table, attr, klass):
    students = klass.get_students().order_by(attr)
    table.update_table(students)

  def students_list_dialog_response(self, dialog, response):
    dialog.destroy()

  def on_student_activated(self,dialog,student):
    dialog.destroy()
    self.edit_student(dialog,student.id)

  def export_klass_students_html(self, dialog, klass):
    table_html = dialog.list.to_html()
    title = '<h1>Alumnos de la clase: '+klass.name+'</h1>'
    self.export_html(exporter.html_wrapper(title+table_html))

  def export_klass_students_csv(self, dialog, klass):
    table_csv = dialog.list.to_csv()
    filename = 'alumnos_'+exporter.string_to_csv_filename(klass.name)+'.csv'
    self.export_csv(table_csv,filename)



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

    page = PackagesList(Package.where('for_user', 0))
    self.window.add_page(page)
    page.connect('package-add',self.add_package)
    page.connect('package-edit', self.edit_package)
    page.connect('package-delete', self.ask_delete_package)
    page.package_e.connect('changed',self.filter_packages, page)
    self.save_signal(self.connect('package-changed', self.refresh_packages, page), page)
    self.save_signal(self.connect('package-deleted', self.refresh_packages, None, page), page)
    return page

  def filter_packages(self, entry, page):
    t = entry.get_text().strip()
    packages = Package.all()
    if t != '':
      packages = packages.where('name LIKE :name',{'name': '%'+entry.get_text()+'%'})
    page.refresh_list(packages)

  def add_package(self, widget):
    package = Package()
    klasses = Klass.all()
    return self.package_form(package, klasses)

  def edit_user_package(self, page, package):
    dialog = EditUserPackageDialog(package, Klass.by_day())
    dialog.connect('response', self.on_update_user_package, page)
    dialog.run()

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
        self.emit('package-deleted', package)
      else:
        ErrorMessage("No se puede borrar el paquete:", deleted).run()
    dialog.destroy()

  def new_user_package(self, page):
    dialog = NewUserPackageDialog(Klass.by_day())
    dialog.connect('response', self.on_new_user_package, page)
    dialog.run()

  def on_new_user_package(self, dialog, response, page):
    if response == gtk.RESPONSE_ACCEPT:
      klasses = dialog.form.get_checked_klasses()
      if len(klasses) > 0:
        package = Package.for_user_with_klasses(klasses)
        package.for_user = page.user.id
        package.fee = dialog.form.get_amount()
        package.save()
        membership = Membership()
        membership.klass_or_package = package
        membership.student = page.user
        if membership.save() is True: page.membership_added(membership)

        if dialog.form.should_create_installments() is True:
          created = membership.create_installments(datetime.date.today().year, dialog.form.get_initial_month(), dialog.form.get_final_month(), dialog.form.get_amount())

          if created is True: page.update()

        dialog.destroy()
      else:
        ErrorMessage("No se puede crear el paquete:", 'Tenés que elegir al menos una clase').run()
    else:
      dialog.destroy()

  def on_update_user_package(self, dialog, response, page):
    if response == gtk.RESPONSE_ACCEPT:
      klasses = dialog.form.get_checked_klasses()
      if len(klasses) > 0:
        p = dialog.package
        old_p = False
        if p.for_user != page.user.id:
          old_p = p
          p = Package()
          p.for_user = page.user.id
        p.klasses = klasses
        ids = sorted(map(lambda k: k.id, klasses))
        p.name = 'Clases ' + str(datetime.date.today().year) + ' (' + ','.join(map(lambda i: str(i), ids)) + ')'
        p.fee = dialog.form.get_amount()
        if p.save() is True:
          if old_p:
            m = Membership.for_student_and_klass_or_package(page.user, old_p)
            m.klass_or_package = p
            m.save()
          page.update()
          dialog.destroy()
        else:
          ErrorMessage("No se puede crear el paquete:", package.full_errors()).run()
      else:
        ErrorMessage("No se puede crear el paquete:", 'Tenés que elegir al menos una clase').run()
    else:
      dialog.destroy()

  # memberships
  def new_membership(self, page):
    membership = Membership()
    klasses = Klass.all()
    packages = Package.where('for_user', 0)

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
          page.membership_added(membership)
        else:
          ErrorMessage("No se puede guardar la inscripción:", membership.full_errors()).run()
          destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_membership(self, page, membership):
    dialog = ConfirmDialog('Vas a borrar la inscripción a '+membership.klass_or_package.name+"\n¿Estás seguro?")
    dialog.connect('response', self.delete_membership, membership)
    dialog.run()

  def delete_membership(self, dialog, response, membership):
    if response == gtk.RESPONSE_ACCEPT:
      membership.student.reload_memberships()
      membership.delete()
      self.emit('membership-deleted', membership)

    dialog.destroy()

  def add_installments(self, page, membership):
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

  def ask_delete_installments(self, page, installments):
    dialog = DeleteInstallmentDialog(installments)
    dialog.connect('response', self.delete_installments, installments)
    dialog.run()

  def delete_installments(self, dialog, response, installments):
    if response == gtk.RESPONSE_ACCEPT:
      for i in installments:
        if dialog.delete_payments():
          for p in i.payments:
            p.delete()
        i.delete()
      self.emit('installment-deleted', i)

    dialog.destroy()

  def edit_installment(self, widget, installment):
    dialog = EditInstallmentDialog(installment)
    dialog.connect('response', self.on_edit_installment, widget)
    dialog.run()

  def on_edit_installment(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      ins = dialog.installment
      amount = dialog.get_amount()
      if amount < ins.paid():
        ErrorMessage('No se pueden editar la cuota:', 'Tiene pagos cargados por un valor mayor.').run()
        destroy_dialog = False
      elif ins.amount != Money(amount):
        ins.amount = amount
        ins.update_status()
        page.update()

    if destroy_dialog: dialog.destroy()





  #payments controls
  def add_payment(self, page, related, done):
    if related:
      if len(related) > 1:
        ErrorMessage('No se pueden cargar pagos:', 'Tenés que seleccionar una sola cuota/deuda.').run()
        return
      else:
        related = related[0]

    if related and related.to_pay() == 0:
      ErrorMessage('No se pueden cargar pagos:', 'La cuota/deuda seleccionada ya está pagada.').run()
    else:
      payment = Payment()
      payment.user = page.object
      payment.done = done
      if isinstance(related, Installment):
        payment.installment = related
        payment.amount = related.to_pay()
      elif isinstance(related, Liability):
        payment.liability = related
        payment.amount = related.to_pay()

      dialog = AddPaymentDialog(payment)
      dialog.connect('response', self.on_add_payment, page, related)
      dialog.run()

  def add_payments(self, page):
    installments = Installment.to_pay_for(page.object)

    if len(installments) == 0:
      ErrorMessage('No se pueden cargar pagos:', 'No hay cuotas para pagar.').run()
    else:
      dialog = AddPaymentsDialog(installments)
      dialog.connect('response', self.on_add_payments, page)
      dialog.run()

  def on_add_payment(self, dialog, response, page, related = None):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT or response == constants.SAVE_AND_PRINT:
      data = dialog.form.get_values()
      if isinstance(related, Installment):
        added = related.add_payment(data)
      elif isinstance(related, Liability):
        added = related.add_payment(data)
      else:
        payment = dialog.payment
        payment.set_attrs(data)
        added = payment.save()
        if added is False:
          added = payment.full_errors()
        else:
          added = payment
      if added:
        if isinstance(added, Payment):
          if response == constants.SAVE_AND_PRINT: Receipt([added]).do_print()
          self.emit('payment-changed', added, True)
        page.update()
      else:
        ErrorMessage('No se pudo cargar el pago:', added).run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def on_add_payments(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT or response == constants.SAVE_AND_PRINT:
      installments = dialog.get_selected_installments()
      if installments:
        if len(installments) == 1:
          installment = installments[0]
          added = installment.add_payment({'amount': dialog.get_amount(), 'date': dialog.date_e.get_text()})
          if added:
            if isinstance(added, Payment): self.emit('payment-changed', added, True)
            page.update()
          else:
            ErrorMessage('No se pudo cargar el pago:', added).run()
            destroy_dialog = False
        else:
          amount_paid = dialog.get_amount()
          total = sum(map(lambda i: i.to_pay(), installments))

          if total < amount_paid:
            ErrorMessage('No se pueden cargar los pagos:', 'El monto ingresado es mayor al monto a pagar').run()
            destroy_dialog = False
          else:
            rest = amount_paid
            payments = []
            for i in installments:
              if rest > 0:
                amount = i.to_pay()
                if amount > rest: amount = rest
                payments.append(i.add_payment({'date': dialog.date_e.get_text(), 'amount': amount}))
                rest -= amount
            if response == constants.SAVE_AND_PRINT: Receipt(payments).do_print()
            self.emit('payment-changed', None, True)
            page.update()

      else:
        ErrorMessage('No se pueden cargar los pagos:', 'No se seleccionó ninguna cuota.').run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_payments(self, page, payments):
    descriptions = "\n".join(map(lambda p: p.description, payments))
    dialog = ConfirmDialog("Vas a borrar los pagos:\n"+descriptions+"\n\n¿Estás seguro?")
    dialog.connect('response', self.delete_payments, payments)
    dialog.run()

  def delete_payments(self, dialog, response, payments):
    if response == gtk.RESPONSE_ACCEPT:
      for p in payments:
        p.delete()
        self.emit('payment-deleted', p)

    dialog.destroy()

  def print_payments(self, widget, payments):
    r = Receipt(payments)
    r.do_print()
    widget.update()

  def edit_installment_payments(self, widget, installment):
    dialog = EditInstallmentPaymentsDialog(installment)
    dialog.connect('response', self.on_edit_installment_payments, widget)
    dialog.run()

  def on_edit_installment_payments(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      data = dialog.get_payments_data()
      total = Money(0)
      for p_id, p_data in data.iteritems():
        if not p_data['remove']: total += Money(p_data['amount'])

      if total > dialog.installment.total():
        ErrorMessage('No se pueden editar los pagos:', 'El total de los pagos es mayor que el valor de la cuota.').run()
        destroy_dialog = False
      else:
        for p_id, p_data in data.iteritems():
          payment = Payment.find(p_id)
          if p_data['remove']:
            payment.delete()
            self.emit('payment-deleted', payment)
          else:
            if payment.str_date() != p_data['date'] or payment.amount != Money(p_data['amount']) or payment.description != p_data['description']:
              payment.date = p_data['date']
              payment.amount = Money(p_data['amount'])
              payment.description = p_data['description']
              #payment.receipt_number = p_data['receipt_number']
              if payment.save(): self.emit('payment-changed', payment, False)
        dialog.installment.update_status()
        page.update()

    if destroy_dialog: dialog.destroy()

  def edit_payment(self, widget, payment):
    dialog = AddPaymentDialog(payment)
    dialog.connect('response', self.on_edit_payment, widget)
    dialog.run()

  def on_edit_payment(self, dialog, response, page):
    if response == gtk.RESPONSE_ACCEPT:
      data = dialog.form.get_values()
      payment = dialog.payment
      if payment.str_date() != data['date'] or payment.amount != data['amount'] or payment.description != data['description']:
        payment.date = data['date']
        payment.amount = data['amount']
        payment.description = data['description']
        #payment.receipt_number = p_data['receipt_number']
        if payment.save():
          self.emit('payment-changed', payment, False)
          page.update()

    dialog.destroy()




  #liabilities controls
  def add_liability(self, page):
    dialog = AddLiabilityDialog(page.object.new_liability())
    dialog.connect('response', self.on_add_liability, page)
    dialog.run()

  def on_add_liability(self, dialog, response, page):
    destroy_dialog = True
    if response == gtk.RESPONSE_ACCEPT:
      liability = dialog.form.object
      liability.set_attrs(dialog.form.get_values())
      liability.user_id = page.object.id
      if liability.save() is True:
        page.update()
      else:
        ErrorMessage('No se pudo agregar la deuda:', created).run()
        destroy_dialog = False

    if destroy_dialog:
      dialog.destroy()

  def ask_delete_liabilities(self, page, liabilities):
    dialog = DeleteLiabilitiesDialog(liabilities)
    dialog.connect('response', self.delete_liability, liabilities)
    dialog.run()

  def delete_liability(self, dialog, response, liabilities):
    if response == gtk.RESPONSE_ACCEPT:
      for l in liabilities:
        if dialog.delete_payments():
          for p in l.payments: p.delete()
        l.delete()
        self.emit('liability-deleted', l)

    dialog.destroy()




  #reports
  def payments_report(self, menu_item):
    today = datetime.datetime.today().date()
    page = PaymentsReport(Payment.filter(today,today,False), Movement.by_date(today,today).incoming(),User.all(), Klass.all(), Package.all())
    page.export_html.connect_object('clicked', self.export_payments_report_html, page)
    page.export_csv.connect_object('clicked', self.export_payments_report_csv, page)
    page.connect('print-payments', self.print_payments)
    page.filter.connect_object('clicked', self.filter_payments, page)
    page.connect('student-edit', self.edit_student)
    self.window.add_page(page)
    return page

  def filter_payments(self, page):
    f = page.get_from()
    t = page.get_to()
    done_or_received = page.get_done_or_received()
    user = page.get_selected_user()
    k_or_p = page.get_selected_klass_or_package()
    q_term = page.get_filter()
    inactive = page.should_include_inactive()
    payments = Payment.filter(f,t, done_or_received, user, k_or_p,page.get_group(), page.get_receipt_number(), q_term, inactive)
    if user is None and k_or_p is None and page.get_group() == '' and page.get_receipt_number() == '':
      movements = Movement.by_date(f,t)
      if done_or_received:
        movements = movements.outgoing()
      else:
        movements = movements.incoming()
      if q_term != '':
        movements = movements.where('description', '%%%s%%' % q_term, comparission = 'LIKE')
    else:
      movements = []

    page.update(payments, movements)

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
    page.mark_closers.connect_object('clicked', self.mark_closers, page)
    page.connect('student-edit', self.edit_student)
    self.window.add_page(page)
    return page

  def mark_closers(self, page):
    dialog = ConfirmDialog('¿Marcar cierre?')
    dialog.connect('response', self.do_mark_closers)
    dialog.run()

  def do_mark_closers(self, dialog, response):
    if response == gtk.RESPONSE_ACCEPT:
      Payment.mark_last_as_closer()
      Movement.mark_last_as_closer()

    dialog.destroy()


  def filter_daily_cash(self, page):
    date = page.get_date()
    since_closer = page.since_closer.get_active()
    payments = Payment.filter(date, date, None, since_closer = since_closer)
    movements = Movement.by_date(date, since_closer = since_closer)

    page.update(payments = payments, movements = movements)

  def export_daily_cash_html(self, page):
    self.export_html(page.to_html())

  def export_daily_cash_csv(self, page):
    self.export_csv(page.to_csv(),page.csv_filename())


  def installments_report(self, menu_item):
    page = InstallmentsReport(Installment.overdues(), Klass.all())
    page.filter.connect_object('clicked', self.filter_overdues, page)
    page.export_html.connect_object('clicked', self.export_overdue_installments_report_html, page)
    page.export_csv.connect_object('clicked', self.export_overdue_installments_report_csv, page)
    page.connect('student-edit', self.edit_student)
    self.window.add_page(page)
    return page

  def filter_overdues(self, page):
    inst = Installment.order_by('users.name ASC, users.lastname ASC')

    klass = page.get_selected_klass()
    if klass is not None: inst = Installment.for_klass(klass,inst)
    if page.is_only_overdue(): inst = Installment.overdues(None, inst)
    if not page.include_paid.get_active(): inst.where('status','waiting')
    if page.get_selected_month() is not None: inst.where('month', int(page.get_selected_month()))
    if page.get_year() != '': inst.where('year', int(page.get_year()))

    if page.is_only_active(): inst = Installment.only_active_users(inst)
    else:
      #hago join para que ande el order_by
      inst.set_join('LEFT JOIN memberships ON memberships.id = installments.membership_id LEFT JOIN users ON memberships.student_id = users.id')

    page.update(inst)

  def export_overdue_installments_report_html(self, page):
    self.export_html(page.to_html())

  def export_overdue_installments_report_csv(self, page):
    self.export_csv(page.to_csv(), page.csv_filename())


  def debts(self, menu_item):
    page = Debts(Liability.overdues())
    page.filter.connect_object('clicked', self.filter_debts, page)
    page.export_html.connect_object('clicked', self.export_debts_report_html, page)
    page.export_csv.connect_object('clicked', self.export_debts_report_csv, page)
    page.connect('student-edit', self.edit_student)
    self.window.add_page(page)
    return page

  def filter_debts(self, page):
    inactive = page.should_include_inactive_users()
    debts = Liability.overdues(desc=page.get_filter(), include_inactive=inactive)
    page.update(debts)

  def export_debts_report_html(self, page):
    self.export_html(page.to_html())

  def export_debts_report_csv(self, page):
    self.export_csv(page.to_csv(), page.csv_filename())


  def receipts(self, menu_item):
    page = Receipts()
    page.filter.connect_object('clicked', self.filter_receipts, page)
    page.reprint.connect_object('clicked', self.reprint_payments, page)
    self.window.add_page(page)
    return page

  def filter_receipts(self, page):
    receipts = Payment.where('receipt_number', page.receipt_value())
    page.update(receipts)

  def reprint_payments(self, page):
    Receipt(page.payments).do_print(False)


  def students_hours_report(self, menu_item):
    page = StudentsHoursReport(Student.where('inactive', False), Klass.active())
    page.export_html.connect_object('clicked', self.export_students_hours_report_html, page)
    page.export_csv.connect_object('clicked', self.export_students_hours_report_csv, page)
    self.window.add_page(page)
    return page

  def export_students_hours_report_html(self, page):
    self.export_html(page.to_html())

  def export_students_hours_report_csv(self, page):
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
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #klass id

gobject.signal_new('klass-deactivated', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #klass id

gobject.signal_new('klass-reactivated', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #klass id

gobject.signal_new('teacher-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #teacher id

gobject.signal_new('student-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #student id

gobject.signal_new('installment-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #installment id

gobject.signal_new('membership-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #membership id

gobject.signal_new('package-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #package id

gobject.signal_new('payment-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #payment id

gobject.signal_new('movement-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #movement id

gobject.signal_new('liability-deleted', \
                   Controller, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
                   #liability id

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
