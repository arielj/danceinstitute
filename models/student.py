#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import user

class Student(user.User):
  def __init__(self, data = {}):
    user.User.__init__(self, data)

  @classmethod
  def search(cls, value):
    return cls.get_many("SELECT * FROM users WHERE name LIKE :value OR lastname LIKE :value OR dni LIKE :value", {'value': "%"+value+"%"})

