#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
import klass

class Package(Model):
  db = {1: {'klass_ids': [1], 'amount': 350, 'alt_amount': 200}, 2: {'klass_ids': [2], 'amount': 300, 'alt_amount': 200}, 3: {'klass_ids': [1,2], 'amount': 500, 'alt_amount': 350}}
  
  def __init__(self, attrs = {}):
    Model.__init__(self)
    self.klass_ids = []
    self._klasses = None
    self.amount = 0.00
    self.alt_amount = 0.00

  @property
  def klasses(self, requery = False):
    if requery or self._klasses is None:
      self._klasses = []
      for k in self.klass_ids:
        self._klasses.append(Klass.find(k))
    return self._klasses
