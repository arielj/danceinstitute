#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import datetime
import installment
import package
import student
import teacher
from lib.query_builder import Query

class Payment(Model):
  table = 'payments'
  fields_for_save = ['amount','installment_id','user_id','user_type','date','description', 'done','receipt_number']
  default_order = 'date ASC'

  def __init__(self, attrs = {}):
    self._amount = 0
    self.installment_id = None
    self._installment = None
    self.user_id = None
    self.user_type = ''
    self._user = None
    self._date = datetime.datetime.now().date()
    self._description = ''
    self._done = False
    self._receipt_number = None
    Model.__init__(self, attrs)

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
  def description(self):
    descs = []
    if self._description:
      descs.append(self._description)
    
    ins = self.installment
    if ins:
      descs.append(ins.membership.klass_or_package.name + ' ' + ins.month_name() + ' ' + str(ins.year))
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
  def date(self):
    return self._date

  @date.setter
  def date(self,value):
    if isinstance(value,datetime.date):
      self._date = value
    else:
      try:
        self._date = datetime.datetime.strptime(value,'%Y/%m/%d').date()
      except:
        try:
          self._date = datetime.datetime.strptime(value,'%Y/%d/%m').date()
        except:
          try:
            self._date = datetime.datetime.strptime(value,'%Y-%m-%d').date()
          except:
            try:
              self._date = datetime.datetime.strptime(value,'%Y-%d-%m').date()
            except:
              try:
                self._date = datetime.datetime.strptime(value,'%d-%m-%Y').date()
              except:
                try:
                  self._date = datetime.datetime.strptime(value,'%d/%m/%Y').date()
                except:
                  self._date = ''

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

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'installment_id': self.installment_id, 'user_id': self.user_id, 'user_type': self.user_type, 'description': self._description, 'done': int(self.done), 'receipt_number': self.receipt_number}

  def to_s(self):
    s = str(self.date) + ": $" + str(self.amount)
    if self._description: s += ' ('+self._description+')'
    if self.receipt_number is not None: s += ' (R.N°:'+str(self.receipt_number)+')'
    return s

  @classmethod
  def for_installment(cls,ins_id):
    return cls.where('installment_id',ins_id)

  @classmethod
  def for_user(cls,u_id,include_installments = True, done = None):
    q = cls.where('user_id', u_id)

    if not include_installments: q.where('installment_id IS NULL')
    if done is not None: q.where('done', int(done))

    return q

  @classmethod
  def filter(cls, f, t, done = None, user = None, klass = None):
    q = cls.where('date', str(f), comparission = '>=', placeholder = 'from').where('date', str(t), comparission = '<=', placeholder = 'to')
    
    if done is not None: q.where('done', int(done))
    if user is not None: q.where('user_id', user.id)
    if klass is not None:
      where = 'memberships.for_id = :klass_id AND memberships.for_type = "Klass"'
      args = {'klass_id': klass.id}
      packages = package.Package.with_klass(klass)
      if packages.anything():
        where = '('+where+') OR (memberships.for_id IN (:p_ids) AND memberships.for_type = "Package")'
        args['p_ids'] = ','.join(map(lambda p: str(p.id), packages))

      q.set_join('LEFT JOIN installments ON installments.id = payments.installment_id LEFT JOIN memberships ON installments.membership_id = memberships.id').where(where,args)

    return q

