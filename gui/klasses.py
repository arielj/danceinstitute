import gtk

ROOMS = ['Agua', 'Fuego', 'Aire']

class KlassForm(gtk.Frame):
  def __init__(self, controller, klass):
    gtk.Frame.__init__(self)
    self.klass = klass
    self.controller = controller

    self.fields = self.get_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.submit.connect('clicked',self.controller.submit_klass, self)
    self.fields.pack_start(self.submit,False)
    
    self.add(self.fields)
    
    self.show_all()

  def get_tab_label(self):
    return 'Editar Clase' if self.klass.id else 'Agregar Clase'
  
  def get_form_fields(self):
    self.name_l = gtk.Label('Nombre')
    self.name_e = gtk.Entry(100)
    
    self.from_time_l = gtk.Label('Desde')
    self.from_time_e = gtk.Entry(5)
    
    self.to_time_l = gtk.Label('Hasta')
    self.to_time_e = gtk.Entry(5)
        
    self.room_l = gtk.Label('Sala')
    self.rooms = {}
    radio_group = None
    for r in ROOMS:
      self.rooms[r] = gtk.RadioButton(radio_group, r)
      if radio_group is None:
        radio_group = self.rooms[r]
    
    self.name_e.set_text(self.klass.name)
    self.from_time_e.set_text(self.klass.from_time)
    self.to_time_e.set_text(self.klass.to_time)
    for r in ROOMS:
      self.rooms[r].set_active(self.klass.room == r)
    
    fields = gtk.VBox()
    fields.pack_start(self.name_l,False)
    fields.pack_start(self.name_e,False)
    fields.pack_start(self.from_time_l,False)
    fields.pack_start(self.from_time_e,False)
    fields.pack_start(self.to_time_l,False)
    fields.pack_start(self.to_time_e,False)
    fields.pack_start(self.room_l,False)
    for r in ROOMS:
      fields.pack_start(self.rooms[r],False)
      
    return fields
  
  def get_selected_room(self):
    for r in ROOMS:
      if self.rooms[r].get_active() is True:
        return r
    return ''

  def get_values(self):
    return {'name': self.name_e.get_text(), 'from_time': self.from_time_e.get_text(), 'to_time': self.to_time_e.get_text(), 'room': self.get_selected_room()}
