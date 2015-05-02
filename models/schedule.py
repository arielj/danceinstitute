#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from room import Room
import datetime

schedules = {1: {'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 0},
             2: {'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 3},
             3: {'from_time': '19:00', 'to_time': '20:00', 'room': 'Aire', 'day': 1},
             4: {'from_time': '19:00', 'to_time': '20:30', 'room': 'Aire', 'day': 3},}

class Schedule(Model):
  DAYS = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
  days = ['mon','tue','wed','thu','fri','sat','sun']

  def __init__(self, attrs = {}):
    self.id = False
    self.from_time = '00:00'
    self.to_time = '00:00'
    self.day = 0
    self.room = ''

    self.set_attrs(attrs)
  
  def set_attrs(self, attrs):
    for key in attrs.iterkeys():
      vars(self)[key] = attrs[key]

  def get_day_name(self):
    return Schedule.DAYS[self.day]

  def get_day_abbr(self):
    return Schedule.days[self.day]

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


  @classmethod
  def possible_rooms(cls):
    return Room.all()

  @classmethod
  def get_days(cls):
    return cls.DAYS

  @classmethod
  def find(cls, id):
    schedule = cls(schedules[id])
    schedule.id = id
    return schedule

