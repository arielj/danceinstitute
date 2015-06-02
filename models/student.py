#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import user
import re

class Student(user.User):
  def __init__(self, data = {}):
    user.User.__init__(self, data)

  @classmethod
  def search(cls, value):
    return cls.get_many("SELECT * FROM users WHERE is_teacher = 0 AND (name LIKE :value OR lastname LIKE :value OR dni = :dni_value)", {'value': "%"+value+"%", 'dni_value': re.sub(r'\.','',value)})

