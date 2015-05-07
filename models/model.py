#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from translations import _a, _e
import re

class Model(object):
  def __init__(self):
    self.id = None
    self.errors = {}
    
  def set_attrs(self, data = {}):
    if data:
      for attr in data.keys():
        self.__setattr__(attr,data[attr])

  def add_error(self, field, error):
    if field not in self.errors:
      self.errors[field] = []
    self.errors[field].append(error)

  def clear_errors(self):
    self.errors = {}

  def full_errors(self):
    errs = []
    for k in self.errors.keys():
      for e in self.errors[k]:
        errs.append(e) 
    
    return "\n".join(errs)
  
  def is_valid(self):
    self.clear_errors()
    self._is_valid()
    return not self.errors

  def validate_presence_of(self, field):
    if not vars(self)[field]:
      self.add_error(field, _e('field_not_blank') % {'field': _a(self.cls_name(),field)})

  def validate_numericallity_of(self, field, great_than = None, less_than = None):
    v = vars(self)[field]
    field_name = _a(self.cls_name(),field)
    err = False
    extra = False
    try:
      v = int(v)
      if great_than is not None and v <= great_than:
        err = 'field_not_greate_than'
        extra = {'than': great_than}
      if less_than is not None and v >= less_than:
        err = 'field_not_less_than'
        extra = {'than': less_than}
    except:
      err = 'field_not_number'
    
    if err:
      args = {'field': field_name}
      if extra:
        args.update(extra)
      self.add_error(field, _e(err) % args)

  def validate_format_of(self, field, frmt = None, expr = None, message = None):
    field_name = _a(self.cls_name(),field)
    if expr is None:
      if frmt == 'name':
        expr = '^[a-zA-ZáéíóúÁÉÍÓÚüÜñÑ\'\s]+$'
        if message is None:
          message = _e('only_letters') % {'field': field_name}
    
    if expr is not None and not re.match(expr, vars(self)[field]):
      if message is None:
        message = _e('wrong_format') % {'field': field_name}
      
      self.add_error(field, message)

  def cls_name(self):
    return self.__class__.__name__

  @classmethod
  def find(cls, id):
    # implementar bien cuando tenga la db
    return None

  def save(self):
    if self.is_valid():
      if self.is_new_record():
        if self.__class__.db.keys():
          self.id = max(self.__class__.db.keys())+1
        else:
          self.id = 1
      if self.before_save():
        self.do_save()
        self.after_save()
        return True
      else:
        return False
    else:
      return False

  def do_save(self):
    # meter en DB real
    self.__class__.db[self.id] = self.to_db()

  def before_save(self):
    return True

  def after_save(self):
    return True

  def is_new_record(self):
    return self.id is None

  def is_not_new_record(self):
    return not self.is_new_record()

  def delete(self):
    self.before_delete()
    del self.__class__.db[self.id]

  def before_delete(self):
    return True

