from user import User

class Teacher(User):
  def __init__(self, data = {}):
    User.__init__(self, data)
    self.is_teacher = True

