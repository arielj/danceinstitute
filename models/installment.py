#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from translations import _t

class Installment(Model):
  #borrar después
  db = {1: {'month': 4, 'paid': True, 'amount': '300'},
        2: {'month': 5, 'paid': False, 'amount': '300'}}
  
  def __init__(self, data = {}):
    Model.__init__(self)
    self.month = 0
    self.membership_id = None
    self.paid = False
    self.amount = 0.00
    self.payment_ids = []
    
    self.set_attrs(data)

  def get_amount(self):
    recharge = 0
    
    # calcular recargo según fecha del mes?
    # debería ser configurable la fecha y el porcentaje
    # debería poder configurar 2 recargos

    return self.amount*(1+recharge)
  
  def get_month(self):
    return _t('months')[self.month]

  def get_status(self):
    if self.paid:
      return 'Pagado'
    elif self.get_amount() != self.amount:
      return 'Atrasado'
    else:
      return 'A pagar'

  @classmethod
  def find(cls, id):
    i = cls(cls.db[id])
    i.id = id
    return i

  def to_db(self):
    return {'month': self.month, 'membership_id': self.membership_id, 'paid': self.paid, 'amount': self.amount, 'payment_ids': self.payment_ids}

  def _is_valid(self):
    self.validate_numericallity_of('month', great_than = -1, less_than = 12)

