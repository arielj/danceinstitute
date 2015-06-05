import datetime
from models import *

class Factory():

  DATA = {'student': {'name': 'Arielo', 'lastname': 'Juodziukynas', 'is_teacher': 0},
          'teacher': {'name': 'Lau', 'lastname': 'Cronopia', 'is_teacher': 1},
          'payment': {'description': 'Cuota loca', 'amount': 200, 'date': str(datetime.datetime.today())},
          'klass': {'name': 'Pop', 'fee': 100},
          'package': {'fee': 300, 'name': 'Paquete loco'},
          'membership': {},
          'schedule': {'from_time': '1800', 'to_time': '1900'},
          'room': {'name': 'Sala1'}}
  
  @classmethod
  def build(cls, model, attrs = {}):
    data = cls.DATA[model]
    data.update(attrs)
    return vars(globals()[model])[model.capitalize()](data)

  @classmethod
  def create(cls, model, attrs = {}):
    obj = cls.build(model,attrs)
    obj.save()
    return obj

