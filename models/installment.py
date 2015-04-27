#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model

installments = {1: {'month': 4, 'year': 2015, 'paid': True, 'amount': '300'},
                2: {'month': 5, 'year': 2015, 'paid': False, 'amount': '300'}}

class Installment(Model):
  def __init__(self, data = {}):
    Model.__init__(self)
    self.month = 1
    self.year = 2015
    self.membership_id = None
    self.paid = False
    self.amount = 0.00
    self.payment_id = None
    
    self.set_attrs(data)

  def get_amount(self):
    recharge = 0
    
    # calcular recargo según fecha del mes?
    # debería ser configurable la fecha y el porcentaje
    # debería poder configurar 2 recargos

    return self.amount*(1+recharge)
  
  def get_month(self):
    return ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'][self.month-1]

  @classmethod
  def find(cls, id):
    return cls(installments[id])
