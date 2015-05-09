#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from user import User
import membership

class Student(User):
  def __init__(self, data = {}):
    self._memberships = None
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

  @property
  def memberships(self, requery = False):
    if requery or self._memberships is None:
      self._memberships = []
      for id in self.membership_ids:
        self._memberships.append(membership.Membership.find(id))
    return self._memberships

  def add_membership(self, membership):
    self.memberships.append(membership)
    if not membership.is_new_record():
      self.membership_ids.append(membership.id)
  
  def remove_membership(self, membership_id):
    if membership_id in self.membership_ids:
      self.membership_ids.remove(membership_id)
    for m in self.memberships:
      if m.id and m.id == membership_id:
        self.memberships.remove(m)

  def before_save(self):
    self.membership_ids = []
    for m in self.memberships:
      m.save()
      self.membership_ids.append(m.id)
    return True

  def _is_valid(self):
    User._is_valid(self)
    self.validate_has_many('memberships')

  def to_db(self):
    h = User.to_db(self)
    h['membership_ids'] = self.membership_ids
    return h
