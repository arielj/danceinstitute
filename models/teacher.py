from user import User

class Teacher(User):
  def __init__(self, data = {}):
    User.__init__(self, data)
    self.is_teacher = True

  @classmethod
  def for_klass(cls,kls):
    return cls.get_many('SELECT users.* FROM klasses_teachers LEFT JOIN users ON klasses_teachers.teacher_id = users.id WHERE klasses_teachers.klass_id = ?',(kls.id,))

