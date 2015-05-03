#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from model import Model
from teacher import Teacher
from schedule import Schedule

klasses = {1: {'name': 'Flamenco Adultos', 'normal_fee': 350, 'half_fee': 200, 'once_fee': 50, 'inscription_fee': 0, 'min_age': 15, 'max_age': 0, 'quota': 15, 'info': 'Traer zapatos con taco ancho y una pollera larga.', 'teacher_ids': [1], 'schedule_ids': [1,2]},
           2: {'name': 'HipHop Adolescentes', 'normal_fee': 300, 'half_fee': 200, 'once_fee': 30, 'inscription_fee': 0, 'min_age': 13, 'max_age': 22, 'quota': 30, 'info': 'Zapatillas y ropa cómoda', 'teacher_ids': [2], 'schedule_ids': [3,4]}}

class Klass(Model):
  def __init__(self, data = {}):
    Model.__init__(self)
    self.name = ''
    self.normal_fee = 0
    self.half_fee = 0
    self.once_fee = 0
    self.inscription_fee = 0
    self.min_age = 0
    self.max_age = 0
    self.quota = 0
    self.info = ''
    self.teacher_ids = []
    self.schedule_ids = []
    self.user_ids = []
    self.teachers = []
    self.schedules = []
    self.users = []
    
    self.set_attrs(data)

  def _is_valid(self):
    self.validate_presence_of('name')

    if not self.normal_fee:
      self.add_error('normal_fee', 'No puede ser 0.')
    
    for t in self.get_teachers():
      if not t.is_valid():
        self.add_error('teachers', 'No es válido.')
    
    for s in self.get_schedules():
      if not s.is_valid():
        self.add_error('schedules', 'No es válido.')

  @classmethod
  def find(cls, id):
    klass = cls(klasses[id])
    klass.id = id
    return klass

  @classmethod
  def by_room_and_time(cls, from_time, to_time):
    klasses = {}
    for r in Schedule.possible_rooms():
      klasses[r] = {}
      for h in range(from_time, to_time, 1):
        for h2 in [str(h) + ':00', str(h) + ':30']:
          klasses[r][h2] = {'mon': None, 'tue': None, 'wed': None, 'thu': None,
                            'fri': None, 'sat': None, 'sun': None}
   
    for kls in cls.all():
      for sch in kls.get_schedules():
        for interval in sch.get_intervals():
          klasses[sch.room][interval][sch.get_day_abbr()] = kls
    
    return klasses

  @classmethod
  def all(cls):
    return [cls.find(1), cls.find(2)]

  def find_schedule(self, sch_id):
    for sch in self.schedules:
      if sch.id == sch_id:
        return sch
    return None

  def build_schedule(self, data):
    sch = Schedule(data)
    self.schedules.append(sch)
    return sch

  def get_teachers(self, requery = False):
    if requery or not self.teachers:
      self.teachers = []
      for id in self.teacher_ids:
        self.teachers.append(Teacher.find(id))
    return self.teachers

  def get_schedules(self, requery = False):
    if requery or not self.schedules:
      self.teachers = []
      for id in self.schedule_ids:
        self.schedules.append(Schedule.find(id))
    return self.schedules

  def add_schedule(self, schedule):
    if not schedule.is_new_record:
      self.schedule_ids.append(schedule.id)
    self.schedules.append(schedule)

  def add_teacher(self, teacher):
    if not teacher.is_new_record:
      self.teacher_ids.append(teacher.id)
    self.teachers.append(teacher)

  def remove_schedule(self, schedule):
    if schedule in self.get_schedules():
      if schedule.id in self.schedule_ids:
        self.schedule_ids.remove(schedule.id)
      self.schedules.remove(schedule)

  def remove_teacher(self, teacher):
    if teacher in self.get_teachers():
      if teacher.id in self.teacher_ids:
        self.teacher_ids.remove(teacher.id)
      self.teachers.remove(teacher)

  def get_fee_for(self, fee_type):
    return vars(self)[fee_type+'_fee']
