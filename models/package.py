#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import datetime
from lib.query_builder import Query
import membership
import klass
from settings import Settings

class Package(Model):
  table = 'packages'
  fields_for_save = ['name','fee','alt_fee','for_user']
  default_order = 'name ASC'

  def __init__(self, attrs = {}):
    self.name = ''
    self._klasses = None
    self._fee = 0
    self._alt_fee = 0
    self._for_user = 0
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

  def get_hours_fee(self):
    hours = 0
    fixed_fee = 0
    for klass in self.klasses():
      if klass.normal_fee > 0:
        fixed_fee += int(klass.normal_fee)
      else:
        hours += klass.get_duration()

    if hours == int(hours): hours = int(hours)
    hours_fee = Settings.get_settings().get_fee_for(str(hours)) if hours > 0 else 0

    return str(hours_fee+fixed_fee)

  @property
  def klasses(self):
    if self._klasses is None: self._klasses = klass.Klass.for_package(self.id)
    return self._klasses

  @klasses.setter
  def klasses(self, kls):
    self._klasses = kls

  def klasses_names(self, separator = ', '):
    return separator.join(map(lambda x: x.name, self.klasses))

  @property
  def for_user(self):
    return self._for_user

  @for_user.setter
  def for_user(self,value):
    self._for_user = int(value)

  def to_db(self):
    return {'name': self.name, 'fee': self.fee, 'alt_fee': self.alt_fee, 'for_user': self.for_user}

  def after_save(self):
    c = self.__class__.get_conn()
    self.__class__.set_from('klasses_packages').where('package_id', self.id).delete_all()
    for k in self.klasses:
      args = {'klass_id': k.id, 'package_id': self.id}
      self.__class__.get_conn().execute('INSERT INTO klasses_packages (klass_id,package_id) VALUES (:klass_id,:package_id)', args)

  def _is_valid(self):
    self.validate_presence_of('name')
    if self.for_user == 0: self.validate_numericallity_of('fee', great_than = 0)
    if self.is_new_record():
      if self.for_user == 0:
        self.validate_quantity_of('klasses', great_than = 1, message = 'Tenés que elegir por lo menos dos clases')
      else:
        self.validate_quantity_of('klasses', great_than = 0, message = 'Tenés que elegir por lo menos una clase')

  @classmethod
  def with_klass(cls,klass):
    return cls.set_from('klasses_packages').set_join('LEFT JOIN packages ON klasses_packages.package_id = packages.id').where('klasses_packages.klass_id', klass.id, placeholder='klass_id')

  @classmethod
  def for_user_with_klasses(cls, klasses):
    ids = sorted(map(lambda k: k.id, klasses))
    name = 'Clases ' + str(datetime.date.today().year) + ' (' + ','.join(map(lambda i: str(i), ids)) + ')'

    p = cls({'name': name, 'for_user': 1})
    p.klasses = klasses
    p.save()
    return p

  @classmethod
  def for_user(cls, user):
    return cls.find_by('for_user', user.id)

  def can_delete(self):
    if membership.Membership.for_klass_or_package(self).anything():
      return "Hay alumnos inscriptos a este paquete."
    return True

  def before_delete(self):
    self.__class__.get_conn().execute('DELETE FROM klasses_packages WHERE package_id = :package_id', {'package_id': self.id})
    return True
