#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from klass import Klass
from installment import Installment
from translations import _t
import datetime

class Membership(Model):
  #borrar después
  db = {1: {'student_id': 1, 'klass_id': 1, 'installment_ids': [1,2], 'year': 2015}}

  def __init__(self, data = {}):
    Model.__init__(self)
    self.student_id = None
    self._student = None
    self.klass_id = None
    self._klass = None
    self._year = 2015
    self.type = 'normal'
    self.info = ''
    self._initial_month = 0
    self._final_month = 11
    self._date = datetime.date.today()
    self.fee = 0
    self.installment_ids = []
    self.installments = None
    
    self.set_attrs(data)

  @property
  def date(self):
    if self._date is not None:
      return self._date.strftime('%Y-%m-%d')
    else:
      return ''
  
  @date.setter
  def date(self,value):
    try:
      self._date = datetime.datetime.strptime(value, '%Y-%m-%d')
    except:
      try:
        self._date = datetime.datetime.strptime(value, '%Y/%m/%d')
      except:
        try:
          self._date = datetime.datetime.strptime(value, '%d/%m/%Y')
        except:
          try:
            self._date = datetime.datetime.strptime(value, '%d-%m-%Y')
          except:
            self._date = None

  @property
  def year(self):
    return self._year

  @year.setter
  def year(self,value):
    try:
      self._year = int(value)
    except:
      self._year = 0

  @property
  def initial_month(self):
    return self._initial_month

  @initial_month.setter
  def initial_month(self,value):
    try:
      self._initial_month = int(value)
    except:
      self._initial_month = 0

  @property
  def final_month(self):
    return self._final_month

  @final_month.setter
  def final_month(self,value):
    try:
      self._final_month = int(value)
    except:
      self._final_month = 0

  @property
  def klass(self):
    return self._klass
  
  @klass.setter
  def klass(self,klass):
    if klass.id is not None:
      self.klass_id = klass.id
    self._klass = klass

  def get_student(self, requery = False):
    if requery or self.student is None:
      self.student = Student.find(self.student_id)
    return self.student

  def get_klass(self, requery = False):
    if requery or self.klass is None:
      self.klass = Klass.find(self.klass_id)
    return self.klass

  def get_installments(self, requery = False):
    if requery or self.installments is None:
      self.installments = []
      for i in self.installment_ids:
        self.installments.append(Installment.find(i))
    return self.installments

  def build_installments(self):
    self.get_installments()
    for m in range(self.initial_month,self.final_month+1):
      self.installments.append(Installment({'amount': self.fee, 'month': m}))

  @classmethod
  def find(cls, id):
    m = cls(cls.db[id])
    m.id = id
    return m

  @classmethod
  def get_types(cls):
    return {'normal': 'Normal', 'half': 'Mitad de clases', 'once': 'Una sola clase'}

  def _is_valid(self):
    if self.type == 'normal' or self.type == 'half':
      if self.initial_month > self.final_month:
        self.add_error('initial_month', 'El mes inicial no puede ser mayor al mes final.')
    else:
      if self.date is None:
        self.add_error('date', 'El campo "Fecha" tiene un formato inválido.')
    
    valid_installments = True
    for i in self.get_installments():
      if not i.is_valid():
        valid_installments = False
    if not valid_installments:
      self.add_error('installments', 'Una o más cuotas son inválidas.')

  def to_db(self):
    return {'student_id': self.student_id, 'klass_id': self.klass_id, 'year': self.year, 'type': self.type, 'info': self.info, 'initial_month': self.initial_month, 'final_month': self.final_month, 'date': self.date, 'fee': self.fee, 'installment_ids': self.installment_ids}

  def before_save(self):
    for i in self.get_installments():
      i.membership_id = self.id
      if i.save():
        if i.id not in self.installment_ids:
          self.installment_ids.append(i.id)
    return True
