#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
import student
import installment
from translations import _t
import datetime

class Membership(Model):
  #borrar después
  db = {1: {'student_id': 1, 'for_id': 1, 'for_type': 'Package', 'installment_ids': [1,2]}}

  def __init__(self, data = {}):
    Model.__init__(self)
    self.student_id = None
    self._student = None
    self.for_id = None
    self.for_type = ''
    self._for = None
    self.installment_ids = []
    self._installments = None
    
    self.set_attrs(data)

  @property
  def klass_or_package(self, requery = False):
    if self.for_id and (requery or self._for is None):
      if self.for_type = 'Package':
        self._for = package.Package.find(self.for_id)
      elif self.for_type = 'Klass'
        self._for = klass.Klass.find(self.for_id)
    return self._for
  
  @klass_or_package.setter
  def klass_or_package(self, klass_or_package):
    if klass_or_package.id is not None:
      self.for_id = for.id
    self._for = klass_or_package

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

  def build_installments(self, year, initial_month, final_month, fee):
    self.get_installments()
    for m in range(initial_month,final_month+1):
      self.installments.append(Installment({'package': self.package, 'year': year, 'amount': fee, 'month': m}))

  @classmethod
  def find(cls, id):
    m = cls(cls.db[id])
    m.id = id
    return m

  @classmethod
  def get_types(cls):
    return {'normal': 'Normal', 'half': 'Mitad de clases', 'once': 'Una sola clase'}

  def _is_valid(self):
    valid_installments = True
    for i in self.get_installments():
      if not i.is_valid():
        valid_installments = False
    if not valid_installments:
      self.add_error('installments', 'Una o más cuotas son inválidas.')

  def to_db(self):
    return {'student_id': self.student_id, 'package_id': self.package_id, 'type': self.type, 'info': self.info, 'installment_ids': self.installment_ids}

  def before_save(self):
    for i in self.get_installments():
      i.membership_id = self.id
      if i.save():
        if i.id not in self.installment_ids:
          self.installment_ids.append(i.id)
    return True

  def before_delete(self):
    for i in self.get_installments():
      i.delete()
    self.student.remove_membership(self.id)
    self.student.save()
