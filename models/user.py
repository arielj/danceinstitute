#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
from model import Model
from database import Conn
import payment
import liability
import membership
import datetime

def titleize(value):
  names = []
  for name in (value or '').split(' '):
    titleized = ''
    if len(name) > 0:
      titleized += name[0]
    if len(name) > 1:
      titleized += name[1:]
    names.append(titleized)
  return ' '.join(names)

class User(Model):
  table = 'users'
  fields_for_save = ['name', 'lastname', 'dni', 'cellphone', 'alt_phone', 'birthday', 'address', 'male', 'email', 'is_teacher', 'comments', 'facebook_uid', 'age', 'group', 'inactive']
  default_order = 'name ASC, lastname ASC'

  def __init__(self, data = {}):
    self._name = ''
    self._lastname = ''
    self._dni = ''
    self.cellphone = ''
    self.alt_phone = ''
    self.birthday = ''
    self._age = 0
    self.address = ''
    self._male = True
    self.email = ''
    self._is_teacher = False
    self.comments = ''
    self.facebook_uid = ''
    self._memberships = None
    self.family = None
    self.group = ''
    self.inactive = False
    
    Model.__init__(self,data)

  @property
  def name(self):
    return self._name
  
  @name.setter
  def name(self,value):
    #str.title() broken if str has accented chars
    self._name = titleize(value)

  @property
  def lastname(self):
    return self._lastname

  @lastname.setter
  def lastname(self,value):
    #str.title() broken if str has accented chars
    self._lastname = titleize(value)

  @property
  def male(self):
    return bool(self._male)
  
  @male.setter
  def male(self,value):
    self._male = int(value)

  @property
  def is_teacher(self):
    return bool(self._is_teacher)
  
  @is_teacher.setter
  def is_teacher(self,value):
    self._is_teacher = int(value)

  @property
  def dni(self):
    if self._dni:
      return self._dni[0:2]+'.'+self._dni[2:5]+'.'+self._dni[5:8]
    else:
      return ''

  @dni.setter
  def dni(self, value):
    if value:
      self._dni = re.sub(r'\.','',str(value))

  @property
  def age(self):
    return self._age
  
  @age.setter
  def age(self,value):
    try:
      self._age = int(value)
    except:
      self._age = 0

  @property
  def memberships(self):
    if self.is_new_record(): self._memberships = []
    if self._memberships is None: self._memberships = membership.Membership.for_student(self.id)
    return self._memberships

  def reload_memberships(self):
    self._memberships = None
    return self.memberships

  def to_label(self, add_group = False):
    s = ' '.join([self.name,self.lastname])
    if add_group is True and self.group is not None and self.group != "": s += ' (%s)' % self.group
    return s

  def after_save(self):
    for m in self.memberships:
      m.save(validate = False)
    return True

  def can_delete(self):
    if membership.Membership.where('student_id', self.id).anything():
      return "El alumno está inscripto en una o más clases."
    if payment.Payment.for_user(self.id).anything():
      return "El alumno realizó pagos."
    return True


  def _is_valid(self):
    user.User._is_valid(self)
    self.validate_has_many('memberships')

  def update_id_on_associations(self):
    for m in self.memberships: m.student_id = self.id

  def to_db(self):
    return {'name': self.name, 'lastname': self.lastname, 'dni': self._dni, 'cellphone': self.cellphone, 'alt_phone': self.alt_phone, 'birthday': self.birthday, 'address': self.address, 'male': self._male, 'email': self.email, 'is_teacher': self._is_teacher, 'comments': self.comments, 'facebook_uid': self.facebook_uid, 'age': self.age, 'family': self.family, 'group': self.group, 'inactive': self.inactive}

  def _is_valid(self):
    self.validate_presence_of('name')
    self.validate_presence_of('lastname')
    self.validate_format_of('name', frmt = 'name')
    self.validate_format_of('lastname', frmt = 'name')
    self.validate_format_of('dni', expr = '^\d\d\.\d\d\d\.\d\d\d$')
    self.validate_uniqueness_of('dni', self._dni)

  def get_payments(self, include_installments = True, done = None):
    return payment.Payment.for_user(self.id, include_installments, done)

  def get_liabilities(self):
    return liability.Liability.to_pay_for(self.id)
  
  def new_liability(self):
    return liability.Liability({'user_id': self.id})

  def family_members(self):
    if self.family is not None:
      q = self.__class__.where('family',self.family).where('id',self.id,comparission='!=')
    else:
      q = self.__class__.where('1 = 0')
    return q

  def add_family_member(self, user):
    if self.id != user.id:
      if user.family is None or self.family is None:
        family_id = self.family or user.family or self.id
        self.family = family_id
        user.family = family_id
        Conn.execute('UPDATE users SET family = :family WHERE id IN (:id1, :id2)', {'family': family_id, 'id1': self.id, 'id2': user.id})
  
  def remove_family_member(self, user):
    if self.id != user.id:
      if user.family == self.family and self.family is not None:
        user.family = None
        Conn.execute('UPDATE users SET family = :family WHERE id = :id', {'family': None, 'id': user.id})
        if self.family_members().count() == 0:
          self.family = None
          Conn.execute('UPDATE users SET family = :family WHERE id = :id', {'family': None, 'id': self.id})

  def inactivate(self):
    self.inactive = True
    for m in self.memberships: m.inactivate()
    self.save()

  def reactivate(self):
    self.inactive = False
    for m in self.memberships: m.reactivate()
    self.save()

  @classmethod
  def calculate_age(cls,born):
    if not isinstance(born,datetime.date):
      born = cls.parse_date(born)
      if born == '': born = False

    if born:
      today = datetime.date.today()
      return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    else:
      return False

  def is_inscription_payed(self):
    return len(payment.Payment.for_user(self.id, include_installments = False, done = None).where('description', 'Insc%', comparission = 'like')) > 0

  @classmethod
  def birthday_today(cls):
    today = datetime.datetime.now().date()
    return cls.where('birthday', '%%%s' % (today.strftime('-%m-%d'),), comparission='LIKE')
