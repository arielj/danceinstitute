#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from memberships import *
from translations import _a, _t, _m
from widgets import *
import exporter

class UserForm(FormFor):
  def __init__(self, user):
    FormFor.__init__(self, user)
    self.user = user

    self.create_form_fields()

    self.form_actions = gtk.HBox()
    self.submit = gtk.Button('Guardar')
    self.inactivate = gtk.Button('Desactivar')
    self.activate = gtk.Button('Activar')

    self.update_user_status()

    self.form_actions.pack_start(self.submit,True)
    self.form_actions.pack_start(self.inactivate, False)
    self.form_actions.pack_start(self.activate, False)

    self.fields.pack_start(self.form_actions, False)

    self.add_family_block()

    self.tabs = gtk.Notebook()
    self.tabs.set_scrollable(True)
    self.tabs.set_sensitive(not self.object.is_new_record())

    self.add_tabs()

    self.pack_start(self.fields, True)
    self.pack_start(self.tabs, True)

    self.show_all()

    self.set_inscription_message()

  def get_tab_label(self):
    if self.user.id:
      if self.user.is_teacher:
        title = 'Profesor' if self.user.male else 'Profesora'
      else:
        title = 'Alumno' if self.user.male else 'Alumna'

      return 'Editar ' + title + ":\n" + self.user.name + ' ' + self.user.lastname
    else:
      if self.user.is_teacher:
        return 'Agregar Profesor/a'
      else:
        return 'Agregar Alumno/a'

  def create_form_fields(self):
    self.fields = gtk.VBox(False, 5)

    label = gtk.Label('Información personal')
    self.fields.pack_start(label, False)

    full_name_box = gtk.HBox(True, 8)
    self.add_field('name', attrs=100, box=full_name_box)
    self.add_field('lastname', attrs=100, box=full_name_box)
    self.fields.pack_start(full_name_box, False)

    personal_info_box = gtk.HBox(True, 8)
    self.add_field('dni', attrs=10, box=personal_info_box)

    age_hbox = gtk.HBox(True, 8)
    self.add_field('birthday', attrs=10, box=age_hbox)
    self.birthday_e.connect('focus-out-event',self.on_birthday_focus_out)
    self.add_field('age', attrs=2, box=age_hbox)
    personal_info_box.pack_start(age_hbox, True)
    self.fields.pack_start(personal_info_box, False)

    contact_info_box = gtk.HBox(True, 8)
    self.add_field('cellphone', attrs=16, box=contact_info_box)
    self.add_field('alt_phone', attrs=16, box=contact_info_box)
    self.fields.pack_start(contact_info_box, False)

    addresses_box = gtk.HBox(True, 8)
    self.add_field('email', attrs=256, box=addresses_box)
    self.add_field('address', attrs=256, box=addresses_box)
    self.fields.pack_start(addresses_box, False)

    hbox = gtk.HBox(True, 8)
    self.gender_l = gtk.Label('Sexo')
    self.male_r = gtk.RadioButton(None, 'Hombre')
    self.male_r.set_active(True)
    self.female_r = gtk.RadioButton(self.male_r, 'Mujer')
    self.female_r.set_active(not self.object.male)

    gender_field = gtk.VBox()
    radios_hbox = gtk.HBox()
    radios_hbox.pack_start(self.male_r, False)
    radios_hbox.pack_start(self.female_r, False)
    gender_field.pack_start(self.gender_l, False)
    gender_field.pack_start(radios_hbox, False)
    hbox.pack_start(gender_field, False)

    group_field = gtk.VBox()
    self.group_l = gtk.Label(_a(self.object.__class__.__name__.lower(), 'group'))
    self.group_e = gtk.Entry(255)
    v = self.object.group
    v = v if v is not None else ''
    self.group_e.set_text(str(v))

    group_field.pack_start(self.group_l, False)
    group_field.pack_start(self.group_e, False)
    hbox.pack_start(group_field, False)

    fb_field = gtk.VBox()
    self.facebook_uid_l = gtk.Label(_a(self.object.__class__.__name__.lower(), 'facebook_uid'))
    self.facebook_uid_e = gtk.Entry(300)
    v = self.object.facebook_uid
    v = v if v is not None else ''
    self.facebook_uid_e.set_text(str(v))
    self.open_fb = gtk.Button('Abrir')

    inner_hbox = gtk.HBox()
    inner_hbox.pack_start(self.facebook_uid_e, True)
    inner_hbox.pack_start(self.open_fb, False)

    fb_field.pack_start(self.facebook_uid_l, False)
    fb_field.pack_start(inner_hbox, False)

    hbox.pack_start(fb_field, True)

    self.fields.pack_start(hbox, False)

    f, l, e = self.add_field('comments', field_type = 'text')
    e.set_size_request(-1,140)
    f.set_child_packing(e,True,True,0,gtk.PACK_START)
    self.fields.set_child_packing(e,True,True,0,gtk.PACK_START)

  def add_family_block(self):
    self.family_vbox = gtk.VBox()

    label = gtk.Label('Familia')
    self.family_list = StudentsList(self.object.family_members())

    self.actions = gtk.HBox(False, 4)
    self.add_family = gtk.Button('Agregar')
    self.remove_family = gtk.Button('Quitar')
    self.remove_family.set_sensitive(False)
    self.family_list.students_t.get_selection().connect('changed', self.on_family_selection_changed)

    self.actions.pack_start(self.add_family, False)
    self.actions.pack_start(self.remove_family, False)

    self.family_vbox.pack_start(label, False)
    self.family_vbox.pack_start(self.family_list, True)
    self.family_vbox.pack_start(self.actions, False)

    self.fields.pack_start(self.family_vbox, True)
    self.family_vbox.set_sensitive(not self.object.is_new_record())

  def add_tabs(self):
    if self.user.is_teacher:
      t2 = PaymentsTab(self.user, True)
      self.tabs.append_page(t2,gtk.Label('Pagos al profesor'))
      t2.delete_b.connect_object('clicked', self.on_delete_payments_clicked, t2)
      t2.add_b.connect_object('clicked', self.on_add_payment_clicked, t2, None, True)
      t2.list.connect('row-activated', self.on_edit_payment)

    t = PaymentsTab(self.user)
    self.tabs.append_page(t,gtk.Label('Pagos del '+_m(self.user.cls_name().lower())))
    t.delete_b.connect_object('clicked', self.on_delete_payments_clicked, t)
    t.add_b.connect_object('clicked', self.on_add_payment_clicked, t, None)
    t.print_b.connect_object('clicked', self.on_print_payments_clicked, t)
    t.list.connect('row-activated', self.on_edit_payment)

    self.liabilities = LiabilitiesTab(self.user)
    self.tabs.append_page(self.liabilities, gtk.Label('Deudas'))
    self.liabilities.delete_b.connect_object('clicked', self.on_delete_liabilities_clicked, self.liabilities)
    self.liabilities.add_b.connect_object('clicked', self.on_add_liability_clicked, self.liabilities)
    self.liabilities.connect('add-payment', self.on_add_payment_clicked)

    self.memberships = MembershipsTab(self.user)
    self.tabs.append_page(self.memberships, gtk.Label('Clases'))
    self.memberships.enroll_b.connect('clicked', self.on_add_membership_clicked)
    self.memberships.delete_b.connect('clicked', self.on_delete_membership_clicked)
    self.memberships.create_package_b.connect('clicked', self.on_create_user_package_clicked)
    self.memberships.connect('add-installments', self.on_add_installments_clicked)
    self.memberships.connect('add-payment', self.on_add_payment_clicked)
    self.memberships.connect('add-payments', self.on_add_payments_clicked)
    self.memberships.connect('delete-installments', self.on_delete_installments_clicked)
    self.memberships.connect('edit-package', self.on_edit_package_clicked)
    self.memberships.connect('edit-installment', self.on_edit_installment_clicked)
    self.memberships.connect('edit-installment-payments', self.on_edit_installment_payments_clicked)

  def get_comments_text(self):
    buff = self.comments_e.get_buffer()
    return buff.get_text(buff.get_start_iter(), buff.get_end_iter())

  def get_values(self):
    return {'name': self.name_e.get_text(), 'lastname': self.lastname_e.get_text(), 'dni': self.dni_e.get_text(), 'male': self.male_r.get_active(), 'cellphone': self.cellphone_e.get_text(), 'alt_phone': self.alt_phone_e.get_text(), 'address': self.address_e.get_text(), 'birthday': self.birthday_e.get_text(), 'email': self.email_e.get_text(), 'facebook_uid': self.facebook_uid_e.get_text(), 'age': self.age_e.get_text(), 'comments': self.get_comments_text(), 'group': self.group_e.get_text()}

  def enable_memberships(self):
    self.tabs.set_sensitive(True)
    self.family_vbox.set_sensitive(True)
    self.set_inscription_message()

  def membership_added(self, membership):
    self.update()
    self.memberships.select_membership(membership)

  def set_inscription_message(self):
    if not self.user.is_inscription_payed():
      self.set_flash("Falta pagar inscripción")
    else:
      self.hide_flash()

  def update(self):
    for tab in self.tabs.get_children():
      tab.refresh()
    self.tabs.show_all()
    self.set_inscription_message()
    self.update_user_status()

  def update_user_status(self):
    self.inactivate.set_sensitive(not self.user.inactive)
    self.activate.set_sensitive(self.user.inactive)

  def on_add_membership_clicked(self, button):
    self.emit('add-membership')

  def on_delete_membership_clicked(self, button):
    self.emit('ask-delete-membership', self.memberships.get_current_membership())

  def on_membership_deleted(self, emmiter, m_id):
    for tab in self.tabs.get_children():
      if not isinstance(tab,MembershipsTab):
        tab.refresh()
      else:
        tab.on_membership_deleted(m_id)

  def on_delete_installments_clicked(self, tab, installments):
    self.emit('delete-installments', installments)

  def on_add_payment_clicked(self, tab, related, done = False):
    if isinstance(tab,MembershipsTab):
      self.emit('add-payment', related, done)
    elif isinstance(tab, LiabilitiesTab):
      self.emit('add-payment', related, done)
    else:
      self.emit('add-payment', None, done)

  def on_add_payments_clicked(self, tab):
    self.emit('add-payments')

  def on_print_payments_clicked(self, tab):
    self.emit('print-payments', tab.printable_payments())

  def on_add_installments_clicked(self, tab):
    self.emit('add-installments', tab.get_current_membership())

  def on_delete_payments_clicked(self, tab):
    self.emit('delete-payments', tab.get_selected_payments())

  def on_add_liability_clicked(self, tab):
    self.emit('add-liability')

  def on_delete_liabilities_clicked(self, tab):
    self.emit('delete-liabilities', tab.get_selected_liabilities())

  def on_create_user_package_clicked(self, button):
    self.emit('create-user-package')

  def on_edit_package_clicked(self, memberships, package):
    self.emit('edit-package', package)

  def on_edit_installment_clicked(self, memberships, installment):
    self.emit('edit-installment', installment)

  def on_edit_installment_payments_clicked(self, memberships, installment):
    self.emit('edit-installment-payments', installment)

  def on_payment_deleted(self, emmiter, p_id):
    for tab in self.tabs.get_children():
      tab.on_payment_deleted(p_id)

  def on_installment_deleted(self, emmiter, i_id):
    self.memberships.on_installment_deleted(i_id)

  def on_liability_deleted(self, emmiter, l_id):
    self.liabilities.on_liability_deleted(l_id)

  def on_birthday_focus_out(self, entry, event):
    date = entry.get_text()
    age = self.object.__class__.calculate_age(date)
    if age:
      self.age_e.set_text(str(age))

  def on_family_selection_changed(self, selection):
    model, iter = selection.get_selected()
    self.remove_family.set_sensitive(iter is not None)

  def get_selected_family_member(self):
    return self.family_list.get_selected()

  def refresh_family(self):
    self.family_list.update_table(self.object.family_members())

  def show_installment(self, installment):
    self.tabs.set_current_page(self.tabs.page_num(self.memberships))
    self.memberships.show_installment(installment)

  def on_edit_payment(self, tree, path, view_column):
    model = tree.get_model()
    itr = model.get_iter(path)
    payment = model.get_value(itr, 0)
    self.emit('edit-payment', payment)

