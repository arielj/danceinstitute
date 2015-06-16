#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import datetime
import installment
import student
import teacher
from lib.query_builder import Query

class Payment(Model):
  table = 'payments'
  fields_for_save = ['amount','installment_id','user_id','user_type','date','description', 'done']

  def __init__(self, attrs = {}):
    self._amount = 0
    self.installment_id = None
    self._installment = None
    self.user_id = None
    self.user_type = ''
    self._user = None
    self._date = datetime.datetime.now().date()
    self._description = ''
    self.done = False
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
    return ' '.join(descs)

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

  def _is_valid(self):
    self.validate_numericallity_of('amount', great_than = 0, only_integer = False)

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'installment_id': self.installment_id, 'user_id': self.user_id, 'user_type': self.user_type, 'description': self._description, 'done': int(self.done)}

  def to_s(self):
    return str(self.date) + ": $" + str(self.amount)

  @classmethod
  def for_installment(cls,ins_id):
    return Query(cls).where('installment_id',ins_id)

  @classmethod
  def for_user(cls,u_id,include_installments = True, done = None):
    q = Query(cls).where('user_id', u_id)

    if not include_installments: q.where('installment_id IS NULL')
    if done is not None: q.where('done', int(done))

    return q

  @classmethod
  def filter(cls, f, t, done = None, user_id = None):
    q = Query(cls).where('date', str(f), comparission = '>=', placeholder = 'from').where('date', str(t), comparission = '<=', placeholder = 'to')
    
    if done is not None: q.where('done', int(done))
    if user_id is not None: q.where('user_id', user_id)

    return q.order_by('date ASC')
