#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor

class StudentForm(FormFor):
  def __init__(self, student):
    FormFor.__init__(self, student)

    self.create_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.memberships_panel = MembershipsPanel(self.object)
    self.memberships_panel.set_sensitive(not self.object.is_new_record())
    
    columns_hbox = gtk.HBox()
    columns_hbox.pack_start(self.fields, True)
    columns_hbox.pack_start(self.memberships_panel, True)
    
    self.add(columns_hbox)
    
    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      title = 'Alumno' if self.object.male else 'Alumna'
      return 'Editar ' + title + ': ' + self.object.name + ' ' + self.object.lastname
    else:
      return 'Agregar Alumno/a'
  
  def create_form_fields(self):
    self.fields = gtk.VBox()
    full_name_box = gtk.HBox()
    self.add_field('Nombre', 'name', attrs=100, box=full_name_box)
    self.add_field('Apellido', 'lastname', attrs=100, box=full_name_box)
    self.fields.pack_start(full_name_box, False)
    
    personal_info_box = gtk.HBox()
    self.add_field('D.N.I.', 'dni', attrs=10, box=personal_info_box)
    self.add_field('Fecha de nacimiento', 'birthday', attrs=10, box=personal_info_box)
    self.fields.pack_start(personal_info_box, False)
    
    contact_info_box = gtk.HBox()
    self.gender_l = gtk.Label('Sexo')
    self.male_r = gtk.RadioButton(None, 'Hombre')
    self.male_r.set_active(True)
    self.female_r = gtk.RadioButton(self.male_r, 'Mujer')
    self.female_r.set_active(not self.object.male)
    self.fields.pack_start(self.gender_l,False)
    self.fields.pack_start(self.male_r,False)
    self.fields.pack_start(self.female_r,False)
    
    self.add_field('Celular', 'cellphone', attrs=16, box=contact_info_box)
    self.add_field('Dirección', 'address', attrs=256, box=contact_info_box)
    self.add_field('Email', 'email', attrs=256, box=contact_info_box)
    self.fields.pack_start(contact_info_box, False)
    
    self.add_field('Comentarios', 'comments', attrs=500)
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'lastname': self.lastname_e.get_text(), 'dni': self.dni_e.get_text(), 'male': self.male_r.get_active(), 'cellphone': self.cellphone_e.get_text(), 'address': self.address_e.get_text(), 'birthday': self.birthday_e.get_text(), 'email': self.email_e.get_text()}

class SearchStudent(gtk.Frame):
  def get_tab_label(self):
    return "Buscar alumno/a"

  def __init__(self):
    gtk.Frame.__init__(self)
    
    self.vbox = gtk.VBox()
    self.add(self.vbox)
    
    self.form = SearchForm()
    self.form.submit.connect('clicked', self.on_search)
    self.form.entry.connect('activate', self.on_search)
    self.vbox.pack_start(self.form, False)
    
    self.results = StudentsList([])
    self.results.connect('student-activated', self.on_student_activated)
    self.vbox.pack_start(self.results, True)
    
    self.show_all()

  def update_results(self, students = None):
    self.results.update_table(students)

  def on_search(self, widget, data = None):
    print 'on-searchhhhh'
    self.emit('search', self.form.get_value())

  def on_student_activated(self, widget, student):
    self.emit('student-edit', student)

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

class MembershipsPanel(gtk.Frame):
  def __init__(self, student):
    gtk.Frame.__init__(self)
    self.notebook = gtk.Notebook()
    self.student = student
    
    for m in student.get_memberships():
      self.notebook.append_page(Membership(m),gtk.Label(m.get_klass().name))
    
    self.add(self.notebook)

class Membership(gtk.ScrolledWindow):
  def __init__(self, membership):
    gtk.ScrolledWindow.__init__(self)
    
    #installment, year, month, base, recharges, paid
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,int,str,str,str,bool)
    
    for ins in membership.get_installments():
      self.store.append((ins,ins.year,ins.get_month(),ins.amount, ins.get_amount(), ins.paid))
    
    self.list = gtk.TreeView(self.store)
    
    self.add_column('Año',1)
    self.add_column('Mes',2)
    self.add_column('Monto',3)
    self.add_column('Con intereses',4)
    self.add_column('Pagado',5)
    
    self.add_with_viewport(self.list)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col
