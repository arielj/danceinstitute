#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
import datetime
from settings import Settings
from forms import FormFor
from translations import _t, _m

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
  def __init__(self, klasses, title = 'Nuevo paquete'):
    self.form = NewUserPackageForm(klasses)
    gtk.Dialog.__init__(self, title, None,
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
    self.day_checks = {}
    for day in klasses:
      day_box = gtk.VBox(False, 2)
      day_box.pack_start(gtk.Label(_t('days')[day]))
      self.day_checks[day] = day_box
      for klass in sorted(klasses[day]):
        sch = klass.schedule_for_day(day)
        check = gtk.CheckButton(sch.get_full_name(add_day = False))
        check.connect('toggled', self.on_klass_toggled)
        self.checks[check] = sch
        day_box.pack_start(check)

    self.days_wrapper = gtk.HBox(False, 2)
    for day in sorted(self.day_checks):
      self.days_wrapper.pack_start(self.day_checks[day])

    self.pack_start(self.days_wrapper)

    self.create_installments = gtk.CheckButton('Agregar cuotas?')
    self.create_installments.set_active(True)
    self.pack_start(self.create_installments)

    label2 = gtk.Label('Precio')
    self.pack_start(label2)

    self.fee_e = gtk.Entry(10)
    self.fee_e.set_text('0')
    self.pack_start(self.fee_e)

    self.months = gtk.HBox(False, 4)

    field = gtk.VBox()
    self.initial_month_l = gtk.Label('Mes inicial')
    store = gtk.ListStore(int, str)
    for i,m in enumerate(_t('months')):
      store.append((i,m))
    self.initial_month_e = gtk.ComboBox(store)
    cell = gtk.CellRendererText()
    self.initial_month_e.pack_start(cell, True)
    self.initial_month_e.add_attribute(cell, 'text', 1)
    start_m = datetime.datetime.today().month
    if datetime.datetime.today().day <= 25: start_m = start_m-1
    if start_m < 0: start_m = 0
    if Settings.get_settings().installments_from > start_m: start_m = Settings.get_settings().installments_from
    self.initial_month_e.set_active(start_m)
    field.pack_start(self.initial_month_l, False)
    field.pack_start(self.initial_month_e, False)
    self.months.pack_start(field, True)

    field = gtk.VBox()
    self.final_month_l = gtk.Label('Mes final')
    store = gtk.ListStore(int, str)
    for i,m in enumerate(_t('months')):
      store.append((i,m))
    self.final_month_e = gtk.ComboBox(store)
    cell = gtk.CellRendererText()
    self.final_month_e.pack_start(cell, True)
    self.final_month_e.add_attribute(cell, 'text', 1)
    end_m = Settings.get_settings().installments_to
    if end_m <= start_m: end_m = start_m + 3
    if end_m > 11: end_m = 11
    self.final_month_e.set_active(end_m)
    field.pack_start(self.final_month_l, False)
    field.pack_start(self.final_month_e, False)
    self.months.pack_start(field, True)

    self.pack_start(self.months, False)

  def on_klass_toggled(self, check):
    hours = 0
    fixed_fee_klasses = []
    for sch in self.get_checked_schedules():
      if int(sch.klass.normal_fee) > 0:
        if not [k for k in fixed_fee_klasses if k.id == sch.klass.id]:
          fixed_fee_klasses.append(sch.klass)
      else:
        hours += sch.duration()

    if hours == int(hours): hours = int(hours)
    hours_fee = Settings.get_settings().get_fee_for(str(hours)) if hours > 0 else 0
    fixed_fee = sum(map((lambda k: k.normal_fee), fixed_fee_klasses))

    self.fee_e.set_text(str(hours_fee+fixed_fee))

  def get_checked_schedules(self):
    checked = []
    for (c,sch) in self.checks.items():
      if c.get_active() is True: checked.append(sch)
    return checked

  def get_checked_klasses(self):
    checked = []
    for (c,sch) in self.checks.items():
      if c.get_active() is True:
        if not [k for k in checked if k.id == sch.klass.id]: checked.append(sch.klass)
    return checked

  def should_create_installments(self):
    return self.create_installments.get_active()

  def get_initial_month(self):
    itr = self.initial_month_e.get_active_iter()
    return self.initial_month_e.get_model().get_value(itr,0)

  def get_final_month(self):
    itr = self.final_month_e.get_active_iter()
    return self.final_month_e.get_model().get_value(itr,0)

  def get_amount(self):
    return int(self.fee_e.get_text())

class EditUserPackageDialog(NewUserPackageDialog):
  def __init__(self, package, klasses):
    NewUserPackageDialog.__init__(self, klasses, 'Editar Paquete')
    self.package = package
    for (c,k) in self.form.checks.items():
      if k in package.klasses: c.set_active(True)
    self.form.months.set_no_show_all(True)
    self.form.create_installments.set_no_show_all(True)
    self.form.months.hide()
    self.form.create_installments.hide()

class CustomCheckButton(gtk.CheckButton):
  def __init__(self,k):
    gtk.CheckButton.__init__(self,k.name)
    self.k = k
