#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from translations import _t
from model import Model
import payment
import membership

class Installment(Model):
  table = 'installments'
  fields_for_save = ['year','month','membership_id','amount']

  def __init__(self, data = {}):
    self._year = datetime.today().year
    self.month = 0
    self.membership_id = None
    self._membership = None
    self._amount = 0
    self._payments = None
    
    Model.__init__(self, data)

  @property
  def year(self):
    return self._year

  @year.setter
  def year(self, value):
    try:
      self._year = int(value)
    except:
      self._year = 0

  @property
  def amount(self):
    return self._amount/100

  @amount.setter
  def amount(self,value):
    try:
      v = int(Decimal(value)*100)
    except:
      v = 0
    self._amount = v

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
  def membership(self):
    if self.membership_id and self._membership is None:
      self._membership = membership.Membership.find(self.membership_id)
    return self._membership

  @property
  def payments(self):
    if self._payments is None:
      self._payments = payment.Payment.for_installment(self.id)
    return self._payments

  def to_db(self):
    return {'year': self.year, 'month': self.month, 'membership_id': self.membership_id, 'amount': self.amount}

  def _is_valid(self):
    self.validate_numericallity_of('month', great_than_or_equal = 0, less_than_or_equal = 11)
    self.validate_numericallity_of('amount', great_than_or_equal = 0, only_integer = False)

  def add_payment(self, date, amount):
    amount = Decimal(amount)
    if amount <= self.to_pay():
      p = payment.Payment({'date': date, 'amount': amount, 'installment_id': self.id, 'student_id': self.get_student_id()})
      if p.save():
        self.payments.append(p)
        return True
      else:
        return p.full_errors()
    else:
      return "No se puede agregar un pago con mayor valor que resto a pagar."

  def get_student_id(self):
    s = self.membership.student
    return s.id if s else None

  def payments_details(self):
    return "\n".join(map(lambda p: p.to_s(), self.payments))

  def build_payment(self, data = {}):
    p = payment.Payment(data)
    p.installment_id = self.id
    return p

  @classmethod
  def for_membership(cls,membership_id):
    return cls.get_where('membership_id',membership_id)
