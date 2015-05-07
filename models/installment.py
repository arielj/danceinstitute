#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from translations import _t
import payment

class Installment(Model):
  #borrar después
  db = {1: {'year': 2015, 'month': 4, 'amount': 300, 'payment_ids': [1,2]},
        2: {'year': 2015, 'month': 5, 'amount': 300, 'payment_ids': [3]}}
  
  def __init__(self, data = {}):
    Model.__init__(self)
    self.month = 0
    self.membership_id = None
    self.amount = 0.00
    self.payment_ids = []
    self._payments = None
    
    self.set_attrs(data)

  def paid(self):
    total = 0
    for p in self.payments:
      total += p.amount
    return total

  def to_pay(self):
    recharge = 0
    
    # calcular recargo según fecha del mes?
    # debería ser configurable la fecha y el porcentaje
    # debería poder configurar 2 recargos

    return self.amount*(1+recharge)
  
  def month_name(self):
    return _t('months')[self.month]

  def status(self):
    if self.to_pay() <= self.paid():
      return 'Pagado'
    else:
      return 'A pagar'

  @property
  def payments(self, requery = False):
    if requery or self._payments is None:
      self._payments = []
      for i in self.payment_ids:
        self._payments.append(payment.Payment.find(i))
    return self._payments

  def to_db(self):
    return {'month': self.month, 'membership_id': self.membership_id, 'amount': self.amount, 'payment_ids': self.payment_ids}

  def _is_valid(self):
    self.validate_numericallity_of('month', great_than = -1, less_than = 12)

