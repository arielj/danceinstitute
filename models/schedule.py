#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from room import Room

schedules = {1: {'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 0},
             2: {'from_time': '20:00', 'to_time': '21:30', 'room': 'Fuego', 'day': 3}}

class Schedule(Model):
  DAYS = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']

  def __init__(self, attrs = None):
    self.id = False
    self.from_time = ''
    self.to_time = ''
    self.day = 0
    self.room = ''
    
    if attrs:
      self.set_attrs(attrs)
  
  def set_attrs(self, attrs):
    for key in attrs.iterkeys():
      vars(self)[key] = attrs[key]

  def get_day_name(self):
    return Schedule.DAYS[self.day]

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

