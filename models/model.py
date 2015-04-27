class Model(object):
  def __init__(self):
    self.id = None
    
  def set_attrs(self, data = {}):
    for attr in data.keys():
      self.__setattr__(attr,data[attr])


  @classmethod
  def find(cls, id):
    # implementar bien cuando tenga la db
    return None

  def save(self):
    # implementar bien cuando tenga la db
    return False

  def is_new_record(self):
    return self.id is None
