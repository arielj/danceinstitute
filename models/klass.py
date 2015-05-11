#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from translations import _t
from model import Model
import teacher
import schedule

class Klass(Model):
  table = 'klasses'
  fields_for_save = ['name', 'normal_fee', 'half_fee', 'once_fee',
                     'inscription_fee', 'min_age', 'max_age', 'quota', 'info']
  
  def __init__(self, data = {}):
    self.name = ''
    self.normal_fee = 0
    self.half_fee = 0
    self.once_fee = 0
    self.inscription_fee = 0
    self.min_age = 0
    self.max_age = 0
    self.quota = 0
    self.info = ''
    self._teachers = None
    self._schedules = None
    self._users = None
    
    Model.__init__(self, data)

  def to_db(self):
    return {'name': self.name, 'normal_fee': self.normal_fee, 'half_fee': self.half_fee, 'once_fee': self.once_fee, 'inscription_fee': self.inscription_fee, 'min_age': self.min_age, 'max_age': self.max_age, 'quota': self.quota, 'info': self.info}

  def _is_valid(self):
    self.validate_presence_of('name')
    self.validate_numericallity_of('normal_fee', great_than = 0, only_integer = False)
    self.validate_numericallity_of('half_fee', great_than_or_equal = 0, only_integer = False)
    self.validate_numericallity_of('once_fee', great_than_or_equal = 0, only_integer = False)
    self.validate_numericallity_of('inscription_fee', great_than_or_equal = 0, only_integer = False)
    self.validate_numericallity_of('min_age', great_than_or_equal = 0)
    self.validate_numericallity_of('max_age', great_than_or_equal = 0)
    self.validate_numericallity_of('quota', great_than_or_equal = 0)
    self.validate_has_many('schedules')

  def after_save(self):
    for sch in self.schedules:
      sch.save(validate = False)

  def update_id_on_associations(self):
    for sch in self.schedules:
      sch.klass_id = self.id

  @classmethod
  def by_room_and_time(cls, from_time, to_time):
    klasses = {}
    for r in schedule.Schedule.possible_rooms():
      klasses[r] = {}
      for h in range(from_time, to_time, 1):
        for h2 in [str(h) + ':00', str(h) + ':30']:
          klasses[r][h2] = {}
          for d in _t('abbr_days','en'):
            klasses[r][h2][d] = None
   
    for kls in cls.all():
      for sch in kls.schedules:
        for interval in sch.get_intervals():
          klasses[sch.room][interval][sch.day_abbr()] = kls
    
    return klasses

  def find_schedule(self, sch_id):
    for sch in self.schedules:
      if sch.id == sch_id:
        return sch
    return None

  def build_schedule(self, data):
    sch = schedule.Schedule(data)
    self.schedules.append(sch)
    return sch

  @property
  def teachers(self, requery = False):
    if requery or self._teachers is None:
      self._teachers = teacher.Teacher.for_klass(self)
    return self._teachers

  @property
  def schedules(self, requery = False):
    if requery or self._schedules is None:
      self._schedules = schedule.Schedule.for_klass(self)
    return self._schedules

  def add_schedule(self, schedule):
    self.schedules.append(schedule)
    schedule.klass_id = self.id
    if not schedule.is_new_record():
      self.schedule_ids.append(schedule.id)

  def add_teacher(self, teacher):
    self.teachers.append(teacher)
    if not teacher.is_new_record():
      if teacher.id not in self.teacher_ids:
        self.teacher_ids.append(teacher.id)

  def remove_schedule(self, schedule):
    if schedule in self.schedules:
      if schedule.id in self.schedule_ids:
        self.schedule_ids.remove(schedule.id)
      self.schedules.remove(schedule)

  def remove_teacher(self, teacher):
    if teacher in self.teachers:
      if teacher.id in self.teacher_ids:
        self.teacher_ids.remove(teacher.id)
      self.teachers.remove(teacher)

  def get_fee_for(self, fee_type):
    return getattr(self,fee_type+'_fee')

  @classmethod
  def for_package(cls,package_id):
    results = []
    rs = cls.get_conn().execute('''SELECT klasses.* FROM klasses_packages LEFT JOIN klasses ON klasses_packages.klass_id = klasses.id WHERE klasses_packages.package_id = ?''', (package_id,)).fetchall()
    for r in rs:
      results.append(cls(r))
    return results
