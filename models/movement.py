#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from model import Model
import datetime

class Movement(Model):
  table = 'movements'
  fields_for_save = ['amount', 'date', 'description', 'done']

  def __init__(self, attrs = {}):
    self._amount = 0
    self._date = datetime.datetime.now().date()
    self.description = ''
    self.done = False
    Model.__init__(self, attrs)

  @property
  def amount(self):
    return self._amount/100

  @amount.setter
  def amount(self,value):
    try:
      v = int(Decimal(value)*100)
    except:
      v = 0
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

  def to_db(self):
    return {'amount': self.amount, 'date': self.date, 'description': self.description, 'done': int(self.done)}

  def to_s(self):
    return str(self.date) + ": $" + str(self.amount)

  @classmethod
  def incoming(cls, date_f = None, date_t = None):
    if date_f or date_t:
      return cls.by_date(date_f, date_t, 'done = :done', {'done': 0})
    else:
      return cls.get_where('done',0)

  @classmethod
  def outgoing(cls, date_f = None, date_t = None):
    if date_f or date_t:
      return cls.by_date(date_f, date_t, 'done = :done', {'done': 1})
    else:
      return cls.get_where('done',1)

  @classmethod
  def by_date(cls, date_f, date_t = None, where = '', args = {}):
    if date_t is None:
      date_t = date_f
    if where != '':
      where = where + ' AND '
    args['date_f'] = str(date_f)
    args['date_t'] = str(date_t)
    return cls.get_many('SELECT * FROM movements WHERE ' + where + ' date >= :date_f AND date <= :date_t', args)
