#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor

class TeacherForm(FormFor):
  def __init__(self, teacher):
    FormFor.__init__(self, teacher)

    self.create_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      title = 'Profesor' if self.object.male else 'Profesora'
      return 'Editar ' + title + ': ' + self.object.name + ' ' + self.object.lastname
    else:
      return 'Agregar Profesor/a'
  
  def create_form_fields(self):
    self.fields = gtk.VBox()
    self.add_field('Nombre', 'name', attrs=100)
    self.add_field('Apellido', 'lastname', attrs=100)
    self.add_field('D.N.I.', 'dni', attrs=10)
    
    self.gender_l = gtk.Label('Sexo')
    self.male_r = gtk.RadioButton(None, 'Hombre')
    self.male_r.set_active(True)
    self.female_r = gtk.RadioButton(self.male_r, 'Mujer')
    self.female_r.set_active(not self.object.male)
    self.fields.pack_start(self.gender_l,False)
    self.fields.pack_start(self.male_r,False)
    self.fields.pack_start(self.female_r,False)
    
    self.add_field('Celular', 'cellphone', attrs=16)
    self.add_field('Dirección', 'address', attrs=256)
    self.add_field('Fecha de nacimiento', 'birthday', attrs=10)
    self.add_field('Email', 'email', attrs=256)
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'lastname': self.lastname_e.get_text(), 'dni': self.dni_e.get_text(), 'male': self.male_r.get_active(), 'cellphone': self.cellphone_e.get_text(), 'address': self.address_e.get_text(), 'birthday': self.birthday_e.get_text(), 'email': self.email_e.get_text()}

class TeachersList(gtk.ScrolledWindow):
  def __init__(self, teachers):
    gtk.ScrolledWindow.__init__(self)
    self.teachers = teachers
    
    self.vbox = gtk.VBox()
    
    self.teachers_t = TeachersTable(teachers)
    self.teachers_t.connect('row-activated', self.on_row_activated)
    
    self.vbox.pack_start(self.teachers_t, True)
    
    self.add_b = gtk.Button('Agregar')
    self.edit_b = gtk.Button('Editar')
    self.edit_b.set_sensitive(False)
    self.delete_b = gtk.Button('Borrar')
    self.delete_b.set_sensitive(False)
    
    self.actions = gtk.HBox()
    self.actions.pack_start(self.add_b, False)
    self.actions.pack_start(self.edit_b, False)
    self.actions.pack_start(self.delete_b, False)
    
    self.vbox.pack_start(self.actions, False)
    
    self.add_with_viewport(self.vbox)
    
    self.show_all()

  def get_tab_label(self):
    return 'Profesores/as'

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    teacher_id = model.get_value(itr, 0)
    self.emit('teacher-edit', teacher_id)

gobject.type_register(TeachersList)
gobject.signal_new('teacher-edit', \
                   TeachersList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class TeachersTable(gtk.TreeView):
  def __init__(self, teachers):
    self.create_store(teachers)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.name_col = gtk.TreeViewColumn('Nombre', gtk.CellRendererText(), text=1)
    self.lastname_col = gtk.TreeViewColumn('Apellido', gtk.CellRendererText(), text=2)
    self.dni_col = gtk.TreeViewColumn('D.N.I.', gtk.CellRendererText(), text=3)
    self.email_col = gtk.TreeViewColumn('Email', gtk.CellRendererText(), text=4)
    self.address_col = gtk.TreeViewColumn('Dirección', gtk.CellRendererText(), text=5)

    self.name_col.set_expand(True)
    self.lastname_col.set_expand(True)
    self.dni_col.set_expand(True)
    self.email_col.set_expand(True)
    self.address_col.set_expand(True)
    
    self.append_column(self.name_col)
    self.append_column(self.lastname_col)
    self.append_column(self.dni_col)
    self.append_column(self.email_col)
    self.append_column(self.address_col)
  
  def create_store(self, teachers):
    # teacher, name, lastname, dni, email, address
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str,str)
    
    for t in teachers:
      self.store.append((t,t.name,t.lastname,t.dni,t.email,t.address))

