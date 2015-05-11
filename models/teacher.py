from user import User

class Teacher(User):
  def __init__(self, data = {}):
    User.__init__(self, data)
    self.is_teacher = True

  @classmethod
  def for_klass(cls,kls):
    results = []
    rs = cls.get_conn().execute('''SELECT users.* FROM klasses_teachers LEFT JOIN users ON klasses_teachers.teacher_id = users.id WHERE klasses_teachers.klass_id = ?''', (kls.id,)).fetchall()
    for r in rs:
      results.append(cls(r))
    return results
