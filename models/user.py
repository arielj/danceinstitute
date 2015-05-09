#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
from model import Model

class User(Model):
  #borrar después
  db = {1: {'name': 'Lau', 'lastname': 'Gut', 'dni': '35.592.392', 'cellphone': '0299-15-453-4315',
            'birthday': '12/02/1991', 'address': '9 de Julio 1140', 'male': False, 'email': 'lali_gut@yahoo.com.ar',
            'is_teacher': True, 'membership_ids': [1]},
        2: {'name': 'Tincho', 'lastname': 'Arce', 'dni': 'nose', 'cellphone': 'niidea',
            'birthday': '12/02/1980', 'address': 'barrio mercantil', 'male': True, 'email': 'tincho@sharife.com',
            'is_teacher': True, 'membership_ids': []}
        }

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

