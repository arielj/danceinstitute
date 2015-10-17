#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from lib.money import Money
from model import Model
from lib.query_builder import Query
import datetime

class Movement(Model):
  table = 'movements'
  fields_for_save = ['amount', 'date', 'description', 'done']

  def __init__(self, attrs = {}):
    self._amount = Money(0)
    self._date = datetime.datetime.now().date()
    self.description = ''
    self.done = False
    Model.__init__(self, attrs)

  @classmethod
  def from_db(cls, r):
    m = cls(r)
    m._amount._cents = r['amount']
    return m

  @property
  def amount(self):
    return self._amount

  @amount.setter
  def amount(self,value):
    try:
      v = Money(value)
    except:
      v = Money(0)
    self._amount = v

  @property
  def date(self):
    return self._date

  @date.setter
  def date(self,value):
    if isinstance(value,datetime.date):
      self._date = value
    else:
      try:
        self._date = datetime.datetime.strptime(value,'%Y/%m/%d').date()
      except:
        try:
          self._date = datetime.datetime.strptime(value,'%Y/%d/%m').date()
        except:
          try:
            self._date = datetime.datetime.strptime(value,'%Y-%m-%d').date()
          except:
            try:
              self._date = datetime.datetime.strptime(value,'%Y-%d-%m').date()
            except:
              try:
                self._date = datetime.datetime.strptime(value,'%d-%m-%Y').date()
              except:
                try:
                  self._date = datetime.datetime.strptime(value,'%d/%m/%Y').date()
                except:
                  self._date = ''

  @property
  def done(self):
    return bool(self._done)

  @done.setter
  def done(self,value):
    self._done = bool(value)

  @property
  def direction(self):
    return 'out' if self.done else 'in'

  @direction.setter
  def direction(self, d):
    self._done = d == 'out'

  def is_incoming(self):
    return self.direction == 'in'

  def is_outgoing(self):
    return self.direction == 'out'

  def _is_valid(self):
    self.validate_numericallity_of('amount', great_than = 0, only_integer = False)
    self.validate_presence_of('date')

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'description': self.description, 'done': int(self.done)}

  def to_s(self):
    return str(self.date) + ": $" + str(self.amount)

  @classmethod
  def incoming(cls, date_f = None, date_t = None):
    q = cls.by_date(date_f, date_t) if date_f or date_t else Query(cls)
    return q.where('done', 0)

  @classmethod
  def outgoing(cls, date_f = None, date_t = None):
    q = cls.by_date(date_f, date_t) if date_f or date_t else Query(cls)
    return q.where('done', 1)

  @classmethod
  def by_date(cls, date_f, date_t = None):
    if isinstance(date_f, datetime.datetime): date_f = date_f.strftime('%Y-%m-%d')
    if date_t is None: date_t = date_f

    return cls.where('date', date_f, comparission = '>=', placeholder = 'date_f').where('date', date_t, comparission = '<=', placeholder = 'date_t')

