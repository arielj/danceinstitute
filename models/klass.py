from teacher import Teacher
from schedule import Schedule

class Klass():
  def __init__(self):
    self.id = False
    self.name = ''
    self.from_time = '16:00'
    self.to_time = '17:00'
    self.room = 'Agua'
    self.teachers = []
    self.schedules = []
    self.users = []

  @classmethod
  def find(cls,id):
    klass = cls()
    klass.id = id
    klass.name = 'Flamenco Adultos'
    klass.teachers = [Teacher.find(1)]
    klass.schedules = [Schedule({'from_time': '20:30', 'to_time': '21:30', 'room': 'Fuego', 'day': 0}),
                       Schedule({'from_time': '20:30', 'to_time': '21:30', 'room': 'Fuego', 'day': 3})]
    return klass

