#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import datetime
import installment
import liability
import package
import klass
import student
import teacher
from lib.money import Money
from lib.query_builder import Query
from settings import Settings

class Payment(Model):
  table = 'payments'
  fields_for_save = ['amount', 'installment_id', 'user_id', 'user_type', 'date', 'description', 'done', 'receipt_number', 'liability_id']
  default_order = 'date ASC'

  def __init__(self, attrs = {}):
    self._amount = Money(0)
    self.installment_id = None
    self._installment = None
    self.liability_id = None
    self._liability = None
    self.user_id = None
    self.user_type = ''
    self._user = None
    self._date = datetime.datetime.now().date()
    self._description = ''
    self._done = False
    self._receipt_number = None
    Model.__init__(self, attrs)
    
  @classmethod
  def from_db(cls, r):
    m = cls(r)
    m._amount._cents = r['amount']
    return m

  @property
  def amount(self):
    return self._amount

  @amount.setter
  def amount(self,value):
    try:
      v = Money(value)
    except:
      v = Money(0)
    self._amount = v

  @property
  def description(self):
    descs = []
    if self._description: descs.append(self._description)
    
    if self.installment:
      ins = self.installment
      if self._description != ins.description(): descs.append(ins.description())
    
    if self.liability:
      li = self.liability
      if self._description != li.description: descs.append(li.description)

    return '. '.join(descs)

  @description.setter
  def description(self, value):
    value = value or ''
    self._description = value

  @property
  def user(self):
    if self.user_id and self._user is None:
      if self.user_type == 'Student':
        self._user = student.Student.find(self.user_id)
      else:
        self._user = teacher.Teacher.find(self.user_id)
    return self._user
    
  @user.setter
  def user(self, u):
    if u is None:
      self.user_id = None
      self.user_type = ''
    else:
      self.user_id = u.id
      self.user_type = u.__class__.__name__
    self._user = u

  @property
  def installment(self):
    if self.installment_id and self._installment is None:
      self._installment = installment.Installment.find(self.installment_id)
    return self._installment

  @installment.setter
  def installment(self, ins):
    if ins is None:
      self.installment_id = None
    else:
      self.installment_id = ins.id
    self._installment = ins
    
  @property
  def liability(self):
    if self.liability_id and self._liability is None:
      self._liability = liability.Liability.find(self.liability_id)
    return self._liability

  @liability.setter
  def liability(self, li):
    if li is None:
      self.liability_id = None
    else:
      self.liability_id = li.id
    self._liability = li

  @property
  def date(self):
    return self._date

  @date.setter
  def date(self,value):
    if isinstance(value,datetime.date):
      self._date = value
    else:
      self._date = self.parse_date(value)

  @property
  def done(self):
    return bool(self._done)

  @done.setter
  def done(self,value):
    self._done = bool(value)

  @property
  def receipt_number(self):
    return self._receipt_number
  
  @receipt_number.setter
  def receipt_number(self, value):
    try:
      self._receipt_number = int(value)
    except:
      self._receipt_number = None

  def _is_valid(self):
    self.validate_numericallity_of('amount', great_than = 0, only_integer = False)
    self.validate_presence_of('date')

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'installment_id': self.installment_id, 'user_id': self.user_id, 'user_type': self.user_type, 'description': self.description, 'done': int(self.done), 'receipt_number': self.receipt_number, 'liability_id': self.liability_id}

  def to_s(self):
    s = self.date.strftime(Settings.get_settings().date_format) + ": $" + str(self.amount)

    if self._description:
      d = self.installment.description() if self.installment else ''
      if self._description != d: s += ' ('+self._description+')'

    if self.receipt_number is not None: s += ' (R.N°:'+str(self.receipt_number)+')'
    return s

  @classmethod
  def for_installment(cls,ins_id):
    return cls.where('installment_id',ins_id)

  @classmethod
  def for_liability(cls,li_id):
    return cls.where('liability_id',li_id)

  @classmethod
  def for_user(cls,u_id,include_installments = True, done = None):
    q = cls.where('user_id', u_id)

    if not include_installments: q.where('installment_id IS NULL')
    if done is not None: q.where('done', int(done))

    return q

  @classmethod
  def filter(cls, f, t, done = None, user = None, k_or_p = None, group = '', q_term = '', include_inactive = False):
    if isinstance(f, datetime.datetime): f = f.strftime('%Y-%m-%d')
    if isinstance(t, datetime.datetime): t = t.strftime('%Y-%m-%d')
    q = cls.where('date', f, comparission = '>=', placeholder = 'from').where('date', t, comparission = '<=', placeholder = 'to')
    
    if done is not None: q.where('done', int(done))
    if user is not None: q.where('user_id', user.id)
    if q_term != '': q.where('description', '%%%s%%' % q_term, comparission = 'LIKE')
    if include_inactive is False:
      q.set_join('LEFT JOIN users ON users.id = payments.user_id')
      q.where('users.inactive = 0')

    if k_or_p is not None:
      if isinstance(k_or_p, klass.Klass):
        where = 'memberships.for_id = :klass_id AND memberships.for_type = "Klass"'
        args = {'klass_id': k_or_p.id}
        packages = package.Package.with_klass(k_or_p)
        if packages.anything():
          where = '('+where+') OR (memberships.for_id IN (%s) AND memberships.for_type = "Package")' % ','.join(map(lambda p: str(p.id), packages))

      elif isinstance(k_or_p, package.Package):
        where = 'memberships.for_id = :package_id AND memberships.for_type = "Package"'
        args = {'package_id': k_or_p.id}
        where = '('+where+') OR (memberships.for_id IN (%s) AND memberships.for_type = "Klass")' % ','.join(map(lambda k: str(k.id), k_or_p.klasses))
          
      q.set_join('LEFT JOIN installments ON installments.id = payments.installment_id LEFT JOIN memberships ON installments.membership_id = memberships.id').where(where,args)
    
    if group:
      q.set_join('LEFT JOIN users ON users.id = payments.user_id')
      q = q.where('group', '%'+group+'%', comparission = 'LIKE')

    return q

