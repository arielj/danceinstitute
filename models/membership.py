#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
import student
import installment
from translations import _t
import datetime
import klass
import package

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

  @classmethod
  def get_types(cls):
    return {'normal': 'Normal', 'half': 'Mitad de clases', 'once': 'Una sola clase'}

  def to_db(self):
    return {'student_id': self.student_id, 'for_id': self.for_id, 'for_type': self.for_type, 'info': self.info, 'installment_ids': self.installment_ids}

  def _is_valid(self):
    return True

  def before_delete(self):
    for i in self.get_installments():
      i.delete()
    self.student.remove_membership(self.id)
    self.student.save()

