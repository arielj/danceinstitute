import gtk

class MainMenu(gtk.MenuBar):
  def __init__(self,main_window):
    gtk.MenuBar.__init__(self)
    self.controller = main_window.controller

    #dashboard menu
    self.home = gtk.MenuItem('Inicio')
    self.append(self.home)
    
    self.show_home = gtk.MenuItem('Inicio')
    self.quit = gtk.MenuItem('Salir')
    
    self.home_menu = gtk.Menu()
    self.home_menu.append(self.show_home)
    self.home_menu.append(self.quit)
    
    self.home.set_submenu(self.home_menu)
    
    #classes menu
    self.klasses = gtk.MenuItem('Clases')
    self.append(self.klasses)
    
    self.klasses_menu = gtk.Menu()
    self.add_klass = gtk.MenuItem('Agregar Clase')
    self.view_klasses = gtk.MenuItem('Ver Clases')
    
    self.klasses_menu.append(self.add_klass)
    self.klasses_menu.append(self.view_klasses)
    
    self.klasses.set_submenu(self.klasses_menu)
    
    #teachers menu
    self.teachers = gtk.MenuItem('Profesores')
    self.append(self.teachers)
    
    self.teachers_menu = gtk.Menu()
    self.add_teacher = gtk.MenuItem('Agregar Profesor')
    self.view_teachers = gtk.MenuItem('Ver Profesores')
    
    self.teachers_menu.append(self.add_teacher)
    self.teachers_menu.append(self.view_teachers)
    
    self.teachers.set_submenu(self.teachers_menu)
    
    #students menu
    self.students = gtk.MenuItem('Alumnos')
    self.append(self.students)
    
    self.students_menu = gtk.Menu()
    self.add_student = gtk.MenuItem('Agregar Alumno')
    self.search_student = gtk.MenuItem('Buscar Alumno')
    
    self.students_menu.append(self.add_student)
    self.students_menu.append(self.search_student)
    
    self.students.set_submenu(self.students_menu)
    
    self.bind_events()
    self.show_all()

  def bind_events(self):
    self.quit.connect('activate',self.controller.quit)
    self.add_teacher.connect('activate', self.controller.add_teacher)
    ##
    self.view_teachers.connect('activate', self.controller.edit_teacher)
    ##
    self.add_klass.connect('activate', self.controller.add_klass)
    self.view_klasses.connect('activate', self.controller.edit_klass)

