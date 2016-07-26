#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk

class MainMenu(gtk.MenuBar):
  def __init__(self):
    gtk.MenuBar.__init__(self)

    #dashboard menu
    self.home = gtk.MenuItem('Inicio')
    self.append(self.home)
    
    self.show_home = gtk.MenuItem('Inicio')
    self.config = gtk.MenuItem('Configuración')
    self.quit = gtk.MenuItem('Salir')
    
    self.home_menu = gtk.Menu()
    self.home_menu.append(self.show_home)
    self.home_menu.append(self.config)
    self.home_menu.append(self.quit)
    
    self.home.set_submenu(self.home_menu)
    
    #rooms menu
    self.rooms = gtk.MenuItem('Salas')
    self.append(self.rooms)
    
    self.rooms_menu = gtk.Menu()
    self.list_rooms = gtk.MenuItem('Salas')
    self.show_schedules = gtk.MenuItem('Horarios')
    
    self.rooms_menu.append(self.list_rooms)
    self.rooms_menu.append(self.show_schedules)
    self.rooms.set_submenu(self.rooms_menu)
    
    #classes menu
    self.klasses = gtk.MenuItem('Clases')
    self.append(self.klasses)
    
    self.klasses_menu = gtk.Menu()
    self.add_klass = gtk.MenuItem('Agregar Clase')
    self.list_klasses = gtk.MenuItem('Clases')
    self.show_packages = gtk.MenuItem('Paquetes')
    
    self.klasses_menu.append(self.add_klass)
    self.klasses_menu.append(self.list_klasses)
    self.klasses_menu.append(self.show_packages)
    
    self.klasses.set_submenu(self.klasses_menu)
    
    #teachers menu
    self.teachers = gtk.MenuItem('Profesores')
    self.append(self.teachers)
    
    self.teachers_menu = gtk.Menu()
    self.add_teacher = gtk.MenuItem('Agregar Profesor/a')
    self.list_teachers = gtk.MenuItem('Profesores/as')
    
    self.teachers_menu.append(self.add_teacher)
    self.teachers_menu.append(self.list_teachers)
    
    self.teachers.set_submenu(self.teachers_menu)
    
    #students menu
    self.students = gtk.MenuItem('Alumnos')
    self.append(self.students)
    
    self.students_menu = gtk.Menu()
    self.add_student = gtk.MenuItem('Agregar Alumno/a')
    self.search_student = gtk.MenuItem('Buscar Alumno/a')
    
    self.students_menu.append(self.add_student)
    self.students_menu.append(self.search_student)
    
    self.students.set_submenu(self.students_menu)
    
    #reports menu
    self.reports = gtk.MenuItem('Reportes')
    self.append(self.reports)
    
    self.reports_menu = gtk.Menu()
    self.payments = gtk.MenuItem('Pagos')
    self.daily_cash = gtk.MenuItem('Caja Diaria')
    self.installments = gtk.MenuItem('Cuotas')
    self.debts = gtk.MenuItem('Deudas')
    
    self.reports_menu.append(self.payments)
    self.reports_menu.append(self.daily_cash)
    self.reports_menu.append(self.installments)
    self.reports_menu.append(self.debts)
    
    self.reports.set_submenu(self.reports_menu)
    
    #help menu
    self.help = gtk.MenuItem('Ayuda')
    self.append(self.help)
    
    self.help_menu = gtk.Menu()
    self.license = gtk.MenuItem('Licencia')
    self.show_help = gtk.MenuItem('Ayuda')
    self.about = gtk.MenuItem('Acerca de')
    
    self.help_menu.append(self.license)
    self.help_menu.append(self.show_help)
    self.help_menu.append(self.about)
    
    self.help.set_submenu(self.help_menu)

    self.show_all()

