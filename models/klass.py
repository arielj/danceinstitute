from teacher import Teacher
from user import User

class Klass():
  def __init__(self):
    self.id = 1
    self.name = ''
    self.from_time = '16:00'
    self.to_time = '17:00'
    self.room = 'Agua'
    self.teachers = []
    #self.users = ...

  @classmethod
  def find(cls,id):
    klass = cls()
    klass.id = id
    klass.name = 'Flamenco Adultos'
    klass.from_time = '20:00'
    klass.to_time = '21:30'
    klass.room = 'Fuego'
    klass.teachers = [Teacher.find(1)]
    return klass

