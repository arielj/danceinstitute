import user

class Teacher(user.User):
  def __init__(self, data = {}):
    user.User.__init__(self, data)
    self.is_teacher = True

  @classmethod
  def for_klass(cls,kls):
    return cls.get_many('SELECT users.* FROM klasses_teachers LEFT JOIN users ON klasses_teachers.teacher_id = users.id WHERE klasses_teachers.klass_id = ?',(kls.id,))

  @classmethod
  def get(cls, where = '', args = {}, exclude = None):
    w = 'is_teacher = 1'
    if exclude:
      w = w + ' AND id NOT IN (:ids)'
      args['ids'] = ','.join(map(lambda i: str(i),exclude))

    where = where + ' AND ' + w if where else w

    return cls.all(where=where,args=args)
 
  def before_delete(self):
    return self.get_conn().execute('DELETE FROM klasses_teachers WHERE klasses_teachers.teacher_id = :teacher_id',{'teacher_id': self.id})
