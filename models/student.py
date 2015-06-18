#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import user
import re

class Student(user.User):
  def __init__(self, data = {}):
    user.User.__init__(self, data)

  @classmethod
  def search(cls, value):
    return cls.where('is_teacher',0).where("name LIKE :name_like OR lastname LIKE :name_like OR dni = :dni_value",{'name_like': "%"+value+"%", 'dni_value': re.sub(r'\.','',value)})
