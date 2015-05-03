class Model(object):
  def __init__(self):
    self.id = None
    self.errors = {}
    
  def set_attrs(self, data = {}):
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
    self._is_valid()
    return not self.errors

  def validate_presence_of(self, field):
    if not vars(self)[field]:
      self.add_error(field, 'El campo ' + field + ' no puede estar en blanco')

  @classmethod
  def find(cls, id):
    # implementar bien cuando tenga la db
    return None

  def save(self):
    # implementar bien cuando tenga la db
    return False

  def is_new_record(self):
    return self.id is None
