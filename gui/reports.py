#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import gtk
import gobject
import datetime

class DailyPayments(gtk.VBox):
  def __init__(self, payments):
    self.payments = payments
    gtk.VBox.__init__(self)
    
    self.from_e = gtk.Entry(10)
    self.from_e.set_text(str(datetime.datetime.today()))
    self.to_e = gtk.Entry(10)
    self.to_e.set_text(str(datetime.datetime.today()))
    self.done_rb = gtk.RadioButton(None, 'Hechos')
    self.received_rb = gtk.RadioButton(self.done_rb, 'Recibidos')
    self.received_rb.set_active(True)
    self.filter = gtk.Button('Buscar')
    
    self.form = gtk.HBox(False, 5)
    self.form.pack_start(gtk.Label('Desde:'), False)
    self.form.pack_start(self.from_e, False)
    self.form.pack_start(gtk.Label('Hasta:'), False)
    self.form.pack_start(self.to_e, False)
    self.form.pack_start(self.done_rb, False)
    self.form.pack_start(self.received_rb, False)
    self.form.pack_start(self.filter, False)
    
    self.pack_start(self.form, False)
    
    self.headings = ['Alumno', 'Fecha', 'Monto', 'Detalle']
    
    self.list = PaymentsList(payments, self.headings)
    
    self.pack_start(self.list, True)
    
    self.export = gtk.Button('Exportar')
    self.pack_start(self.export, False)
    
    self.show_all()

  def get_tab_label(self):
    return "Pagos"

  def to_html(self):
    done_or_received = 'hechos' if self.done_rb.get_active() else 'recibidos'
    title = "<h1>Pagos %s entre %s y %s</h1>" % (done_or_received, str(self.get_from()), str(self.get_to()))

    header = ''.join(map(lambda h: '<th>'+h+'</th>', self.headings))
    rows = ''.join(map(lambda p: '<tr>'+self.html_row(p)+'</tr>', self.payments))
    
    total = sum(map(lambda p: p.amount, self.payments))
    
    return html_wrapper(title+'<table><tr>'+header+'</td>'+rows+'</table><div id="total">Total: <span class="amount">$'+str(total)+'</span></div>')
    
  def html_row(self,p):
    values = [p.user.to_label(),str(p.date),str(p.amount),str(p.description)]
    return ''.join(map(lambda td: "<td>" + td + "</td>", values))

  def get_from(self):
    return self.from_e.get_text()

  def get_to(self):
    return self.to_e.get_text()

  def get_done_or_received(self):
    return self.done_rb.get_active()

  def update(self, payments = None):
    if payments is not None:
      self.payments = payments
    self.list.update(self.payments)

class PaymentsList(gtk.TreeView):
  def __init__(self, payments, headings):
    self.create_store(payments)
    
    gtk.TreeView.__init__(self, self.store)
    self.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
    
    for idx, heading in enumerate(headings, 1):
      self.add_column(heading,idx)

  def add_column(self, label, text_idx):
    col = gtk.TreeViewColumn(label, gtk.CellRendererText(), text=text_idx)
    col.set_expand(True)
    self.append_column(col)
    return col

  def create_store(self, payments):
    # payment, user name, date, amount, description
    self.store = gtk.ListStore(gobject.TYPE_PYOBJECT,str,str,str,str)
    self.update(payments)

  def update(self, payments):
    self.store.clear()
    self.set_model(payments)
  
  def set_model(self, payments):
    for p in payments:
      self.store.append((p,p.user.to_label(),str(p.date),str(p.amount), p.description))









