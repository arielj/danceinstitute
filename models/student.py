#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from user import User
import membership

class Student(User):
  def __init__(self, data = {}):
    self._memberships = None
    User.__init__(self, data)

  @classmethod
  def search(cls, value):
    results = []
    rs = cls.get_conn().execute("SELECT * FROM users WHERE is_teacher = 0 AND (name LIKE :value OR lastname LIKE :value OR dni LIKE :value)", {'value': "%"+value+"%"}).fetchall()
    for r in rs:
      results.append(cls(r))
    return results

  @property
  def memberships(self):
    if self._memberships is None:
      self._memberships = membership.Membership.for_student(self.id)
    return self._memberships

  def add_membership(self, membership):
    self.memberships.append(membership)
  
  def remove_membership(self, membership_id):
    for m in self.memberships:
      if m.id and m.id == membership_id:
        self.memberships.remove(m)

  def after_save(self):
    for m in self.memberships:
      m.save(validate = False)
    return True

  def _is_valid(self):
    User._is_valid(self)
    self.validate_has_many('memberships')

  def update_id_on_associations(self):
    for m in self.memberships:
      m.student_id = self.id
