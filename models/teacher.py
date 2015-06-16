#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import user
import membership
import payment

class Teacher(user.User):
  def __init__(self, data = {}):
    user.User.__init__(self, data)
    self.is_teacher = True

  @classmethod
  def for_klass(cls,kls):
    return cls.get_many('SELECT users.* FROM klasses_teachers LEFT JOIN users ON klasses_teachers.teacher_id = users.id WHERE klasses_teachers.klass_id = ?',(kls.id,))

  @classmethod
  def get(cls, where = '', args = {}, exclude = None):
    q = Query(cls).where('is_teacher', 1)

    if exclude: q.where('id', ','.join(map(lambda i: str(i),exclude)), comparission = 'NOT IN', placeholder = '(:ids)')

    return q

  def can_delete(self):
    if membership.Membership.for_student(self.id):
      return "El profesor está inscripto en una o más clases."
    if payment.Payment.for_user(self.id):
      return "El profesor tiene pagos hechos o recibidos."
    return True
 
  def before_delete(self):
    self.get_conn().execute('DELETE FROM klasses_teachers WHERE klasses_teachers.teacher_id = :teacher_id',{'teacher_id': self.id})
    return True
