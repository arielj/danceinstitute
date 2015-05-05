#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from user import User
from membership import Membership

class Student(User):
  def __init__(self, data = {}):
    self.memberships = None
    self.membership_ids = []
    User.__init__(self, data)

  @classmethod
  def search(cls, value):
    if value == 'Lau':
      return [cls.find(1)]
    elif value == 'Tincho':
      return [cls.find(2)]
    elif value == 'Prof':
      return [cls.find(1),cls.find(2)]
    else:
      return cls.all()

  def get_memberships(self, requery = False):
    if requery or self.memberships is None:
      self.memberships = []
      for id in self.membership_ids:
        self.memberships.append(Membership.find(id))
    return self.memberships

  def add_membership(self, membership):
    if not membership.is_new_record():
      self.membership_ids.append(membership.id)
    self.memberships.append(membership)

  def before_save(self):
    for m in self.get_memberships():
      if m.save():
        if m.id not in self.membership_ids:
          self.membership_ids.append(m.id)
    return True

  def _is_valid(self):
    User._is_valid(self)
    
    valid_memberships = True
    for m in self.get_memberships():
      if not m.is_valid():
        valid_memberships = False
    if not valid_memberships:
      self.add_error('memberships', 'Una o más inscripciones son inválidas.')

  def to_db(self):
    h = User.to_db(self)
    h['membership_ids'] = self.membership_ids
    return h
