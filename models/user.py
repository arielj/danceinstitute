#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
from model import Model

class User(Model):
  table = 'users'

  def __init__(self, data = {}):
    self._name = ''
    self._lastname = ''
    self.dni = ''
    self.cellphone = ''
    self.alt_phone = ''
    self.birthday = ''
    self.address = ''
    self.male = True
    self.email = ''
    self.is_teacher = False
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

  def to_db(self):
    return {'name': self.name, 'lastname': self.lastname, 'dni': self.dni, 'cellphone': self.cellphone,
            'birthday': self.birthday, 'address': self.address, 'male': self.male,
            'email': self.email, 'is_teacher': self.is_teacher}

  def _is_valid(self):
    self.validate_format_of('name', frmt = 'name')
    self.validate_format_of('lastname', frmt = 'name')
    self.validate_format_of('dni', expr = '^\d\d\.?\d\d\d\.?\d\d\d$')

