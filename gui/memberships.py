#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor
from translations import _t

class MembershipsPanel(gtk.VBox):
  def __init__(self, student):
    gtk.VBox.__init__(self)
    self.student = student

    self.pack_start(gtk.Label('Clases y cuotas:'), False)

    self.enroll_b = gtk.Button('Incribir a una clase')
    
    self.pack_start(self.enroll_b, False)

    self.notebook = gtk.Notebook()
    
    self.add_tabs()
      
    self.pack_start(self.notebook, True)
    
  def add_tabs(self):
    for m in self.student.memberships:
      self.add_tab(m)

  def add_tab(self,m):
    t = MembershipTab(m)
    self.notebook.append_page(t,gtk.Label(m.klass_or_package.name))
    t.delete_b.connect('clicked', self.on_delete_clicked, m)
    t.add_installments_b.connect('clicked', self.on_add_ins_clicked, m)

  def update(self):
    children = self.notebook.get_children()
    for m in self.student.memberships:
      found = False
      for tab in children:
        if tab.membership == m:
          tab.refresh()
          found = True
      if not found:
        self.add_tab(m)
    self.notebook.show_all()

  def on_membership_deleted(self, m_id):
    self.student.remove_membership(m_id)
    for tab in self.notebook.get_children():
      if tab.membership.id == m_id:
        self.notebook.remove_page(self.notebook.page_num(tab))
    self.update()

  def on_delete_clicked(self, widget, membership):
    self.emit('ask-delete-membership', membership)

  def on_add_ins_clicked(self, widget, membership):
    self.emit('add-installments', membership)

gobject.type_register(MembershipsPanel)
gobject.signal_new('ask-delete-membership', \
                   MembershipsPanel, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))
gobject.signal_new('add-installments', \
                   MembershipsPanel, \
                   gobject.SIGNAL_RUN_FIRST, \
                   gobject.TYPE_NONE, (gobject.TYPE_PYOBJECT,))

class MembershipTab(gtk.VBox):
  def __init__(self, membership):
    gtk.VBox.__init__(self)
    
    self.membership = membership
    
    self.info_vbox =gtk.VBox()
    self.info_vbox.pack_start(gtk.Label('Información:'), False)
    self.info_vbox.pack_start(gtk.Label(membership.info), False)   

    self.pack_start(self.info_vbox, False)

    #installment, year, month, base, recharges, status
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,int,str,str,str,str)
    
    self.refresh()
    
    self.list = gtk.TreeView(self.store)
    
    self.add_column('Año',1)
    self.add_column('Mes',2)
    self.add_column('Monto',3)
    self.add_column('Pagado',4)
    self.add_column('Estado',5)

    self.scrolled = gtk.ScrolledWindow()
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.list)
    self.scrolled.add(viewport)
    
    self.pack_start(self.scrolled, True)
    
    self.actions = gtk.HBox(True, 5)
    
    self.add_installments_b = gtk.Button('Agregar Cuotas')
    self.delete_b = gtk.Button('Eliminar inscripción')
    
    self.actions.pack_start(self.add_installments_b, False)
    self.actions.pack_start(self.delete_b, False)
    
    self.pack_start(self.actions, False)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col

  def refresh(self):
    self.store.clear()
    
    for ins in self.membership.installments:
      self.store.append((ins,ins.year,ins.month_name(),ins.to_pay(), ins.paid(), ins.status()))

class MembershipDialog(gtk.Dialog):
  def __init__(self, membership, options):
    self.form = MembershipForm(membership, options)
    gtk.Dialog.__init__(self, self.form.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()
    
class MembershipForm(FormFor):
  def __init__(self, membership, options):
    FormFor.__init__(self, membership)
    
    self.fields = gtk.VBox()
    
    store = gtk.ListStore(int, str, gobject.TYPE_PYOBJECT)
    for o in options:
      store.append((o.id,o.name,o))
    self.add_field('klass_or_package', field_type = 'combo', list_store = store)
    
    self.add_field('info', attrs = 250)
    
    self.pack_start(self.fields, False)

  def get_values(self):
    return {'klass_or_package': self.get_selected_klass_or_package(),'info': self.info_e.get_text()}

  def get_tab_label(self):
    if self.object.id:
      return "Editar inscripción:\n" + self.object.klass_or_package.name
    else:
      return 'Agregar nueva inscripción'

  def get_selected_klass_or_package(self):
    m = self.klass_or_package_e.get_model()
    itr = self.klass_or_package_e.get_active_iter()
    if itr is not None:
      return m.get_value(itr,2)


class AddInstallmentsDialog(gtk.Dialog):
  def __init__(self,membership):
    self.membership = membership
    self.form = AddInstallmentsForm(membership)
    gtk.Dialog.__init__(self, 'Agregar cuotas', None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()

class AddInstallmentsForm(FormFor):
  """hola"""

