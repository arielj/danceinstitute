import gtk

class TeacherForm(gtk.Frame):
  def __init__(self,teacher):
    gtk.Frame.__init__(self)
    self.teacher = teacher

    self.fields = self.get_form()
    self.add(self.fields)
    
    self.show_all()
  
  def get_tab_label(self):
    if self.teacher.id:
      title = 'Profesor' if self.teacher.male else 'Profesora'
      return 'Editar ' + title + ': ' + self.teacher.name + ' ' + self.teacher.lastname
    else:
      return 'Agregar Profesor'
  
  def get_form(self):
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
    
    self.name_e.set_text(self.teacher.name)
    self.lastname_e.set_text(self.teacher.lastname)
    self.dni_e.set_text(self.teacher.dni)
    self.female_r.set_active(not self.teacher.male)
    self.cellphone_e.set_text(self.teacher.cellphone)
    self.address_e.set_text(self.teacher.address)
    self.birthday_e.set_text(self.teacher.birthday)
    
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
      
    return fields
