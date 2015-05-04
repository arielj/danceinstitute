#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from room import Room
import datetime
from translations import _t, ts

schedules = {1: {'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 0},
             2: {'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 3},
             3: {'from_time': '19:00', 'to_time': '20:00', 'room': 'Aire', 'day': 1},
             4: {'from_time': '19:00', 'to_time': '20:30', 'room': 'Aire', 'day': 3},}

class Schedule(Model):
  def __init__(self, attrs = {}):
    Model.__init__(self)
    self.from_time = '00:00'
    self.to_time = '00:00'
    self.day = 0
    self.room = ''

    self.set_attrs(attrs)
  
  def set_attrs(self, attrs):
    for key in attrs.iterkeys():
      vars(self)[key] = attrs[key]

  def get_day_name(self):
    return _t('days')[self.day]

  def get_day_abbr(self):
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
    return self._get_datetime(self.from_time)
  
  def _get_to_datetime(self):
    return self._get_datetime(self.to_time)

  def _get_datetime(self,t):
    return datetime.datetime(2000,1,1,int(t[0:2]),int(t[3:5]),0)


  def _is_valid(self):
    if self.from_time >= self.to_time:
      self.add_error('from_time', 'Desde debe ser anterior a Hasta.')
    self.validate_presence_of('room')



  @classmethod
  def possible_rooms(cls):
    return Room.all()

  @classmethod
  def find(cls, id):
    schedule = cls(schedules[id])
    schedule.id = id
    return schedule

