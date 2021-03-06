#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from lib.query_builder import Query
import user
import membership
import payment

class Teacher(user.User):
  def __init__(self, data = {}):
    user.User.__init__(self, data)
    self.is_teacher = True

  @classmethod
  def for_klass(cls,kls):
    return cls.set_from('klasses_teachers').set_join('LEFT JOIN users ON klasses_teachers.teacher_id = users.id').where('klass_id',kls.id)

  @classmethod
  def get(cls, where = '', args = {}, exclude = None):
    q = cls.where('is_teacher', 1)

    if exclude: q.where('id', exclude, comparission = 'NOT IN', placeholder = 'ids')

    return q

  def can_delete(self):
    if not membership.Membership.for_student(self.id):
      return "El profesor está inscripto en una o más clases."
    if not payment.Payment.for_user(self.id):
      return "El profesor tiene pagos hechos o recibidos."
    if self.get_conn().execute('SELECT COUNT(*) FROM klasses_teachers WHERE klasses_teachers.teacher_id = :teacher_id', {'teacher_id': self.id}).fetchone()[0] != 0:
      return "El profesor está asignado a una o más clases."
    return True
 
  def before_delete(self):
    self.get_conn().execute('DELETE FROM klasses_teachers WHERE klasses_teachers.teacher_id = :teacher_id',{'teacher_id': self.id})
    return True
