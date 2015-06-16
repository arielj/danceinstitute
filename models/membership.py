#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime
from translations import _t
from model import Model
from lib.query_builder import Query
import student
import installment
import klass
import package

class Membership(Model):
  table = 'memberships'
  fields_for_save = ['student_id','for_id','for_type','info']

  def __init__(self, data = {}):
    self.student_id = None
    self._student = None
    self.for_id = None
    self.for_type = ''
    self._for = None
    self._installments = None
    self.info = ''
    self.active = True
    
    Model.__init__(self, data)

  @property
  def klass_or_package(self):
    if self.for_id and self._for is None:
      if self.for_type == 'Package':
        self._for = package.Package.find(self.for_id)
      elif self.for_type == 'Klass':
        self._for = klass.Klass.find(self.for_id)
    return self._for
  
  @klass_or_package.setter
  def klass_or_package(self, klass_or_package):
    self.for_id = klass_or_package.id
    self.for_type = klass_or_package.__class__.__name__
    self._for = klass_or_package

  def get_fee(self):
    obj = self.klass_or_package
    if isinstance(obj, klass.Klass):
      return obj.normal_fee
    else:
      return obj.fee

  @property
  def student(self):
    if self.student_id and self._student is None:
      self._student = student.Student.find(self.student_id)
    return self._student

  @student.setter
  def student(self, st):
    if st is not None:
      self.student_id = st.id
      self._student = st
    else:
      self.student_id = None
      self._student = None

  @property
  def installments(self):
    if self._installments is None:
      self._installments = installment.Installment.for_membership(self.id)
    return self._installments

  def add_installment(self, i):
    if i.id not in map(lambda i: i.id, self.installments):
      self.installments.append(i)

  def remove_installment(self, i):
    if isinstance(i,installment.Installment):
      i = i.id

    for ins in self.installments:
      if ins.id == i:
        self.installments.remove(ins)

  def create_installments(self, year, initial_month, final_month, fee):
    year = year
    initial_month = initial_month
    final_month = final_month
    fee = Decimal(fee)
    if initial_month >= 0:
      if final_month <= 11:
        if initial_month <= final_month:
          if fee > 0:
            ins = []
            for m in range(initial_month, final_month+1):
              i = installment.Installment({'year': year, 'month': m, 'amount': fee, 'membership_id': self.id, 'student_id': self.student_id})
              if i.save():
                self.add_installment(i)
              else:
                return "Al menos una de las cuotas no se puede agregar: " + i.full_errors()
            return True
          else:
            return "El precio debe ser mayor a 0."
        else:
          return "El mes inicial no puede ser mayor al mes final."
      else:
        return "El mes final no puede ser mayor a 11."
    else:
      return "El mes inicial no puede ser menor a 0."

  @classmethod
  def get_types(cls):
    return {'normal': 'Normal', 'half': 'Mitad de clases', 'once': 'Una sola clase'}

  def to_db(self):
    return {'student_id': self.student_id, 'for_id': self.for_id, 'for_type': self.for_type, 'info': self.info}

  def _is_valid(self):
    self.validate_presence_of('student')

  def before_delete(self):
    for i in self.installments:
      i.delete()
    return True

  def is_package(self):
    return self.for_type == 'Package'

  @classmethod
  def for_student(cls,st_id):
    return Query(cls).where('student_id', st_id)

  @classmethod
  def for_klass_or_package(cls,k_or_p):
    return Query(cls).where('for_id', k_or_p.id).where('for_type', k_or_p.cls_name())
