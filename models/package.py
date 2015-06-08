#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import membership
import klass

class Package(Model):
  table = 'packages'
  fields_for_save = ['name','fee','alt_fee']
  
  def __init__(self, attrs = {}):
    self.name = ''
    self._klasses = None
    self._fee = 0
    self._alt_fee = 0
    Model.__init__(self,attrs)

  @property
  def fee(self):
    return self._fee/100
  
  @fee.setter
  def fee(self,value):
    try:
      self._fee = int(Decimal(value)*100)
    except:
      self._fee = 0

  @property
  def alt_fee(self):
    return self._alt_fee/100
  
  @alt_fee.setter
  def alt_fee(self,value):
    try:
      self._alt_fee = int(Decimal(value)*100)
    except:
      self._alt_fee = 0

  @property
  def klasses(self):
    if self._klasses is None:
      self._klasses = klass.Klass.for_package(self.id)
    return self._klasses

  @klasses.setter
  def klasses(self, kls):
    self._klasses = kls

  def klasses_names(self):
    return ', '.join(map(lambda x: x.name, self.klasses))

  def to_db(self):
    return {'name': self.name, 'fee': self._fee, 'alt_fee': self._alt_fee}

  def after_save(self):
    c = self.__class__.get_conn()
    for k in self.klasses:
      args = {'klass_id': k.id, 'package_id': self.id}
      if c.execute('SELECT COUNT(*) FROM klasses_packages WHERE klass_id = :klass_id AND package_id = :package_id', args).fetchone()[0] == 0:
        self.__class__.get_conn().execute('INSERT INTO klasses_packages (klass_id,package_id) VALUES (:klass_id,:package_id)', args)

  def _is_valid(self):
    self.validate_presence_of('name')
    self.validate_numericallity_of('fee', great_than = 0)
    if self.is_new_record():
      self.validate_quantity_of('klasses', great_than = 1, message = 'Tenés que elegir por lo menos dos clases')

  @classmethod
  def with_klass(cls,klass):
    return cls.get_many('SELECT packages.* FROM klasses_packages LEFT JOIN packages ON klasses_packages.package_id = packages.id WHERE klasses_packages.klass_id = :k_id', {'k_id': klass.id})

  def can_delete(self):
    if membership.Membership.for_klass_or_package(self):
      return "Hay alumnos inscriptos a este paquete."
    return True

  def before_delete(self):
    self.__class__.get_conn().execute('DELETE FROM klasses_packages WHERE package_id = :package_id', {'package_id': self.id})
    return True
