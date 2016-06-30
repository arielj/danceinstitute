#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
import datetime
from decimal import Decimal
from translations import _t, _a
from model import Model
from lib.query_builder import Query
import payment
import user
import settings

class Liability(Model):
  table = 'liabilities'
  fields_for_save = ['date', 'amount', 'status', 'description', 'user_id']
  default_order = 'date ASC'

  def __init__(self, data = {}):
    self._date = datetime.datetime.now().date()
    self.month = 0
    self.description = ""
    self._amount = 0
    self._payments = None
    self._status = 'waiting'
    self.user_id = None
    self._user = None
    
    Model.__init__(self, data)

  @property
  def user(self):
    if self.user_id and self._user is None:
      self._user = user.User.find(self.user_id)
    return self._user

  @user.setter
  def user(self, value):
    self.user_id = None if value is None else value.id
    self._user = value

  def to_label(self):
    return self.description + ' (' + self.date.strftime('%d/%m/%Y') + ')'

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

  @property
  def date(self):
    return self._date

  @date.setter
  def date(self,value):
    if isinstance(value,datetime.date):
      self._date = value
    else:
      self._date = self.parse_date(value)

  def paid(self):
    return sum(map(lambda p: p.amount, self.payments),0)

  def detailed_amount(self):
    return '$'+str(self.amount)

  def detailed_to_pay(self):
    return '$'+str(self.to_pay())

  def to_pay(self):
    return self.amount-self.paid()
  
  def month_name(self):
    return _t('months')[self.month]

  @property
  def status(self):
    return _a(self.cls_name(), self._status)

  @status.setter
  def status(self, value):
    self._status = value

  @property
  def payments(self):
    if self._payments is None: self._payments = payment.Payment.for_liability(self.id).do_get()
    return self._payments

  def to_db(self):
    return {'date': self.date, 'description': self.description, 'amount': self.amount, 'status': self._status, 'user_id': self.user_id}

  def _is_valid(self):
    self.validate_numericallity_of('amount', great_than_or_equal = 0, only_integer = False)

  def add_payment(self, data = None):
    if data is None: data = {}
    if 'amount' not in data: data['amount'] = self.to_pay()
    amount = Decimal(data['amount'])
    
    if amount <= self.to_pay():
      data['liability_id'] = self.id
      #data['description'] = self.description
      p = payment.Payment(data)
      p.user = self.user
      if p.save():
        self.payments.append(p)
        if int(self.to_pay()) == 0:
          self._status = 'paid'
          self.save(validate = False)
        return p
      else:
        return p.full_errors()
    else:
      return "No se puede agregar un pago con mayor valor que el resto a pagar."

  def payments_details(self):
    return "\n".join(map(lambda p: p.to_s(), self.payments))

  def build_payment(self, data = {}):
    p = payment.Payment(data)
    p.liability = self
    self.payments.append(p)
    return p

  def before_delete(self):
    for p in self.payments:
      p.description = self.description
      p.liability = None
      p.save(validate=False)
    return True

  @classmethod
  def overdues(cls, recharge_after = None, klass = None, desc = '', include_inactive = False):
    q = cls.where('status != "paid"')
    if desc != '': q.where('description', '%%%s%%' % desc, comparission = 'LIKE')
    if include_inactive is False:
      q.set_join('LEFT JOIN users ON users.id = liabilities.user_id')
      q.where('users.inactive = 0')

    return q

  @classmethod
  def to_pay_for(cls, user_id):
    today = cls._today()
    w = 'status = "waiting" AND user_id = :user_id'
    args = {'user_id': user_id}
    
    return cls.where(w,args)

  @classmethod
  def _today(cls):
    return datetime.datetime.today()
