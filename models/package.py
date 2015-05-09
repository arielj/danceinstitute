#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import klass

class Package(Model):
  db = {1: {'name': 'Paquete A', 'klass_ids': [1,2], 'fee': 500, 'alt_fee': 350}}
  
  def __init__(self, attrs = {}):
    self.name = ''
    self.klass_ids = []
    self._klasses = None
    self.fee = 0.00
    self.alt_fee = 0.00
    Model.__init__(self,attrs)

  @property
  def fee(self):
    return self.fee
  
  @fee.setter
  def fee(self,value):
    try:
      self.fee = Decimal(value)
    except:
      self.fee = 0.00

  @property
  def klasses(self, requery = False):
    if requery or self._klasses is None:
      self._klasses = []
      for k in self.klass_ids:
        self._klasses.append(klass.Klass.find(k))
    return self._klasses

  def klasses_names(self):
    return ', '.join(map(lambda x: x.name, self.klasses))

  def to_db(self):
    return {'name': self.name, 'klass_ids': self.klass_ids, 'fee': self.fee, 'alt_fee': self.alt_fee}

  def _is_valid(self):
    self.validate_presence_of('name')
    self.validate_numericallity_of('fee', great_than = 0)
    self.validate_quantity_of('klass_ids', great_than = 1, message = 'Tenés que elegir por lo menos dos clases')
