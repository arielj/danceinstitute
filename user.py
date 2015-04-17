class User():
  def __init__(self):
    self.id = None
    self.name = ''
    self.lastname = ''
    self.dni = ''
    self.cellphone = ''
    self.birthday = ''
    self.address = ''
    self.male = True
    self.is_teacher = False

  @classmethod
  def find(cls, id):
    user = cls()
    user.id = id
    user.name = 'Lau'
    user.lastname = 'Gut'
    user.dni = '35.592.392'
    user.cellphone = '0299-15-453-4315'
    user.birthday = '12/02/1991'
    user.address = '9 de Julio 1140'
    user.male = False
    user.is_teacher = False
    
    return user

