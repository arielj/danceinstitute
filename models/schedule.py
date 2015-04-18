#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from room import Room

class Schedule():
  def __init__(self, attrs = None):
    self.id = 0
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
    days = ['Lunes','Martes','Miércoles','Jueves','Viernes']
    return days[self.day]

  @classmethod
  def possible_rooms(cls):
    return Room.all()

