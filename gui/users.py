#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from memberships import *
from translations import _a

class UserForm(FormFor):
  def __init__(self, user):
    FormFor.__init__(self, user)

    self.create_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.memberships_panel = MembershipsPanel(self.object)
    self.memberships_panel.set_sensitive(not self.object.is_new_record())

    self.pack_start(self.fields, True)
    self.pack_start(self.memberships_panel, True)
    
    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      if self.object.is_teacher:
        title = 'Profesor' if self.object.male else 'Profesora'
      else:
        title = 'Alumno' if self.object.male else 'Alumna'

      return 'Editar ' + title + ":\n" + self.object.name + ' ' + self.object.lastname
    else:
      if self.object.is_teacher:
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
    e.set_size_request(-1,200)
    f.set_child_packing(e,True,True,0,gtk.PACK_START)
    self.fields.set_child_packing(e,True,True,0,gtk.PACK_START)
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'lastname': self.lastname_e.get_text(), 'dni': self.dni_e.get_text(), 'male': self.male_r.get_active(), 'cellphone': self.cellphone_e.get_text(), 'address': self.address_e.get_text(), 'birthday': self.birthday_e.get_text(), 'email': self.email_e.get_text(), 'facebook_uid': self.facebook_uid_e.get_text()}

  def enable_memberships(self):
    self.memberships_panel.set_sensitive(True)

  def update(self):
    self.memberships_panel.update()

  def on_membership_deleted(self, emmiter, m_id):
    self.memberships_panel.on_membership_deleted(m_id)

  def on_payment_deleted(self, emmiter, p_id):
    self.memberships_panel.on_payment_deleted(p_id)

  def on_installment_deleted(self, emmiter, i_id):
    self.memberships_panel.on_installment_deleted(i_id)

class SearchStudent(gtk.VBox):
  def get_tab_label(self):
    return "Buscar alumno/a"

  def __init__(self):
    gtk.VBox.__init__(self, False, 8)
    self.set_border_width(4)
    
    self.form = SearchForm()
    self.form.submit.connect('clicked', self.on_search)
    self.form.entry.connect('activate', self.on_search)
    self.pack_start(self.form, False)
    
    self.results = StudentsList([])
    self.results.connect('student-activated', self.on_student_activated)
    self.pack_start(self.results, True)
    
    self.show_all()

  def update_results(self, students = None):
    self.results.update_table(students)

  def on_search(self, widget, student = None, new_record = None):
    self.emit('search', self.form.get_value())

  def on_student_activated(self, widget, student):
    self.emit('student-edit', student.id)

gobject.type_register(SearchStudent)
gobject.signal_new('search', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (str, ))
gobject.signal_new('student-edit', \
                   SearchStudent, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class SearchForm(gtk.HBox):
  def __init__(self):
    gtk.HBox.__init__(self)

    self.label = gtk.Label('Nombre, Apellido o D.N.I: ')
    self.entry = gtk.Entry(100)
    self.submit = gtk.Button('Buscar')
    
    self.pack_start(self.label, False)
    self.pack_start(self.entry, False)
    self.pack_start(self.submit, False)

  def get_value(self):
    return self.entry.get_text()

gobject.type_register(SearchForm)
gobject.signal_new('search', \
                   SearchForm, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())

class StudentsList(gtk.ScrolledWindow):
  def __init__(self, students):
    gtk.ScrolledWindow.__init__(self)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.students = students
    
    self.vbox = gtk.VBox()
    
    self.students_t = StudentsTable(students)
    self.students_t.connect('row-activated', self.on_row_activated)
    
    self.vbox.pack_start(self.students_t, True)
    
    self.add_with_viewport(self.vbox)
    
    self.show_all()

  def update_table(self, students):
    self.students_t.update(students)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    student = model.get_value(itr, 0)
    self.emit('student-activated', student)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

gobject.type_register(StudentsList)
gobject.signal_new('student-activated', \
                   StudentsList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class StudentsTable(gtk.TreeView):
  def __init__(self, students):
    self.students = students
    self.create_store(students)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Nombre',1)
    self.add_column('Apellido',2)
    self.add_column('D.N.I.',3)
    self.add_column('Email',4)
    self.add_column('Dirección',5)
    self.add_column('Celular', 6)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, students):
    # student, name, lastname, dni, email, address, cellphone
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str,str)
    self.set_model(students)

  def update(self, students):
    if students is not None:
      self.students = students
    self.store.clear()
    self.set_model(students)
  
  def set_model(self, students):
    for t in self.students:
      self.store.append((t,t.name,t.lastname,t.dni,t.email,t.address,t.cellphone))

class StudentsListDialog(gtk.Dialog):
  def __init__(self, klass):
    gtk.Dialog.__init__(self, 'Alumnos de la clase '+klass.name, None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        ())
    self.set_size_request(700,400)
    self.list = StudentsList(klass.get_students())
    self.vbox.pack_start(self.list,True)
    
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

class TeachersList(gtk.ScrolledWindow):
  def __init__(self, teachers, with_actions = True):
    gtk.ScrolledWindow.__init__(self)
    self.set_border_width(4)
    self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    self.teachers = teachers
    self.with_actions = with_actions
    
    self.vbox = gtk.VBox()
    
    self.teachers_t = TeachersTable(teachers)
    self.teachers_t.connect('row-activated', self.on_row_activated)
    self.t_selection = self.teachers_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)
    
    self.vbox.pack_start(self.teachers_t, True)
    
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
      
      self.vbox.pack_start(self.actions, False)
    
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.vbox)
    self.add(viewport)
    
    self.show_all()

  def get_tab_label(self):
    return 'Profesores/as'

  def update_table(self, teachers):
    self.teachers_t.update(teachers)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    teacher = model.get_value(itr, 0)
    self.emit('teacher-edit', teacher)

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
      self.emit('teacher-edit', teacher)

  def on_delete_clicked(self, btn):
    teacher = self.get_selected()
    if teacher is not None:
      self.emit('teacher-delete', teacher.id)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

  def refresh_list(self, teachers):
    self.teachers_t.update(teachers)

gobject.type_register(TeachersList)
gobject.signal_new('teacher-edit', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
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

class TeachersTable(gtk.TreeView):
  def __init__(self, teachers):
    self.create_store(teachers)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Nombre',1)
    self.add_column('Apellido',2)
    self.add_column('D.N.I.',3)
    self.add_column('Email',4)
    self.add_column('Dirección',5)
    self.add_column('Celular', 6)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
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

