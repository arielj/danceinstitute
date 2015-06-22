import datetime
from models import *

class Factory():

  DATA = {'student': {'name': 'Arielo', 'lastname': 'Juodziukynas', 'is_teacher': 0, 'dni': None},
          'teacher': {'name': 'Lau', 'lastname': 'Cronopia', 'is_teacher': 1},
          'payment': {'description': 'Cuota loca', 'amount': 200},
          'movement': {'description': 'pago de todo', 'amount': 200, 'direction': 'in'},
          'klass': {'name': 'Pop', 'normal_fee': 100},
          'package': {'fee': 300, 'name': 'Paquete loco'},
          'membership': {},
          'schedule': {'from_time': '1800', 'to_time': '1900'},
          'room': {'name': 'Sala1'},
          'installment': {'amount': 250, 'status': 'waiting'}}
  CREATED = {}
  
  @classmethod
  def build(cls, model, attrs = {}):
    data = cls.data_for(model, attrs)
    return vars(globals()[model])[model.capitalize()](data)

  @classmethod
  def create(cls, model, attrs = {}):
    obj = cls.build(model,attrs)
    obj.save()
    return obj

  @classmethod
  def data_for(cls, model, attrs = {}):
    if model in cls.CREATED:
      cls.CREATED[model] += 1
    else:
      cls.CREATED[model] = 1

    data = cls.DATA[model].copy()
    if model+'_seq' in vars(cls):
      method = getattr(cls, model+'_seq')
      for field in data:
        seq = method(field)
        if seq is not None: data[field] = seq
    data.update(attrs)
    return data

  @classmethod
  def student_seq(cls,field):
    if field == 'dni':
      return str(cls.CREATED['student']).zfill(8)
    else:
      return None
