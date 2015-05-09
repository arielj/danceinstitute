#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from translations import _t
from model import Model
import payment
import membership

class Installment(Model):
  #borrar después
  db = {1: {'year': 2015, 'month': 4, 'amount': 300, 'payment_ids': [1,2], 'membership_id': 1},
        2: {'year': 2015, 'month': 5, 'amount': 300, 'payment_ids': [3], 'membership_id': 1}}
  
  def __init__(self, data = {}):
    self.month = 0
    self.membership_id = None
    self._membership = None
    self.amount = 0.00
    self.payment_ids = []
    self._payments = None
    
    Model.__init__(self, data)

  def paid(self):
    return sum(map(lambda p: p.amount, self.payments),0)

  def total(self):
    recharge = 0
    
    # calcular recargo según fecha del mes?
    # debería ser configurable la fecha y el porcentaje
    # debería poder configurar 2 recargos

    return self.amount*(1+recharge)

  def to_pay(self):
    return self.total()-self.paid()
  
  def month_name(self):
    return _t('months')[self.month]

  def status(self):
    return 'Pagado' if self.to_pay() == 0 else 'A pagar'

  @property
  def membership(self, requery = False):
    if self.membership_id and (requery or self._membership is None):
      self._membership = membership.Membership.find(self.membership_id)
    return self._membership

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

  def add_payment(self, date, amount):
    amount = Decimal(amount)
    if amount <= self.to_pay():
      p = payment.Payment({'date': date, 'amount': amount, 'installment_id': self.id, 'student_id': self.membership.student_id})
      if p.is_valid():
        p.save()
        self.payment_ids.append(p.id)
        self.payments.append(p)
        return True
      else:
        return p.full_errors()
    else:
      return "No se puede agregar un pago con mayor valor que resto a pagar."

  def get_student_id(self):
    s = self.membership.student
    return s.id if s else None
    
