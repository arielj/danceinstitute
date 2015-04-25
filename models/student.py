from user import User

class Student(User):
  def __init__(self, data = {}):
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
      return []

