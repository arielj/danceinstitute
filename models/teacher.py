from user import User

class Teacher(User):
  def __init__(self):
    User.__init__(self)
    self.is_teacher = True
  
  @classmethod
  def all(cls):
    return [cls.find(1),cls.find(2)]

