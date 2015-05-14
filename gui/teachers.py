#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from payments import PaymentsPanel

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
    self.fields = gtk.VBox()
    self.add_field('name', attrs=100)
    self.add_field('lastname', attrs=100)
    self.add_field('dni', attrs=10)
    
    self.gender_l = gtk.Label('Sexo')
    self.male_r = gtk.RadioButton(None, 'Hombre')
    self.male_r.set_active(True)
    self.female_r = gtk.RadioButton(self.male_r, 'Mujer')
    self.female_r.set_active(not self.object.male)
    self.fields.pack_start(self.gender_l,False)
    self.fields.pack_start(self.male_r,False)
    self.fields.pack_start(self.female_r,False)
    
    self.add_field('cellphone', attrs=16)
    self.add_field('alt_phone', attrs=16)
    self.add_field('address', attrs=256)
    self.add_field('birthday', attrs=10)
    self.add_field('email', attrs=256)
  
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
      self.emit('teacher-delete', teacher)

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
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
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

