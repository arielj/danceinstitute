from translations import _a, _e

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

  def validate_numericallity_of(self, field, greate_than = None, less_than = None):
    v = vars(self)[field]
    field_name = _a(self.cls_name(),field)
    err = False
    extra = False
    try:
      v = int(v)
      if greate_than is not None and v <= greate_than:
        err = 'field_not_greate_than'
        extra = {'than': greate_than}
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

  def cls_name(self):
    return self.__class__.__name__

  @classmethod
  def find(cls, id):
    # implementar bien cuando tenga la db
    return None

  def save(self):
    if self.is_valid():
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
    if self.id is None:
      i = max(self.__class__.db.keys())+1
      self.id = i
    self.__class__.db[self.id] = self.to_db()

  def before_save(self):
    return True

  def after_save(self):
    return True

  def is_new_record(self):
    return self.id is None

  def is_not_new_record(self):
    return not self.is_new_record()
