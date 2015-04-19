import gtk

class StudentForm(gtk.Frame):
  def __init__(self, student):
    gtk.Frame.__init__(self)
    self.student = student

    self.fields = self.get_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    if self.student.id:
      title = 'Alumno' if self.student.male else 'Alumna'
      return 'Editar ' + title + ': ' + self.student.name + ' ' + self.student.lastname
    else:
      return 'Agregar Alumno/a'
  
  def get_form_fields(self):
    self.name_l = gtk.Label('Nombre')
    self.name_e = gtk.Entry(100)
    
    self.lastname_l = gtk.Label('Apellido')
    self.lastname_e = gtk.Entry(100)
    
    self.dni_l = gtk.Label('D.N.I')
    self.dni_e = gtk.Entry(10)
    
    self.gender_l = gtk.Label('Sexo')
    self.male_r = gtk.RadioButton(None, 'Hombre')
    self.male_r.set_active(True)
    self.female_r = gtk.RadioButton(self.male_r, 'Mujer')
    
    self.cellphone_l = gtk.Label('Celular')
    self.cellphone_e = gtk.Entry(16)
    
    self.address_l = gtk.Label('Address')
    self.address_e = gtk.Entry(256)
    
    self.birthday_l = gtk.Label('Fecha de nacimiento')
    self.birthday_e = gtk.Entry(10)
    
    self.email_l = gtk.Label('Email')
    self.email_e = gtk.Entry(256)
    
    self.name_e.set_text(self.student.name)
    self.lastname_e.set_text(self.student.lastname)
    self.dni_e.set_text(self.student.dni)
    self.female_r.set_active(not self.student.male)
    self.cellphone_e.set_text(self.student.cellphone)
    self.address_e.set_text(self.student.address)
    self.birthday_e.set_text(self.student.birthday)
    self.email_e.set_text(self.student.email)
    
    fields = gtk.VBox()
    fields.pack_start(self.name_l,False)
    fields.pack_start(self.name_e,False)
    fields.pack_start(self.lastname_l,False)
    fields.pack_start(self.lastname_e,False)
    fields.pack_start(self.dni_l,False)
    fields.pack_start(self.dni_e,False)
    fields.pack_start(self.gender_l,False)
    fields.pack_start(self.male_r,False)
    fields.pack_start(self.female_r,False)
    fields.pack_start(self.cellphone_l,False)
    fields.pack_start(self.cellphone_e,False)
    fields.pack_start(self.address_l,False)
    fields.pack_start(self.address_e,False)
    fields.pack_start(self.birthday_l,False)
    fields.pack_start(self.birthday_e,False)
    fields.pack_start(self.email_l,False)
    fields.pack_start(self.email_e,False)
      
    return fields
  
  def get_values(self):
    return {'name': self.name_e.get_text(), 'lastname': self.lastname_e.get_text(), 'dni': self.dni_e.get_text(), 'male': self.male_r.get_active(), 'cellphone': self.cellphone_e.get_text(), 'address': self.address_e.get_text(), 'birthday': self.birthday_e.get_text(), 'email': self.email_e.get_text()}