def html_wrapper(content):
  css = """#wrapper {
	  padding:0px;
	  width:900px;
	  margin: 0 auto;
	  border:1px solid #000000;
	
	  -moz-border-radius-bottomleft:0px;
	  -webkit-border-bottom-left-radius:0px;
	  border-bottom-left-radius:0px;
	
	  -moz-border-radius-bottomright:0px;
	  -webkit-border-bottom-right-radius:0px;
	  border-bottom-right-radius:0px;
	
	  -moz-border-radius-topright:0px;
	  -webkit-border-top-right-radius:0px;
	  border-top-right-radius:0px;
	
	  -moz-border-radius-topleft:0px;
	  -webkit-border-top-left-radius:0px;
	  border-top-left-radius:0px;
  }
  #wrapper table{
    border-collapse: collapse;
    border-spacing: 0;
	  width:100%;
	  margin:0px;padding:0px;
  }
  #wrapper tr:last-child td:last-child {
	  -moz-border-radius-bottomright:0px;
	  -webkit-border-bottom-right-radius:0px;
	  border-bottom-right-radius:0px;
  }
  #wrapper table tr th {
	  -moz-border-radius-topleft:0px;
	  -webkit-border-top-left-radius:0px;
	  border-top-left-radius:0px;
  }
  #wrapper table tr:first-child td:last-child {
	  -moz-border-radius-topright:0px;
	  -webkit-border-top-right-radius:0px;
	  border-top-right-radius:0px;
  }
  #wrapper tr th {
	  -moz-border-radius-bottomleft:0px;
	  -webkit-border-bottom-left-radius:0px;
	  border-bottom-left-radius:0px;
  }
  #wrapper tr:hover td{
	
  }
  #wrapper tr:nth-child(odd){ background-color:#e5e5e5; }
  #wrapper tr:nth-child(even){ background-color:#b2b2b2; }
  #wrapper td{
	  vertical-align:middle;
	
	
	  border:1px solid #000000;
	  border-width:0px 1px 1px 0px;
	  text-align:left;
	  padding:7px;
	  font-size:14px;
	  font-family:Arial;
	  font-weight:normal;
	  color:#000000;
  }
  #wrapper tr:last-child td{
	  border-width:0px 1px 0px 0px;
  }
  #wrapper tr td:last-child{
	  border-width:0px 0px 1px 0px;
  }
  #wrapper tr:last-child td:last-child{
	  border-width:0px 0px 0px 0px;
  }
  #wrapper tr th{
		  background:-o-linear-gradient(bottom, #7f7f7f 5%, #cccccc 100%);	background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #7f7f7f), color-stop(1, #cccccc) );
	  background:-moz-linear-gradient( center top, #7f7f7f 5%, #cccccc 100% );
	  filter:progid:DXImageTransform.Microsoft.gradient(startColorstr="#7f7f7f", endColorstr="#cccccc");	background: -o-linear-gradient(top,#7f7f7f,cccccc);
    padding: 4px 0px;
	  background-color:#7f7f7f;
	  border:0px solid #000000;
	  text-align:center;
	  border-width:0px 0px 1px 1px;
	  font-size:18px;
	  font-family:Arial;
	  font-weight:bold;
	  color:#000000;
  }
  #wrapper tr:hover th {
	  background:-o-linear-gradient(bottom, #7f7f7f 5%, #cccccc 100%);	background:-webkit-gradient( linear, left top, left bottom, color-stop(0.05, #7f7f7f), color-stop(1, #cccccc) );
	  background:-moz-linear-gradient( center top, #7f7f7f 5%, #cccccc 100% );
	  filter:progid:DXImageTransform.Microsoft.gradient(startColorstr="#7f7f7f", endColorstr="#cccccc");	background: -o-linear-gradient(top,#7f7f7f,cccccc);

	  background-color:#7f7f7f;
  }
  #wrapper tr th:first-child{
	  border-width:0px 0px 1px 0px;
  }
  #wrapper tr th:last-child{
	  border-width:0px 0px 1px 1px;
  }
  #total {
    padding: 10px 5px;
    font-weight: bold;
  }
  #total span {
    font-weight: normal;
  }
"""

  return '<html><head><meta content="text/html; charset=UTF-8" http-equiv="Content-Type"><style>'+ css +'</style></head><body><div id="wrapper">'+content+'</div></body></html'

