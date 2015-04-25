users = {1: {'name': 'Lau', 'lastname': 'Gut', 'dni': '35.592.392', 'cellphone': '0299-15-453-4315',
          'birthday': '12/02/1991', 'address': '9 de Julio 1140', 'male': False, 'email': 'lali_gut@yahoo.com.ar',
          'is_teacher': True},
         2: {'name': 'Tincho', 'lastname': 'Arce', 'dni': 'nose', 'cellphone': 'niidea',
         'birthday': '12/02/1980', 'address': 'barrio mercantil', 'male': True, 'email': 'tincho@sharife.com',
         'is_teacher': True}
        }

class User(object):
  def __init__(self, data = {}):
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
    
    self.set_attrs(data)

  def set_attrs(self, data = {}):
    for attr in data.keys():
      self.__setattr__(attr,data[attr])

  @classmethod
  def find(cls, id):
    user = cls(users[id])
    user.id = id
    return user

  def save(self):
    if not self.id:
      self.id = 3
    users[self.id] = {'name': self.name, 'lastname': self.lastname, 'dni': self.dni, 'cellphone': self.cellphone,
                      'birthday': self.birthday, 'address': self.address, 'male': self.male,
                      'email': self.email, 'is_teacher': self.is_teacher}
    print users

