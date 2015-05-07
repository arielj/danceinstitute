#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
import klass

class Package(Model):
  db = {1: {'name': 'Paquete A', 'klass_ids': [1,2], 'amount': 500, 'alt_amount': 350}}
  
  def __init__(self, attrs = {}):
    Model.__init__(self)
    self.name = ''
    self.klass_ids = []
    self._klasses = None
    self.amount = 0.00
    self.alt_amount = 0.00
    
    self.set_attrs(attrs)

  @property
  def klasses(self, requery = False):
    if requery or self._klasses is None:
      self._klasses = []
      for k in self.klass_ids:
        self._klasses.append(klass.Klass.find(k))
    return self._klasses

  def klasses_names(self):
    return ', '.join(map(lambda x: x.name, self.klasses))

  @classmethod
  def all(cls):
    packages = []
    for p in cls.db:
      packages.append(cls.find(p))
    return packages
