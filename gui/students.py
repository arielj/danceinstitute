#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
from forms import FormFor

class StudentForm(FormFor):
  def __init__(self, student):
    FormFor.__init__(self, student)

    self.create_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      title = 'Alumno' if self.object.male else 'Alumna'
      return 'Editar ' + title + ': ' + self.object.name + ' ' + self.object.lastname
    else:
      return 'Agregar Alumno/a'
  
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
