from teacher import Teacher
from schedule import Schedule

class Klass():
  def __init__(self):
    self.id = False
    self.name = ''
    self.fee = '0'
    self.half_fee = '0'
    self.once_fee = '0'
    self.min_age = '0'
    self.max_age = '0'
    self.quota = '0'
    self.info = ''
    self.teachers = []
    self.schedules = []
    self.users = []

  @classmethod
  def find(cls,id):
    klass = cls()
    klass.id = id
    klass.name = 'Flamenco Adultos'
    klass.fee = '350'
    klass.half_fee = '200'
    klass.once_fee = '50'
    klass.min_age = '15'
    klass.max_age = '0'
    klass.quota = '15'
    klass.info = 'Traer zapatos con taco ancho y una pollera larga.'
    klass.teachers = [Teacher.find(1)]
    klass.schedules = [Schedule({'from_time': '20:30', 'to_time': '21:30', 'room': 'Fuego', 'day': 0}),
                       Schedule({'from_time': '20:30', 'to_time': '21:30', 'room': 'Fuego', 'day': 3})]
    return klass

