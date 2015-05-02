#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
from forms import FormFor

class MembershipsPanel(gtk.VBox):
  def __init__(self, student):
    gtk.VBox.__init__(self)
    self.student = student

    self.pack_start(gtk.Label('Clases y cuotas:'), False)

    self.enroll_b = gtk.Button('Incribir a una clase')
    
    self.pack_start(self.enroll_b, False)

    self.notebook = gtk.Notebook()
    
    for m in student.get_memberships():
      self.notebook.append_page(MembershipTab(m),gtk.Label(m.get_klass().name))
      
    self.pack_start(self.notebook, True)

class MembershipTab(gtk.VBox):
  def __init__(self, membership):
    gtk.VBox.__init__(self)
    
    #installment, year, month, base, recharges, status
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,int,str,str,str,str)
    
    for ins in membership.get_installments():
      self.store.append((ins,membership.year,ins.get_month(),ins.amount, ins.get_amount(), ins.get_status()))
    
    self.list = gtk.TreeView(self.store)
    
    self.add_column('Año',1)
    self.add_column('Mes',2)
    self.add_column('Monto',3)
    self.add_column('Con intereses',4)
    self.add_column('Estado',5)

    self.scrolled = gtk.ScrolledWindow()
    viewport = gtk.Viewport()
    viewport.set_shadow_type(gtk.SHADOW_NONE)
    viewport.add(self.list)
    self.scrolled.add(viewport)
    
    self.pack_start(self.scrolled, True)
    
    self.delete_b = gtk.Button('Eliminar inscripción')
    
    self.pack_start(self.delete_b, False)
    
  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.list.append_column(col)
    return col

class MembershipDialog(gtk.Dialog):
  def __init__(self, membership, klasses):
    self.form = MembershipForm(membership, klasses)
    gtk.Dialog.__init__(self, self.form.get_tab_label(), None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_NO_SEPARATOR,
                        (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                         gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    self.vbox.pack_start(self.form, False)
    self.vbox.show_all()
    self.form.on_type_changed(None)
    
class MembershipForm(FormFor):
  def __init__(self, membership, klasses):
    FormFor.__init__(self, membership)
    
    self.fields = gtk.VBox()
    
    self.add_field('Año', 'year', attrs=4)

    store = gtk.ListStore(int, str, gobject.TYPE_PYOBJECT)
    for k in klasses:
      store.append((k.id,k.name,k))
    self.add_field('Clase', 'klass_id', field_type = 'combo', list_store = store)
    
    store = gtk.ListStore(str, str)
    types = membership.__class__.get_types()
    for t in types.keys():
      store.append((t,types[t]))
    self.add_field('Tipo de inscripción', 'type', field_type = 'combo', list_store = store)

    store = gtk.ListStore(int, str)
    for i,m in enumerate(membership.__class__.months()):
      store.append((i,m))
    self.add_field('Mes inicial', 'initial_month', field_type = 'combo', list_store = store)

    store = gtk.ListStore(int, str)
    for i,m in enumerate(membership.__class__.months()):
      store.append((i,m))
    self.add_field('Mes final', 'final_month', field_type = 'combo', list_store = store)
    self.add_field('Fecha', 'date', attrs=10)
    self.add_field('Precio', 'fee', attrs=10)
    
    self.pack_start(self.fields, False)

    self.type_e.connect('changed', self.on_type_changed)
    self.klass_id_e.connect('changed', self.on_klass_changed)
    
  def update_fee(self, data = None):
    klass = self.get_selected_klass()
    t = self.get_selected_type()
    if t is not None and klass is not None:
      self.fee_e.set_text(str(klass.get_fee_for(t) or ''))
      self.fee_e.grab_focus()

  def on_type_changed(self, entry):
    t = self.get_selected_type()
    if t == 'once':
      self.date_field.show()
      self.initial_month_field.hide()
      self.final_month_field.hide()
    else:
      self.date_field.hide()
      self.initial_month_field.show()
      self.final_month_field.show()
  
    self.update_fee()
  
  def on_klass_changed(self, entry):
    self.update_fee()

  def get_tab_label(self):
    if self.object.id:
      return "Editar inscripción:\n" + self.object.klass.name + ' ' + self.object.year
    else:
      return 'Agregar nueva inscripción'

  def get_selected_klass(self):
    m = self.klass_id_e.get_model()
    itr = self.klass_id_e.get_active_iter()
    if itr is not None:
      return m.get_value(itr,2)
    
  def get_selected_type(self):
    m = self.type_e.get_model()
    itr = self.type_e.get_active_iter()
    if itr is not None:
      return m.get_value(itr,0)

