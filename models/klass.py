from teacher import Teacher
from schedule import Schedule

class Klass():
  def __init__(self):
    self.id = False
    self.name = ''
    self.fee = '0'
    self.half_fee = '0'
    self.once_fee = '0'
    self.inscription_fee = '0'
    self.min_age = '0'
    self.max_age = '0'
    self.quota = '0'
    self.info = ''
    self.teachers = []
    self.schedules = []
    self.users = []

  @classmethod
  def find(cls, id):
    klass = cls()
    klass.id = id
    klass.name = 'Flamenco Adultos'
    klass.fee = '350'
    klass.half_fee = '200'
    klass.once_fee = '50'
    klass.inscription_fee = '0'
    klass.min_age = '15'
    klass.max_age = '0'
    klass.quota = '15'
    klass.info = 'Traer zapatos con taco ancho y una pollera larga.'
    klass.teachers = [Teacher.find(1)]
    klass.schedules = [Schedule({'id': 1, 'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 0}),
                       Schedule({'id': 2, 'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 3})]
    return klass

  @classmethod
  def by_room_and_time(cls):
    klasses = {}
    for r in Schedule.possible_rooms():
      klasses[r] = {}
      for h in range(14,23,1):
        klasses[r][str(h) + ':00'] = {'mon': ['', ''], 'tue': ['', ''], 'wed': ['', ''], 'thu': ['', ''],
                                 'fri': ['', ''], 'sat': ['', ''], 'sun': ['', '']}
        klasses[r][str(h) + ':30'] = {'mon': ['', ''], 'tue': ['', ''], 'wed': ['', ''], 'thu': ['', ''],
                                 'fri': ['', ''], 'sat': ['', ''], 'sun': ['', '']}
    
    klasses['Fuego']['20:00']['mon'] = [1, 'Flamenco adultos']
    klasses['Fuego']['20:30']['mon'] = [1, 'Flamenco adultos']
    klasses['Fuego']['21:00']['mon'] = [1, 'Flamenco adultos']
    
    return klasses

  def find_schedule(self, sch_id):
    for sch in self.schedules:
      if sch.id == sch_id:
        return sch
    return None
