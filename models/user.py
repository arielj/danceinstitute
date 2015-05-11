#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
from model import Model

class User(Model):
  table = 'users'
  fields_for_save = ['name','lastname','dni','cellphone','alt_phone','birthday',
                     'address','male','email','is_teacher','comments']

  def __init__(self, data = {}):
    self._name = ''
    self._lastname = ''
    self.dni = ''
    self.cellphone = ''
    self.alt_phone = ''
    self.birthday = ''
    self.address = ''
    self._male = True
    self.email = ''
    self._is_teacher = False
    self.comments = ''
    
    Model.__init__(self,data)

  @property
  def name(self):
    return self._name
  
  @name.setter
  def name(self,value):
    self._name = value.title()

  @property
  def lastname(self):
    return self._lastname

  @lastname.setter
  def lastname(self,value):
    self._lastname = value.title()

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

  def to_db(self):
    return {'name': self.name, 'lastname': self.lastname, 'dni': self.dni, 'cellphone': self.cellphone, 'alt_phone': self.alt_phone, 'birthday': self.birthday, 'address': self.address, 'male': self._male, 'email': self.email, 'is_teacher': self._is_teacher, 'comments': self.comments}

  def _is_valid(self):
    self.validate_format_of('name', frmt = 'name')
    self.validate_format_of('lastname', frmt = 'name')
    self.validate_format_of('dni', expr = '^\d\d\.?\d\d\d\.?\d\d\d$')

