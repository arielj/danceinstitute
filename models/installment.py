#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import re
from datetime import datetime
from decimal import Decimal
from translations import _t, _a
from model import Model
from lib.query_builder import Query
import payment
import membership
import package
import settings

class Installment(Model):
  table = 'installments'
  fields_for_save = ['year','month','membership_id','amount', 'status']
  default_order = 'year ASC, month ASC'

  def __init__(self, data = {}):
    self._year = datetime.today().year
    self.month = 0
    self.membership_id = None
    self._membership = None
    self._amount = 0
    self._payments = None
    self._status = 'waiting'
    
    Model.__init__(self, data)

  @property
  def year(self):
    return self._year

  @year.setter
  def year(self, value):
    try:
      self._year = int(value)
    except:
      self._year = 0

  def to_label(self):
    return self.month_name() + " " + str(self.year)

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

  def paid(self):
    return sum(map(lambda p: p.amount, self.payments),0)

  def total(self, ignore_recharge = False):
    recharge = 0 if ignore_recharge else self.get_recharge()
    return self.amount+recharge

  def get_recharge(self, after_day = None, recharge_value = None):
    sets = settings.Settings.get_settings()
    
    if after_day is None: after_day = sets.recharge_after
    if recharge_value is None: recharge_value = sets.recharge_value

    recharge = 0
    
    sets = settings.Settings.get_settings()
    today = self.__class__._today().date()
    
    if self._status != 'paid':
      if self.date(after_day) < today:
        if re.match('^\d+%$',recharge_value):
          recharge = self.amount*(int(recharge_value[0:-1]))/100
        elif re.match('^\d+$',recharge_value):
          recharge = int(recharge_value)
    
    return recharge

  def date(self, after_day = None):
    if after_day is None: after_day = settings.Settings.get_settings().recharge_after

    return datetime.strptime(str(self.year)+"-"+str(self.month+1)+"-"+str(after_day),'%Y-%m-%d').date()

  def detailed_total(self):
    if self._status != 'paid_with_interests':
      recharge = self.get_recharge()
      recharge = '(+'+str(recharge)+')' if recharge > 0 else ''
    else:
      recharge = '(+'+str(self.paid() - self.amount)+')'

    return '$'+str(self.amount)+recharge

  def to_pay(self, ignore_recharge = False):
    return self.total(ignore_recharge)-self.paid()
  
  def month_name(self):
    return _t('months')[self.month]

  @property
  def status(self):
    return _a(self.cls_name(), self._status)

  @status.setter
  def status(self, value):
    self._status = value

  @property
  def membership(self):
    if self.membership_id and self._membership is None:
      self._membership = membership.Membership.find(self.membership_id)
    return self._membership

  @membership.setter
  def membership(self, value):
    self.membership_id = None if value is None else value.id
    self._membership = value

  @property
  def payments(self):
    if self._payments is None: self._payments = payment.Payment.for_installment(self.id).do_get()
    return self._payments

  def to_db(self):
    return {'year': self.year, 'month': self.month, 'membership_id': self.membership_id, 'amount': self.amount, 'status': self._status}

  def _is_valid(self):
    self.validate_numericallity_of('month', great_than_or_equal = 0, less_than_or_equal = 11)
    self.validate_numericallity_of('amount', great_than_or_equal = 0, only_integer = False)

  def add_payment(self, data):
    amount = Decimal(data['amount'])
    ignore_recharge = data['ignore_recharge']
    if amount <= self.to_pay(ignore_recharge):
      data['installment_id'] = self.id
      p = payment.Payment(data)
      p.user = self.get_student()
      if p.save():
        self.payments.append(p)
        if self.to_pay(ignore_recharge) == 0:
          if self.get_recharge() > 0 and ignore_recharge is False:
            self._status = 'paid_with_interests'
          else:
            self._status = 'paid'
          self.save(validate = False)
        return True
      else:
        return p.full_errors()
    else:
      return "No se puede agregar un pago con mayor valor que el resto a pagar."

  def get_student_id(self):
    s = self.get_student()
    return s.id if s else None

  def get_student(self):
    return self.membership.student

  def payments_details(self):
    return "\n".join(map(lambda p: p.to_s(), self.payments))

  def build_payment(self, data = {}):
    p = payment.Payment(data)
    p.installment = self
    self.payments.append(p)
    return p

  @classmethod
  def for_membership(cls,membership_id):
    return cls.where('membership_id', membership_id)

  def before_delete(self):
    for p in self.payments:
      p.description = p.description
      p.installment = None
      p.save(validate=False)
    return True

  @classmethod
  def overdues(cls, recharge_after = None, klass = None):
    today = cls._today()
    if recharge_after is None: recharge_after = settings.Settings.get_settings().recharge_after

    month = today.month-1
    year = today.year
    if today.day <= recharge_after: month = month-1
    if month == -1:
      month = 11
      year = year-1

    q = cls.where('status = "waiting" AND ((year = :year AND month <= :month) OR year < :year)', {'year': year, 'month': month}).set_join('LEFT JOIN memberships ON memberships.id = installments.membership_id LEFT JOIN users ON memberships.student_id = users.id').order_by('users.name ASC, users.lastname ASC')
    
    if klass is not None:
      where = 'memberships.for_id = :klass_id AND memberships.for_type = "Klass"'
      args = {'klass_id': klass.id}
      packages = package.Package.with_klass(klass)
      if packages.anything():
        where = '('+where+') OR (memberships.for_id IN (:p_ids) AND memberships.for_type = "Package")'
        args['p_ids'] = ','.join(map(lambda p: str(p.id), packages))

      q.where(where,args)
    
    return q

  @classmethod
  def _today(cls):
    return datetime.today()