gobject.type_register(UserForm)
gobject.signal_new('ask-delete-membership', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('add-membership', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('add-installments', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('add-payment', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, bool))
gobject.signal_new('add-payments', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('delete-payments', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('add-liability', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('delete-liabilities', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('delete-installments', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('create-user-package', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('edit-package', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('print-payments', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-installment', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-installment-payments', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('edit-payment', \
                   UserForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class SearchStudent(gtk.VBox):
  def get_tab_label(self):
    return "Buscar alumno/a"

  def __init__(self):
    gtk.VBox.__init__(self, False, 8)
    self.set_border_width(4)

    content = gtk.HBox(False, 5)
    self.pack_start(content, True)

    self.form = SearchForm()
    self.form.submit.connect('clicked', self.on_search)
    self.form.term_e.connect('activate', self.on_search)
    self.form.group_e.connect('activate', self.on_search)
    content.pack_start(self.form, False)

    self.results = StudentsList([])
    self.results.connect('student-activated', self.on_student_activated)
    content.pack_start(self.results, True)

    self.actions = gtk.HBox(False, 4)
    self.add = gtk.Button('Agregar')
    self.add.connect('clicked', self.on_add_student_clicked)
    self.edit = gtk.Button('Editar')
    self.edit.set_sensitive(False)
    self.edit.connect('clicked', self.on_edit_student_clicked)
    self.delete = gtk.Button('Borrar')
    self.delete.set_sensitive(False)
    self.delete.connect('clicked', self.on_delete_student_clicked)
    self.results.students_t.get_selection().connect('changed', self.on_selection_changed)
    self.export_html = gtk.Button('Exportar HTML')
    self.export_html.connect('clicked', self.on_export_html_clicked)
    self.export_csv = gtk.Button('Exportar CSV')
    self.export_csv.connect('clicked', self.on_export_csv_clicked)

    self.actions.pack_start(self.add, False)
    self.actions.pack_start(self.edit, False)
    self.actions.pack_start(self.delete, False)
    self.actions.pack_start(self.export_html, False)
    self.actions.pack_start(self.export_csv, False)

    self.pack_start(self.actions, False)

    self.show_all()

  def update_results(self, students = None):
    self.results.update_table(students)
    self.edit.set_sensitive(False)
    self.delete.set_sensitive(False)
    self.form.update_total(students)

  def on_search(self, widget, student = None, new_record = None):
    self.emit('search', self.form.get_value(), self.form.get_group(), self.form.get_active_status())

  def on_student_activated(self, widget, student):
    self.emit('student-edit', student.id)

  def on_selection_changed(self, selection):
    model, iter = selection.get_selected()
    self.edit.set_sensitive(iter is not None)
    self.delete.set_sensitive(iter is not None)

  def on_edit_student_clicked(self, button):
    student = self.results.get_selected()
    if student is not None:
      self.emit('student-edit',student.id)

  def on_delete_student_clicked(self, button):
    student = self.results.get_selected()
    if student is not None:
      self.emit('student-delete',student)

  def on_add_student_clicked(self,button):
    self.emit('student-add')

  def on_export_html_clicked(self,button):
    self.emit('students-export-html')

  def on_export_csv_clicked(self,button):
    self.emit('students-export-csv')

  def to_html(self):
    return self.results.to_html()

  def to_csv(self):
    return self.results.to_csv()

  def csv_filename(self):
    f = 'alumnos-as'
    return f+'.csv'


gobject.type_register(SearchStudent)
gobject.signal_new('search', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (str, str, int))
gobject.signal_new('student-edit', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int, ))
gobject.signal_new('student-add', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('student-delete', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('students-export-csv', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('students-export-html', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())

class SearchForm(gtk.VBox):
  def __init__(self):
    gtk.VBox.__init__(self, False, 5)

    label = gtk.Label()
    label.set_markup('<big><b>Filtrar:</b></big>')
    self.pack_start(label, False)

    self.term_l = gtk.Label('Nombre, Apellido o D.N.I: ')
    self.term_e = gtk.Entry(100)
    self.group_l = gtk.Label('Grupo: ')
    self.group_e = gtk.Entry(255)

    self.active_status_l = gtk.Label('Mostrar:')
    self.active_status_cb = gtk.combo_box_new_text()
    self.active_status_cb.append_text('Sólo activos')
    self.active_status_cb.append_text('Sólo inactivos')
    self.active_status_cb.append_text('Todos')
    self.active_status_cb.set_active(0)

    self.submit = gtk.Button('Buscar')

    self.pack_start(self.term_l, False)
    self.pack_start(self.term_e, False)
    self.pack_start(self.group_l, False)
    self.pack_start(self.group_e, False)
    self.pack_start(self.active_status_l, False)
    self.pack_start(self.active_status_cb, False)
    self.pack_start(self.submit, False)

    self.totals_label = gtk.Label('Total: 0')

    al = gtk.Alignment(yalign=1)
    al.add(self.totals_label)
    self.pack_start(al, True)

  def get_value(self):
    return self.term_e.get_text()

  def get_group(self):
    return self.group_e.get_text()

  def get_active_status(self):
    selected = self.active_status_cb.get_active_text()
    if selected == 'Sólo activos':
      return 0
    elif selected == 'Sólo inactivos':
      return 1
    else:
      return 2

  def update_total(self, students):
    if students is None:
      self.totals_label.set_text('Total: 0')
    else:
      self.totals_label.set_text('Total: %d' % students.count())

gobject.type_register(SearchForm)
gobject.signal_new('search', \
                   SearchForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())

class StudentsList(gtk.VBox):
  def __init__(self, students):
    gtk.VBox.__init__(self, False, 6)
    self.students = students

    self.students_t = StudentsTable(students)
    self.students_t.connect('row-activated', self.on_row_activated)
    self.students_t.connect('column-clicked', self.on_col_clicked)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.students_t)
    self.pack_start(self.scroll, True)

    self.show_all()

  def update_table(self, students):
    self.students_t.update(students)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    student = model.get_value(itr, 0)
    self.emit('student-activated', student)

  def get_selected(self):
    model, iter = self.students_t.get_selection().get_selected()
    return model.get_value(iter,0) if iter is not None else None

  def to_html(self):
    return self.students_t.to_html()

  def to_csv(self):
    return self.students_t.to_csv()

  def on_col_clicked(self, table, column):
    self.emit('query-reorder', column.order_text())

gobject.type_register(StudentsList)
gobject.signal_new('student-activated', \
                   StudentsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('query-reorder', \
                   StudentsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (str, ))

class StudentsTable(gtk.TreeView):
  def __init__(self, students):
    self.students = students
    self.create_store(students)

    gtk.TreeView.__init__(self,self.store)

    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    self.headings = ['name','lastname','dni','email','address','cellphone']

    for idx, h in enumerate(self.headings, 1):
      self.add_column(h,idx)

    self.set_headers_clickable(True)

  def add_column(self, attr, text_idx):
    col = OrderableColumn('student', attr, text_idx)
    col.connect('clicked', self.on_col_clicked)
    self.append_column(col)
    return col

  def create_store(self, students):
    # student, name, lastname, dni, email, address, cellphone
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str,str)
    self.set_model(students)

  def update(self, students):
    if students is not None: self.students = students
    self.store.clear()
    self.set_model(students)

  def set_model(self, students):
    for t in self.students:
      self.store.append((t,t.name,t.lastname,t.dni,t.email,t.address,t.cellphone))

  def to_html(self):
    rows = map(lambda s: [s.name, s.lastname, s.dni, s.email, s.address, s.cellphone], self.students)
    return exporter.html_table(self.headings, rows)

  def to_csv(self):
    h = list(map(lambda x: _a('student',x), self.headings))
    h.insert(2,'Nombre y apellido')
    h.append('Fecha de nacimiento')
    st = ';'.join(h)+"\n"
    st += "\n".join(map(lambda s: ';'.join([s.name, s.lastname, s.to_label(), s.dni, s.email, s.address, s.cellphone, s.birthday.strftime(Settings.get_settings().date_format)]), self.students))
    return st

  def on_col_clicked(self, column):
    self.emit('column-clicked', column)

gobject.type_register(StudentsTable)
gobject.signal_new('column-clicked', \
                   StudentsTable, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class StudentsListDialog(gtk.Dialog):
  def __init__(self, klass):
    gtk.Dialog.__init__(self, 'Alumnos de la clase '+klass.name, None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        ())
    self.set_size_request(700,400)
    self.list = StudentsList(klass.get_students())
    self.total_label = gtk.Label("Total: %d" % klass.get_students().count())
    self.export_csv = gtk.Button('Exportar CSV')
    self.export_html = gtk.Button('Exportar HTML')
    exports = gtk.HBox()
    exports.pack_start(self.export_csv, True)
    exports.pack_start(self.export_html, True)
    self.vbox.pack_start(self.list, True)
    al = gtk.Alignment(xalign=0)
    al.add(self.total_label)
    self.vbox.pack_start(al, False)
    self.vbox.pack_start(exports, False)

    self.show_all()

class TeacherForm(FormFor):
  def __init__(self, teacher):
    FormFor.__init__(self, teacher)

    self.create_form_fields()

    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)

    self.payments = PaymentsPanel(teacher)
    self.payments.set_sensitive(teacher.is_not_new_record())

    self.pack_start(self.fields, True)
    self.pack_start(self.payments, True)

    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      title = 'Profesor' if self.object.male else 'Profesora'
      return 'Editar ' + title + ":\n" + self.object.name + ' ' + self.object.lastname
    else:
      return 'Agregar Profesor/a'

  def create_form_fields(self):
    self.fields = gtk.VBox(False, 5)

    label = gtk.Label('Información personal')
    self.fields.pack_start(label, False)

    full_name_box = gtk.HBox(True, 8)
    self.add_field('name', attrs=100, box=full_name_box)
    self.add_field('lastname', attrs=100, box=full_name_box)
    self.fields.pack_start(full_name_box, False)

    personal_info_box = gtk.HBox(True, 8)
    self.add_field('dni', attrs=10, box=personal_info_box)
    self.add_field('birthday', attrs=10, box=personal_info_box)
    self.fields.pack_start(personal_info_box, False)

    contact_info_box = gtk.HBox(True, 8)
    self.add_field('cellphone', attrs=16, box=contact_info_box)
    self.add_field('alt_phone', attrs=16, box=contact_info_box)
    self.fields.pack_start(contact_info_box, False)

    addresses_box = gtk.HBox(True, 8)
    self.add_field('email', attrs=256, box=addresses_box)
    self.add_field('address', attrs=256, box=addresses_box)
    self.fields.pack_start(addresses_box, False)

    hbox = gtk.HBox(True, 8)
    self.gender_l = gtk.Label('Sexo')
    self.male_r = gtk.RadioButton(None, 'Hombre')
    self.male_r.set_active(True)
    self.female_r = gtk.RadioButton(self.male_r, 'Mujer')
    self.female_r.set_active(not self.object.male)

    gender_field = gtk.VBox()
    radios_hbox = gtk.HBox()
    radios_hbox.pack_start(self.male_r, False)
    radios_hbox.pack_start(self.female_r, False)
    gender_field.pack_start(self.gender_l, False)
    gender_field.pack_start(radios_hbox, False)
    hbox.pack_start(gender_field, False)
    hbox.pack_start(gtk.VBox(), False)
    self.fields.pack_start(hbox, False)

    f, l, e = self.add_field('comments', field_type = 'text')
    e.set_size_request(-1,200)
    f.set_child_packing(e,True,True,0,gtk.PACK_START)
    self.fields.set_child_packing(e,True,True,0,gtk.PACK_START)

  def get_values(self):
    return {'name': self.name_e.get_text(), 'lastname': self.lastname_e.get_text(), 'dni': self.dni_e.get_text(), 'male': self.male_r.get_active(), 'cellphone': self.cellphone_e.get_text(), 'alt_phone': self.alt_phone_e.get_text(), 'address': self.address_e.get_text(), 'birthday': self.birthday_e.get_text(), 'email': self.email_e.get_text()}

  def update(self):
    self.payments.update()

class TeachersList(gtk.VBox):
  def __init__(self, teachers, with_actions = True):
    gtk.VBox.__init__(self)
    self.set_border_width(4)
    self.teachers = teachers
    self.with_actions = with_actions

    self.teachers_t = TeachersTable(teachers)
    self.teachers_t.connect('row-activated', self.on_row_activated)
    self.teachers_t.connect('column-clicked', self.on_col_clicked)
    self.t_selection = self.teachers_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)

    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.scroll.add(self.teachers_t)
    self.pack_start(self.scroll, True)

    if self.with_actions:
      self.add_b = gtk.Button('Agregar')
      self.edit_b = gtk.Button('Editar')
      self.edit_b.set_sensitive(False)
      self.delete_b = gtk.Button('Borrar')
      self.delete_b.set_sensitive(False)
      self.add_b.connect('clicked', self.on_add_clicked)
      self.edit_b.connect('clicked', self.on_edit_clicked)
      self.delete_b.connect('clicked', self.on_delete_clicked)

      self.actions = gtk.HBox()
      self.actions.pack_start(self.add_b, False)
      self.actions.pack_start(self.edit_b, False)
      self.actions.pack_start(self.delete_b, False)

      self.pack_start(self.actions, False)

    self.show_all()

  @classmethod
  def tab_label(cls):
    return 'Profesores/as'

  def get_tab_label(self):
    return self.__class__.tab_label()

  def update_table(self, teachers):
    self.teachers_t.update(teachers)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    teacher = model.get_value(itr, 0)
    self.emit('teacher-edit', teacher.id)

  def on_selection_changed(self, selection):
    if self.with_actions:
      model, iter = selection.get_selected()
      self.edit_b.set_sensitive(iter is not None)
      self.delete_b.set_sensitive(iter is not None)
    self.emit('selection-changed', selection)

  def on_add_clicked(self, btn):
    self.emit('teacher-add')

  def on_edit_clicked(self, btn):
    teacher = self.get_selected()
    if teacher is not None:
      self.emit('teacher-edit', teacher.id)

  def on_delete_clicked(self, btn):
    teacher = self.get_selected()
    if teacher is not None:
      self.emit('teacher-delete', teacher.id)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

  def refresh_list(self, teachers):
    self.teachers_t.update(teachers)

  def on_col_clicked(self, table, column):
    self.emit('query-reorder', column.order_text())

gobject.type_register(TeachersList)
gobject.signal_new('teacher-edit', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int, ))
gobject.signal_new('teacher-delete', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (int, ))
gobject.signal_new('teacher-add', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('selection-changed', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('query-reorder', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (str, ))

class TeachersTable(gtk.TreeView):
  def __init__(self, teachers):
    self.create_store(teachers)

    gtk.TreeView.__init__(self, self.store)

    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)

    self.headings = ['name','lastname','dni','email','address','cellphone']

    for idx, h in enumerate(self.headings, 1):
      self.add_column(h,idx)

    self.set_headers_clickable(True)

  def add_column(self, attr, text_idx):
    col = OrderableColumn('teachers', attr, text_idx)
    col.connect('clicked', self.on_col_clicked)
    self.append_column(col)
    return col

  def create_store(self, teachers):
    # teacher, name, lastname, dni, email, address, cellphone
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str,str)
    self.set_model(teachers)

  def update(self, teachers):
    self.store.clear()
    self.set_model(teachers)

  def set_model(self, teachers):
    for t in teachers:
      self.store.append((t,t.name,t.lastname,t.dni,t.email,t.address,t.cellphone))

  def on_col_clicked(self, column):
    self.emit('column-clicked', column)

gobject.type_register(TeachersTable)
gobject.signal_new('column-clicked', \
                   TeachersTable, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class SelectTeacherDialog(gtk.Dialog):
  def __init__(self, teachers):
    gtk.Dialog.__init__(self, 'Seleccioná un/a profesor/a', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.teachers = teachers

    self.add_teachers_list()

    self.vbox.show_all()

  def add_teachers_list(self):
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    self.list = gtk.TreeView(self.store)
    col = gtk.TreeViewColumn('Apellido, Nombre', gtk.CellRendererText(), text=1)
    col.set_expand(True)
    self.list.append_column(col)
    for t in self.teachers:
      self.store.append((t, t.lastname + ', ' + t.name))

    self.vbox.pack_start(self.list, True)

    self.list.connect('row-activated', self.on_row_activated)

  def get_selected_teacher(self):
    model, iter = self.list.get_selection().get_selected()
    return model.get_value(iter,0) if iter is not None else None

  def on_row_activated(self, tree, path, column):
    t = self.get_selected_teacher()
    self.emit('response', gtk.RESPONSE_ACCEPT)

class AddFamilyDialog(gtk.Dialog):
  def __init__(self, users):
    gtk.Dialog.__init__(self, 'Seleccioná un alumo/profesor', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                       (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                        gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

    self.users = users

    self.add_not_family_list()

    self.vbox.show_all()

  def add_not_family_list(self):
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str)
    for user in self.users:
      self.store.append((user, user.to_label()))

    self.user = gtk.ComboBoxEntry(self.store,1)
    completion = gtk.EntryCompletion()
    completion.set_model(self.store)
    completion.set_text_column(1)
    completion.connect('match-selected', self.on_user_match_selected)
    self.user.child.set_completion(completion)
    self.user.set_active(0)

    self.vbox.pack_start(self.user, True)

  def get_selected_user(self):
    itr = self.user.get_active_iter()
    if itr is not None:
      return self.user.get_model().get_value(itr,0)
    else:
      return None

  def on_user_match_selected(self, completion, model, itr):
    user = model.get_value(itr,0)
    users_model = self.user.get_model()
    found = None

    if user is not None:
      model_iter = users_model.get_iter_first()
      while model_iter is not None and found is None:
        iter_user = users_model.get_value(model_iter,0)
        if iter_user is not None and iter_user.id == user.id:
          found = model_iter
        else:
          model_iter = users_model.iter_next(model_iter)

    if found is not None:
      self.user.set_active_iter(found)
    else:
      self.user.set_active_iter(users_model.get_iter_first())
