#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from settings import Settings
from forms import FormFor

class PackagesList(gtk.VBox):
  def __init__(self, packages, with_actions = True):
    gtk.VBox.__init__(self)
    self.set_border_width(4)
    self.packages = packages
    self.with_actions = with_actions
    
    self.scroll = gtk.ScrolledWindow()
    self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

    store = gtk.ListStore(int, str, gobject.TYPE_PYOBJECT)
    for p in packages: store.append((p.id,p.name,p))
    self.package_e = gtk.Entry(255)
    
    hbox = gtk.HBox(False, 5)
    hbox.pack_start(gtk.Label('Buscar:'), False)
    hbox.pack_start(self.package_e, False)
    self.pack_start(hbox, False)

    self.packages_t = PackagesTable(packages)
    self.packages_t.connect('row-activated', self.on_row_activated)
    self.t_selection = self.packages_t.get_selection()
    self.t_selection.connect('changed', self.on_selection_changed)
    
    self.scroll.add(self.packages_t)
    self.pack_start(self.scroll, True)
    
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
      
      self.pack_start(self.actions, False)
    
    self.show_all()

  @classmethod
  def tab_label(cls):
    return 'Paquetes'

  def get_tab_label(self):
    return self.__class__.tab_label()

  def refresh_list(self, packages):
    self.packages_t.update(packages)

  def on_row_activated(self, tree, path, column):
    model = tree.get_model()
    itr = model.get_iter(path)
    package = model.get_value(itr, 0)
    self.emit('package-edit', package.id)

  def on_selection_changed(self, selection):
    if self.with_actions:
      model, iter = selection.get_selected()
      self.edit_b.set_sensitive(iter is not None)
      self.delete_b.set_sensitive(iter is not None)
    self.emit('selection-changed', selection)

  def on_add_clicked(self, btn):
    self.emit('package-add')

  def on_edit_clicked(self, btn):
    package = self.get_selected()
    if package is not None:
      self.emit('package-edit', package)

  def on_delete_clicked(self, btn):
    package = self.get_selected()
    if package is not None:
      self.emit('package-delete', package)

  def get_selected(self):
    model, iter = self.t_selection.get_selected()
    return model.get_value(iter,0) if iter is not None else None

gobject.type_register(PackagesList)
gobject.signal_new('package-edit', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('package-delete', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))
gobject.signal_new('package-add', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, ())
gobject.signal_new('selection-changed', \
                   PackagesList, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT, ))

class PackagesTable(gtk.TreeView):
  def __init__(self, packages):
    self.create_store(packages)
    
    gtk.TreeView.__init__(self,self.store)
    
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    self.add_column('Nombre', 1)
    self.add_column('Clases', 2)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col
  
  def create_store(self, packages):
    # package, name, klasses names
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str)
    self.update(packages)

  def update(self, packages):
    self.store.clear()
    self.set_model(packages)
  
  def set_model(self, packages):
    for p in packages:
      self.store.append((p,p.name,p.klasses_names()))

class PackageForm(FormFor):
  def __init__(self, package, klasses):
    FormFor.__init__(self, package)

    self.klasses= klasses

    self.create_form_fields()
    
    self.submit = gtk.Button('Guardar')
    self.fields.pack_start(self.submit,False)
    
    self.pack_start(self.fields, True)
    
    self.show_all()

  def get_tab_label(self):
    if self.object.id:
      return "Editar paquete:\n" + self.object.name
    else:
      return 'Agregar paquete'
  
  def create_form_fields(self):
    self.fields = gtk.VBox()
    self.add_field('name', attrs=100)
    self.add_field('fee', attrs=5)
    self.add_field('alt_fee', attrs=5)
    if self.object.is_new_record():
      self.fields.pack_start(gtk.Label('Clases'), False)
      columns = 5
      rows = self.klasses.count()/columns
      if self.klasses.count()%columns > 0:
        rows += 1
      table = gtk.Table(rows, columns)
      self.klass_checks = []
      for idx, k in enumerate(self.klasses):
        check = CustomCheckButton(k)
        self.klass_checks.append(check)
        c = idx%columns
        r = idx/columns
        table.attach(check,c,c+1,r,r+1)
      self.fields.pack_start(table, False)

  def get_klasses(self):
    kls = []
    if self.object.is_new_record():
      for c in self.klass_checks:
        if c.get_active():
          kls.append(c.k)
    return kls
  
  def get_values(self):
    values = {'name': self.name_e.get_text(), 'fee': self.fee_e.get_text(), 'alt_fee': self.alt_fee_e.get_text()}
    kls = self.get_klasses()
    if kls:
      values['klasses'] = kls
    return values

class NewUserPackageDialog(gtk.Dialog):
  def __init__(self, klasses):
    self.form = NewUserPackageForm(klasses)
    gtk.Dialog.__init__(self, 'Nuevo paquete', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class NewUserPackageForm(gtk.VBox):
  def __init__(self, klasses):
    gtk.VBox.__init__(self, False, 4)
    label = gtk.Label('Clases')
    self.pack_start(label)
    
    self.checks = {}
    for klass in klasses:
      check = gtk.CheckButton(klass.get_full_name())
      check.connect('toggled', self.on_klass_toggled)
      self.checks[check] = klass
    
    for check in self.checks.keys():
      self.pack_start(check)
    
    self.create_installments = gtk.CheckButton('Agregar cuotas?')
    self.create_installments.set_active(True)
    self.pack_start(self.create_installments)
    
    label2 = gtk.Label('Precio')
    self.pack_start(label2)
    
    self.fee_e = gtk.Entry(10)
    self.fee_e.set_text('0')
    self.pack_start(self.fee_e)

  def on_klass_toggled(self, check):
    durations = map(lambda (c, k): k.get_duration() if c.get_active() is True else 0, self.checks.items())
    duration = sum(durations)

    klasses_fee = Settings.get_settings().get_fee_for_hours(str(duration)) if duration > 0 else 0
    self.fee_e.set_text(str(klasses_fee))

class CustomCheckButton(gtk.CheckButton):
  def __init__(self,k):
    gtk.CheckButton.__init__(self,k.name)
    self.k = k

