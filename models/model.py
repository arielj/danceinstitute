#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from decimal import Decimal
from database import Conn
from translations import _a, _e
import re
from lib.query_builder import Query

class MetaModel(type):
  def __getattr__(cls,name):
    if name in ['all','where','empty','anything','set_offset',
                'order_by','set_limit','set_join','set_select',
                'set_from','count','exists','first']:
      return getattr(Query(cls),name)
    else:
      raise AttributeError

class Model(object):
  __metaclass__ = MetaModel

  default_order = None
  
  def __str__(self):
    h = {}
    for att in vars(self):
      h[att] = getattr(self,att)
    return str(h)

  def __init__(self, attrs = {}):
    self.id = None
    self.errors = {}
    
    self.set_attrs(attrs)

  @classmethod
  def create(cls, attrs = {}):
    obj = cls(attrs)
    obj.save()
    return obj
    
  def set_attrs(self, data = {}):
    if data:
      for attr in data.keys():
        setattr(self,attr,data[attr])

  def add_error(self, field, error):
    if field not in self.errors:
      self.errors[field] = []
    self.errors[field].append(error)

  def clear_errors(self):
    self.errors = {}

  def full_errors(self):
    return "\n".join(sum(self.errors.values(),[]))
  
  def is_valid(self):
    self.clear_errors()
    self._is_valid()
    return not self.errors

  def validate_presence_of(self, field):
    if not getattr(self,field):
      self.add_error(field, _e('field_not_blank') % {'field': _a(self.cls_name(),field)})

  def validate_numericallity_of(self, field, great_than = None, less_than = None, great_than_or_equal = None, less_than_or_equal = None, only_integer = True):
    v = getattr(self,field)
    if v is not None and v != "":
      field_name = _a(self.cls_name(),field)
      err = False
      extra = False
      try:
        if only_integer:
          v = int(v)
        else:
          v = Decimal(str(v).replace(',','.'))
        if great_than is not None and v <= great_than:
          err = 'field_not_greate_than'
          extra = {'than': great_than}
        if less_than is not None and v >= less_than:
          err = 'field_not_less_than'
          extra = {'than': less_than}
        if great_than_or_equal is not None and v < great_than_or_equal:
          err = 'field_not_great_than_or_equal'
          extra = {'than': great_than_or_equal}
        if less_than_or_equal is not None and v > less_than_or_equal:
          err = 'field_not_less_than_or_equal'
          extra = {'than': less_than_or_equal}
      except:
        err = 'field_not_number'
      
      if err:
        args = {'field': field_name}
        if extra:
          args.update(extra)
        self.add_error(field, _e(err) % args)

  def validate_format_of(self, field, frmt = None, expr = None, message = None):
    if getattr(self,field):
      field_name = _a(self.cls_name(),field)
      if expr is None:
        if frmt == 'name':
          expr = '^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\'\s]+$'
          if message is None:
            message = _e('only_letters') % {'field': field_name}
      
      if expr is not None and not re.match(expr, getattr(self,field)):
        if message is None:
          message = _e('wrong_format') % {'field': field_name}
        
        self.add_error(field, message)

  def validate_quantity_of(self, field, great_than = None, less_than = None, message = None):
    field_name = _a(self.cls_name(),field)
    q = len(getattr(self,field))
    err = False
    if great_than is not None and q <= great_than:
      err = 'wrong_quantity'
    if less_than is not None and q >= less_than:
      err = 'wrong_quantity'
    
    if err:
      if message is None:
        message = _e(err) % {'field': field_name}
      self.add_error(field,message)

  def validate_has_many(self, relationship):
    are_valid = all(map(lambda o: o.is_valid(),getattr(self,relationship)))
    if not are_valid:
      self.add_error(relationship, _e('has_many_invalid') % {'relationship': _a(self.cls_name(),relationship)})

  def validate_uniqueness_of(self, field, value = None):
    if value is None:
      value = getattr(self,field)
    if value:
      q = Query(self.__class__).where(field,value)
      if self.id: q.where('id',self.id,comparission='!=')
      
      if q.anything():
        self.add_error(field, _e('already_in_use') % {'field': _a(self.cls_name(),field)})

  def cls_name(self):
    return self.__class__.__name__

  def save(self, validate = True):
    if not validate or self.is_valid():
      if self.before_save() is True:
        self.do_save()
        self.after_save()
        return True
      else:
        return False
    else:
      return False

  def do_save(self):
    if self.id is None:
      self.id = Conn.execute('INSERT INTO ' + self.table + '(' + ', '.join(map(lambda f: "`"+f+"`",self.fields_for_save)) + ') VALUES (' + ', '.join(map(lambda f: ':'+f, self.fields_for_save)) + ')', self.to_db()).lastrowid
      self.update_id_on_associations()
    else:
      values = self.to_db()
      values['id'] = self.id
      Conn.execute('UPDATE ' + self.table + ' SET ' + ', '.join(map(lambda k: "`"+k+"`"+'=:'+k, self.fields_for_save)) + ' WHERE id = :id', values )

  def before_save(self):
    return True

  def after_save(self):
    return True

  def is_new_record(self):
    return self.id is None

  def is_not_new_record(self):
    return not self.is_new_record()

  def can_delete(self):
    return True

  def delete(self):
    can_delete = self.can_delete()
    if can_delete is True:
      can_delete = self.before_delete()
      if can_delete is True:
        self.do_delete()
        self.after_delete()
    return can_delete

  def before_delete(self):
    return True

  def after_delete(self):
    return True

  @classmethod
  def get_conn(cls):
    return Conn

  def update_id_on_associations(self):
    return True

  def do_delete(self):
    Conn.execute('DELETE from ' + self.table + ' WHERE id = ?', (self.id, ))

  @classmethod
  def get_many(cls,query, params = ()):
    return map(lambda r: cls.from_db(r), Conn.execute(query,params).fetchall())

  @classmethod
  def get_one(cls,query, params = ()):
    r = Conn.execute(query,params).fetchone()
    return cls.from_db(r) if r else False
  
  @classmethod
  def from_db(cls,r):
    return cls(r)

  @classmethod
  def find(cls, id):
    return cls.find_by('id',id)

  @classmethod
  def find_by(cls, field, value):
    return Query(cls).where(field,value).first()
