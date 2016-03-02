#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from translations import _t
from model import Model
from lib.query_builder import Query
import teacher
import schedule
import package
import membership
import student

class Klass(Model):
  table = 'klasses'
  fields_for_save = ['name', 'normal_fee', 'half_fee', 'once_fee',
                     'inscription_fee', 'min_age', 'max_age', 'quota', 'info']
  default_order = 'name ASC'
  
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
    self._teachers_remove = []
    self._schedules_remove = []
    
    Model.__init__(self, data)

  def can_delete(self):
    if package.Package.with_klass(self).anything():
      return "Un paquete incluye a esta clase."
    if membership.Membership.for_klass_or_package(self).anything():
      return "Hay alumnos inscriptos a esta clase."
    return True

  def before_delete(self):
    for sch in self.schedules:
      sch.delete()
    self.__class__.get_conn().execute('DELETE FROM klasses_teachers WHERE klass_id = :klass_id', {'klass_id': self.id})
    return True

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
    c = self.__class__.get_conn()
    for t in self._teachers_remove:
      if t.is_not_new_record():
        c.execute('DELETE FROM klasses_teachers WHERE klass_id = :klass_id AND teacher_id = :teacher_id', {'klass_id': self.id, 'teacher_id': t.id})
    self._teachers_remove = []

    for t in self.teachers:
      args = {'klass_id': self.id, 'teacher_id': t.id}
      if Query(self.__class__).set_from('klasses_teachers').where(args).empty():
        self.__class__.get_conn().execute('INSERT INTO klasses_teachers (klass_id,teacher_id) VALUES (:klass_id,:teacher_id)', args)
    
    for s in self._schedules_remove: s.delete()
    self._schedules_remove = []
    for sch in self.schedules: sch.save(validate = False)

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
          try:
            klasses[sch.room.name][interval][sch.day_abbr()] = kls
          except KeyError as e:
            print e, kls.name
    
    return klasses

  @classmethod
  def for_day(cls, from_time, to_time, day):
    klasses = {}
    for h in range(from_time, to_time, 1):
      for h2 in [str(h) + ':00', str(h) + ':30']:
        klasses[h2] = {}
        for r in schedule.Schedule.possible_rooms():
          klasses[h2][r] = None
   
    for kls in cls.all():
      for sch in kls.schedules:
        if sch.day_abbr() == _t('abbr_days','en')[day]:
          for interval in sch.get_intervals():
            if interval in klasses:
              klasses[interval][sch.room.name] = kls
    
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
  def teachers(self):
    if self._teachers is None:
      self._teachers = [] if self.is_new_record() else teacher.Teacher.for_klass(self).do_get()
    return self._teachers

  @property
  def schedules(self):
    if self._schedules is None:
      self._schedules = [] if self.is_new_record() else schedule.Schedule.for_klass(self).do_get()
    return self._schedules

  def add_schedule(self, schedule):
    if schedule.is_new_record or schedule.id not in map(lambda s: s.id, self.schedules):
      self.schedules.append(schedule)
      schedule.klass_id = self.id

  def add_teacher(self, teacher):
    if teacher.id not in map(lambda t: t.id, self.teachers):
      self.teachers.append(teacher)

  def remove_schedule(self, schedule):
    for s in self.schedules:
      if s.id == schedule.id:
        self.schedules.remove(s)
        self._schedules_remove.append(s)

  def remove_teacher(self, teacher):
    for t in self.teachers:
      if t.id == teacher.id:
        self.teachers.remove(t)
        self._teachers_remove.append(t)

  def get_fee_for(self, fee_type):
    return getattr(self,fee_type+'_fee')

  def get_full_name(self):
    sch = self.schedules[0]
    sch_label = sch.day_name() + ' ' + sch.str_from_time() + '-' + sch.str_to_time()
    return self.name + ' (' + sch_label + ')' 

  def teacher_ids(self):
    return map(lambda t: t.id,self.teachers)
  
  def get_duration(self):
    d = sum(map(lambda s: s.duration(), self.schedules))
    return int(d) if d == int(d) else d

  @classmethod
  def for_package(cls,package_id):
    return cls.set_from('klasses_packages').set_join('LEFT JOIN klasses ON klasses_packages.klass_id = klasses.id').where('package_id',package_id)

  def get_students(self):
    ms = membership.Membership.for_klass_or_package(self).do_get()
    
    for p in package.Package.with_klass(self):
      ms = ms + membership.Membership.for_klass_or_package(p).do_get()
    
    uids = map(lambda m: str(m.student_id), ms)

    return student.Student.where('id IN ('+','.join(uids)+')')
