#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
import student
import installment
from translations import _t
import datetime
import klass
import package
from decimal import Decimal

class Membership(Model):
  #borrar después
  db = {1: {'student_id': 1, 'for_id': 1, 'for_type': 'Klass', 'installment_ids': [1,2], 'info': 'Clase normal lalala'}}

  def __init__(self, data = {}):
    Model.__init__(self)
    self.student_id = None
    self._student = None
    self.for_id = None
    self.for_type = ''
    self._for = None
    self.installment_ids = []
    self._installments = None
    self.info = ''
    self.active = True
    
    self.set_attrs(data)

  @property
  def klass_or_package(self, requery = False):
    if self.for_id and (requery or self._for is None):
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
  def student(self, requery = False):
    if requery or self._student is None:
      self._student = student.Student.find(self.student_id)
    return self._student

  @property
  def installments(self, requery = False):
    if requery or self._installments is None:
      self._installments = []
      for i in self.installment_ids:
        self._installments.append(installment.Installment.find(i))
    return self._installments

  def add_installment(self, i):
    if i not in self.installment_ids:
      self.installment_ids.append(i.id)
      self.installments.append(i)

  def create_installments(self, year, initial_month, final_month, fee):
    try:
      year = int(year)
      initial_month = int(initial_month)
      final_month = int(final_month)
      fee = Decimal(fee)
      if initial_month >= 0:
        if final_month <= 11:
          if initial_month <= final_month:
            if fee > 0:
              for m in range(initial_month, final_month+1):
                i = installment.Installment({'year': year, 'month': m, 'amount': fee, 'membership_id': self.id, 'student_id': self.student_id})
                i.save()
                self.add_installment(i)
            else:
              return "El precio debe ser mayor a 0."
          else:
            return "El mes inicial no puede ser mayor al mes final."
        else:
          return "El mes final no puede ser mayor a 11."
      else:
        return "El mes inicial no puede ser menor a 0."
    except:
      return "No se pueden crear las cuotas, revisá los valores cargados."

  @classmethod
  def get_types(cls):
    return {'normal': 'Normal', 'half': 'Mitad de clases', 'once': 'Una sola clase'}

  def to_db(self):
    return {'student_id': self.student_id, 'for_id': self.for_id, 'for_type': self.for_type, 'info': self.info, 'installment_ids': self.installment_ids}

  def _is_valid(self):
    return True

  def before_delete(self):
    for i in self.installments:
      i.delete()
    self.student.remove_membership(self.id)
    self.student.save()

  def is_package(self):
    return self.for_type == 'Package'
