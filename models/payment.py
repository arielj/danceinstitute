#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import datetime
import installment
import student

class Payment(Model):
  table = 'payments'
  fields_for_save = ['amount','installment_id','student_id','date','description']

  def __init__(self, attrs = {}):
    self._amount = 0
    self.installment_id = None
    self._installment = None
    self.student_id = None
    self._student = None
    self._date = datetime.datetime.now().date()
    self._description = ''
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
      descs.append(ins.membership.klass.name + ' ' + ins.month_name() + ' ' + str(ins.year))
    return ' '.join(descs)

  @description.setter
  def description(self, value):
    value = value or ''
    self._description = value

  @property
  def student(self):
    if self.student_id and self._student is None:
      self._student = student.Student.find(self.student_id)
    return self._student
    
  @student.setter
  def student(self, st):
    if st is None:
      self.student_id = None
    else:
      self.student_id = st.id
    self._student = st

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

  def _is_valid(self):
    self.validate_numericallity_of('amount', great_than = 0, only_integer = False)

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'installment_id': self.installment_id, 'student_id': self.student_id, 'description': self._description}

  def to_s(self):
    return str(self.date) + ": $" + str(self.amount)

  @classmethod
  def for_installment(cls,ins_id):
    return cls.get_where('installment_id',ins_id)

  @classmethod
  def for_student(cls,st_id,include_installments = True):
    q = 'SELECT * FROM payments WHERE student_id = :st_id'
    args = {'st_id': st_id}
    if include_installments:
      return cls.get_many(q,args)
    else:
      return cls.get_many(q + ' AND installment_id IS NULL',args)
