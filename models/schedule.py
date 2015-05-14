#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import datetime
from translations import _t
from model import Model
import room
import klass

class Schedule(Model):
  table = 'schedules'
  fields_for_save = ['klass_id','from_time','to_time','day','room_id']

  def __init__(self, attrs = {}):
    self._klass = None
    self.klass_id = None
    self._from_time = 0000
    self._to_time = 0000
    self.day = 0
    self.room_id = ''
    self._room = None

    Model.__init__(self, attrs)

  @property
  def klass(self):
    if self.klass_id is not None and self._klass is None:
      self._klass = klass.Klass.find(self.klass_id)
    return self._klass

  @klass.setter
  def klass(self,kls):
    self._klass = kls
    if kls is None:
      self.klass_id = None
    else:
      self.klass_id = kls.id

  @property
  def from_time(self):
    return self._from_time

  @from_time.setter
  def from_time(self,value):
    if isinstance(value,str):
      self._from_time = int(value.replace(':',''))
    else:
      self._from_time = value

  def str_from_time(self):
    st = str(self.from_time).zfill(4)
    return st[0:2]+':'+st[2:4]
  
  @property
  def to_time(self):
    return self._to_time

  @to_time.setter
  def to_time(self,value):
    if isinstance(value,str):
      self._to_time = int(value.replace(':',''))
    else:
      self._to_time = value

  @property
  def room(self):
    if self.room_id is not None and self._room is None:
      self._room = room.Room.find(self.room_id)
    return self._room

  @room.setter
  def room(self,r):
    self._room = r
    if r is None:
      self.room_id = None
    else:
      self.room_id = r.id

  @property
  def room_name(self):
    if self._room is not None:
      return self._room.name
    else:
      return ''

  @room_name.setter
  def room_name(self, name):
    self.room = room.Room.find_by('name',name)

  def str_to_time(self):
    st = str(self.to_time).zfill(4)
    return st[0:2]+':'+st[2:4]
  
  def day_name(self):
    return _t('days')[self.day]

  def day_abbr(self):
    return _t('abbr_days','en')[self.day]

  # returns schedule intervals separated by 30 minutes:
  # if schedule goes from 20:00 to 21:30, it returns
  # ['20:00','20:30','21:00']
  def get_intervals(self):
    ints = []
    t_obj = self._get_from_datetime()
    while t_obj < self._get_to_datetime():
      ints.append(t_obj.strftime("%H:%M"))
      t_obj = t_obj + datetime.timedelta(minutes=30)
    return ints

  # internal use for "get_intervals"
  def _get_from_datetime(self):
    return self._get_datetime(self.str_from_time())
  
  def _get_to_datetime(self):
    return self._get_datetime(self.str_to_time())

  def _get_datetime(self,t):
    return datetime.datetime(2000,1,1,int(t[0:2]),int(t[3:5]),0)

  def _is_valid(self):
    if self.from_time >= self.to_time:
      self.add_error('from_time', 'Desde debe ser anterior a Hasta.')
    self.validate_presence_of('room')

  def to_db(self):
    return {'klass_id': self.klass.id, 'from_time': self.from_time, 'to_time': self.to_time, 'day': self.day, 'room_id': self.room_id}

  @classmethod
  def possible_rooms(cls):
    return map(lambda r: r.name, room.Room.all())

  @classmethod
  def for_klass(cls,kls):
    return cls.get_where('klass_id',kls.id)
