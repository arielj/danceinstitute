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
    self.email = ''
    self.is_teacher = False

  @classmethod
  def find(cls, id):
    user = cls()
    user.id = id
    if id == 1:
      user.name = 'Lau'
      user.lastname = 'Gut'
      user.dni = '35.592.392'
      user.cellphone = '0299-15-453-4315'
      user.birthday = '12/02/1991'
      user.address = '9 de Julio 1140'
      user.male = False
      user.email = 'lali_gut@yahoo.com.ar'
      user.is_teacher = True
    else:
      user.name = 'Tincho'
      user.lastname = 'Arce'
      user.dni = 'nose'
      user.cellphone = 'niidea'
      user.birthday = '12/02/1980'
      user.address = 'barrio mercantil'
      user.male = True
      user.email = 'tincho@sharife.com'
      user.is_teacher = True
    
    return user

